from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.models import Response
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from app.auth_utils import decode_access_token
from app.database import Session, get_db

from app.models import User, Product
from app.schemas import ProductModel

product_router = APIRouter(
    prefix="/product"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@product_router.post('/create/', status_code=201)
async def create_product(product: ProductModel, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U don't have right access!")

    new_product = Product(
        name=product.name,
        price=product.price
    )

    new_product.user = user
    db.add(new_product)
    db.commit()

    res = {
        "ok": True,
        "code": 201,
        "message": "Product successfully created!",
        "data": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price
        }
    }
    return res


@product_router.get('/list/', status_code=200)
async def get_product_list(token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    db_user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if db_user.is_staff:
        products = db.query(Product).all()
        custom_res = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]
        return jsonable_encoder(custom_res)

    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U dont have access!")


@product_router.get("/{pk}/", status_code=200)
async def get_product_by_id(pk: int, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token!")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U don't have right access!")

    product = db.query(Product).filter(Product.id == pk).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id: < {pk} > not fount!")

    res = {
        "id": product.id,
        "name": product.name,
        "price": product.price
    }

    return res


@product_router.delete('/{pk}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(pk: int, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token!")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U don't have right access!")

    product = db.query(Product).filter(Product.id == pk).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id: < {pk} > not fount!")

    db.delete(product)
    db.commit()

    res = {
        "message": "Successfully deleted!",
        "ok": True
    }

    return res


@product_router.put("/update/{pk}/", status_code=status.HTTP_200_OK)
async def update_product(pk: int, data: ProductModel, token: oauth2_scheme = Depends(), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token!")

    user = db.query(User).filter(User.id == payload.get('user_id')).first()

    if user.is_staff is False:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="U don't have right access!")

    product = db.query(Product).filter(Product.id == pk).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with id: < {pk} > not fount!")

    # update product

    for key, val in data.dict(exclude_unset=True).items():
        setattr(product, key, val)

    db.commit()

    res = {
        "ok": True,
        "code": 200,
        "message": f"Product with ID {pk} successfully updated!",
        "data": {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    }

    return res
