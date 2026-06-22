// ============================================================
// SENTINELAI - NEO4J KNOWLEDGE GRAPH SCHEMA
// ============================================================

// Create uniqueness constraints
CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT victim_id IF NOT EXISTS FOR (v:Victim) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT accused_id IF NOT EXISTS FOR (a:Accused) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT witness_id IF NOT EXISTS FOR (w:Witness) REQUIRE w.id IS UNIQUE;
CREATE CONSTRAINT vehicle_id IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT vehicle_reg IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.registration_number IS UNIQUE;
CREATE CONSTRAINT phone_id IF NOT EXISTS FOR (p:Phone) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT phone_number IF NOT EXISTS FOR (p:Phone) REQUIRE p.number IS UNIQUE;
CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:BankAccount) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT account_number IF NOT EXISTS FOR (a:BankAccount) REQUIRE a.account_number IS UNIQUE;
CREATE CONSTRAINT crime_id IF NOT EXISTS FOR (c:Crime) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT fir_number IF NOT EXISTS FOR (f:FIR) REQUIRE f.fir_number IS UNIQUE;
CREATE CONSTRAINT location_id IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT org_id IF NOT EXISTS FOR (o:Organization) REQUIRE o.id IS UNIQUE;
CREATE CONSTRAINT gang_id IF NOT EXISTS FOR (g:Gang) REQUIRE g.id IS UNIQUE;
CREATE CONSTRAINT weapon_id IF NOT EXISTS FOR (w:Weapon) REQUIRE w.id IS UNIQUE;

// Create indexes for performance
CREATE INDEX person_name_idx IF NOT EXISTS FOR (p:Person) ON (p.first_name, p.last_name);
CREATE INDEX person_phone_idx IF NOT EXISTS FOR (p:Person) ON (p.phone);
CREATE INDEX crime_date_idx IF NOT EXISTS FOR (c:Crime) ON (c.incident_date);
CREATE INDEX crime_type_idx IF NOT EXISTS FOR (c:Crime) ON (c.crime_type);
CREATE INDEX location_coords_idx IF NOT EXISTS FOR (l:Location) ON (l.latitude, l.longitude);

// ============================================================
// NODE LABELS AND PROPERTIES
// ============================================================

// Note: Nodes are created through the application
// This file documents the schema design

// (:Person {
//   id: string, first_name: string, last_name: string, alias: string[],
//   date_of_birth: date, gender: string, nationality: string,
//   occupation: string, phone: string, aadhaar: string,
//   risk_score: float, is_repeat_offender: boolean
// })

// (:Victim {
//   id: string, injury_severity: string, property_loss: float,
//   is_minor: boolean
// })

// (:Accused {
//   id: string, arrest_date: datetime, charge_sections: string[],
//   bail_status: string, is_repeat_offender: boolean, risk_score: float
// })

// (:Witness {
//   id: string, witness_type: string, is_eye_witness: boolean,
//   credibility_score: float
// })

// (:Crime {
//   id: string, fir_number: string, incident_date: date,
//   incident_time: string, crime_type: string, category: string,
//   description: string, modus_operandi: string,
//   property_loss: float, injury_count: int, fatality_count: int,
//   is_solved: boolean, day_of_week: string, time_period: string,
//   police_station: string, district: string
// })

// (:Vehicle {
//   id: string, registration_number: string, make: string,
//   model: string, year: int, color: string, vehicle_type: string,
//   is_stolen: boolean
// })

// (:Phone {
//   id: string, number: string, imei: string, operator: string,
//   is_prepaid: boolean, is_active: boolean
// })

// (:BankAccount {
//   id: string, account_number: string, ifsc_code: string,
//   bank_name: string, account_type: string, is_active: boolean
// })

// (:Weapon {
//   id: string, weapon_type: string, make: string, serial_number: string,
//   is_illegal: boolean
// })

// (:Location {
//   id: string, name: string, location_type: string,
//   latitude: float, longitude: float, city: string,
//   district: string, state: string, address: string
// })

