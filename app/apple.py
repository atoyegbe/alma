from datetime import time
import os
import jwt

from app.users import get_user
from main import get_db

JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 60 * 60 * 24 * 3  # 3 days
# JWT_SHORT_EXP_DELTA_SECONDS = 60 * 60 * 12  # 12 hours
JWT_SHORT_EXP_DELTA_SECONDS = 144000

# TODO: : ability to login with apple music.
apple_kid = os.getenv('APPLE_KID', '')
# Payload (you can customize this according to your requirements)
header = {
    "alg": "ES256",
    "kid": apple_kid
}

# Payload including additional claims
payload = {
    "iss": apple_kid,
    "iat": int(time.time()),  # Current time in seconds since epoch
    "exp": int(time.time()) + 15777000,  # Expiration time 6 months from now
}

def generate_apple_jwt_token():
    jwt.encode(payload=payload, algorithm=JWT_ALGORITHM, headers=header)


