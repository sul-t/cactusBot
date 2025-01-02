from pydantic import BaseModel, field_validator

from datetime import date



class UserModel(BaseModel):
    user_id: int
    username: str | None
    first_name: str | None
    length: int
    last_grow: date
    bonus_attempts: int
    grow_streak: int

class PromocodeModel(BaseModel):
    id: int
    uses_left: int
    length: int

class UsesOfPromoModel(BaseModel):
    user_id: int
    code_id: int

class BonusModel(BaseModel):
    bonus_cm: int
    bonus_attempts: int
    




class UserDataRequest(BaseModel):
    id: int
    username: str
    first_name: str

    @field_validator('first_name')
    def check_first_name(cls, first_name):
        if first_name is None:
            return 'user'
        
    @field_validator('username')
    def check_username(cls, username):
        if username is None:
            return cls.first_name
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name
        }
        
    
class UserDataResponse(BaseModel):
    first_name: str
    length: int
    last_grow: date