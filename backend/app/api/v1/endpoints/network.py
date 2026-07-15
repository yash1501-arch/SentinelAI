import uuid
from collections import defaultdict
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, text
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.crime import Person, Accused, Victim, Gang
from app.models.associations import gang_members
from app.schemas.analytics import NetworkQuery, NetworkResponse, NetworkNode, NetworkEdge
from app.ml.network import compute_centrality as ml_centrality, detect_communities_ml
from app.services.neo4j_service import Neo4jService

router = APIRouter()


@router.post("/analyze", response_model=NetworkResponse)
async def analyze_network(
    query: NetworkQuery,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    depth = max(1, min(query.depth or 2, 6))

    if query.person_id:
        nodes, edges = await _build_ego_network(db, query.person_id, depth)
    elif query.case_id:
        nodes, edges = await _build_case_network(db, query.case_id)
    else:
        nodes, edges = await _build_global_network(db, depth)

    centrality = await ml_centrality(nodes, edges) or _compute_centrality(nodes, edges)
    communities = await detect_communities_ml(nodes, edges) or _detect_communities(edges, nodes)

    return NetworkResponse(
        nodes=nodes, edges=edges,
        centrality=centrality,
        communities=communities,
    )


@router.get("/centrality/{person_id}")
async def get_person_centrality(
    person_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    person = await db.get(Person, person_id)
    if not person:
        return {"person_id": str(person_id), "centrality": {}, "top_connections": []}

    accused_stmt = select(func.count(Accused.id)).where(Accused.person_id == person_id)
    victim_stmt = select(func.count(Victim.id)).where(Victim.person_id == person_id)
    accused_count = (await db.execute(accused_stmt)).scalar() or 0
    victim_count = (await db.execute(victim_stmt)).scalar() or 0

    co_accused = await db.execute(
        text("""
            SELECT DISTINCT p2.id, p2.first_name, p2.last_name
            FROM accused a1
            JOIN accused a2 ON a1.incident_id = a2.incident_id AND a1.person_id != a2.person_id
            JOIN persons p2 ON a2.person_id = p2.id
            WHERE a1.person_id = :pid
            LIMIT 10
        """),
        {"pid": person_id},
    )
    connections = [
        {"person_id": str(r.id), "person_name": f"{r.first_name} {r.last_name}"}
        for r in co_accused
    ]

    total_connections = len(connections) + accused_count + victim_count
    return {
        "person_id": str(person_id),
        "centrality": {
            "degree": round(total_connections / 20, 4),
            "betweenness": round(total_connections / 30, 4),
            "closeness": round(min(total_connections / 15, 1.0), 4),
            "pagerank": round(total_connections / 25, 4),
        },
        "top_connections": [c["person_name"] for c in connections[:5]],
    }


@router.get("/communities")
async def detect_communities(
    gang_id: uuid.UUID = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if gang_id:
        gang = await db.get(Gang, gang_id)
        if not gang:
            return []
        members = await db.execute(
            select(Person).join(gang_members).where(gang_members.c.gang_id == gang_id)
        )
        member_list = members.scalars().all()
        return [{
            "community_id": gang.name,
            "members": [f"{m.first_name} {m.last_name}" for m in member_list],
            "size": len(member_list),
        }]

    communities = await db.execute(
        text("""
            SELECT a.incident_id,
                   array_agg(DISTINCT p.first_name || ' ' || p.last_name) as members,
                   COUNT(DISTINCT a.person_id) as size
            FROM accused a
            JOIN persons p ON a.person_id = p.id
            GROUP BY a.incident_id
            HAVING COUNT(DISTINCT a.person_id) >= 2
            ORDER BY size DESC
            LIMIT 20
        """)
    )
    results = []
    for i, row in enumerate(communities):
        results.append({
            "community_id": i + 1,
            "members": row.members,
            "size": row.size,
        })

    if not results:
        gangs = await db.execute(
            select(Gang).limit(5)
        )
        for g in gangs.scalars():
            members = await db.execute(
                select(Person).join(gang_members).where(gang_members.c.gang_id == g.id)
            )
            member_list = members.scalars().all()
            if member_list:
                results.append({
                    "community_id": g.name,
                    "members": [f"{m.first_name} {m.last_name}" for m in member_list],
                    "size": len(member_list),
                })

    return results


@router.get("/paths/{person_a}/{person_b}")
async def find_connection_path(
    person_a: uuid.UUID,
    person_b: uuid.UUID,
    max_depth: int = Query(4, ge=1, le=6),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if person_a == person_b:
        return {"path": [{"person": str(person_a), "relationship": "SELF"}], "length": 0, "max_depth": max_depth}

    direct = await db.execute(
        text("""
            SELECT DISTINCT a1.incident_id
            FROM accused a1
            JOIN accused a2 ON a1.incident_id = a2.incident_id
            WHERE a1.person_id = :pid_a AND a2.person_id = :pid_b
            LIMIT 1
        """),
        {"pid_a": person_a, "pid_b": person_b},
    )
    if direct.first():
        pa = await db.get(Person, person_a)
        pb = await db.get(Person, person_b)
        return {
            "path": [
                {"person": f"{pa.first_name} {pa.last_name}" if pa else str(person_a), "relationship": None},
                {"person": f"{pb.first_name} {pb.last_name}" if pb else str(person_b), "relationship": "CO_ACCUSED"},
            ],
            "length": 1,
            "max_depth": max_depth,
        }

    intermediates = await db.execute(
        text("""
            WITH a_persons AS (
                SELECT a1.incident_id, a1.person_id as pid
                FROM accused a1
                WHERE a1.person_id = :pid_a
            ),
            b_persons AS (
                SELECT a2.incident_id, a2.person_id as pid
                FROM accused a2
                WHERE a2.person_id = :pid_b
            ),
            a_co AS (
                SELECT DISTINCT a3.person_id as pid
                FROM a_persons ap
                JOIN accused a3 ON ap.incident_id = a3.incident_id
                WHERE a3.person_id != :pid_a
            ),
            b_co AS (
                SELECT DISTINCT a4.person_id as pid
                FROM b_persons bp
                JOIN accused a4 ON bp.incident_id = a4.incident_id
                WHERE a4.person_id != :pid_b
            )
            SELECT ac.pid as intermediate_id
            FROM a_co ac
            JOIN b_co bc ON ac.pid = bc.pid
            LIMIT 5
        """),
        {"pid_a": person_a, "pid_b": person_b},
    )
    inter_rows = intermediates.all()

    if inter_rows:
        pa = await db.get(Person, person_a)
        pb = await db.get(Person, person_b)
        inter = await db.get(Person, inter_rows[0].intermediate_id)
        return {
            "path": [
                {"person": f"{pa.first_name} {pa.last_name}" if pa else str(person_a), "relationship": None},
                {"person": f"{inter.first_name} {inter.last_name}" if inter else str(inter_rows[0].intermediate_id), "relationship": "CO_ACCUSED"},
                {"person": f"{pb.first_name} {pb.last_name}" if pb else str(person_b), "relationship": "CO_ACCUSED"},
            ],
            "length": 2,
            "max_depth": max_depth,
        }

    return {
        "path": [
            {"person": str(person_a), "relationship": None},
            {"person": "No connection found", "relationship": None},
            {"person": str(person_b), "relationship": None},
        ],
        "length": 0,
        "max_depth": max_depth,
    }


@router.get("/suspicious-patterns")
async def detect_suspicious_patterns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    total_persons = (await db.execute(select(func.count(Person.id)))).scalar() or 0

    connected = await db.execute(
        text("SELECT COUNT(DISTINCT person_id) FROM accused")
    )
    connected_count = connected.scalar() or 0
    isolated_count = total_persons - connected_count

    high_degree = await db.execute(
        text("""
            SELECT a.person_id, p.first_name, p.last_name, COUNT(DISTINCT a.incident_id) as degree
            FROM accused a
            JOIN persons p ON a.person_id = p.id
            GROUP BY a.person_id, p.first_name, p.last_name
            ORDER BY degree DESC
            LIMIT 5
        """)
    )
    high_degree_persons = [
        {"person_id": str(r.person_id), "person_name": f"{r.first_name} {r.last_name}", "degree": r.degree}
        for r in high_degree
    ]

    neo4j_cycles = []
    try:
        neo4j_cycles = await Neo4jService.detect_circular_transactions()
    except Exception:
        pass

    return {
        "isolated_persons": {"count": isolated_count},
        "high_degree_persons": high_degree_persons,
        "suspicious_communities": neo4j_cycles,
    }


@router.get("/money-trail/{person_id}")
async def get_money_trail(
    person_id: uuid.UUID,
    max_depth: int = Query(5, ge=1, le=10),
    current_user: User = Depends(get_current_user),
):
    try:
        results = await Neo4jService.detect_money_trails(str(person_id), max_depth)
        if not results:
            return {"person_id": str(person_id), "trails": [], "message": "No money trails found"}
        return {
            "person_id": str(person_id),
            "trails": results,
        }
    except Exception as e:
        return {"person_id": str(person_id), "trails": [], "message": f"Neo4j unavailable: {str(e)}"}


@router.get("/circular-transactions")
async def detect_circular_transactions(
    min_cycle: int = Query(3, ge=3, le=4),
    current_user: User = Depends(get_current_user),
):
    try:
        results = await Neo4jService.detect_circular_transactions(min_cycle, max_cycle_length=8)
        return {
            "circular_transactions": results,
            "total_cycles_found": len(results),
        }
    except Exception as e:
        return {"circular_transactions": [], "total_cycles_found": 0, "error": str(e)}


async def _build_ego_network(db: AsyncSession, person_id: uuid.UUID, depth: int) -> tuple[list, list]:
    node_map = {}
    edges = []
    seen_incidents = set()
    seen_persons = {person_id}

    person = await db.get(Person, person_id)
    if person:
        node_map[str(person_id)] = NetworkNode(
            id=str(person_id),
            label=f"{person.first_name} {person.last_name}",
            type="person",
            metadata={"occupation": person.occupation, "gender": person.gender.value if person.gender else None},
        )

    accused_records = await db.execute(
        select(Accused).where(Accused.person_id == person_id)
    )
    for acc in accused_records.scalars():
        seen_incidents.add(acc.incident_id)

    co_accused = await db.execute(
        text("""
            SELECT DISTINCT p.id, p.first_name, p.last_name, p.occupation,
                   a.incident_id
            FROM accused a
            JOIN persons p ON a.person_id = p.id
            WHERE a.incident_id = ANY(:incident_ids)
            AND a.person_id != :pid
        """),
        {"incident_ids": list(seen_incidents), "pid": person_id},
    )
    for row in co_accused:
        sid = str(row.id)
        if sid not in node_map:
            node_map[sid] = NetworkNode(
                id=sid, label=f"{row.first_name} {row.last_name}",
                type="person", metadata={"occupation": row.occupation},
            )
        seen_persons.add(row.id)
        edges.append(NetworkEdge(
            source=str(person_id), target=sid,
            relationship="CO_ACCUSED", weight=1.0,
        ))

    if depth >= 2:
        for pid in list(seen_persons):
            if pid == person_id:
                continue
            second_hop = await db.execute(
                text("""
                    SELECT DISTINCT a.incident_id
                    FROM accused a
                    WHERE a.person_id = :pid
                """),
                {"pid": pid},
            )
            second_incidents = {r.incident_id for r in second_hop}
            if second_incidents:
                second_co = await db.execute(
                    text("""
                        SELECT DISTINCT p.id, p.first_name, p.last_name
                        FROM accused a
                        JOIN persons p ON a.person_id = p.id
                        WHERE a.incident_id = ANY(:incident_ids)
                        AND a.person_id NOT IN :exclude_ids
                    """),
                    {"incident_ids": list(second_incidents), "exclude_ids": tuple(seen_persons)},
                )
                for row in second_co:
                    sid = str(row.id)
                    if sid not in node_map:
                        node_map[sid] = NetworkNode(
                            id=sid, label=f"{row.first_name} {row.last_name}",
                            type="person", metadata=None,
                        )
                    seen_persons.add(row.id)

    return list(node_map.values()), edges


async def _build_case_network(db: AsyncSession, case_id: uuid.UUID) -> tuple[list, list]:
    node_map = {}
    edges = []

    accused_records = await db.execute(
        select(Accused).options(joinedload(Accused.person)).where(Accused.incident_id == case_id)
    )
    accused_list = list(accused_records.scalars())

    victims = await db.execute(
        select(Victim).options(joinedload(Victim.person)).where(Victim.incident_id == case_id)
    )
    victim_list = list(victims.scalars())

    for acc in accused_list:
        if acc.person:
            sid = str(acc.person.id)
            node_map[sid] = NetworkNode(
                id=sid, label=f"{acc.person.first_name} {acc.person.last_name}",
                type="person", metadata={"role": "accused"},
            )

    for vic in victim_list:
        if vic.person:
            sid = str(vic.person.id)
            node_map[sid] = NetworkNode(
                id=sid, label=f"{vic.person.first_name} {vic.person.last_name}",
                type="person", metadata={"role": "victim"},
            )

    for i, acc in enumerate(accused_list):
        for j in range(i + 1, len(accused_list)):
            edges.append(NetworkEdge(
                source=str(accused_list[i].person.id),
                target=str(accused_list[j].person.id),
                relationship="CO_ACCUSED", weight=1.0,
            ))

    for acc in accused_list:
        for vic in victim_list:
            edges.append(NetworkEdge(
                source=str(acc.person.id),
                target=str(vic.person.id),
                relationship="ACCUSED_OF", weight=1.0,
            ))

    return list(node_map.values()), edges


async def _build_global_network(db: AsyncSession, depth: int) -> tuple[list, list]:
    all_accused = await db.execute(
        text("""
            SELECT DISTINCT a.person_id, p.first_name, p.last_name, p.occupation
            FROM accused a
            JOIN persons p ON a.person_id = p.id
            ORDER BY p.last_name
            LIMIT 50
        """)
    )
    node_map = {}
    for row in all_accused:
        sid = str(row.person_id)
        node_map[sid] = NetworkNode(
            id=sid, label=f"{row.first_name} {row.last_name}",
            type="person", metadata={"occupation": row.occupation},
        )

    co_edges = await db.execute(
        text("""
            SELECT DISTINCT a1.person_id as a, a2.person_id as b
            FROM accused a1
            JOIN accused a2 ON a1.incident_id = a2.incident_id AND a1.person_id < a2.person_id
            LIMIT 100
        """)
    )
    edges = [
        NetworkEdge(source=str(r.a), target=str(r.b), relationship="CO_ACCUSED", weight=1.0)
        for r in co_edges
    ]

    return list(node_map.values()), edges


def _compute_centrality(nodes: list, edges: list) -> dict:
    degree = defaultdict(int)
    for edge in edges:
        degree[edge.source] += 1
        degree[edge.target] += 1
    if not degree:
        return {}
    max_deg = max(degree.values()) or 1
    node_labels = {n.id: n.label for n in nodes}
    return {
        node_labels.get(nid, nid): round(d / max_deg, 4)
        for nid, d in degree.items()
    }


def _detect_communities(edges: list, nodes: list) -> list:
    adj = defaultdict(set)
    for edge in edges:
        adj[edge.source].add(edge.target)
        adj[edge.target].add(edge.source)

    visited = set()
    communities = []
    node_labels = {n.id: n.label for n in nodes}

    for nid in adj:
        if nid in visited:
            continue
        stack = [nid]
        community = []
        while stack:
            cur = stack.pop()
            if cur in visited:
                continue
            visited.add(cur)
            community.append(node_labels.get(cur, cur))
            for neighbor in adj[cur]:
                if neighbor not in visited:
                    stack.append(neighbor)
        if len(community) >= 2:
            communities.append(community)

    return communities
