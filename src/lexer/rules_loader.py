import json
from pathlib import Path
from typing import Optional, Union


class Rule:
    def __init__(self):
        self.transition = {}
        self.initial_state = {}
        self.final_states = {}
        self.lookup = {}

    def load_rule(self, path: Optional[Union[str, Path]] = None):
        if path is None:
            path = Path(__file__).resolve().parents[1] / "rules" / "dfa.json"
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"DFA rules file not found: {path}")

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read/parse DFA JSON file '{path}': {e}")

        if "initial_state" not in data:
            raise KeyError("Missing 'initial_state' in DFA JSON")
        if "final_states" not in data:
            raise KeyError("Missing 'final_states' in DFA JSON")
        if "transition" not in data:
            raise KeyError("Missing 'transition' in DFA JSON")

        self.initial_state = data["initial_state"]
        self.final_states = data["final_states"]
        self.transition = data["transition"]
        self.lookup = data["lookup"]
        return self
