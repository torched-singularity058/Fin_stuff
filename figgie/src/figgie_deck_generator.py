# File defining Figgie RNG Distributor
# step 3: Abstract to a class for sampling

from enum import Enum
from typing import TypeAlias

import numpy as np
import numpy.random as random
#import matplotlib.pyplot as plt
import time

NSAMPLES = 1e9
SUIT_SIZES = [10, 10, 12, 8]
COMMON_IDX = SUIT_SIZES.index(12)
NONCOMMON_SUIT_SIZES = [10, 10, 8]

Hand: TypeAlias = dict[str, int]
DECK_CAP = 40

class SUIT_CLASS(Enum):
    GOAL = 0
    NORMAL = 1
    COMMON = 2

class Suit():
    def __init__(self, name, color, suit_class_idx: int):
        self._name: str = name
        self._color: str = color
        self._suit_class: SUIT_CLASS = SUIT_CLASS(suit_class_idx)
        self._suit_size: int = 0

    def __str__(self):
        return (f"{self._name}\n  {self._color}\n  {self._suit_class}, {self._suit_size}")
    
    def get_name(self):
        return self._name
    
    def get_color(self) -> str:
        if self._color == "Black":
            return "Black"
        elif self._color == "Red":
            return "Red"
        else:
            return "Invalid card color"
    
    def get_color_int(self) -> int:
        if self._color == "Black":
            return 0
        else:
            return 1
    
    def get_suit_class(self) -> SUIT_CLASS:
        return self._suit_class
    
    def get_suit_class_int(self) -> int:
        return self._suit_class.value
    
    def get_suit_size(self) -> int:
        return self._suit_size

    def set_suit_class(self, class_int):
        self._suit_class = SUIT_CLASS(class_int)

    def set_suit_size(self, size_int):
        if (size_int > self._suit_size): 
            if (self._suit_class == SUIT_CLASS.COMMON):
                self._suit_size = SUIT_SIZES[COMMON_IDX]
            elif (size_int in NONCOMMON_SUIT_SIZES):
                self._suit_size = size_int
            else:
                raise ValueError(f"Disallowed suit size: {size_int}")
        else:
            self._suit_size = size_int

class Figgie_Deck():
    def __init__(self):
        self._suits = [Suit("Spades", "Black", 1), 
                       Suit("Clubs", "Black", 1), 
                       Suit("Hearts", "Red", 1), 
                       Suit("Diamonds", "Red", 1)]
        self._total_size = DECK_CAP
        
        self._available_classes = [SUIT_CLASS.GOAL, 
                                   SUIT_CLASS.NORMAL, 
                                   SUIT_CLASS.NORMAL, 
                                   SUIT_CLASS.COMMON]
        self._noncommon_sizes = [10, 10, 8]
        self._common_suit = None
        self._goal_suit = None
        self._rng = random.default_rng()
    
    def __str__(self):
        deck_str = ""
        for suit in self._suits:
            deck_str += str(suit)
            deck_str += "\n"
        return deck_str

    def get_common_suit(self) -> str | None:
        # must call self.shuffle_deck() at least once before calling this function
        # to get something other than None
        return self._common_suit

    def get_goal_suit(self) -> str | None:
        # must call self.shuffle_deck() at least once before calling this function
        # to get something other than None
        return self._goal_suit

    def get_total_size(self) -> int:
        return self._total_size

    def shuffle_deck(self, show_runtime = True) -> float:
        # randomizes deck distribution according to Figgie rules
        # returns runtime

        self.deck_reset()

        time_start = time.perf_counter()

        noncommon_size_cpy = self._noncommon_sizes.copy()

        common_idx = int(self._rng.integers(len(self._suits)))
        common_suit = self._suits[common_idx]
        self._common_suit = common_suit.get_name()
        # Note: needed to adjust initialization, since type-checking SUIT type
        # is not "array-like"

        self._suits[common_idx].set_suit_class(SUIT_CLASS.COMMON)
        self._suits[common_idx].set_suit_size(SUIT_SIZES[COMMON_IDX])
        for suit in self._suits:
            if suit == common_suit: continue
            rand_size = random.choice(noncommon_size_cpy)
            if (suit.get_color() == common_suit.get_color()):
                if (suit != common_suit):
                    goal_suit = suit
                    self._goal_suit = goal_suit.get_name()
                    goal_idx = self._suits.index(goal_suit)
                    self._suits[goal_idx].set_suit_class(SUIT_CLASS.GOAL)
                    self._suits[goal_idx].set_suit_size(rand_size)
            else:
                self._suits[self._suits.index(suit)].set_suit_class(SUIT_CLASS.NORMAL)
                self._suits[self._suits.index(suit)].set_suit_size(rand_size)

            noncommon_size_cpy.remove(rand_size)
        
        time_elapsed = time.perf_counter() - time_start
        if (show_runtime): 
            print(f"Runtime: {time_elapsed*1e3:.2f}ms")
        return float(time_elapsed)

    def decrement_deck(self, hand):
        for i in range(len(self._suits)):
            suit_name = self._suits[i].get_name()
            new_size = self._suits[i].get_suit_size() - hand[suit_name]
            self._suits[i].set_suit_size(new_size)
    
    def distr_hand(self, hand_size = 8, show_runtime = False) -> Hand:
        #Note: not a private function; may be used for other analysis plots
        if (show_runtime):
            start_time = time.perf_counter()
        
        suit_names = [suit.get_name() for suit in self._suits]
        suit_sizes = [suit.get_suit_size() for suit in self._suits]
        indiv_cts = self._rng.multivariate_hypergeometric(suit_sizes, hand_size)
        #Note: multivariate hypergeometric performs categorized selection w/out replacement

        indiv_hand: Hand = {str(name): int(ct) for name, ct in zip(suit_names, indiv_cts)}
        self.decrement_deck(indiv_hand)
        self._total_size -= hand_size

        if (show_runtime):
            elapsed_time = time.perf_counter() - start_time
            print(f"Deal 1 Hand Runtime: {elapsed_time*1000:.2f}ms")
        return indiv_hand
    
    def deal_deck(self, num_players = 5, show_runtime = True) -> list[Hand]:        
        if (DECK_CAP % num_players != 0):
            raise ValueError(f"Disallowed Number of Players: {num_players}")

        if (show_runtime): start_time = time.perf_counter()        
        all_hands = []
        hand_size: int = DECK_CAP // num_players
        for _ in range(num_players):
            all_hands += [self.distr_hand(hand_size = hand_size)]

        if (show_runtime):        
            elapsed_time = time.perf_counter() - start_time
            print(f"Dealing Runtime: {elapsed_time*1000:.2f}ms")
        return all_hands

    def deck_reset(self):
        self._suits = [Suit("Spades", "Black", 1), 
                       Suit("Clubs", "Black", 1), 
                       Suit("Hearts", "Red", 1), 
                       Suit("Diamonds", "Red", 1)]

        self._noncommon_sizes = [10, 10, 8]
        self._common_suit = None
        self._goal_suit = None