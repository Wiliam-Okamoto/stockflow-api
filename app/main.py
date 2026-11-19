from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import Product
from app.schemas import ProductCreate, ProductResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StockFlow API",
    description="API REST para controle de estoque com FastAPI",
    version="0.2.0",
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    existing_product = db.scalar(
        select(Product).where(Product.sku.ilike(payload.sku))
    )
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto cadastrado com esse SKU.",
        )

    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.get("/products", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def list_products(db: Session = Depends(get_db)) -> list[Product]:
    products = db.scalars(select(Product).order_by(Product.id)).all()
    return list(products)