class RBFunction:
    def __init__(
        self,
        id: int | None = None,
        module_id: int | None = None,
        name: str | None = None,
        expression: int | None = None
    ):
        self.id = id
        self.module_id = module_id
        self.name = name
        self.expression = expression

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "expression": self.expression
        }
        return {k: v for k, v in data.items() if v is not None}
