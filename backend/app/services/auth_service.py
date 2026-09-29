import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import OfficialUser


ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8
DEMO_PASSWORD = "Normex@2026"


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 with a random salt.
    """

    salt = secrets.token_hex(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        120_000,
    ).hex()

    return f"pbkdf2$120000${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """
    Verify a plaintext password against a stored PBKDF2 hash.
    """

    try:
        algorithm, iterations, salt, expected = stored.split("$", 3)

        if algorithm != "pbkdf2":
            return False

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        ).hex()

        return hmac.compare_digest(digest, expected)

    except Exception:
        return False


# ============================================================
# JWT AUTHENTICATION
# ============================================================

def create_access_token(user: OfficialUser) -> str:
    """
    Create JWT access token for an authenticated NORMEX user.
    """

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(hours=TOKEN_EXPIRE_HOURS)
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "name": user.full_name,
        "organization": user.organization,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):
    """
    Decode and validate a NORMEX JWT.
    """

    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[ALGORITHM],
    )


# ============================================================
# DEMO / SYNTHETIC USERS
# ============================================================

def seed_officials(db: Session):
    """
    Create the official/demo accounts used by the NORMEX
    synthetic procurement environment.

    This function is intentionally idempotent:
    running the application multiple times will not create
    duplicate users.
    """

    users = [
        {
            "email": "procurement.officer@normex.gov.in",
            "full_name": "Aarav Sen",
            "role": "PROCUREMENT_OFFICER",
            "organization": "NORMEX Municipal Works Department",
        },
        {
            "email": "standards.officer@normex.gov.in",
            "full_name": "Mira Kapoor",
            "role": "STANDARDS_OFFICER",
            "organization": "National Standards Cell",
        },
        {
            "email": "compliance.officer@normex.gov.in",
            "full_name": "Kabir Rao",
            "role": "COMPLIANCE_OFFICER",
            "organization": "Compliance Review Cell",
        },
        {
            "email": "government.reviewer@normex.gov.in",
            "full_name": "Dev Malhotra",
            "role": "GOVERNMENT_REVIEWER",
            "organization": "NORMEX Municipal Works Department",
        },
        {
            "email": "org.admin@normex.gov.in",
            "full_name": "Riya Mehta",
            "role": "ORGANIZATION_ADMIN",
            "organization": "NORMEX Municipal Works Department",
        },
        {
            "email": "auditor@normex.gov.in",
            "full_name": "Nandita Iyer",
            "role": "AUDITOR",
            "organization": "NORMEX Audit Office",
        },
        {
            "email": "admin@normex.gov.in",
            "full_name": "NORMEX Administrator",
            "role": "ADMIN",
            "organization": "NORMEX Platform",
        },
        {
            "email": "vendor@astergrid.example",
            "full_name": "Anika Bose",
            "role": "VENDOR",
            "organization": "AsterGrid Infrastructure Pvt Ltd",
        },
        {
            "email": "vendor@bluepeak.example",
            "full_name": "Rahul Das",
            "role": "VENDOR",
            "organization": "BluePeak Urban Systems Ltd",
        },
    ]

    created = 0
    updated = 0

    for item in users:

        existing = (
            db.query(OfficialUser)
            .filter(
                OfficialUser.email == item["email"]
            )
            .first()
        )

        if existing:

            # Keep the seeded account synchronized with
            # the intended demo role and organization.
            existing.full_name = item["full_name"]
            existing.role = item["role"]
            existing.organization = item["organization"]
            existing.active = True

            updated += 1

        else:

            user = OfficialUser(
                email=item["email"],
                full_name=item["full_name"],
                role=item["role"],
                organization=item["organization"],
                password_hash=hash_password(DEMO_PASSWORD),
                active=True,
            )

            db.add(user)

            created += 1

    db.commit()

    return {
        "created": created,
        "updated": updated,
        "password": DEMO_PASSWORD,
    }


# ============================================================
# USER LOOKUP HELPERS
# ============================================================

def get_user_by_email(
    db: Session,
    email: str,
):
    """
    Retrieve an active NORMEX user by email.
    """

    return (
        db.query(OfficialUser)
        .filter(
            OfficialUser.email == email,
            OfficialUser.active == True,
        )
        .first()
    )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    """
    Authenticate a NORMEX user.

    Returns:
        OfficialUser if authentication succeeds.
        None otherwise.
    """

    user = get_user_by_email(db, email)

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    return user
