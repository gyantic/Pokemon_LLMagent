import json
'''preserve result of battle'''

class BattleHistory:
  def __init__(self, filepath='battle_history.json'):
    self.filepath = filepath
    self.history = self.load_history

  def load_history(self):
    try:
      with open(self.filepath, 'r') as f:
        return json.load(f)
    except FileNotFoundError:
        return []

  def add_entry():
