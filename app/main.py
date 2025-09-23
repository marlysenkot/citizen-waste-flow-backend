from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from fastapi.middleware.cors import CORSMiddleware
from app.models import *
from app.routers import auth, products, waste, citizens, admin, collectors, payments, locations


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Citizen Waste Flow API")

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(waste.router)
app.include_router(citizens.router)
app.include_router(admin.router)
app.include_router(collectors.router)
app.include_router(payments.router)
app.include_router(locations.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   # Allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)
