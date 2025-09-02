from datetime import datetime, date
from typing import Optional
from sqlalchemy import Column, String, Boolean, Date
from sqlalchemy.dialects.postgresql import UUID

from ...database.model import BaseModel


class User(BaseModel):
    """User entity following PostgreSQL DDL schema"""
    
    __tablename__ = 'users'
    
    # Core user information
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(50), unique=True, nullable=True)
    
    # Personal information
    first_name = Column(String(100), nullable=True)
    paternal_surname = Column(String(100), nullable=True)
    maternal_surname = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10), nullable=True)
    national_id = Column(String(13), nullable=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=True)
    
    # Registration and status
    registration_date = Column('registration_date', nullable=False, server_default='NOW()')
    enabled = Column(Boolean, nullable=False, default=True)
    
    def __init__(self, email: str, username: Optional[str] = None, 
                 first_name: Optional[str] = None, paternal_surname: Optional[str] = None,
                 maternal_surname: Optional[str] = None, phone: Optional[str] = None,
                 date_of_birth: Optional[date] = None, gender: Optional[str] = None,
                 national_id: Optional[str] = None, password_hash: Optional[str] = None,
                 enabled: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.username = username
        self.first_name = first_name
        self.paternal_surname = paternal_surname
        self.maternal_surname = maternal_surname
        self.phone = phone
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.national_id = national_id
        self.password_hash = password_hash
        self.enabled = enabled
    
    def get_full_name(self) -> str:
        """Get user's full name"""
        names = [self.first_name, self.paternal_surname, self.maternal_surname]
        return ' '.join(name for name in names if name)
    
    def enable(self) -> None:
        """Enable user account"""
        self.enabled = True
        self.update_fields()
    
    def disable(self) -> None:
        """Disable user account"""
        self.enabled = False
        self.update_fields()
    
    def update_profile(self, first_name: Optional[str] = None, paternal_surname: Optional[str] = None,
                      maternal_surname: Optional[str] = None, phone: Optional[str] = None,
                      date_of_birth: Optional[date] = None, gender: Optional[str] = None) -> None:
        """Update user profile information"""
        if first_name is not None:
            self.first_name = first_name
        if paternal_surname is not None:
            self.paternal_surname = paternal_surname
        if maternal_surname is not None:
            self.maternal_surname = maternal_surname
        if phone is not None:
            self.phone = phone
        if date_of_birth is not None:
            self.date_of_birth = date_of_birth
        if gender is not None:
            self.gender = gender
        self.update_fields()
    
    def update_contact_info(self, email: Optional[str] = None, phone: Optional[str] = None) -> None:
        """Update contact information"""
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        self.update_fields()
    
    def set_password(self, password_hash: str) -> None:
        """Set user password hash"""
        self.password_hash = password_hash
        self.update_fields()
    
    def is_enabled(self) -> bool:
        """Check if user account is enabled"""
        return self.enabled
    
    def __repr__(self) -> str:
        full_name = self.get_full_name()
        return f"User(id={self.id}, email='{self.email}', name='{full_name}', enabled={self.enabled})"