# SENTINEL AI — Neo4j Graph Design

## Platform: Neo4j Aura (Cloud Graph Database)

## Node Types

| Label | Key Properties | Index/Constraint |
|-------|---------------|------------------|
| Person | id, first_name, last_name, alias, gender, dob, phone, aadhaar | Unique: id |
| Victim | id, injury_severity, property_loss, is_minor | Unique: id |
| Accused | id, arrest_date, charge_sections, bail_status, risk_score | Unique: id |
| Witness | id, witness_type, is_eye_witness, credibility_score | Unique: id |
| Crime | id, fir_number, incident_date, crime_type, district, description | Unique: id |
| Location | id, name, latitude, longitude, city, district | Unique: id |
| Vehicle | id, registration_number, make, model, color | Unique: reg_no |
| BankAccount | id, account_number, ifsc, bank_name | Unique: acct_no |
| Phone | id, number, imei, operator, is_prepaid | Unique: number |
| Organization | id, name, type, registration_number | Unique: id |
| Gang | id, name, alias, territory, risk_level | Unique: id |
| Weapon | id, weapon_type, make, serial_number | Unique: id |

## Relationship Types

| Relationship | Source → Target | Properties | Use Case |
|-------------|----------------|------------|----------|
| PARTICIPATED_IN | Person → Crime | role: string | Links person to incident |
| KNOWS | Person ↔ Person | relationship_type, since | Criminal associations |
| OWNS | Person → Vehicle | | Vehicle ownership |
| USED | Person → Vehicle | incident_id | Vehicle used in crime |
| HAS_ACCOUNT | Person → BankAccount | | Account ownership |
| TRANSFERRED_TO | BankAccount → BankAccount | amount, date, is_suspicious | Money trail |
| CALLED | Person → Phone | duration, timestamp | Communication records |
| LIVES_AT | Person → Location | address_type | Residence tracking |
| VISITED | Person → Location | timestamp, frequency | Location history |
| OCCURRED_AT | Crime → Location | | Crime scene |
| INVOLVED_WEAPON | Crime → Weapon | | Weapon used |
| MEMBER_OF | Person → Organization | role | Organizational links |
| MEMBER_OF_GANG | Person → Gang | role, is_active | Gang membership |
| RIVAL_OF | Gang → Gang | | Gang rivalries |
| SIMILAR_TO | Crime → Crime | score, method | Case similarity |
| FINANCIAL_LINK | Person → Person | total_amount, count, risk_flag | Financial connection |

## Key Cypher Queries

### Find criminal network
```cypher
MATCH (p:Person {id: $personId})-[:KNOWS|MEMBER_OF_GANG*1..3]-(connection)
RETURN p, collect(distinct connection) as network
```

### Detect money laundering chain
```cypher
MATCH path = (a:BankAccount)-[:TRANSFERRED_TO*3..6]->(b:BankAccount)
WHERE ALL(r in relationships(path) WHERE r.is_suspicious = true)
RETURN path LIMIT 10
```

### Find shortest connection path
```cypher
MATCH path = shortestPath(
  (p1:Person {id: $p1})-[:KNOWS|MEMBER_OF*..6]-(p2:Person {id: $p2})
)
RETURN path
```

### Community detection (GDS)
```cypher
CALL gds.louvain.stream('crime-graph')
YIELD nodeId, communityId
MATCH (p:Person) WHERE id(p) = nodeId
RETURN communityId, collect(p.first_name + ' ' + p.last_name) as members
```

### Repeat offenders
```cypher
MATCH (a:Accused)-[:PARTICIPATED_IN]->(c:Crime)
WITH a, count(c) as crimeCount WHERE crimeCount > 1
MATCH (a)-[:KNOWS]-(associate:Person)
RETURN a, crimeCount, collect(associate) as network
```

## Graph Algorithms

| Algorithm | Library | Purpose |
|-----------|---------|---------|
| PageRank | Neo4j GDS | Identify influential criminals |
| Betweenness Centrality | Neo4j GDS | Find bridge persons/gatekeepers |
| Louvain Community Detection | Neo4j GDS | Gang structure discovery |
| Shortest Path | Neo4j Core | Connection between entities |
| Node Similarity | Neo4j GDS | Find similar offenders |
