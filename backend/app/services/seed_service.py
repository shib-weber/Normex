from sqlalchemy.orm import Session

from app.db.models import (
    Standard,
    StandardVersion,
    StandardRelationship,
    CertificationRule,
    EvidenceRecord,
    DemoScenario,
    OfficialUser,
    BasketItem,
)

from app.services.auth_service import seed_officials
from app.services.analysis_service import analyze


# ============================================================
# NORMEX SYNTHETIC DEMO DATA
# ============================================================

DOMAINS = [
    "Lighting",
    "Electrical",
    "Solar",
    "Construction",
    "Medical",
    "IT",
    "Water",
    "Transport",
    "Rail",
    "Laboratory",
]

BASES = [
    "Outdoor LED Street Lighting",
    "Low Voltage Cables",
    "Distribution Transformer",
    "Solar PV Equipment",
    "Structural Steel",
    "Cement",
    "Protective Medical Equipment",
    "Government IT Infrastructure",
    "Water Treatment Equipment",
    "EV Charging Infrastructure",
    "Railway Safety Equipment",
    "Laboratory Equipment",
]

REL_TYPES = [
    "TEST_METHOD",
    "SUPPORTS",
    "SAFETY",
    "ALLIED",
    "REFERENCES",
    "COMPATIBLE_WITH",
    "REQUIRES",
]

SCENARIOS = [
    (
        "SCN-LED",
        "Municipal LED Street Lighting",
        "Lighting",
    ),
    (
        "SCN-SOLAR",
        "Government Solar PV Plant",
        "Solar",
    ),
    (
        "SCN-IT",
        "Government Data Centre Refresh",
        "IT",
    ),
    (
        "SCN-WATER",
        "Municipal Water Treatment Upgrade",
        "Water",
    ),
    (
        "SCN-EV",
        "Public EV Charging Network",
        "Transport",
    ),
    (
        "SCN-MED",
        "Hospital PPE Procurement",
        "Medical",
    ),
    (
        "SCN-RAIL",
        "Railway Safety Equipment",
        "Rail",
    ),
    (
        "SCN-LAB",
        "Public Laboratory Equipment",
        "Laboratory",
    ),
]


