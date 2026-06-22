"""CSV batch importer for Neo4j — handles persons, cases, evidence, locations."""
import csv
import uuid
from datetime import datetime
from .base_importer import BaseImporter


class CSVImporter(BaseImporter):
    async def import_persons(self, csv_path: str) -> int:
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "id": row.get("id", str(uuid.uuid4())),
                    "first_name": row.get("first_name", ""),
                    "last_name": row.get("last_name", ""),
                    "phone": row.get("phone", ""),
                    "gender": row.get("gender", ""),
                    "date_of_birth": row.get("date_of_birth", ""),
                    "occupation": row.get("occupation", ""),
                    "aadhaar_number": row.get("aadhaar_number", ""),
                })
        return await self.execute_batch("""
            MERGE (p:Person {id: row.id})
            SET p.first_name = row.first_name,
                p.last_name = row.last_name,
                p.phone = row.phone,
                p.gender = row.gender,
                p.date_of_birth = row.date_of_birth,
                p.occupation = row.occupation,
                p.aadhaar_number = row.aadhaar_number
        """, records)

    async def import_cases(self, csv_path: str) -> int:
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "id": row.get("id", str(uuid.uuid4())),
                    "fir_number": row.get("fir_number", ""),
                    "description": row.get("description", ""),
                    "incident_date": row.get("incident_date", ""),
                    "crime_type": row.get("crime_type", ""),
                    "is_solved": row.get("is_solved", "false").lower() == "true",
                    "severity": row.get("severity", "standard"),
                })
        return await self.execute_batch("""
            MERGE (c:Case {id: row.id})
            SET c.fir_number = row.fir_number,
                c.description = row.description,
                c.incident_date = row.incident_date,
                c.crime_type = row.crime_type,
                c.is_solved = row.is_solved,
                c.severity = row.severity
        """, records)

    async def import_locations(self, csv_path: str) -> int:
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "id": row.get("id", str(uuid.uuid4())),
                    "case_id": row.get("case_id", ""),
                    "latitude": float(row.get("latitude", 0)),
                    "longitude": float(row.get("longitude", 0)),
                    "address": row.get("address", ""),
                    "district": row.get("district", ""),
                    "city": row.get("city", ""),
                })
        await self.execute_batch("""
            MERGE (l:Location {id: row.id})
            SET l.latitude = row.latitude,
                l.longitude = row.longitude,
                l.address = row.address,
                l.district = row.district,
                l.city = row.city
        """, records)
        return await self.execute_batch("""
            MATCH (c:Case {id: row.case_id})
            MATCH (l:Location {id: row.id})
            MERGE (c)-[:OCCURRED_AT]->(l)
        """, records)

    async def import_evidence(self, csv_path: str) -> int:
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "id": row.get("id", str(uuid.uuid4())),
                    "case_id": row.get("case_id", ""),
                    "name": row.get("name", ""),
                    "evidence_type": row.get("evidence_type", ""),
                    "description": row.get("description", ""),
                })
        await self.execute_batch("""
            MERGE (e:Evidence {id: row.id})
            SET e.name = row.name,
                e.evidence_type = row.evidence_type,
                e.description = row.description
        """, records)
        return await self.execute_batch("""
            MATCH (c:Case {id: row.case_id})
            MATCH (e:Evidence {id: row.id})
            MERGE (c)-[:HAS_EVIDENCE]->(e)
        """, records)

    async def import_relationships(self, csv_path: str) -> int:
        records = []
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append({
                    "source_id": row["source_id"],
                    "target_id": row["target_id"],
                    "type": row["type"],
                    "weight": float(row.get("weight", 1.0)),
                })

        return await self.execute_batch("""
            MATCH (a {id: row.source_id})
            MATCH (b {id: row.target_id})
            CALL apoc.create.relationship(a, row.type, {weight: row.weight}, b)
            YIELD rel
            RETURN count(*)
        """, records)
