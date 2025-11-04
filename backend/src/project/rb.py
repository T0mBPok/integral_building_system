class RBProject:
    def __init__(
        self,
        id: int | None = None,
        user_id: int | None = None,
        name: str | None = None,
        description: int | None = None
    ):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.description = description

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description
        }
        return {k: v for k, v in data.items() if v is not None}
