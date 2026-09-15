from abc import ABC, abstractmethod

from pydantic import BaseModel

from atlas.tools.types import ToolPolicy


class Tool[
    InputT: BaseModel,
    OutputT: BaseModel,
](ABC):
    name: str
    description: str

    input_schema: type[InputT]
    output_schema: type[OutputT]

    policy: ToolPolicy

    @abstractmethod
    async def execute(
        self,
        input_data: InputT,
    ) -> OutputT:
        raise NotImplementedError

    def specification(
        self,
    ) -> dict[str, object]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema.model_json_schema(),
        }
