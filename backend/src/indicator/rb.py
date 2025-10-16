class RBIndicator:
    def __init__(
        self,
        id: int | None = None,
        module_id: int | None = None,
        name: str | None = None,
        value: int | None = None
    ):
        self.id = id
        self.module_id = module_id
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "value": self.value
        }
        return {k: v for k, v in data.items() if v is not None}
