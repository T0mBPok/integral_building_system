class RBLevel:
    def __init__(
        self,
        id: int | None = None,
        project_id: int | None = None,
        number: int | None = None,
        function_id: int | None = None
    ):
        self.id = id
        self.project_id = project_id
        self.number = number
        self.function_id = function_id

    def to_dict(self) -> dict:
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "number": self.number,
            "function_id": self.function_id
        }
        # убираем все None-поля, чтобы удобно фильтровать при get
        return {k: v for k, v in data.items() if v is not None}
