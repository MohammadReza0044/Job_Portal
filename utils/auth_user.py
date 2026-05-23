import uuid


class AuthenticatedUser:
    def __init__(self, payload):
        user_id = payload.get("user_id")

        if not user_id:
            raise ValueError(
                f"JWT payload is missing 'user_id'. Got keys: {list(payload.keys())}"
            )

        self.id = uuid.UUID(str(user_id))
        self.email = payload.get("email", "")
        self.role = payload.get("role", "")
        self.first_name = payload.get("first_name", "")
        self.last_name = payload.get("last_name", "")
        self.payload = payload

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return str(self.id)
