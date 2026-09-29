# NORMEX — Procurement & Standards Intelligence Master

NORMEX is a full-stack GovTech prototype for moving a procurement case through a controlled lifecycle:

**Organisation → requirement authoring → standards/BIS-style intelligence → tender linting → compliance gate → publication → supplier submission → government evaluation → audit trail**

> **Important:** all standards, certification rules, users, organisations, tenders, supplier bids and evidence in the bundled database are synthetic demonstration data. They are not official BIS/ISO/IEC/Government records and must not be used as legal, regulatory or procurement authority.

## What is included

### Role-based workspace

- **Organization Administrator** — create/manage the organisation's tender pipeline and request publication.
- **Procurement Officer** — create tenders, run intelligence, publish eligible cases and evaluate supplier submissions.
- **Government Reviewer** — review published procurement cases and evaluate supplier responses.
- **Standards Officer** — standards/knowledge workflow access for standards review.
- **Compliance Officer** — compliance gate and publication approval.
- **Vendor / Supplier** — see published tenders and submit a bid/proposal.
- **Audit Officer** — inspect the synthetic audit/event trail.
- **Platform Administrator** — platform-wide administration and audit access.

### Intelligence workflow

- Requirement extraction with measurable operators/units
- Standards retrieval and recommendation
- Version/revision signals
- Standards relationship graph
- Certification/compliance checks
- Evidence traceability
- Tender Linter for ambiguity, testing, installation, inspection and acceptance gaps
- Procurement risk signals
- PDF/DOCX/TXT analysis
- Report generation

### Procurement workflow

1. Organisation/user account
2. Draft tender
3. Automatic requirement + standards analysis
4. Compliance/gap review
5. Publication gate
6. Supplier discovery
7. Supplier bid submission
8. Technical/compliance/commercial evaluation
9. Weighted final score calculation
10. Synthetic audit event trail

## Demo accounts

All demo accounts use:

```text
Password: Normex@2026
```

| Role | Email |
|---|---|
| Organization Administrator | `org.admin@normex.gov.in` |
| Procurement Officer | `procurement.officer@normex.gov.in` |
| Government Reviewer | `government.reviewer@normex.gov.in` |
| Standards Officer | `standards.officer@normex.gov.in` |
| Compliance Officer | `compliance.officer@normex.gov.in` |
| Vendor | `vendor@astergrid.example` |
| Vendor | `vendor@bluepeak.example` |
| Audit Officer | `auditor@normex.gov.in` |
| Platform Administrator | `admin@normex.gov.in` |

## Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`

The database is SQLite by default and is automatically created/seeded at startup.

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

Set `VITE_API_BASE_URL` in `frontend/.env` if the backend is hosted elsewhere.

## Main routes

- `/` — landing page
- `/login` — role-aware authentication
- `/dashboard` — intelligence dashboard
- `/procurement` — end-to-end procurement hub
- `/analysis/new` — requirement analysis
- `/tender-linter` — tender quality gate
- `/standards` — standards knowledge base
- `/evidence` — evidence centre
- `/graph` — standards relationship graph
- `/compliance` — certification/compliance checks
- `/reports` — exportable reports
- `/history` — analysis history
- `/scenarios` — synthetic scenario explorer

## API highlights

```text
POST /api/v1/auth/login
GET  /api/v1/procurement/overview
POST /api/v1/procurement/tenders
POST /api/v1/procurement/tenders/{id}/publish
POST /api/v1/procurement/tenders/{id}/submit
POST /api/v1/procurement/submissions/{id}/evaluate
GET  /api/v1/procurement/audit
GET  /api/v1/organizations
GET  /api/v1/standards/search
POST /api/v1/analysis
POST /api/v1/tender/analyze
POST /api/v1/compliance/check
```

## Resetting the synthetic environment

Stop the backend and delete `backend/normex.db`. Restarting the API recreates the complete synthetic dataset.

## Production hardening

Before real use, replace the synthetic knowledge base with authoritative/licensed sources, implement approved identity and access management, use PostgreSQL, add secure object storage, rotate secrets, add formal audit controls, validate every regulatory/procurement rule, and independently review all automated recommendations.

## Real-data / BIS mode

The cleaned bundle contains no NMX-DEMO standards. Synthetic data represents realistic Indian public-procurement scenarios, while every standard returned by the standards layer is an authority-curated BIS/IS metadata record linked to a BIS source. The build does not invent unverified IS numbers; the current LED workflow uses the BIS-listed 2026 IS 10322 family where verified, with older standards retained only where they are the applicable published record.

The recommended live-data pattern is:

`PDF/DOCX/TXT tender → extraction → measurable requirements → BIS metadata retrieval → related standards → evidence/version checks → tender lint → procurement workflow`

The supplied `data/samples/LED_Street_Lighting_Tender.txt` can be uploaded immediately to exercise this end-to-end path.
