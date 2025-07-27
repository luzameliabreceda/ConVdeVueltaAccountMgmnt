from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class Model(ABC):
    
    def __init__(self, **kwargs):
        self._data = {}
        self._set_defaults()
        self._set_attributes(kwargs)
    
    def _set_defaults(self):
        if not hasattr(self, 'id') or not self.id:
            self.id = str(uuid.uuid4())
        if not hasattr(self, 'created_at'):
            self.created_at = datetime.utcnow()
        if not hasattr(self, 'updated_at'):
            self.updated_at = datetime.utcnow()
    
    def _set_attributes(self, attributes: Dict[str, Any]):
        for key, value in attributes.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self._data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        result = {}
        
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                result[attr_name] = getattr(self, attr_name)
        
        result.update(self._data)
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        return cls(**data)
    
    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self._data[key] = value
        self.updated_at = datetime.utcnow()
    
    def __getattr__(self, name: str) -> Any:
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name in ['_data', 'id', 'created_at', 'updated_at'] or hasattr(self, name):
            super().__setattr__(name, value)
        else:
            self._data[name] = value 