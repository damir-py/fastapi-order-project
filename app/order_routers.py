from fastapi import APIRouter, Depends, status
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


@order_router.get('/', status_code=status.HTTP_200_OK)
async def default(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return {"message": "This is order route page!"}


@order_router.post('/create/', status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()
    if user.is_staff is False or user is None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")

    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_statuses,
        product_id=order.product_id
    )

    new_order.user = user
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


@order_router.get('/list/', status_code=status.HTTP_200_OK)
async def order_lists(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False or user is None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")

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
    return custom_res


@order_router.get("/user/", status_code=status.HTTP_200_OK)
async def get_user_orders(token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False or user is None:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")

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
        for order in user.orders
    ]

    return custom_res


@order_router.get('/user/{pk}', status_code=status.HTTP_200_OK)
async def get_orders_by_id(pk: int, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")

    user = db.query(User).filter(User.id == pk).first()
    print(user, "*" * 50)

    if user is None or user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="No access!")

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
        for order in user.orders
    ]

    return custom_res


@order_router.put('/{pk}/update/')
async def update_order(pk: int, order: OrderModel, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    print(payload, "*" * 50)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token!")

    order_to_update = db.query(Order).filter(Order.id == pk).first()

    if order_to_update is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found!")

    if order_to_update.user.id != payload.get("user_id"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="U don't have right access to update!")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    db.commit()

    res = {
        "ok": True,
        "code": 200,
        "message": "Your order updated successfully!",
        "data": {
            "id": order_to_update.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_status": order.order_statuses
        }
    }

    return res


@order_router.get('/{pk}/', status_code=status.HTTP_200_OK)
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
