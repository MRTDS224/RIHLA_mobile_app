from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    first_name: str = None
    last_name: str = None
    preferences: list = None
    
    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()