def seed_demo(db: Session):
    """
    Populate the NORMEX database with synthetic demonstration data.

    All generated records are explicitly marked/documented as synthetic
    demonstration data and must not be treated as official standards,
    certification requirements, or regulatory evidence.
    """

    # ========================================================
    # 1. DEMO OFFICIALS
    # ========================================================

    seed_officials(db)

    # ========================================================
    # 2. AUTHORITATIVE/CURATED BIS KNOWLEDGE + SYNTHETIC DATA
    # ========================================================
    # These records are not copies of the BIS standard text. They are
    # metadata/index records curated from publicly visible BIS catalogue
    # and BIS technical documents. NORMEX never fabricates a standard
    # number or edition. A record is labelled AUTHORITY_CURATED and links
    # back to the BIS source page/document for verification.
    BIS_SOURCE = "https://www.bis.gov.in/know-your-standard/?lang=en"
    BIS_RECORDS = [
        ("IS 10322 (Part 1) : 2026", "Luminaires: Part 1 General Requirements and Tests (Second Revision)", "Lighting", "General luminaire requirements and tests", "2026", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/71/377/"),
        ("IS 10322 (Part 5/Sec 3) : 2026", "Luminaires: Part 5 Particular Requirements: Section 3 Luminaires for Road and Street Lighting (Second Revision)", "Lighting", "Road and street lighting luminaires", "2026", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/71/377/"),
        ("IS 10322 (Part 5/Sec 2) : 2012", "Luminaires: Part 5 Particular Requirements: Section 2 Recessed Luminaires", "Lighting", "Recessed luminaires", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/WCETD37726629_09042025_2.pdf"),
        ("IS 16107 (Part 2/Sec 1) : 2012", "Luminaires Performance: Part 2 Particular Requirements: Section 1 LED Luminaires", "Lighting", "LED luminaire performance", "2012", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/pow_new/Pow/download_pow_pdf_dept_commtt/65/377/"),
        ("IS 16106 : 2012", "Solid State Lighting (LED) Products — Performance and Safety related requirements", "Lighting", "Solid-state LED products", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/WCETD37726629_09042025_2.pdf"),
        ("IS 16102 (Part 1) : 2012", "Self-Ballasted LED Lamps for General Lighting Services: Part 1 Safety Requirements", "Lighting", "LED lamp safety", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/tbl5_2024-11-13-04-02.pdf"),
        ("IS 16102 (Part 2) : 2012", "Self-Ballasted LED Lamps for General Lighting Services: Part 2 Performance Requirements", "Lighting", "LED lamp performance", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/tbl5_2024-11-13-04-02.pdf"),
        ("IS 16103 (Part 2) : 2012", "LED Modules for General Lighting: Part 2 Performance Requirements", "Lighting", "LED module performance", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/WCETD37726629_09042025_2.pdf"),
        ("IS 16105 : 2012", "Methods of Measurement of Lumen Maintenance of Solid State Light (LED) Sources", "Lighting", "LED lumen maintenance measurement", "2012", "CURRENT", "https://www.services.bis.gov.in/tmp/WCETD37726629_09042025_2.pdf"),
        ("IS 694 : 2010", "Polyvinyl chloride insulated unsheathed and sheathed cables/cords with rigid and flexible conductor for rated voltages up to and including 1 100 V (Fourth Revision)", "Electrical", "PVC insulated cables and cords", "2010", "CURRENT", "https://services.bis.gov.in/php/BIS_2.0/bisconnect/ISL/is_details?IDS=MTM4Mjk%3D"),
        ("IS 14700 (Part 3/Sec 2) : 2008", "Electromagnetic Compatibility (EMC) Part 3 Limits Section 2 Limits for Harmonic Current Emissions (Third Revision)", "Electrical", "EMC harmonic current emissions", "2008", "CURRENT", "https://www.services.bis.gov.in/tmp/WCETD37726128_05052025_2.pdf"),
        ("IS/IEC 60529 : 2001", "Degrees of Protection Provided by Enclosures (IP Code)", "Electrical", "Ingress protection / IP code", "2001", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MzE5MDE%3D"),
        ("IS 3043 : 2018", "Code of Practice for Earthing (Second Revision)", "Electrical", "Earthing", "2018", "CURRENT", "https://services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MjQ4NzA%3D"),
        ("IS 1255 : 1983", "Code of Practice for Installation and Maintenance of Power Cables up to and Including 33 kV Rating (Second Revision)", "Electrical", "Power cable installation", "1983", "CURRENT", "https://services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MjU4MDA%3D"),
        ("IS 456 : 2000", "Plain and Reinforced Concrete — Code of Practice (Fourth Revision)", "Construction", "Concrete construction", "2000", "CURRENT", "https://services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MjQ4NzA%3D"),
        ("IS 14286 (Part 2) : 2023", "Terrestrial Photovoltaic (PV) Modules Design Qualification and Type Approval Part 2 Test Procedures (Third Revision)", "Solar", "PV module design qualification and test procedures", "2023", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=Mjg4MjQ%3D"),
        ("IS 9283 : 2024", "Line Operated A.C. Motors for Submersible Pumpsets — Specification (Third Revision)", "Water", "Submersible pump motors", "2024", "CURRENT", "https://www.services.bis.gov.in/tmp/tbl5_2024-11-09_1120.pdf"),
        ("IS 2062 : 2011", "Hot Rolled Medium and High Tensile Structural Steel — Specification (Seventh Revision)", "Construction", "Structural steel", "2011", "CURRENT", "https://www.services.bis.gov.in/tmp/SR2062.pdf"),
        ("IS 383 : 2016", "Coarse and Fine Aggregate for Concrete — Specification (Third Revision)", "Construction", "Concrete aggregates", "2016", "CURRENT", "https://www.services.bis.gov.in/php/BIS_2.0/bisconnect/standard_review/Standard_review/Isdetails?ID=MTQyNDI%3D"),
    ]
    existing = {x.standard_number: x for x in db.query(Standard).all()}
    for number, title, domain, scope, edition, status, url in BIS_RECORDS:
        if number not in existing:
            db.add(Standard(standard_number=number, title=title, short_title=title.split(" — ")[0], domain=domain, subdomain=scope, scope=scope, description=f"Metadata/index record for {number}. Verify the current applicable edition, amendments and conformity requirements on the BIS source before procurement.", edition=edition, publication_date=edition, status=status, revision="See BIS catalogue for current revision/amendments", source_url=url or BIS_SOURCE, source_name="Bureau of Indian Standards (BIS)", source_type="AUTHORITY_CURATED", last_verified="2026-09-29"))
    db.commit()

    # Remove legacy NMX-DEMO standard records from earlier Normex builds.
    # Synthetic procurement scenarios remain, but standards themselves are
    # restricted to BIS/IS authority-curated metadata.
    legacy = db.query(Standard).filter(Standard.standard_number.like("NMX-DEMO-%")).all()
    if legacy:
        legacy_ids = [s.id for s in legacy]
        db.query(StandardRelationship).filter(
            (StandardRelationship.source_standard_id.in_(legacy_ids)) |
            (StandardRelationship.target_standard_id.in_(legacy_ids))
        ).delete(synchronize_session=False)
        db.query(StandardVersion).filter(StandardVersion.standard_id.in_(legacy_ids)).delete(synchronize_session=False)
        db.query(BasketItem).filter(BasketItem.standard_id.in_(legacy_ids)).delete(synchronize_session=False)
        legacy_numbers = [s.standard_number for s in legacy]
        db.query(CertificationRule).filter(CertificationRule.standard_number.in_(legacy_numbers)).delete(synchronize_session=False)
        db.query(EvidenceRecord).filter(EvidenceRecord.standard_number.in_(legacy_numbers)).delete(synchronize_session=False)
        db.query(Standard).filter(Standard.id.in_(legacy_ids)).delete(synchronize_session=False)
        db.commit()

    standards = db.query(Standard).all()
    if not standards:
        return

    # ========================================================
    # 3. STANDARD RELATIONSHIPS / KNOWLEDGE GRAPH
    # ========================================================

    if db.query(StandardRelationship).count() < 60:

        relationship_count = 0

        for i in range(80):

            a = standards[i % len(standards)]

            b = standards[
                (i * 7 + 3) % len(standards)
            ]

            # Do not create self-referencing relationships
            if a.id == b.id:
                continue

            relationship = StandardRelationship(
                source_standard_id=a.id,

                target_standard_id=b.id,

                relationship_type=REL_TYPES[
                    i % len(REL_TYPES)
                ],

                evidence=(
                    f"Synthetic graph edge E-{i + 1:03d}; "
                    "generated for demonstration."
                ),

                confidence=round(
                    0.72 + (i % 26) / 100,
                    2
                ),

                # IMPORTANT:
                # Do NOT pass `source=` here.
                #
                # In the current SQLAlchemy model, `source`
                # is a relationship attribute rather than
                # a plain string column. Passing:
                #
                # source="NORMEX Synthetic Knowledge Base"
                #
                # causes:
                # AttributeError:
                # 'str' object has no attribute '_sa_instance_state'
            )

            db.add(relationship)

            relationship_count += 1

        db.commit()

    # Deterministic, domain-relevant edges for the working LED workflow.
    led_numbers = [
        "IS 10322 (Part 1) : 2026",
        "IS 10322 (Part 5/Sec 3) : 2026",
        "IS 16107 (Part 2/Sec 1) : 2012",
        "IS 16106 : 2012",
        "IS 14700 (Part 3/Sec 2) : 2008",
        "IS/IEC 60529 : 2001",
    ]
    led = {x.standard_number: x for x in db.query(Standard).filter(Standard.standard_number.in_(led_numbers)).all()}
    led_edges = [
        ("IS 10322 (Part 5/Sec 3) : 2026", "IS 10322 (Part 1) : 2026", "REQUIRES", "BIS technical document lists Part 5/Sec 3 with Part 1 general requirements."),
        ("IS 16107 (Part 2/Sec 1) : 2012", "IS 10322 (Part 1) : 2026", "SUPPORTS", "Performance requirements complement luminaire general safety requirements."),
        ("IS 16106 : 2012", "IS 16107 (Part 2/Sec 1) : 2012", "SUPPORTS", "LED product performance/safety relationship for procurement analysis."),
        ("IS 10322 (Part 5/Sec 3) : 2026", "IS/IEC 60529 : 2001", "SAFETY", "Ingress protection is a relevant enclosure characteristic for outdoor luminaires."),
        ("IS 16107 (Part 2/Sec 1) : 2012", "IS 14700 (Part 3/Sec 2) : 2008", "COMPATIBLE_WITH", "EMC considerations may apply to powered LED equipment."),
    ]
    existing_edges={(r.source_standard_id,r.target_standard_id,r.relationship_type) for r in db.query(StandardRelationship).all()}
    for a_num,b_num,rel,evidence in led_edges:
        a,b=led.get(a_num),led.get(b_num)
        if a and b and (a.id,b.id,rel) not in existing_edges:
            db.add(StandardRelationship(source_standard_id=a.id,target_standard_id=b.id,relationship_type=rel,evidence=evidence,confidence=0.94,source_name="BIS-indexed relationship / NORMEX curated metadata"))
    db.commit()

    # ========================================================
    # 4. STANDARD VERSIONS
    # ========================================================

    if db.query(StandardVersion).count() < 60:

        for i, standard in enumerate(standards):

            version = StandardVersion(
                standard_id=standard.id,

                version=(
                    f"DEMO-{2026 - (i % 3)}."
                    f"{i % 4 + 1}"
                ),

                edition=standard.edition,

                publication_date=standard.publication_date,

                status=standard.status,

                supersedes_version=(
                    f"DEMO-{2025 - (i % 2)}.1"
                ),

                verified_at="2026-09-28",
            )

            db.add(version)

        db.commit()

    # ========================================================
    # 5. CERTIFICATION RULES
    # ========================================================

    if db.query(CertificationRule).count() < 25:

        for i in range(25):

            standard = standards[
                i % len(standards)
            ]

            rule = CertificationRule(
                product_category=standard.short_title,

                standard_number=standard.standard_number,

                scheme=(
                    "BIS applicability verification workflow (demo)"
                ),

                authority="BIS source verification required",

                mandatory=(i % 3 == 0),

                conditions=(
                    "Demonstration rule only; verify against "
                    "the applicable official authority before "
                    "procurement."
                ),

                source="NORMEX synthetic workflow dataset",

                verification_date="2026-09-28",

                source_type="SYNTHETIC_WORKFLOW",
            )

            db.add(rule)

        db.commit()

    # ========================================================
    # 6. EVIDENCE RECORDS
    # ========================================================

    if db.query(EvidenceRecord).count() < 100:

        evidence_types = [
            "REQUIREMENT_MATCH",
            "VERSION_RECORD",
            "TEST_METHOD",
            "SAFETY_SIGNAL",
            "CERTIFICATION_SIGNAL",
        ]

        evidence_strength = [
            "HIGH",
            "MEDIUM",
            "LOW",
        ]

        for i in range(120):

            standard = standards[
                i % len(standards)
            ]

            evidence = EvidenceRecord(
                evidence_code=f"EVD-{i + 1:04d}",

                title=(
                    f"Synthetic evidence item "
                    f"{i + 1:03d} — "
                    f"{standard.short_title}"
                ),

                evidence_type=evidence_types[
                    i % len(evidence_types)
                ],

                source_name=(
                    "NORMEX Synthetic Evidence Pack"
                ),

                source_reference=(
                    f"SYNTH-{i + 1:04d} / "
                    f"Section {(i % 8) + 1}"
                ),

                excerpt=(
                    "Synthetic excerpt demonstrating "
                    f"traceability for "
                    f"{standard.standard_number}. "
                    "This text is not an official quotation."
                ),

                strength=evidence_strength[
                    i % len(evidence_strength)
                ],

                standard_number=standard.standard_number,

                requirement_code=(
                    f"REQ-{i % 30 + 1:03d}"
                ),

                synthetic=True,
            )

            db.add(evidence)

        db.commit()

    # ========================================================
    # 7. DEMO PROCUREMENT SCENARIOS
    # ========================================================

    if db.query(DemoScenario).count() < 8:

        for i, (code, title, category) in enumerate(
            SCENARIOS
        ):

            scenario = DemoScenario(
                scenario_code=code,

                title=title,

                category=category,

                description=(
                    f"Synthetic demonstration scenario "
                    f"for {title.lower()}."
                ),

                requirements={
                    "requirements": [
                        {
                            "code": (
                                f"REQ-{i * 3 + 1:03d}"
                            ),
                            "name": (
                                "Performance threshold"
                            ),
                            "value": (
                                "Synthetic measurable threshold"
                            ),
                        },
                        {
                            "code": (
                                f"REQ-{i * 3 + 2:03d}"
                            ),
                            "name": (
                                "Safety verification"
                            ),
                            "value": (
                                "Required before acceptance"
                            ),
                        },
                        {
                            "code": (
                                f"REQ-{i * 3 + 3:03d}"
                            ),
                            "name": (
                                "Testing evidence"
                            ),
                            "value": (
                                "Laboratory/test record"
                            ),
                        },
                    ]
                },

                risk_level=[
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                ][i % 3],

                synthetic=True,
            )

            db.add(scenario)

        db.commit()

# ============================================================
# PROCUREMENT WORKFLOW SEED EXTENSION
# ============================================================
from app.db.models import Organization, Tender, TenderSubmission
from app.services.auth_service import hash_password

def seed_procurement_workflow(db):
    org_specs=[
        ("NORMEX Municipal Works Department","GOVERNMENT","GOV-DEL-NMWD-001"),
        ("NORMEX Public Lighting Corporation","PUBLIC_SECTOR","PSE-LED-002"),
        ("AsterGrid Infrastructure Pvt Ltd","VENDOR","VEN-AST-101"),
        ("BluePeak Urban Systems Ltd","VENDOR","VEN-BLU-202"),
        ("CivicVolt Technologies Ltd","VENDOR","VEN-CVT-303"),
    ]
    orgs={}
    for name,typ,code in org_specs:
        o=db.query(Organization).filter_by(registration_code=code).first()
        if not o:
            o=Organization(name=name,org_type=typ,registration_code=code,jurisdiction="India",synthetic=True); db.add(o); db.flush()
        orgs[code]=o
    users=[
        ("org.admin@normex.gov.in","Riya Mehta","ORGANIZATION_ADMIN","NORMEX Municipal Works Department","GOV-DEL-NMWD-001"),
        ("procurement.officer@normex.gov.in","Aarav Sen","PROCUREMENT_OFFICER","NORMEX Municipal Works Department","GOV-DEL-NMWD-001"),
        ("government.reviewer@normex.gov.in","Dev Malhotra","GOVERNMENT_REVIEWER","NORMEX Municipal Works Department","GOV-DEL-NMWD-001"),
        ("standards.officer@normex.gov.in","Mira Kapoor","STANDARDS_OFFICER","National Standards Cell","GOV-DEL-NMWD-001"),
        ("compliance.officer@normex.gov.in","Kabir Rao","COMPLIANCE_OFFICER","Compliance Review Cell","GOV-DEL-NMWD-001"),
        ("vendor@astergrid.example","Anika Bose","VENDOR","AsterGrid Infrastructure Pvt Ltd","VEN-AST-101"),
        ("vendor@bluepeak.example","Rahul Das","VENDOR","BluePeak Urban Systems Ltd","VEN-BLU-202"),
        ("auditor@normex.gov.in","Nandita Iyer","AUDITOR","NORMEX Audit Office","GOV-DEL-NMWD-001"),
        ("admin@normex.gov.in","NORMEX Administrator","ADMIN","NORMEX Platform","GOV-DEL-NMWD-001"),
    ]
    for email,name,role,orgname,code in users:
        u=db.query(OfficialUser).filter_by(email=email).first()
        if not u:
            u=OfficialUser(email=email,full_name=name,role=role,organization=orgname,organization_id=orgs[code].id,password_hash=hash_password("Normex@2026")); db.add(u)
        else:
            u.role=role; u.organization=orgname; u.organization_id=orgs[code].id
    db.commit()
    if db.query(Tender).count()==0:
        org=orgs["GOV-DEL-NMWD-001"]; creator=db.query(OfficialUser).filter_by(email="procurement.officer@normex.gov.in").first()
        examples=[
            ("Municipal LED Street Lighting Modernisation","Outdoor LED street lights for municipal roads with approximately 90W power, IP66 protection, minimum 90 lm/W efficacy, surge protection, outdoor environmental performance, measurable testing and acceptance criteria.","Lighting",8500000,"2026-11-30","PUBLISHED"),
            ("Solar PV Rooftop Systems for Public Buildings","Grid-connected rooftop solar PV systems with defined capacity, electrical safety, monitoring, commissioning tests, documentation and maintenance requirements.","Solar",12500000,"2026-12-15","PUBLISHED"),
            ("Government Data Centre Network Refresh","Enterprise switching and routing equipment with measurable throughput, redundancy, warranty, security hardening, installation, acceptance testing and support requirements.","IT",18500000,"2026-12-20","DRAFT"),
        ]
        for idx,(title,desc,cat,budget,deadline,status) in enumerate(examples,1):
            result=analyze(db,desc)
            t=Tender(tender_number=f"NMX-TND-2026-{idx:04d}",title=title,description=desc,category=cat,issuing_org_id=org.id,created_by=creator.id,budget=budget,deadline=deadline,status=status,requirements=result["extraction"],analysis_result=result,compliance_status="ANALYSIS_READY" if not result["gaps"] else "REVIEW_REQUIRED"); db.add(t); db.flush()
        db.commit()
        published=db.query(Tender).filter_by(status="PUBLISHED").first()
        if published:
            a=db.get(Organization,orgs["VEN-AST-101"].id); b=db.get(Organization,orgs["VEN-BLU-202"].id)
            db.add_all([
                TenderSubmission(tender_id=published.id,vendor_org_id=a.id,bid_amount=8025000,technical_score=88,commercial_score=86,final_score=88*0.45+82*0.30+86*0.25,proposal={"delivery":"14 weeks","warranty":"5 years","test_pack":"Synthetic evidence pack A-17"},status="SHORTLISTED"),
                TenderSubmission(tender_id=published.id,vendor_org_id=b.id,bid_amount=7740000,technical_score=81,commercial_score=91,final_score=81*0.45+78*0.30+91*0.25,proposal={"delivery":"16 weeks","warranty":"4 years","test_pack":"Synthetic evidence pack B-11"},status="SUBMITTED"),
            ]); db.commit()
