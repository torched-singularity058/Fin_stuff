# Player Defn File

from figgie_deck_generator import Hand

class Player():
    def __init__(self, name, starting_chips):
        self._name: str = name
        self._chips: int = starting_chips
        self._hand: Hand = {}

    def __str__(self):
        return (f"Player {self._name}: {self._chips}")

class Bot(Player):
    def __init__(self, name, starting_chips, difficulty):
        super.__init__(name, starting_chips)
        self._difficulty: str = difficulty

    def __str__(self):
        return (f"Bot {self._name}: {self._chips}")
