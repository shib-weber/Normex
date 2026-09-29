from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, ForeignKey, Boolean, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True)
    org_type: Mapped[str] = mapped_column(String(80))
    registration_code: Mapped[str] = mapped_column(String(80), unique=True)
    jurisdiction: Mapped[str] = mapped_column(String(120), default="India")
    status: Mapped[str] = mapped_column(String(40), default="ACTIVE")
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Standard(Base):
    __tablename__ = "standards"
    id: Mapped[int] = mapped_column(primary_key=True)
    standard_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    short_title: Mapped[str | None] = mapped_column(String(250))
    domain: Mapped[str] = mapped_column(String(100), index=True)
    subdomain: Mapped[str | None] = mapped_column(String(100))
    scope: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    edition: Mapped[str | None] = mapped_column(String(100))
    publication_date: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(50), default="CURRENT")
    revision: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    source_name: Mapped[str | None] = mapped_column(String(200))
    source_type: Mapped[str] = mapped_column(String(40), default="AUTHORITY_CURATED")
    last_verified: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    versions = relationship("StandardVersion", back_populates="standard", cascade="all, delete-orphan")
    outgoing = relationship("StandardRelationship", foreign_keys="StandardRelationship.source_standard_id", back_populates="source")
    incoming = relationship("StandardRelationship", foreign_keys="StandardRelationship.target_standard_id", back_populates="target")

class StandardVersion(Base):
    __tablename__ = "standard_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("standards.id"), index=True)
    version: Mapped[str] = mapped_column(String(100))
    edition: Mapped[str | None] = mapped_column(String(100))
    publication_date: Mapped[str | None] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(50))
    supersedes_version: Mapped[str | None] = mapped_column(String(100))
    source_url: Mapped[str | None] = mapped_column(String(1000))
    verified_at: Mapped[str | None] = mapped_column(String(30))
    standard = relationship("Standard", back_populates="versions")

class StandardRelationship(Base):
    __tablename__ = "standard_relationships"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_standard_id: Mapped[int] = mapped_column(ForeignKey("standards.id"), index=True)
    target_standard_id: Mapped[int] = mapped_column(ForeignKey("standards.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(80), index=True)
    evidence: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    source_name: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source = relationship("Standard", foreign_keys=[source_standard_id], back_populates="outgoing")
    target = relationship("Standard", foreign_keys=[target_standard_id], back_populates="incoming")

class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(primary_key=True)
    input_text: Mapped[str] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(20), default="en")
    product: Mapped[str | None] = mapped_column(String(250))
    domain: Mapped[str | None] = mapped_column(String(100))
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("official_users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class CertificationRule(Base):
    __tablename__ = "certification_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_category: Mapped[str] = mapped_column(String(200))
    standard_number: Mapped[str | None] = mapped_column(String(80))
    scheme: Mapped[str] = mapped_column(String(150))
    authority: Mapped[str] = mapped_column(String(200))
    mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    conditions: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(500))
    verification_date: Mapped[str | None] = mapped_column(String(30))
    source_type: Mapped[str] = mapped_column(String(40), default="CURATED_PROTOTYPE")

class BasketItem(Base):
    __tablename__ = "basket_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    standard_id: Mapped[int] = mapped_column(ForeignKey("standards.id"), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class OfficialUser(Base):
    __tablename__ = "official_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(60), default="PROCUREMENT_OFFICER")
    password_hash: Mapped[str] = mapped_column(String(300))
    organization: Mapped[str] = mapped_column(String(250), default="NORMEX Demo Authority")
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Tender(Base):
    __tablename__ = "tenders"
    id: Mapped[int] = mapped_column(primary_key=True)
    tender_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(120))
    issuing_org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_by: Mapped[int] = mapped_column(ForeignKey("official_users.id"))
    status: Mapped[str] = mapped_column(String(40), default="DRAFT", index=True)
    budget: Mapped[float] = mapped_column(Float, default=0)
    deadline: Mapped[str] = mapped_column(String(30))
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    analysis_result: Mapped[dict] = mapped_column(JSON, default=dict)
    compliance_status: Mapped[str] = mapped_column(String(40), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TenderSubmission(Base):
    __tablename__ = "tender_submissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    vendor_org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    bid_amount: Mapped[float] = mapped_column(Float)
    technical_score: Mapped[float] = mapped_column(Float, default=0)
    commercial_score: Mapped[float] = mapped_column(Float, default=0)
    final_score: Mapped[float] = mapped_column(Float, default=0)
    proposal: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="SUBMITTED")
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EvaluationRecord(Base):
    __tablename__ = "evaluation_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    tender_id: Mapped[int] = mapped_column(ForeignKey("tenders.id"), index=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("tender_submissions.id"))
    evaluator_id: Mapped[int] = mapped_column(ForeignKey("official_users.id"))
    technical_score: Mapped[float] = mapped_column(Float)
    compliance_score: Mapped[float] = mapped_column(Float)
    commercial_score: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(Text)
    decision: Mapped[str] = mapped_column(String(40), default="REVIEW")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("official_users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(80))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    evidence_code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    evidence_type: Mapped[str] = mapped_column(String(80))
    source_name: Mapped[str] = mapped_column(String(250))
    source_reference: Mapped[str] = mapped_column(String(500))
    excerpt: Mapped[str] = mapped_column(Text)
    strength: Mapped[str] = mapped_column(String(30), default="MEDIUM")
    standard_number: Mapped[str | None] = mapped_column(String(80), index=True)
    requirement_code: Mapped[str | None] = mapped_column(String(80))
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DemoScenario(Base):
    __tablename__ = "demo_scenarios"
    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(250))
    category: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[dict] = mapped_column(JSON, default=dict)
    risk_level: Mapped[str] = mapped_column(String(30), default="MEDIUM")
    synthetic: Mapped[bool] = mapped_column(Boolean, default=True)

Index("ix_standard_domain_status", Standard.domain, Standard.status)
