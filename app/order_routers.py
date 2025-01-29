from statistics import quantiles

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from app.auth_utils import decode_access_token
from app.database import Session, get_db

from app.models import User, Product, Order
from app.schemas import OrderModel, OrderStatusModel

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
        order_status=order.order_statuses
        # product_id = order.product_id
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
            "order_statuses": new_order.order_status
        }
    }

    return res