// (:Organization {
//   id: string, name: string, type: string,
//   registration_number: string, is_legitimate: boolean
// })

// (:Gang {
//   id: string, name: string, alias: string[], type: string,
//   territory: string, primary_crime_type: string,
//   estimated_strength: int, risk_level: string, is_active: boolean
// })

// ============================================================
// RELATIONSHIPS
// ============================================================

// Person to Crime
// (p:Person)-[:PARTICIPATED_IN {role: 'victim'|'accused'|'witness'|'offender'}]->(c:Crime)

// Person to Person
// (p1:Person)-[:KNOWS {relationship_type: 'friend'|'family'|'associate'|'rival', since: date}]->(p2:Person)
// (p1:Person)-[:CONNECTED_WITH {method: 'phone'|'email'|'co-located', confidence: float}]->(p2:Person)

// Person to Vehicle
// (p:Person)-[:OWNS]->(v:Vehicle)
// (p:Person)-[:USED {incident_id: string}]->(v:Vehicle)

// Person to Phone
// (p:Person)-[:HAS]->(ph:Phone)
// (p:Person)-[:CALLED {duration: int, timestamp: datetime, frequency: int}]->(ph:Phone)

// Person to BankAccount
// (p:Person)-[:HAS_ACCOUNT]->(a:BankAccount)

// BankAccount to BankAccount (Transactions)
// (a1:BankAccount)-[:TRANSFERRED_TO {
//   amount: float, transaction_date: datetime,
//   transaction_id: string, mode: string,
//   is_suspicious: boolean, risk_score: float
// }]->(a2:BankAccount)

// Person to Location
// (p:Person)-[:LIVES_AT]->(l:Location)
// (p:Person)-[:VISITED {timestamp: datetime, frequency: int}]->(l:Location)

// Crime to Location
// (c:Crime)-[:OCCURRED_AT]->(l:Location)

// Crime to Weapon
// (c:Crime)-[:INVOLVED_WEAPON]->(w:Weapon)

// Person to Organization
// (p:Person)-[:MEMBER_OF {role: string, joined_at: datetime}]->(o:Organization)

// Person to Gang
// (p:Person)-[:MEMBER_OF_GANG {role: string, joined_at: datetime, is_active: boolean}]->(g:Gang)

// Gang Rivalry
// (g1:Gang)-[:RIVAL_OF]->(g2:Gang)

// Crime to Crime (Similarity)
// (c1:Crime)-[:SIMILAR_TO {score: float, method: string}]->(c2:Crime)

// Person to Person (Financial Link)
// (p1:Person)-[:FINANCIAL_LINK {
//   total_transaction_amount: float,
//   transaction_count: int,
//   risk_flag: boolean
// }]->(p2:Person)

// ============================================================
// SAMPLE QUERIES (documentation)
// ============================================================

// Find all associates of a known criminal:
// MATCH (p:Person {id: $personId})-[:KNOWS]-(associate:Person)
// RETURN associate, p

// Detect money laundering chains:
// MATCH path = (a1:BankAccount)-[:TRANSFERRED_TO*3..6]->(a2:BankAccount)
// WHERE ALL(r in relationships(path) WHERE r.is_suspicious = true)
// RETURN path LIMIT 10

// Find hidden connections between two people:
// MATCH path = shortestPath((p1:Person {id: $personA})-[:KNOWS|MEMBER_OF|CALLED*..6]-(p2:Person {id: $personB}))
// RETURN path

// Community detection on criminal networks:
// CALL gds.louvain.stream('crime-graph')
// YIELD nodeId, communityId
// RETURN communityId, count(*) AS members
// ORDER BY members DESC

// Find repeat offenders and their networks:
// MATCH (a:Accused)-[:PARTICIPATED_IN]->(c:Crime)
// WITH a, count(c) as crimeCount
// WHERE crimeCount > 1
// MATCH (a)-[:KNOWS]-(associate:Person)
// RETURN a, crimeCount, collect(associate) as network
