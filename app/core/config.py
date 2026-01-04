import os
from dotenv import load_dotenv

load_dotenv()

# --------------------
# ADMIN CREDENTIALS
# --------------------
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# --------------------
# JWT CONFIG
# --------------------
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# --------------------
# GROQ
# --------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --------------------
# GOOGLE BLOGGER OAUTH
# --------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# --------------------
# VALIDATION (FAIL FAST)
# --------------------
missing = []

if not ADMIN_USERNAME or not ADMIN_PASSWORD:
    missing.append("ADMIN_USERNAME / ADMIN_PASSWORD")

if not JWT_SECRET_KEY:
    missing.append("JWT_SECRET_KEY")

if not GROQ_API_KEY:
    missing.append("GROQ_API_KEY")

if missing:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(missing)
    )
