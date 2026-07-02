"""
Seed data for the official Karnataka Police ER schema tables.

Populates master tables and creates sample CaseMaster records
that align with the official CrimeNo format.
"""
import random
from datetime import datetime, timezone, timedelta, date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.official_schema import (
    StateMaster, DistrictMaster, UnitTypeMaster, UnitMaster,
    RankMaster, DesignationMaster, OccupationMaster, ReligionMaster,
    CasteMaster, CaseCategoryMaster, GravityOffenceMaster, CaseStatusMaster,
    ActMaster, SectionMaster, CrimeHeadMaster, CrimeSubHeadMaster,
    CourtMaster, EmployeeMaster, CaseMaster, ComplainantDetails,
    VictimOfficial, AccusedOfficial, ArrestSurrender, ActSectionAssociation,
    ChargesheetDetails,
)

random.seed(42)


async def seed_official_schema(db: AsyncSession):
    """Seed all official schema tables."""
    # Check if already seeded
    existing = await db.execute(select(StateMaster).limit(1))
    if existing.scalar_one_or_none():
        return

    # --- States ---
    karnataka = StateMaster(state_id=1, state_name="Karnataka", active=True)
    db.add(karnataka)
    await db.flush()

    # --- Districts ---
    districts_data = [
        (1, "Bengaluru Urban"), (2, "Bengaluru Rural"), (3, "Mysuru"),
        (4, "Dakshina Kannada"), (5, "Belagavi"), (6, "Hubballi-Dharwad"),
        (7, "Shivamogga"), (8, "Ballari"), (9, "Tumakuru"), (10, "Kalaburagi"),
        (11, "Udupi"), (12, "Raichur"), (13, "Hassan"), (14, "Mandya"),
    ]
    district_objs = {}
    for did, dname in districts_data:
        d = DistrictMaster(district_id=did, district_name=dname, state_id=1, active=True)
        db.add(d)
        district_objs[did] = d
    await db.flush()

    # --- Unit Types ---
    unit_types = [
        (1, "Police Station", "City", 5),
        (2, "Circle Inspector Office", "City", 4),
        (3, "Sub-Division", "District", 3),
        (4, "District SP Office", "District", 2),
        (5, "Range IG Office", "State", 1),
    ]
    for uid, uname, level, hier in unit_types:
        db.add(UnitTypeMaster(unit_type_id=uid, unit_type_name=uname, city_dist_state=level, hierarchy=hier, active=True))
    await db.flush()

    # --- Units (Police Stations) ---
    stations = [
        (1, "Cubbon Park PS", 1, 1), (2, "Jayanagar PS", 1, 1),
        (3, "Koramangala PS", 1, 1), (4, "Whitefield PS", 1, 1),
        (5, "Indiranagar PS", 1, 1), (6, "HSR Layout PS", 1, 1),
        (7, "Mysuru North PS", 1, 3), (8, "Mysuru South PS", 1, 3),
        (9, "Mangaluru City PS", 1, 4), (10, "Belgaum City PS", 1, 5),
        (11, "Hubli Market PS", 1, 6), (12, "Shimoga Town PS", 1, 7),
        (13, "Bellary Fort PS", 1, 8), (14, "Tumkur Town PS", 1, 9),
        (15, "Gulbarga City PS", 1, 10),
    ]
    for uid, uname, type_id, dist_id in stations:
        db.add(UnitMaster(unit_id=uid, unit_name=uname, type_id=type_id, district_id=dist_id, state_id=1, active=True))
    await db.flush()

    # --- Ranks ---
    ranks = [
        (1, "Director General", 1), (2, "Inspector General", 2),
        (3, "DIG", 3), (4, "Superintendent", 4), (5, "DSP", 5),
        (6, "Inspector", 6), (7, "Sub-Inspector", 7), (8, "ASI", 8),
        (9, "Head Constable", 9), (10, "Constable", 10),
    ]
    for rid, rname, hier in ranks:
        db.add(RankMaster(rank_id=rid, rank_name=rname, hierarchy=hier, active=True))
    await db.flush()

    # --- Designations ---
    desigs = [
        (1, "SHO"), (2, "Investigating Officer"), (3, "Circle Inspector"),
        (4, "ACP"), (5, "DCP"), (6, "Writer"),
    ]
    for did, dname in desigs:
        db.add(DesignationMaster(designation_id=did, designation_name=dname, active=True, sort_order=did))
    await db.flush()

    # --- Occupations ---
    occupations = [
        "Farmer", "Government Employee", "Private Employee", "Business",
        "Student", "Daily Wage Worker", "Unemployed", "Retired",
        "Homemaker", "Driver", "Other",
    ]
    for i, occ in enumerate(occupations, 1):
        db.add(OccupationMaster(occupation_id=i, occupation_name=occ))
    await db.flush()

    # --- Religions ---
    religions = ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"]
    for i, r in enumerate(religions, 1):
        db.add(ReligionMaster(religion_id=i, religion_name=r))
    await db.flush()

    # --- Castes ---
    castes = ["General", "OBC", "SC", "ST", "Other"]
    for i, c in enumerate(castes, 1):
        db.add(CasteMaster(caste_master_id=i, caste_master_name=c))
    await db.flush()

    # --- Case Categories ---
    categories = [(1, "FIR"), (2, "NCR"), (3, "UDR"), (4, "PAR"), (5, "Zero FIR")]
    for cid, val in categories:
        db.add(CaseCategoryMaster(case_category_id=cid, lookup_value=val))
    await db.flush()

    # --- Gravity ---
    db.add(GravityOffenceMaster(gravity_offence_id=1, lookup_value="Heinous"))
    db.add(GravityOffenceMaster(gravity_offence_id=2, lookup_value="Non-Heinous"))
    await db.flush()

    # --- Case Status ---
    statuses = [
        (1, "Under Investigation"), (2, "Charge Sheeted"), (3, "Pending Trial"),
        (4, "Convicted"), (5, "Acquitted"), (6, "Closed"), (7, "Undetected"),
    ]
    for sid, sname in statuses:
        db.add(CaseStatusMaster(case_status_id=sid, case_status_name=sname))
    await db.flush()

    # --- Acts ---
    acts = [
        ("IPC", "Indian Penal Code, 1860", "IPC"),
        ("CRPC", "Code of Criminal Procedure, 1973", "CrPC"),
        ("NDPS", "Narcotic Drugs and Psychotropic Substances Act, 1985", "NDPS"),
        ("ITA", "Information Technology Act, 2000", "IT Act"),
        ("POCSO", "Protection of Children from Sexual Offences Act, 2012", "POCSO"),
        ("SC_ST", "SC/ST Prevention of Atrocities Act, 1989", "SC/ST Act"),
        ("ARMS", "Arms Act, 1959", "Arms Act"),
        ("BNS", "Bharatiya Nyaya Sanhita, 2023", "BNS"),
    ]
    for code, desc, short in acts:
        db.add(ActMaster(act_code=code, act_description=desc, short_name=short, active=True))
    await db.flush()

    # --- Sections ---
    ipc_sections = [
        ("302", "Murder"), ("307", "Attempt to Murder"),
        ("376", "Rape"), ("392", "Robbery"), ("394", "Dacoity"),
        ("420", "Cheating"), ("379", "Theft"), ("354", "Assault on woman"),
        ("498A", "Cruelty by husband"), ("304B", "Dowry death"),
        ("323", "Voluntarily causing hurt"), ("506", "Criminal intimidation"),
        ("406", "Criminal breach of trust"), ("341", "Wrongful restraint"),
    ]
    for sec_code, sec_desc in ipc_sections:
        db.add(SectionMaster(act_code="IPC", section_code=sec_code, section_description=sec_desc, active=True))
    await db.flush()

    # --- Crime Heads ---
    crime_heads = [
        (1, "Crimes Against Body"), (2, "Crimes Against Property"),
        (3, "Crimes Against Women"), (4, "Economic Offences"),
        (5, "Crimes Against Children"), (6, "Cyber Crimes"),
        (7, "Drug Related Offences"), (8, "Crimes Against Public Order"),
    ]
    for hid, hname in crime_heads:
        db.add(CrimeHeadMaster(crime_head_id=hid, crime_group_name=hname, active=True))
    await db.flush()

    # --- Crime Sub Heads ---
    sub_heads = [
        (1, 1, "Murder", 1), (2, 1, "Attempt to Murder", 2),
        (3, 1, "Kidnapping", 3), (4, 2, "Robbery", 1),
        (5, 2, "Burglary", 2), (6, 2, "Theft", 3),
        (7, 3, "Rape", 1), (8, 3, "Dowry Death", 2),
        (9, 4, "Cheating", 1), (10, 4, "Fraud", 2),
        (11, 5, "POCSO", 1), (12, 6, "Online Fraud", 1),
        (13, 7, "NDPS", 1), (14, 8, "Rioting", 1),
    ]
    for sid, hid, sname, seq in sub_heads:
        db.add(CrimeSubHeadMaster(crime_sub_head_id=sid, crime_head_id=hid, crime_head_name=sname, seq_id=seq))
    await db.flush()

    # --- Courts ---
    courts = [
        (1, "City Civil Court Bengaluru", 1), (2, "Sessions Court Mysuru", 3),
        (3, "JMFC Mangaluru", 4), (4, "Sessions Court Belagavi", 5),
        (5, "High Court of Karnataka", 1),
    ]
    for cid, cname, dist in courts:
        db.add(CourtMaster(court_id=cid, court_name=cname, district_id=dist, state_id=1, active=True))
    await db.flush()

    # --- Employees ---
    employees = [
        (1, 1, 1, 6, 2, "KGID001", "Rajesh Kumar"),
        (2, 1, 2, 7, 2, "KGID002", "Suresh Patil"),
        (3, 3, 7, 6, 1, "KGID003", "Venkatesh Rao"),
        (4, 1, 3, 6, 2, "KGID004", "Anil Sharma"),
        (5, 4, 9, 7, 2, "KGID005", "Manjunath Gowda"),
    ]
    for eid, dist, unit, rank, desig, kgid, name in employees:
        db.add(EmployeeMaster(
            employee_id=eid, district_id=dist, unit_id=unit,
            rank_id=rank, designation_id=desig, kgid=kgid, first_name=name,
        ))
    await db.flush()

    # --- Sample Cases (Official CrimeNo format) ---
    await _seed_sample_cases(db)
    await db.commit()


