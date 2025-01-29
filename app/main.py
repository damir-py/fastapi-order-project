from fastapi import FastAPI

from app.auth_routers import auth_router
from app.order_routers import order_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)


@app.get('/')
def get_app():
    return {'message': 'main page'}
