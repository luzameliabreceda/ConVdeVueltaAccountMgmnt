from datetime import datetime
from typing import Optional

from ...database.model import Model


class User(Model):
    
    def __init__(self, email: str, name: str, is_active: bool = True, **kwargs):
        super().__init__(email=email, name=name, is_active=is_active, **kwargs)
    
    @property
    def email(self) -> str:
        return getattr(self, '_email', '')
    
    @email.setter
    def email(self, value: str):
        self._email = value
    
    @property
    def name(self) -> str:
        return getattr(self, '_name', '')
    
    @name.setter
    def name(self, value: str):
        self._name = value
    
    @property
    def is_active(self) -> bool:
        return getattr(self, '_is_active', True)
    
    @is_active.setter
    def is_active(self, value: bool):
        self._is_active = value
    
    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def update_profile(self, name: Optional[str] = None, email: Optional[str] = None) -> None:
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        self.updated_at = datetime.utcnow() 