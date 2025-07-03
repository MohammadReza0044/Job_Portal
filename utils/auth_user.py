class AuthenticatedUser:
    def __init__(self, payload):
        self.id = payload.get("user_id")
        self.email = payload.get("email")
        self.role = payload.get("role")
        self.first_name = payload.get("first_name")
        self.last_name = payload.get("last_name")
        self.payload = payload  # optionally store full JWT
        self.is_authenticated = True

    def __str__(self):
        return self.id

    def is_anonymous(self):
        return False