async def _seed_sample_cases(db: AsyncSession):
    """Create sample cases with official CrimeNo format."""
    cases_data = [
        # (crime_no, category, district_ps, date, gravity, major_head, minor_head, status, brief)
        ("104430001202600001", 1, 1, "2026-01-15", 1, 1, 1, 1, "Victim found murdered at MG Road. Multiple stab wounds observed."),
        ("104430002202600001", 1, 2, "2026-02-03", 2, 2, 4, 1, "Armed robbery at jewelry shop in Jayanagar 4th Block."),
        ("104430003202600002", 1, 3, "2026-02-20", 2, 2, 6, 2, "Chain snatching incident near Koramangala market."),
        ("104430004202600001", 1, 4, "2026-03-08", 1, 1, 2, 1, "Attempted murder using knife at Whitefield tech park."),
        ("104430001202600002", 1, 1, "2026-03-15", 2, 4, 9, 1, "Online fraud — victim lost ₹5L to fake investment scheme."),
        ("104430005202600001", 1, 5, "2026-03-22", 2, 6, 12, 1, "Cyber crime — phishing attack on corporate email."),
        ("104430006202600001", 1, 6, "2026-04-01", 2, 2, 5, 2, "House burglary at HSR Layout — electronics stolen."),
        ("104430001202600003", 1, 1, "2026-04-10", 1, 3, 7, 1, "Sexual assault reported near bus stop."),
        ("104430007202600001", 1, 7, "2026-04-18", 2, 7, 13, 1, "NDPS — 2kg cannabis seized, two arrested."),
        ("104430002202600002", 1, 2, "2026-05-05", 1, 1, 3, 1, "Kidnapping of minor for ransom demand."),
        ("104430003202600003", 1, 3, "2026-05-12", 2, 4, 10, 2, "Fraudulent property registration documents detected."),
        ("104430001202600004", 1, 1, "2026-05-20", 2, 2, 6, 1, "Motor vehicle theft — Innova from parking lot."),
        ("104430008202600001", 1, 8, "2026-05-28", 1, 3, 8, 1, "Dowry death — unnatural death of newly wed woman."),
        ("104430004202600002", 1, 4, "2026-06-05", 2, 8, 14, 1, "Rioting during local protest — property damaged."),
        ("104430009202600001", 1, 9, "2026-06-12", 2, 2, 4, 1, "Dacoity at rural bank — ₹12L looted."),
        ("104430002202600003", 1, 2, "2026-06-18", 2, 4, 9, 2, "Cheating by real estate agent — ₹25L defrauded."),
        ("104430010202600001", 1, 10, "2026-06-22", 1, 1, 1, 1, "Double murder at farmhouse in Belgaum."),
        ("104430003202600004", 1, 3, "2026-06-25", 2, 6, 12, 1, "Cyberstalking and threatening messages to woman."),
        ("304430001202600001", 3, 1, "2026-06-27", 2, 1, 1, 7, "UDR — Unidentified body found near lake."),
        ("804430001202600001", 5, 1, "2026-06-28", 1, 1, 2, 1, "Zero FIR — Inter-state gang attack on merchant."),
    ]

    for i, (crime_no, cat, ps, reg_date, grav, major, minor, status, brief) in enumerate(cases_data):
        case_no = crime_no[-9:]  # Last 9 digits
        case = CaseMaster(
            case_master_id=i + 1,
            crime_no=crime_no,
            case_no=case_no,
            crime_registered_date=date.fromisoformat(reg_date),
            police_person_id=random.choice([1, 2, 3, 4, 5]),
            police_station_id=ps,
            case_category_id=cat,
            gravity_offence_id=grav,
            crime_major_head_id=major,
            crime_minor_head_id=minor,
            case_status_id=status,
            court_id=random.choice([1, 2, 3, 4, 5]) if status >= 2 else None,
            incident_from_date=datetime.fromisoformat(reg_date + "T08:00:00+05:30"),
            latitude=12.9 + random.uniform(-0.3, 0.3),
            longitude=77.5 + random.uniform(-0.3, 0.3),
            brief_facts=brief,
        )
        db.add(case)
    await db.flush()

    # Add complainants, victims, accused for each case
    names_m = ["Ravi Kumar", "Ajay Singh", "Vikram Patil", "Manoj Gowda", "Suresh Rao"]
    names_f = ["Priya Sharma", "Sneha Reddy", "Deepa Kumari", "Kavita Naik", "Anita Devi"]

    for case_id in range(1, 21):
        # Complainant
        db.add(ComplainantDetails(
            case_master_id=case_id,
            complainant_name=random.choice(names_m + names_f),
            age_year=random.randint(22, 55),
            occupation_id=random.randint(1, 10),
            religion_id=random.randint(1, 5),
            caste_id=random.randint(1, 4),
            gender_id=random.choice([1, 2]),
        ))

        # Victims (1-2)
        for v in range(random.randint(1, 2)):
            db.add(VictimOfficial(
                case_master_id=case_id,
                victim_name=random.choice(names_m + names_f),
                age_year=random.randint(18, 60),
                gender_id=random.choice([1, 2]),
                victim_police="0",
            ))

        # Accused (1-3)
        for a_idx in range(random.randint(1, 3)):
            db.add(AccusedOfficial(
                case_master_id=case_id,
                accused_name=random.choice(names_m),
                age_year=random.randint(20, 45),
                gender_id=1,
                person_id=f"A{a_idx + 1}",
            ))

        # Act-Section (IPC sections)
        db.add(ActSectionAssociation(
            case_master_id=case_id,
            act_id="IPC",
            section_id=random.choice(["302", "307", "392", "420", "379", "376", "354", "323"]),
            act_order_id=1,
            section_order_id=1,
        ))

    await db.flush()
