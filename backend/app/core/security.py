import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from app.core.config import get_settings


ALGORITHM = "HS256"
PASSWORD_SCHEME = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    salt = secrets.token_urlsafe(18)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), PASSWORD_ITERATIONS)
    encoded = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations_raw, salt, encoded = password_hash.split("$", 3)
        iterations = int(iterations_raw)
    except ValueError:
        return False
    if scheme != PASSWORD_SCHEME:
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    candidate = base64.urlsafe_b64encode(digest).decode("ascii")
    return hmac.compare_digest(candidate, encoded)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return None
    subject = payload.get("sub")
    return subject if isinstance(subject, str) else None
