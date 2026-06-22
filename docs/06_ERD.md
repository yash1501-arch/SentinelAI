# SENTINEL AI — Entity Relationship Diagram (ERD)

## Core Entities and Relationships

```
┌────────────────────────────────────────────────────────────────────┐
│  RELATIONSHIP MAP                                                  │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  USERS 1──N CASE_NOTES N──1 CRIME_INCIDENTS 1──N FIRS              │
│    │                           │                                    │
│    │                           1                                    │
│    │                           │                                    │
│    │                           N                                    │
│    │                     ┌─────┴──────┐                            │
│    │                     │   PERSONS   │                            │
│    │                     └──┬──┬──┬───┘                            │
│    │                   1│   │  │   │1                               │
│    │                ┌───┘   │  │   └───┐                            │
│    │                │       │  │       │                            │
│    │                ▼       │  │       ▼                            │
│    │            VICTIMS     │  │  WITNESSES                         │
│    │               N        │  │    N                               │
│    │               │        1  │     │                               │
│    │               1        │  │     1                               │
│    │               └────────┴──┴──────┘                             │
│    │                           │                                    │
│    │                           N                                    │
│    │                      ┌────┴─────┐                              │
│    │                      │ ACCUSED  │                              │
│    │                      └────┬─────┘                              │
│    │                           │                                    │
│    │                           N                                    │
│    │                    ┌──────┴──────┐                              │
│    │                    │  OFFENDERS  │                              │
│    │                    └─────────────┘                              │
│                                                                     │
│    ADDRESSES N──N PERSONS ──── M2M ──── VEHICLES/BANK ACCOUNTS    │
│    LOCATIONS N──1 CRIME_INCIDENTS (geo-located)                    │
│    PHONE_NUMBERS N──N INCIDENTS                                    │
│    EMAILS N──N INCIDENTS                                           │
│    BANK_ACCOUNTS N──N INCIDENTS                                    │
│    VEHICLES N──N INCIDENTS                                         │
│    WEAPONS N──N INCIDENTS                                          │
│                                                                     │
│    GANGS N──N PERSONS (gang_members)                               │
│    ORGANIZATIONS N──N PERSONS (org_members)                        │
│    TRANSACTIONS N──1 BANK_ACCOUNTS (from/to)                       │
│                                                                     │
│    CRIME_TYPES 1──N CRIME_INCIDENTS                                │
│    INVESTIGATION_STATUS N──1 CRIME_INCIDENTS                       │
│    EVIDENCE N──1 FIRS                                              │
│    SIMILAR_CASES N──1 CRIME_INCIDENTS (self-ref)                   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Cardinality Summary

| Entity A | Relationship | Entity B |
|----------|-------------|----------|
| FIR | 1 → N | CrimeIncident |
| CrimeType | 1 → N | CrimeIncident |
| Person | 1 → N | Victim |
| Person | 1 → N | Accused |
| Person | 1 → N | Witness |
| CrimeIncident | 1 → N | Victim |
| CrimeIncident | 1 → N | Accused |
| CrimeIncident | 1 → N | Witness |
| CrimeIncident | 1 → N | InvestigationStatus |
| CrimeIncident | 1 → N | CaseNote |
| CrimeIncident | 1 → N | Location |
| CrimeIncident | M → N | Vehicle |
| CrimeIncident | M → N | Weapon |
| CrimeIncident | M → N | PhoneNumber |
| CrimeIncident | M → N | Email |
| CrimeIncident | M → N | BankAccount |
| Person | M → N | Address |
| Person | M → N | Gang |
| Person | M → N | Organization |
| Person | 1 → N | Vehicle (owner) |
| Person | 1 → N | PhoneNumber |
| Person | 1 → N | BankAccount |
| BankAccount | 1 → N | Transaction (from) |
| BankAccount | 1 → N | Transaction (to) |
| CrimeIncident | M → N | CrimeIncident (SimilarCase) |
| User | 1 → N | ConversationHistory |
| User | 1 → N | CaseNote |
| User | 1 → N | AuditLog |
