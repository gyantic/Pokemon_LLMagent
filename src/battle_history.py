
from typing import List, Dict, Any

class BattleHistory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add_event(self, event: Dict[str, Any]):
        self.history.append(event)

    def get_history(self) -> List[Dict[str, Any]]:
        return self.history
