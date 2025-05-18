from typing import TypeVar, Generic, List
import json

T = TypeVar('T')

class DataManager(Generic[T]):
    def __init__(self, filename: str):
        self.filename = filename

    def load(self) -> List[T]:
        try:
            with open(self.filename, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return []

    def save(self, data: List[T]) -> None:
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

# Automata sederhana (DFA) untuk validasi ID member
def is_valid_member_id(member_id: str) -> bool:
    state = 0
    for char in member_id:
        if state == 0 and char == 'M':
            state = 1
        elif state == 1 and char.isdigit():
            state = 2
        elif state == 2 and char.isdigit():
            continue
        else:
            return False
    return state == 2
