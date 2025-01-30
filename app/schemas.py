from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                'username': 'Damir',
                'email': 'test@example.com',
                'password': 'pass123',
                'is_staff': False,
                'is_active': True,
            }
        }


class LogInModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    # id: Optional[int]
    quantity: int
    order_statuses: Optional[str] = '1'
    # user_id: Optional[int] = None
    product_id: int

    class Config:
        form_attributes = True
        json_schema_extra = {
            "example": {
                "quantity": 20
                # "product_id": 12
            }
        }

class OrderStatusModel(BaseModel):
    order_statuses: Optional[str] = '1'

    class Config:
        form_attributes = True
        json_schema_extra = {
            "example": {
                "order_statuses": 1
                # "product_id": 12
            }
        }

class ProductModel(BaseModel):
    name: str
    price: int

    class Config:
        form_attributes = True
        json_schema_extra = {
            "example": {
                "name": "Just write some name dude!",
                "price": 200
            }
        }