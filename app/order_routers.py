from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from app.auth_utils import decode_access_token
from app.database import Session, get_db

from app.models import User, Order
from app.schemas import OrderModel

order_router = APIRouter(
    prefix="/order"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@order_router.get('/')
async def default(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"message": "This is order route page!"}


@order_router.post('/create/')
async def create_order(order: OrderModel, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_user = db.query(User).filter(User.id == payload.get('user_id')).first()
    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_statuses,
        product_id=order.product_id
    )

    new_order.user = db_user
    db.add(new_order)
    db.commit()

    res = {
        "ok": True,
        "code": 201,
        "message": "Order successfully created!",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_status,
            "product": {
                "id": new_order.product.id,
                "name:": new_order.product.name,
                "price": new_order.product.price
            },
            "total_price": new_order.quantity * new_order.product.price
        }
    }

    return res


@order_router.get('/list/')
async def order_lists(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if db_user.is_staff:
        orders = db.query(Order).all()
        custom_res = [
            {
                "id": order.id,
                "user_id": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_status": order.order_status.value,
                "total_price": order.quantity * order.product.price
            }
            for order in orders
        ]
        return jsonable_encoder(custom_res)

    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")


@order_router.get('/{pk}/')
async def get_order_by_id(pk: int, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")

    order = db.query(Order).filter(Order.id == pk).first()

    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id: < {pk} > not fount!")

    res = {
        "ok": True,
        "code": 200,
        "data": {
            "id": order.id,
            "user_id": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_status": order.order_status,
            "total_price": order.quantity * order.product.price

        }
    }
    return res
