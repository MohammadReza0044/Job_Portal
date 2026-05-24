import datetime

import jwt
from decouple import config

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = "HS256"


def generate_test_jwt(user_id=1, username="testuser", role="Employer", exp_minutes=30):

    payload = {
        "id": str(user_id),
        "username": username,
        "role": role,  # ensure IsEmployer sees the correct role
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=exp_minutes),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
