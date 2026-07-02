"""
Official Karnataka Police FIR ER Diagram — Database Models.

These models align with the official Police_FIR_ER_Diagram.pdf
provided by hackathon organizers. They work alongside the existing
models to provide the official data structure.
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, Text, Integer,
    Float, ForeignKey, Table, Numeric,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


# ============================================================
# MASTER / LOOKUP TABLES
# ============================================================

class StateMaster(Base):
    """State master table."""
    __tablename__ = "state_master"

    state_id = Column(Integer, primary_key=True, autoincrement=True)
    state_name = Column(String(100), nullable=False, index=True)
    nationality_id = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)

    districts = relationship("DistrictMaster", back_populates="state")


class DistrictMaster(Base):
    """District master table."""
    __tablename__ = "district_master"

    district_id = Column(Integer, primary_key=True, autoincrement=True)
    district_name = Column(String(100), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey("state_master.state_id"), nullable=False)
    active = Column(Boolean, default=True)

    state = relationship("StateMaster", back_populates="districts")
    units = relationship("UnitMaster", back_populates="district")


class UnitTypeMaster(Base):
    """Unit type master (Police Station, Circle Office, etc.)."""
    __tablename__ = "unit_type_master"

    unit_type_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_type_name = Column(String(100), nullable=False)
    city_dist_state = Column(String(50), nullable=True)  # City / District / State
    hierarchy = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)


class UnitMaster(Base):
    """Police unit/station master table."""
    __tablename__ = "unit_master"

    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String(255), nullable=False, index=True)
    type_id = Column(Integer, ForeignKey("unit_type_master.unit_type_id"), nullable=True)
    parent_unit = Column(Integer, nullable=True)  # Self-reference
    state_id = Column(Integer, ForeignKey("state_master.state_id"), nullable=True)
    district_id = Column(Integer, ForeignKey("district_master.district_id"), nullable=True)
    nationality_id = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)

    district = relationship("DistrictMaster", back_populates="units")


class RankMaster(Base):
    """Police rank master table."""
    __tablename__ = "rank_master"

    rank_id = Column(Integer, primary_key=True, autoincrement=True)
    rank_name = Column(String(100), nullable=False)
    hierarchy = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)


class DesignationMaster(Base):
    """Designation master table."""
    __tablename__ = "designation_master"

    designation_id = Column(Integer, primary_key=True, autoincrement=True)
    designation_name = Column(String(100), nullable=False)
    active = Column(Boolean, default=True)
    sort_order = Column(Integer, nullable=True)


class OccupationMaster(Base):
    """Occupation master table."""
    __tablename__ = "occupation_master"

    occupation_id = Column(Integer, primary_key=True, autoincrement=True)
    occupation_name = Column(String(100), nullable=False)


class ReligionMaster(Base):
    """Religion master table."""
    __tablename__ = "religion_master"

    religion_id = Column(Integer, primary_key=True, autoincrement=True)
    religion_name = Column(String(100), nullable=False)


class CasteMaster(Base):
    """Caste master table."""
    __tablename__ = "caste_master"

    caste_master_id = Column(Integer, primary_key=True, autoincrement=True)
    caste_master_name = Column(String(100), nullable=False)


class CaseCategoryMaster(Base):
    """Case category: FIR, UDR, PAR, Zero FIR."""
    __tablename__ = "case_category_master"

    case_category_id = Column(Integer, primary_key=True, autoincrement=True)
    lookup_value = Column(String(50), nullable=False)  # FIR, UDR, PAR, Zero FIR


class GravityOffenceMaster(Base):
    """Gravity of offence: Heinous, Non-Heinous."""
    __tablename__ = "gravity_offence_master"

    gravity_offence_id = Column(Integer, primary_key=True, autoincrement=True)
    lookup_value = Column(String(50), nullable=False)


class CaseStatusMaster(Base):
    """Case status master."""
    __tablename__ = "case_status_master"

    case_status_id = Column(Integer, primary_key=True, autoincrement=True)
    case_status_name = Column(String(100), nullable=False)


# ============================================================
# LEGAL FRAMEWORK TABLES
# ============================================================

class ActMaster(Base):
    """Legal acts (IPC, CrPC, NDPS, IT Act, etc.)."""
    __tablename__ = "act_master"

    act_code = Column(String(50), primary_key=True)
    act_description = Column(String(500), nullable=False)
    short_name = Column(String(100), nullable=True)
    active = Column(Boolean, default=True)

    sections = relationship("SectionMaster", back_populates="act")


class SectionMaster(Base):
    """Sections under each Act."""
    __tablename__ = "section_master"

    id = Column(Integer, primary_key=True, autoincrement=True)
    act_code = Column(String(50), ForeignKey("act_master.act_code"), nullable=False)
    section_code = Column(String(50), nullable=False)
    section_description = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)

    act = relationship("ActMaster", back_populates="sections")


class CrimeHeadMaster(Base):
    """Major crime head classification."""
    __tablename__ = "crime_head_master"

    crime_head_id = Column(Integer, primary_key=True, autoincrement=True)
    crime_group_name = Column(String(255), nullable=False)
    active = Column(Boolean, default=True)

    sub_heads = relationship("CrimeSubHeadMaster", back_populates="crime_head")


class CrimeSubHeadMaster(Base):
    """Crime sub-head under major crime head."""
    __tablename__ = "crime_sub_head_master"

    crime_sub_head_id = Column(Integer, primary_key=True, autoincrement=True)
    crime_head_id = Column(Integer, ForeignKey("crime_head_master.crime_head_id"), nullable=False)
    crime_head_name = Column(String(255), nullable=False)  # Sub-head name
    seq_id = Column(Integer, nullable=True)

    crime_head = relationship("CrimeHeadMaster", back_populates="sub_heads")


class CrimeHeadActSection(Base):
    """Maps crime heads to act+section combinations."""
    __tablename__ = "crime_head_act_section"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crime_head_id = Column(Integer, ForeignKey("crime_head_master.crime_head_id"), nullable=False)
    act_code = Column(String(50), ForeignKey("act_master.act_code"), nullable=False)
    section_code = Column(String(50), nullable=True)


class CourtMaster(Base):
    """Court registry."""
    __tablename__ = "court_master"

    court_id = Column(Integer, primary_key=True, autoincrement=True)
    court_name = Column(String(255), nullable=False)
    district_id = Column(Integer, ForeignKey("district_master.district_id"), nullable=True)
    state_id = Column(Integer, ForeignKey("state_master.state_id"), nullable=True)
    active = Column(Boolean, default=True)


# ============================================================
# EMPLOYEE TABLE
# ============================================================

class EmployeeMaster(Base):
    """Police employee/officer table."""
    __tablename__ = "employee_master"

    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    district_id = Column(Integer, ForeignKey("district_master.district_id"), nullable=True)
    unit_id = Column(Integer, ForeignKey("unit_master.unit_id"), nullable=True)
    rank_id = Column(Integer, ForeignKey("rank_master.rank_id"), nullable=True)
    designation_id = Column(Integer, ForeignKey("designation_master.designation_id"), nullable=True)
    kgid = Column(String(50), nullable=True)  # Karnataka Government ID
    first_name = Column(String(100), nullable=False)
    employee_dob = Column(Date, nullable=True)
    gender_id = Column(Integer, nullable=True)
    blood_group_id = Column(Integer, nullable=True)
    physically_challenged = Column(Boolean, default=False)
    appointment_date = Column(Date, nullable=True)


# ============================================================
# CORE CASE TABLES (Official Schema)
# ============================================================

class CaseMaster(Base):
    """
    Main FIR/Case table — aligns with official Karnataka Police schema.

    CrimeNo format: 1-digit category + 4-digit district + 4-digit PS + 4-digit year + 5-digit serial
    Example: 104430006202600001 (FIR from district 0443, PS 0006, year 2026, serial 00001)
    """
    __tablename__ = "case_master"

    case_master_id = Column(Integer, primary_key=True, autoincrement=True)
    crime_no = Column(String(50), unique=True, nullable=False, index=True)
    case_no = Column(String(20), nullable=True)  # YYYY + 5-digit serial (last 9 from CrimeNo)
    crime_registered_date = Column(Date, nullable=False)
    police_person_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=True)
    police_station_id = Column(Integer, ForeignKey("unit_master.unit_id"), nullable=True)
    case_category_id = Column(Integer, ForeignKey("case_category_master.case_category_id"), nullable=True)
    gravity_offence_id = Column(Integer, ForeignKey("gravity_offence_master.gravity_offence_id"), nullable=True)
    crime_major_head_id = Column(Integer, ForeignKey("crime_head_master.crime_head_id"), nullable=True)
    crime_minor_head_id = Column(Integer, ForeignKey("crime_sub_head_master.crime_sub_head_id"), nullable=True)
    case_status_id = Column(Integer, ForeignKey("case_status_master.case_status_id"), nullable=True)
    court_id = Column(Integer, ForeignKey("court_master.court_id"), nullable=True)
    incident_from_date = Column(DateTime(timezone=True), nullable=True)
    incident_to_date = Column(DateTime(timezone=True), nullable=True)
    info_received_ps_date = Column(DateTime(timezone=True), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    brief_facts = Column(Text, nullable=True)

    # Relationships
    complainants = relationship("ComplainantDetails", back_populates="case")
    victims_official = relationship("VictimOfficial", back_populates="case")
    accused_official = relationship("AccusedOfficial", back_populates="case")
    arrest_surrenders = relationship("ArrestSurrender", back_populates="case")
    act_sections = relationship("ActSectionAssociation", back_populates="case")
    chargesheets = relationship("ChargesheetDetails", back_populates="case")


class ComplainantDetails(Base):
    """Complainant details linked to a case."""
    __tablename__ = "complainant_details"

    complainant_id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    complainant_name = Column(String(255), nullable=False)
    age_year = Column(Integer, nullable=True)
    occupation_id = Column(Integer, ForeignKey("occupation_master.occupation_id"), nullable=True)
    religion_id = Column(Integer, ForeignKey("religion_master.religion_id"), nullable=True)
    caste_id = Column(Integer, ForeignKey("caste_master.caste_master_id"), nullable=True)
    gender_id = Column(Integer, nullable=True)

    case = relationship("CaseMaster", back_populates="complainants")


class VictimOfficial(Base):
    """Victim table — official schema."""
    __tablename__ = "victim_official"

    victim_master_id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    victim_name = Column(String(255), nullable=False)
    age_year = Column(Integer, nullable=True)
    gender_id = Column(Integer, nullable=True)  # M, F, T
    victim_police = Column(String(5), nullable=True)  # 1 if victim is police, else 0

    case = relationship("CaseMaster", back_populates="victims_official")


class AccusedOfficial(Base):
    """Accused table — official schema."""
    __tablename__ = "accused_official"

    accused_master_id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    accused_name = Column(String(255), nullable=False)
    age_year = Column(Integer, nullable=True)
    gender_id = Column(Integer, nullable=True)  # M/F/T
    person_id = Column(String(10), nullable=True)  # Sorting: A1, A2, A3...

    case = relationship("CaseMaster", back_populates="accused_official")
    arrest_links = relationship("ArrestSurrenderAccused", back_populates="accused")


class ArrestSurrender(Base):
    """Arrest/Surrender events."""
    __tablename__ = "arrest_surrender"

    arrest_surrender_id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    arrest_surrender_type_id = Column(Integer, nullable=True)  # Arrest or Surrender
    arrest_surrender_date = Column(Date, nullable=True)
    arrest_surrender_state_id = Column(Integer, ForeignKey("state_master.state_id"), nullable=True)
    arrest_surrender_district_id = Column(Integer, ForeignKey("district_master.district_id"), nullable=True)
    police_station_id = Column(Integer, ForeignKey("unit_master.unit_id"), nullable=True)
    io_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=True)
    court_id = Column(Integer, ForeignKey("court_master.court_id"), nullable=True)
    accused_master_id = Column(Integer, ForeignKey("accused_official.accused_master_id"), nullable=True)
    is_accused = Column(Boolean, default=True)
    is_complainant_accused = Column(Boolean, default=False)

    case = relationship("CaseMaster", back_populates="arrest_surrenders")


class ArrestSurrenderAccused(Base):
    """Junction table linking arrest/surrender events to accused."""
    __tablename__ = "arrest_surrender_accused"

    id = Column(Integer, primary_key=True, autoincrement=True)
    arrest_surrender_id = Column(Integer, ForeignKey("arrest_surrender.arrest_surrender_id"), nullable=False)
    accused_master_id = Column(Integer, ForeignKey("accused_official.accused_master_id"), nullable=False)

    accused = relationship("AccusedOfficial", back_populates="arrest_links")


class ActSectionAssociation(Base):
    """Links cases to act+section combinations."""
    __tablename__ = "act_section_association"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    act_id = Column(String(50), ForeignKey("act_master.act_code"), nullable=False)
    section_id = Column(String(50), nullable=True)
    act_order_id = Column(Integer, nullable=True)
    section_order_id = Column(Integer, nullable=True)

    case = relationship("CaseMaster", back_populates="act_sections")


class ChargesheetDetails(Base):
    """Chargesheet filing details."""
    __tablename__ = "chargesheet_details"

    cs_id = Column(Integer, primary_key=True, autoincrement=True)
    case_master_id = Column(Integer, ForeignKey("case_master.case_master_id"), nullable=False, index=True)
    cs_date = Column(DateTime(timezone=True), nullable=True)
    cs_type = Column(String(5), nullable=True)  # A=Chargesheet, B=False Case, C=Undetected
    police_person_id = Column(Integer, ForeignKey("employee_master.employee_id"), nullable=True)

    case = relationship("CaseMaster", back_populates="chargesheets")
