import json


class Component:
    def to_json(self) -> str:
        return json.dumps(
            self,
            default=lambda object: object.__dict__,
            sort_keys=True,
            indent=4,
        )

    @classmethod
    def from_json(cls, json_string: str):
        component_dict = json.loads(json_string)
        return cls(**component_dict)
