'''player configuration'''
from typing import Counter, NamedTuple, Optional

CONFIGURATION_FROM_PLAYER_COUNTER: Counter[str] = Counter()

class AccountConfiguration(NamedTuple):
  username: staticmethod
  password: Optional[str]
#usernameとpasswordの指定
