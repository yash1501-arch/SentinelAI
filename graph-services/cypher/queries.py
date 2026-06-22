CRIMINAL = """
MATCH (p:Person {id: $person_id})
OPTIONAL MATCH (p)-[r:MEMBER_OF]->(g:Gang)
OPTIONAL MATCH (p)-[:KNOWN|CO_CONSPIRATOR]-(associate:Person)
OPTIONAL MATCH (p)-[:INVOLVED_IN]->(c:Case)
OPTIONAL MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)
OPTIONAL MATCH (c)-[:OCCURRED_AT]->(l:Location)
RETURN p AS person,
       collect(DISTINCT g) AS gangs,
       collect(DISTINCT associate) AS associates,
       collect(DISTINCT {case: c, evidence: collect(DISTINCT e), location: l}) AS cases
"""

SUSPECT_NETWORK = """
MATCH (p:Person {id: $person_id})
CALL apoc.path.spanningTree(p, {
    relationshipFilter: 'KNOWN|CO_CONSPIRATOR|MEMBER_OF|FAMILY|ASSOCIATE',
    minLevel: 1,
    maxLevel: $depth
})
YIELD path
UNWIND nodes(path) AS node
UNWIND relationships(path) AS rel
RETURN collect(DISTINCT {id: node.id, type: labels(node)[0], name: node.name}) AS nodes,
       collect(DISTINCT {source: startNode(rel).id,
                         target: endNode(rel).id,
                         type: type(rel)}) AS relationships
"""

GANG_NETWORK = """
MATCH (g:Gang {id: $gang_id})
MATCH (g)<-[:MEMBER_OF]-(member:Person)
OPTIONAL MATCH (member)-[r:KNOWN|CO_CONSPIRATOR]-(other:Person)
WHERE other IS NOT NULL
RETURN g AS gang,
       collect(DISTINCT member) AS members,
       collect(DISTINCT {source: member.id, target: other.id, type: type(r)}) AS connections
"""

CONNECTION_PATH = """
MATCH path = shortestPath(
    (a:Person {id: $person_a})-[:KNOWN|CO_CONSPIRATOR|MEMBER_OF|FAMILY*1..$max_depth]-(b:Person {id: $person_b})
)
UNWIND nodes(path) AS node
UNWIND relationships(path) AS rel
RETURN [n IN nodes(path) | {id: n.id, type: labels(n)[0], name: n.name}] AS node_sequence,
       [r IN relationships(path) | {source: startNode(r).id, target: endNode(r).id, type: type(r)}] AS rel_sequence,
       length(path) AS hops
"""

CASE_TIMELINE = """
MATCH (c:Case {id: $case_id})
OPTIONAL MATCH (c)-[:INVOLVES]->(p:Person)
OPTIONAL MATCH (c)-[:HAS_EVIDENCE]->(e:Evidence)
OPTIONAL MATCH (c)-[:OCCURRED_AT]->(l:Location)
OPTIONAL MATCH (c)-[:FOLLOWED_BY]->(next:Case)
OPTIONAL MATCH (prev:Case)-[:FOLLOWED_BY]->(c)
RETURN c AS case,
       collect(DISTINCT p) AS persons,
       collect(DISTINCT e) AS evidence,
       collect(DISTINCT l) AS locations,
       collect(DISTINCT prev) AS preceding_cases,
       collect(DISTINCT next) AS subsequent_cases
"""

SIMILAR_MODUS_OPERANDI = """
MATCH (c:Case {id: $case_id})
MATCH (c)-[:HAS_MO]->(mo:ModusOperandi)
MATCH (similar:Case)-[:HAS_MO]->(similar_mo:ModusOperandi)
WHERE similar.id <> $case_id
  AND (mo.technique = similar_mo.technique
       OR mo.signature = similar_mo.signature
       OR mo.entry_point = similar_mo.entry_point)
RETURN similar.id AS similar_case_id,
       similar.fir_number AS fir_number,
       mo.technique AS shared_technique,
       count(*) AS similarity_score
ORDER BY similarity_score DESC
LIMIT $top_k
"""

RECIDIVISM_RISK = """
MATCH (p:Person {id: $person_id})
MATCH (p)-[:INVOLVED_IN]->(c:Case)
WITH p, count(c) AS total_cases,
     collect(c.is_solved) AS solved_flags,
     collect(c.severity) AS severities
RETURN p.id AS person_id,
       total_cases,
       total_cases > 1 AS is_repeat_offender,
       [s IN solved_flags WHERE s = false] AS unsolved_cases,
       [sev IN severities WHERE sev = 'heinous'] AS heinous_cases_count
"""

GEO_SPATIAL_HOTSPOT = """
MATCH (c:Case)-[:OCCURRED_AT]->(l:Location)
WHERE l.latitude IS NOT NULL AND l.longitude IS NOT NULL
  AND c.incident_date >= datetime($date_from)
  AND c.incident_date <= datetime($date_to)
WITH l.latitude AS lat, l.longitude AS lon, count(*) AS density
WITH lat, lon, density,
     round(lat * 100) / 100 AS lat_bin,
     round(lon * 100) / 100 AS lon_bin
WITH lat_bin, lon_bin, sum(density) AS cluster_density
ORDER BY cluster_density DESC
RETURN avg(lat_bin) AS center_lat,
       avg(lon_bin) AS center_lon,
       sum(cluster_density) AS crime_density
LIMIT 20
"""

PERSON_CENTRALITY = """
MATCH (p:Person)
OPTIONAL MATCH (p)-[r]-()
WITH p, count(r) AS degree
OPTIONAL MATCH (p)-[:KNOWN|CO_CONSPIRATOR]-(neighbor:Person)
WHERE neighbor IS NOT NULL
WITH p, degree, count(DISTINCT neighbor) AS connections
ORDER BY connections DESC
RETURN p.id AS person_id,
       p.name AS name,
       degree,
       connections,
       (connections * 1.0 / (degree + 1)) AS influence_score
"""

QUERIES = {
    "criminal": CRIMINAL,
    "suspect_network": SUSPECT_NETWORK,
    "gang_network": GANG_NETWORK,
    "connection_path": CONNECTION_PATH,
    "case_timeline": CASE_TIMELINE,
    "similar_modus_operandi": SIMILAR_MODUS_OPERANDI,
    "recidivism_risk": RECIDIVISM_RISK,
    "geo_hotspot": GEO_SPATIAL_HOTSPOT,
    "person_centrality": PERSON_CENTRALITY,
}
