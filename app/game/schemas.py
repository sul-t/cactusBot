from pydantic import BaseModel

from datetime import date



class UserModel(BaseModel):
    user_id: int
    username: str
    first_name: str
    length: int
    last_grow: date

class PromocodeModel(BaseModel):
    code_id: int
    uses_left: int
    length: int

class UsesOfPromoModel(BaseModel):
    id: int
    user_id: int
    code_id: int
    