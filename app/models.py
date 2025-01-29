from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from app.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import ChoiceType


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True)
    email = Column(String(100), unique=True)
    password = Column(String, nullable=True)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    orders = relationship("Order", back_populates="user")  # one-to-many field

    def __repr__(self):
        return f"<user {self.username}"


class Order(Base):
    ORDER_STATUS = (
        ('1', "pending"),
        ('2', "in_transit"),
        ('3', "delivered"),
    )
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUS), default='1')
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship('User', back_populates='orders')

    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship('Product', back_populates='orders')

    def __repr__(self):
        return f"<order {self.id}"


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    price = Column(Integer)
    orders = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<product {self.name}"

