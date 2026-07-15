import random
from datetime import datetime, timezone, timedelta, date, time
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.models.user import User, Role, Permission, RolePermission
from app.models.crime import (
    CrimeType, CrimeCategory, FIR, CrimeIncident, Victim, Accused, Witness,
    Person, Location, Evidence, InvestigationStatus, EvidenceType, CaseNote, GenderEnum,
)
from app.models.analytics import CrimeHotspot, SocialIndicator, CaseForecast, OffenderProfile
from app.models.associations import user_roles


random.seed(42)

SEED_PERMISSIONS = [
    {"name": "cases:read", "resource": "cases", "action": "read", "description": "Read case records"},
    {"name": "cases:write", "resource": "cases", "action": "write", "description": "Create/update case records"},
    {"name": "cases:delete", "resource": "cases", "action": "delete", "description": "Delete case records"},
    {"name": "evidence:read", "resource": "evidence", "action": "read", "description": "Read evidence records"},
    {"name": "evidence:write", "resource": "evidence", "action": "write", "description": "Create/update evidence"},
    {"name": "analytics:read", "resource": "analytics", "action": "read", "description": "View analytics"},
    {"name": "analytics:export", "resource": "analytics", "action": "export", "description": "Export analytics"},
    {"name": "network:read", "resource": "network", "action": "read", "description": "View network analysis"},
    {"name": "forecast:read", "resource": "forecast", "action": "read", "description": "View crime forecasts"},
    {"name": "profiles:read", "resource": "profiles", "action": "read", "description": "View offender profiles"},
    {"name": "users:read", "resource": "users", "action": "read", "description": "View user records"},
    {"name": "users:write", "resource": "users", "action": "write", "description": "Manage users"},
    {"name": "users:delete", "resource": "users", "action": "delete", "description": "Delete users"},
    {"name": "audit:read", "resource": "audit", "action": "read", "description": "View audit logs"},
    {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
]

SEED_ROLES = [
    {
        "name": "investigator",
        "description": "Front-line investigating officer",
        "priority_level": "standard",
        "permissions": ["cases:read", "cases:write", "evidence:read", "evidence:write"],
    },
    {
        "name": "analyst",
        "description": "Crime data analyst",
        "priority_level": "standard",
        "permissions": ["cases:read", "analytics:read", "analytics:export", "network:read", "forecast:read", "profiles:read"],
    },
    {
        "name": "supervisor",
        "description": "Supervising officer",
        "priority_level": "elevated",
        "permissions": ["cases:read", "cases:write", "evidence:read", "evidence:write", "analytics:read", "network:read", "forecast:read", "profiles:read", "users:read"],
    },
    {
        "name": "policymaker",
        "description": "Policy decision maker",
        "priority_level": "elevated",
        "permissions": ["cases:read", "analytics:read", "analytics:export", "forecast:read"],
    },
    {
        "name": "admin",
        "description": "System administrator",
        "priority_level": "critical",
        "permissions": ["*"],
    },
]

SEED_CRIME_TYPES = [
    {"name": "Murder", "category": CrimeCategory.VIOLENT, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Attempt to Murder", "category": CrimeCategory.VIOLENT, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Robbery", "category": CrimeCategory.VIOLENT, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
    {"name": "Burglary", "category": CrimeCategory.PROPERTY, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Theft", "category": CrimeCategory.PROPERTY, "severity_level": 4, "is_cognizable": True, "is_bailable": True},
    {"name": "Cyber Crime", "category": CrimeCategory.CYBER, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Fraud", "category": CrimeCategory.FINANCIAL, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Money Laundering", "category": CrimeCategory.FINANCIAL, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
    {"name": "Drug Trafficking", "category": CrimeCategory.DRUG_RELATED, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Kidnapping", "category": CrimeCategory.VIOLENT, "severity_level": 9, "is_cognizable": True, "is_bailable": False},
    {"name": "Assault", "category": CrimeCategory.VIOLENT, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Domestic Violence", "category": CrimeCategory.VIOLENT, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Human Trafficking", "category": CrimeCategory.TRAFFICKING, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Organized Crime", "category": CrimeCategory.ORGANIZED, "severity_level": 10, "is_cognizable": True, "is_bailable": False},
    {"name": "Criminal Breach of Trust", "category": CrimeCategory.WHITE_COLLAR, "severity_level": 5, "is_cognizable": True, "is_bailable": True},
    {"name": "Cheating", "category": CrimeCategory.FINANCIAL, "severity_level": 4, "is_cognizable": True, "is_bailable": True},
    {"name": "Rioting", "category": CrimeCategory.VIOLENT, "severity_level": 6, "is_cognizable": True, "is_bailable": True},
    {"name": "Arson", "category": CrimeCategory.PROPERTY, "severity_level": 7, "is_cognizable": True, "is_bailable": False},
    {"name": "Extortion", "category": CrimeCategory.ORGANIZED, "severity_level": 7, "is_cognizable": True, "is_bailable": False},
    {"name": "Hate Crime", "category": CrimeCategory.VIOLENT, "severity_level": 8, "is_cognizable": True, "is_bailable": False},
]

DISTRICTS = [
    ("Bengaluru Urban", "Bengaluru"),
    ("Mysuru", "Mysore"),
    ("Dakshina Kannada", "Mangaluru"),
    ("Belagavi", "Belgaum"),
    ("Hubballi-Dharwad", "Hubli"),
    ("Shivamogga", "Shimoga"),
    ("Ballari", "Bellary"),
    ("Tumakuru", "Tumkur"),
    ("Kalaburagi", "Gulbarga"),
    ("Udupi", "Udupi"),
]

POLICE_STATIONS = [
    "Cubbon Park PS", "Jayanagar PS", "Koramangala PS", "Whitefield PS",
    "Mysuru North PS", "Mysuru South PS", "Mangaluru City PS", "Mangaluru Rural PS",
    "Belgaum City PS", "Hubli Market PS", "Shimoga Town PS", "Bellary Fort PS",
    "Tumkur Town PS", "Gulbarga City PS", "Udupi Town PS",
]

FIRST_NAMES_MALE = [
    "Ravi", "Ajay", "Vikram", "Manoj", "Sanjay", "Vijay", "Arun", "Suresh",
    "Mahesh", "Kiran", "Rakesh", "Dinesh", "Prakash", "Anil", "Sunil",
    "Girish", "Harish", "Naveen", "Pavan", "Satish", "Vinay", "Deepak",
]

FIRST_NAMES_FEMALE = [
    "Priya", "Sneha", "Deepa", "Kavita", "Anita", "Lakshmi", "Pooja",
    "Neha", "Shweta", "Divya", "Meena", "Rekha", "Geeta", "Nandini",
    "Asha", "Shalini", "Bhavana", "Chitra",
]

LAST_NAMES = [
    "Kumar", "Singh", "Sharma", "Patel", "Reddy", "Nair", "Joshi", "Verma",
    "Desai", "Gupta", "Rao", "Naik", "Hegde", "Shetty", "Acharya",
    "Murthy", "Iyer", "Bhat", "Kulkarni", "Pillai", "Menon", "Prasad",
]

LOCATIONS_KARNATAKA = [
    (12.9716, 77.5946), (12.9344, 77.6101), (12.9352, 77.6245), (12.9718, 77.6412),
    (12.2958, 76.6394), (12.3095, 76.6530), (12.3400, 76.6300),
    (12.9141, 74.8560), (12.8697, 74.8430), (12.9000, 74.8800),
    (15.8497, 74.4977), (15.3600, 75.1400), (13.9299, 75.5681),
    (15.1400, 76.9200), (13.3400, 77.1000), (17.3300, 76.8300),
    (13.3500, 74.7500),
]

INDIAN_CITIES = [
    "Bengaluru", "Mysuru", "Mangaluru", "Belagavi", "Hubballi",
    "Shivamogga", "Ballari", "Tumakuru", "Kalaburagi", "Udupi",
]

FIR_BRIEFS = [
    "Complainant reported that unknown persons broke into the residence and stole gold jewellery and cash.",
    "Victim was attacked by known accused with a sharp weapon near the bus stop, sustained serious injuries.",
    "A group of unidentified individuals forcibly entered the shop and demanded protection money.",
    "Victim reported receiving threatening calls demanding ransom for the safe return of her son.",
    "Cyber fraudsters duped the victim by posing as bank officials and obtained OTP details.",
    "During a routine patrol, police apprehended an individual in possession of 500g of MDMA.",
    "Complainant states that the accused has been harassing her daughter for marriage over the past six months.",
    "Multiple vehicles were broken into in the apartment parking lot during the night.",
    "The accused was caught red-handed accepting a bribe of Rs. 50,000 for clearing a government file.",
    "A known criminal gang attacked the complainant's brother with iron rods and sickles.",
    "The victim's wife has been missing since last evening; suspected kidnapping by known persons.",
    "An altercation between two groups at the market escalated into a full-blown riot with arson.",
    "The complainant found that his company's bank account was siphoned of Rs. 2 crores through fraudulent transfers.",
    "A minor girl was trafficked from the village with promises of employment in the city.",
    "The accused set fire to the complainant's agricultural shed, destroying crops and equipment worth Rs. 5 lakhs.",
    "Unknown persons created fake social media profiles to impersonate and defame the complainant.",
    "The victim was found dead in his apartment with visible strangulation marks on the neck.",
    "A group of bootleggers was caught with 2000 litres of illicit liquor during a raid.",
    "The complainant reported that his two-wheeler was stolen from outside the railway station.",
    "An organized gang was involved in illegal sand mining and threatening local residents.",
]

SEED_CASES = [
    {
        "crime_type_name": "Robbery",
        "district": "Bengaluru Urban",
        "police_station": "Koramangala PS",
        "solved": True,
        "heinous": False,
        "injury": 1,
        "fatality": 0,
        "property_loss": 450000.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 2,
    },
    {
        "crime_type_name": "Murder",
        "district": "Mysuru",
        "police_station": "Mysuru North PS",
        "solved": True,
        "heinous": True,
        "injury": 0,
        "fatality": 1,
        "property_loss": 0.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 3,
    },
    {
        "crime_type_name": "Cyber Crime",
        "district": "Bengaluru Urban",
        "police_station": "Cubbon Park PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 2800000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 0,
    },
    {
        "crime_type_name": "Drug Trafficking",
        "district": "Dakshina Kannada",
        "police_station": "Mangaluru City PS",
        "solved": True,
        "heinous": True,
        "injury": 0,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 3,
        "victim_count": 0,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Burglary",
        "district": "Hubballi-Dharwad",
        "police_station": "Hubli Market PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 185000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 0,
    },
    {
        "crime_type_name": "Assault",
        "district": "Belagavi",
        "police_station": "Belgaum City PS",
        "solved": True,
        "heinous": False,
        "injury": 2,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 2,
    },
    {
        "crime_type_name": "Kidnapping",
        "district": "Shivamogga",
        "police_station": "Shimoga Town PS",
        "solved": True,
        "heinous": True,
        "injury": 0,
        "fatality": 0,
        "property_loss": 500000.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Fraud",
        "district": "Bengaluru Urban",
        "police_station": "Whitefield PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 20000000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 0,
    },
    {
        "crime_type_name": "Drug Trafficking",
        "district": "Ballari",
        "police_station": "Bellary Fort PS",
        "solved": True,
        "heinous": True,
        "injury": 0,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 4,
        "victim_count": 0,
        "witness_count": 2,
    },
    {
        "crime_type_name": "Domestic Violence",
        "district": "Tumakuru",
        "police_station": "Tumkur Town PS",
        "solved": True,
        "heinous": False,
        "injury": 1,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Arson",
        "district": "Kalaburagi",
        "police_station": "Gulbarga City PS",
        "solved": False,
        "heinous": True,
        "injury": 0,
        "fatality": 0,
        "property_loss": 500000.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Theft",
        "district": "Udupi",
        "police_station": "Udupi Town PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 85000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 0,
    },
    {
        "crime_type_name": "Murder",
        "district": "Dakshina Kannada",
        "police_station": "Mangaluru Rural PS",
        "solved": False,
        "heinous": True,
        "injury": 0,
        "fatality": 1,
        "property_loss": 0.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 2,
    },
    {
        "crime_type_name": "Extortion",
        "district": "Bengaluru Urban",
        "police_station": "Jayanagar PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 200000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Human Trafficking",
        "district": "Belagavi",
        "police_station": "Belgaum City PS",
        "solved": True,
        "heinous": True,
        "injury": 0,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 3,
        "victim_count": 4,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Robbery",
        "district": "Mysuru",
        "police_station": "Mysuru South PS",
        "solved": False,
        "heinous": False,
        "injury": 1,
        "fatality": 0,
        "property_loss": 125000.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 1,
    },
    {
        "crime_type_name": "Rioting",
        "district": "Hubballi-Dharwad",
        "police_station": "Hubli Market PS",
        "solved": True,
        "heinous": True,
        "injury": 5,
        "fatality": 0,
        "property_loss": 750000.00,
        "accused_count": 6,
        "victim_count": 3,
        "witness_count": 4,
    },
    {
        "crime_type_name": "Cheating",
        "district": "Kalaburagi",
        "police_station": "Gulbarga City PS",
        "solved": False,
        "heinous": False,
        "injury": 0,
        "fatality": 0,
        "property_loss": 350000.00,
        "accused_count": 1,
        "victim_count": 1,
        "witness_count": 0,
    },
    {
        "crime_type_name": "Attempt to Murder",
        "district": "Shivamogga",
        "police_station": "Shimoga Town PS",
        "solved": True,
        "heinous": True,
        "injury": 3,
        "fatality": 0,
        "property_loss": 0.00,
        "accused_count": 2,
        "victim_count": 1,
        "witness_count": 2,
    },
    {
        "crime_type_name": "Organized Crime",
        "district": "Ballari",
        "police_station": "Bellary Fort PS",
        "solved": False,
        "heinous": True,
        "injury": 2,
        "fatality": 1,
        "property_loss": 1500000.00,
        "accused_count": 5,
        "victim_count": 2,
        "witness_count": 3,
    },
]

ACT_SECTIONS_POOL = {
    "Murder": ["IPC 302", "IPC 201"],
    "Attempt to Murder": ["IPC 307", "IPC 324"],
    "Robbery": ["IPC 392", "IPC 397", "IPC 34"],
    "Burglary": ["IPC 454", "IPC 380"],
    "Theft": ["IPC 379", "IPC 411"],
    "Cyber Crime": ["IT Act 66", "IT Act 43", "IPC 420"],
    "Fraud": ["IPC 420", "IPC 467", "IPC 468"],
    "Money Laundering": ["PMLA 3", "PMLA 4"],
    "Drug Trafficking": ["NDPS 20", "NDPS 21", "NDPS 29"],
    "Kidnapping": ["IPC 363", "IPC 364", "IPC 365"],
    "Assault": ["IPC 323", "IPC 341", "IPC 504"],
    "Domestic Violence": ["DV Act 3", "DV Act 4", "IPC 498A"],
    "Human Trafficking": ["IPC 370", "IPC 370A", "ITPA 5"],
    "Organized Crime": ["IPC 120B", "MCA 3", "MCA 4"],
    "Criminal Breach of Trust": ["IPC 405", "IPC 406", "IPC 409"],
    "Cheating": ["IPC 415", "IPC 420"],
    "Rioting": ["IPC 147", "IPC 148", "IPC 149", "IPC 323"],
    "Arson": ["IPC 435", "IPC 436"],
    "Extortion": ["IPC 384", "IPC 385", "IPC 506"],
    "Hate Crime": ["IPC 153A", "IPC 295A", "IPC 505"],
}

OFFICER_NAMES = [
    ("Insp. Rajesh Kumar", "INSP-042"),
    ("SI Manjunath G.", "SI-108"),
    ("ACP Shankar Rao", "ACP-015"),
    ("SI Geetha R.", "SI-203"),
    ("Insp. Venkatesh P.", "INSP-087"),
    ("SI Ashok Naik", "SI-156"),
    ("ACP Meera Devi", "ACP-032"),
    ("SI Prakash Hegde", "SI-189"),
]

EVIDENCE_NAMES = [
    "Blood sample from scene", "Fingerprint lift cards", "CCTV footage", "Mobile phone forensic dump",
    "Weapon recovered", "Clothing samples", "Shoe impressions", "Digital evidence hard drive",
    "Bank statement copies", "Call detail records", "Narcotics sample", "Tool marks cast",
    "Hair samples", "Fibre samples", "Document originals",
]


def random_date_back(days: int) -> date:
    return (datetime.now(timezone.utc) - timedelta(days=random.randint(1, days))).date()


def random_datetime_back(days: int) -> datetime:
    d = datetime.now(timezone.utc) - timedelta(days=random.randint(1, days))
    return d.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))


def generate_person() -> dict:
    is_male = random.random() < 0.65
    first = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    gender = GenderEnum.MALE if is_male else GenderEnum.FEMALE
    age = random.randint(18, 65)
    dob = date.today() - timedelta(days=age * 365 + random.randint(0, 365))
    return {
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "date_of_birth": dob,
        "age_at_incident": age,
        "occupation": random.choice(["Farmer", "Shopkeeper", "Teacher", "Driver", "Labourer", "Government Employee", "Private Sector", "Unemployed", "Student", "Business Owner"]),
    }


async def seed_database(db: AsyncSession):
    existing = await db.execute(select(Role).limit(1))
    if existing.scalar_one_or_none():
        # Ensure demo user passwords are correct (reset if needed)
        await _ensure_demo_passwords(db)
        return

    permission_map = {}
    for perm_data in SEED_PERMISSIONS:
        perm = Permission(**perm_data)
        db.add(perm)
        permission_map[perm.name] = perm
    await db.flush()

    crime_type_map = {}
    for crime_data in SEED_CRIME_TYPES:
        ct = CrimeType(**crime_data)
        db.add(ct)
        crime_type_map[ct.name] = ct
    await db.flush()

    for role_data in SEED_ROLES:
        role = Role(name=role_data["name"], description=role_data["description"], priority_level=role_data["priority_level"])
        db.add(role)
        await db.flush()
        if role_data["permissions"] == ["*"]:
            for perm in permission_map.values():
                db.add(RolePermission(role_id=role.id, permission_id=perm.id))
        else:
            for perm_name in role_data["permissions"]:
                if perm_name in permission_map:
                    db.add(RolePermission(role_id=role.id, permission_id=permission_map[perm_name].id))
    await db.flush()

    admin_role = (await db.execute(select(Role).where(Role.name == "admin"))).scalar_one()
    investigator_role = (await db.execute(select(Role).where(Role.name == "investigator"))).scalar_one()

    admin_user = User(
        email="admin@sentinelai.gov.in", username="admin",
        full_name="System Administrator", hashed_password=get_password_hash("Admin@123"),
        designation="System Administrator", badge_number="ADM-001",
        department="Administration", is_superuser=True,
    )
    db.add(admin_user)
    await db.flush()
    await db.execute(user_roles.insert().values(user_id=admin_user.id, role_id=admin_role.id))

    investigator_user = User(
        email="investigator@sentinelai.gov.in", username="investigator",
        full_name="Insp. Rajesh Kumar", hashed_password=get_password_hash("Investigator@123"),
        designation="Inspector", badge_number="INSP-042",
        department="CID", jurisdiction="Bengaluru Urban",
    )
    db.add(investigator_user)
    await db.flush()
    await db.execute(user_roles.insert().values(user_id=investigator_user.id, role_id=investigator_role.id))

    analyst_role = (await db.execute(select(Role).where(Role.name == "analyst"))).scalar_one()
    analyst_user = User(
        email="analyst@sentinelai.gov.in", username="analyst",
        full_name="Dr. Priya Sharma", hashed_password=get_password_hash("Analyst@123"),
        designation="Data Analyst", badge_number="ANL-007",
        department="Crime Analytics Unit", jurisdiction="Karnataka State",
    )
    db.add(analyst_user)
    await db.flush()
    await db.execute(user_roles.insert().values(user_id=analyst_user.id, role_id=analyst_role.id))

    await _seed_crime_data(db, crime_type_map, admin_user)
    await db.commit()


async def _seed_crime_data(db: AsyncSession, crime_type_map: dict, admin_user=None):
    used_persons = []
    used_fir_numbers = set()

    def next_fir_number(police_station: str) -> str:
        num = random.randint(1, 999)
        code = police_station[:3].upper()
        while f"{num:03d}/{code}/2025" in used_fir_numbers:
            num = random.randint(1, 999)
        fir_no = f"{num:03d}/{code}/2025"
        used_fir_numbers.add(fir_no)
        return fir_no

    for case_data in SEED_CASES:
        ct = crime_type_map[case_data["crime_type_name"]]
        district_full = case_data["district"]
        city = district_full.split(" (")[0]
        ps = case_data["police_station"]
        fir_number = next_fir_number(ps)
        reg_date = random_datetime_back(300)
        incident_date = reg_date.date() - timedelta(days=random.randint(0, 5))
        incident_time = time(random.randint(0, 23), random.randint(0, 59))
        officer = random.choice(OFFICER_NAMES)
        sections = ACT_SECTIONS_POOL.get(ct.name, ["IPC 34"])
        brief = random.choice(FIR_BRIEFS)

        fir = FIR(
            fir_number=fir_number, police_station=ps, district=district_full,
            state="Karnataka", registration_date=reg_date,
            act_sections=sections, brief_fact=brief,
            recorded_by=officer[0], io_name=officer[0], io_badge=officer[1],
            is_cognizable=ct.is_cognizable, is_bailable=ct.is_bailable,
        )
        db.add(fir)
        await db.flush()

        incident = CrimeIncident(
            fir_id=fir.id, crime_type_id=ct.id,
            incident_date=incident_date, incident_time=incident_time,
            reported_date=reg_date, description=brief,
            modus_operandi=random.choice([
                "Forced entry at night", "Armed robbery in daylight",
                "Social engineering via phone", "Break-in during business hours",
                "Pickpocketing in crowded area", "Ambush on isolated road",
            ]),
            property_value_loss=case_data["property_loss"],
            injury_count=case_data["injury"], fatality_count=case_data["fatality"],
            is_solved=case_data["solved"], is_heinous=case_data["heinous"],
            day_of_week=incident_date.strftime("%A"),
            time_period=random.choice(["Morning", "Afternoon", "Evening", "Night"]),
        )
        db.add(incident)
        await db.flush()

        lat, lng = random.choice(LOCATIONS_KARNATAKA)
        loc = Location(
            incident_id=incident.id,
            name=f"Scene near {city}",
            location_type=random.choice(["Residential", "Commercial", "Street", "Public Space", "Isolated Area"]),
            latitude=lat + random.uniform(-0.02, 0.02),
            longitude=lng + random.uniform(-0.02, 0.02),
            address=f"Near {ps}, {district_full}, Karnataka",
            city=city, district=district_full, state="Karnataka",
            pincode=random.choice(["560001", "570001", "575001", "590001", "580001", "577201"]),
            is_crime_scene=True,
            description=f"Location of {ct.name.lower()} incident reported at {ps}",
        )
        db.add(loc)

        for v in range(case_data["victim_count"]):
            pdata = generate_person()
            person = Person(**pdata)
            db.add(person)
            await db.flush()
            used_persons.append(person)
            victim = Victim(
                person_id=person.id, incident_id=incident.id,
                injury_description=random.choice([
                    "Minor bruises", "Laceration on arm", "Head trauma",
                    "No physical injury", "Multiple fractures", "Burn injuries",
                ]) if case_data["injury"] > 0 else "No injury",
                injury_severity=random.choice(["Minor", "Moderate", "Severe"]),
                property_loss=case_data["property_loss"] if v == 0 else None,
                is_minor=random.random() < 0.1,
            )
            db.add(victim)

        accused_persons = []
        for a in range(case_data["accused_count"]):
            pdata = generate_person()
            person = Person(**pdata)
            db.add(person)
            await db.flush()
            used_persons.append(person)
            accused_persons.append(person)
            accused = Accused(
                person_id=person.id, incident_id=incident.id,
                arrest_date=random_datetime_back(200) if case_data["solved"] and random.random() < 0.7 else None,
                arrest_location=random.choice(["At scene", "From residence", "At hideout", "At checkpoint"]),
                arresting_officer=officer[0] if case_data["solved"] else None,
                charge_sections=sections,
                bail_status=random.choice(["Granted", "Denied", "Pending", "None"]),
                bail_amount=random.choice([0, 25000, 50000, 100000, 500000]) if random.random() < 0.4 else None,
                custody_type=random.choice(["Judicial", "Police", "None"]),
                is_repeat_offender=random.random() < 0.25,
                risk_score=round(random.uniform(0.1, 0.95), 4),
            )
            db.add(accused)

        for w in range(case_data["witness_count"]):
            pdata = generate_person()
            person = Person(**pdata)
            db.add(person)
            await db.flush()
            used_persons.append(person)
            witness = Witness(
                person_id=person.id, incident_id=incident.id,
                witness_type=random.choice(["Eyewitness", "Expert", "Character", "Medical"]),
                statement=random.choice([
                    "Saw the accused fleeing the scene",
                    "Heard loud noises and saw struggling",
                    "Was present during the incident",
                    "Saw a suspicious vehicle near the location",
                    "Identified the accused in the lineup",
                ]),
                statement_recorded_date=reg_date + timedelta(days=random.randint(1, 7)),
                statement_recorded_by=officer[0],
                is_eye_witness=random.random() < 0.6,
                credibility_score=round(random.uniform(0.4, 1.0), 2),
            )
            db.add(witness)

        evidence_count = random.randint(2, 5)
        for e in range(evidence_count):
            ev = Evidence(
                fir_id=fir.id,
                evidence_type=random.choice(list(EvidenceType)),
                name=random.choice(EVIDENCE_NAMES),
                description=f"Evidence collected during investigation of FIR {fir_number}",
                collection_date=reg_date + timedelta(days=random.randint(1, 14)),
                collected_by=officer[0],
                location_found=random.choice(["Crime scene", "Victim's residence", "Forensic lab", "Suspect's property"]),
                is_forensically_analyzed=random.random() < 0.6,
                is_admissible=random.random() < 0.8,
            )
            db.add(ev)

        statuses = ["registered", "under_investigation", "evidence_collection", "suspect_identified"]
        if case_data["solved"]:
            statuses += ["arrest_made", "chargesheet_filed"]
        for i, st in enumerate(statuses):
            istatus = InvestigationStatus(
                incident_id=incident.id,
                status=st,
                remarks=f"Status updated to {st.replace('_', ' ')}",
                updated_by=officer[0],
                updated_at=reg_date + timedelta(days=i * random.randint(3, 10)),
            )
            db.add(istatus)

        note = CaseNote(
            incident_id=incident.id,
            title=f"Initial investigation notes - FIR {fir_number}",
            content=random.choice([
                "Preliminary investigation reveals the accused had prior enmity with the victim.",
                "Forensic team has collected samples from the scene. Awaiting lab reports.",
                "CCTV footage from nearby establishments has been seized for analysis.",
                "Witness statements have been recorded. Suspect description matches known offender.",
                "Recovered stolen property has been handed over to the complainant.",
            ]),
            note_type=random.choice(["Investigation", "Evidence", "Witness", "General"]),
            created_by=admin_user.id,
            created_at=reg_date + timedelta(days=1),
        )
        db.add(note)
        await db.flush()

        # Generate hotspots for ~60% of cases
        if random.random() < 0.6:
            for _ in range(random.randint(1, 2)):
                db.add(CrimeHotspot(
                    incident_id=incident.id,
                    latitude=lat + random.uniform(-0.03, 0.03),
                    longitude=lng + random.uniform(-0.03, 0.03),
                    cluster_id=random.randint(1, 8),
                    risk_score=round(random.uniform(0.3, 0.95), 4),
                    crime_density=round(random.uniform(0.2, 0.9), 4),
                    radius_meters=random.randint(200, 1500),
                ))

        # Generate forecasts for each case
        for day_offset in [7, 14, 30, 60]:
            fc_date = datetime.now(timezone.utc) + timedelta(days=day_offset)
            db.add(CaseForecast(
                incident_id=incident.id,
                forecast_date=fc_date,
                forecast_type=random.choice(["crime_volume", "hotspot_risk", "recidivism"]),
                predicted_value=round(random.uniform(10, 100), 2),
                lower_bound=round(random.uniform(5, 60), 2),
                upper_bound=round(random.uniform(40, 120), 2),
                confidence_level=round(random.uniform(0.75, 0.95), 4),
                model_used=random.choice(["Prophet", "XGBoost", "ARIMA"]),
                features_used=random.sample(["seasonality", "trend", "day_of_week", "month", "historical_volume", "weather", "events"], 4),
            ))

        # Generate offender profiles for accused
        for p in accused_persons:
            db.add(OffenderProfile(
                incident_id=incident.id,
                person_id=p.id,
                archetype=random.choice(["Violent Offender", "Financial Fraudster", "Drug Trafficker", "Property Criminal", "Cyber Criminal", "Serial Offender", "Gang Leader"]),
                risk_level=random.choice(["Low", "Medium", "High", "Critical"]),
                risk_score=round(random.uniform(0.1, 0.95), 4),
                escalation_risk=random.choice(["Low", "Moderate", "High"]),
                recidivism_probability=round(random.uniform(0.1, 0.9), 4),
                behavioral_pattern=random.sample([
                    "Night-time activity", "Repeat offenses", "Targets vulnerable victims",
                    "Uses violence", "Operates in groups", "Cross-jurisdictional",
                    "Weekend patterns", "Festival season spikes", "Financial motivation",
                ], random.randint(2, 5)),
                profile_summary=f"Subject exhibits {random.choice(['violent', 'financial', 'property', 'cyber', 'organized'])} criminal patterns with {random.choice(['low', 'moderate', 'high'])} escalation risk.",
            ))

    # --- Generate 60 additional randomized cases for richer data ---
    additional_crime_types = list(crime_type_map.keys())
    for i in range(60):
        ct_name = random.choice(additional_crime_types)
        ct = crime_type_map[ct_name]
        district_full, city = random.choice(DISTRICTS)
        ps = random.choice(POLICE_STATIONS)
        fir_number = next_fir_number(ps)

        # Create temporal patterns: more crimes on weekends, evening/night
        days_back = random.randint(1, 365)
        reg_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        # Bias towards weekends
        if random.random() < 0.35:
            while reg_date.weekday() < 5:  # push to Saturday/Sunday
                reg_date -= timedelta(days=1)
        incident_date = reg_date.date() - timedelta(days=random.randint(0, 3))
        incident_time = time(random.choice([0, 1, 2, 19, 20, 21, 22, 23] if random.random() < 0.5 else list(range(24))),
                           random.randint(0, 59))

        officer = random.choice(OFFICER_NAMES)
        sections = ACT_SECTIONS_POOL.get(ct_name, ["IPC 34"])
        brief = random.choice(FIR_BRIEFS)
        is_solved = random.random() < 0.45
        is_heinous = ct.severity_level >= 8

        fir = FIR(
            fir_number=fir_number, police_station=ps, district=district_full,
            state="Karnataka", registration_date=reg_date,
            act_sections=sections, brief_fact=brief,
            recorded_by=officer[0], io_name=officer[0], io_badge=officer[1],
            is_cognizable=ct.is_cognizable, is_bailable=ct.is_bailable,
        )
        db.add(fir)
        await db.flush()

        property_loss = round(random.uniform(0, 5000000), 2) if ct.category.value in ["property", "financial"] else 0
        injury = random.randint(0, 3) if ct.category.value == "violent" else 0
        fatality = 1 if ct_name == "Murder" and random.random() < 0.8 else 0

        incident = CrimeIncident(
            fir_id=fir.id, crime_type_id=ct.id,
            incident_date=incident_date, incident_time=incident_time,
            reported_date=reg_date, description=brief,
            modus_operandi=random.choice([
                "Forced entry at night", "Armed robbery in daylight",
                "Social engineering via phone", "Break-in during business hours",
                "Pickpocketing in crowded area", "Ambush on isolated road",
                "Online fraud via fake website", "Chain snatching from vehicle",
                "Burglary during wedding function", "Impersonation of official",
            ]),
            property_value_loss=property_loss,
            injury_count=injury, fatality_count=fatality,
            is_solved=is_solved, is_heinous=is_heinous,
            day_of_week=incident_date.strftime("%A"),
            time_period=random.choice(["Morning", "Afternoon", "Evening", "Night"]),
        )
        db.add(incident)
        await db.flush()

        lat, lng = random.choice(LOCATIONS_KARNATAKA)
        lat += random.uniform(-0.05, 0.05)
        lng += random.uniform(-0.05, 0.05)
        loc = Location(
            incident_id=incident.id,
            name=f"Scene near {city}",
            location_type=random.choice(["Residential", "Commercial", "Street", "Public Space", "Isolated Area"]),
            latitude=lat, longitude=lng,
            address=f"Near {ps}, {district_full}, Karnataka",
            city=city, district=district_full, state="Karnataka",
            pincode=random.choice(["560001", "570001", "575001", "590001", "580001"]),
            is_crime_scene=True,
        )
        db.add(loc)

        # 1 victim per case
        pdata = generate_person()
        person = Person(**pdata)
        db.add(person)
        await db.flush()
        db.add(Victim(person_id=person.id, incident_id=incident.id, injury_description="Reported to police", is_minor=random.random() < 0.05))

        # 1-3 accused
        acc_count = random.randint(1, 3)
        for _ in range(acc_count):
            pdata = generate_person()
            person = Person(**pdata)
            db.add(person)
            await db.flush()
            db.add(Accused(
                person_id=person.id, incident_id=incident.id,
                charge_sections=sections,
                bail_status=random.choice(["Granted", "Denied", "Pending"]),
                is_repeat_offender=random.random() < 0.2,
                risk_score=round(random.uniform(0.1, 0.95), 4),
            ))

        # Hotspot
        if random.random() < 0.5:
            db.add(CrimeHotspot(
                incident_id=incident.id,
                latitude=lat, longitude=lng,
                cluster_id=random.randint(1, 8),
                risk_score=round(random.uniform(0.3, 0.95), 4),
                crime_density=round(random.uniform(0.2, 0.9), 4),
                radius_meters=random.randint(200, 1500),
            ))

        # Forecast
        db.add(CaseForecast(
            incident_id=incident.id,
            forecast_date=datetime.now(timezone.utc) + timedelta(days=random.randint(7, 60)),
            forecast_type="crime_volume",
            predicted_value=round(random.uniform(15, 90), 2),
            lower_bound=round(random.uniform(8, 50), 2),
            upper_bound=round(random.uniform(50, 120), 2),
            confidence_level=round(random.uniform(0.7, 0.95), 4),
            model_used=random.choice(["Prophet", "XGBoost"]),
            features_used=["seasonality", "trend", "day_of_week"],
        ))

        # Investigation status
        db.add(InvestigationStatus(
            incident_id=incident.id, status="registered",
            remarks="Case registered", updated_by=officer[0], updated_at=reg_date,
        ))
        if is_solved:
            db.add(InvestigationStatus(
                incident_id=incident.id, status="arrest_made",
                remarks="Accused arrested", updated_by=officer[0],
                updated_at=reg_date + timedelta(days=random.randint(5, 30)),
            ))

    # --- Social Indicators ---
    indicators = []
    for dist_name, _ in DISTRICTS[:6]:
        for year in [2023, 2024, 2025]:
            indicators.append(SocialIndicator(
                district=dist_name, state="Karnataka", year=year,
                unemployment_rate=round(random.uniform(3, 12), 1),
                literacy_rate=round(random.uniform(65, 95), 1),
                population_density=round(random.uniform(200, 5000), 0),
                police_per_capita=round(random.uniform(0.5, 3.0), 2),
                crime_rate_per_100k=round(random.uniform(100, 800), 0),
            ))
    for ind in indicators:
        db.add(ind)


async def _ensure_demo_passwords(db: AsyncSession):
    """Ensure demo accounts have the correct passwords (for development)."""
    demo_accounts = [
        ("admin", "Admin@123"),
        ("investigator", "Investigator@123"),
        ("analyst", "Analyst@123"),
    ]
    for username, password in demo_accounts:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash(password)
    await db.commit()
