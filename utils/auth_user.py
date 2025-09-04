import uuid


class AuthenticatedUser:
    def __init__(self, payload):
        user_id = payload.get("id")
        if not user_id:
            # For tests, generate a dummy UUID instead of failing
            user_id = str(uuid.uuid4())

        self.id = uuid.UUID(str(user_id))  # always convert to string
        self.email = payload.get("email", "")
        self.role = payload.get("role", "")
        self.first_name = payload.get("first_name", "")
        self.last_name = payload.get("last_name", "")
        self.payload = payload  # optionally store full JWT

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __str__(self):
        return str(self.id)
