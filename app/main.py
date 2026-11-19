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


from app.schemas import ProductCreate, ProductResponse, ProductUpdate, StockMovementCreate

@app.get("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )
    return product


@app.patch("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    updates = payload.model_dump(exclude_unset=True)
    if "sku" in updates and updates["sku"] is not None:
        duplicate = db.scalar(
            select(Product).where(
                Product.sku.ilike(updates["sku"]),
                Product.id != product_id,
            )
        )
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro produto cadastrado com esse SKU.",
            )

    for field, value in updates.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)) -> None:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    db.delete(product)
    db.commit()


@app.post(
    "/products/{product_id}/movements",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def register_stock_movement(
    product_id: int,
    payload: StockMovementCreate,
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    if payload.movement_type == "in":
        product.quantity += payload.quantity
    else:
        if payload.quantity > product.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quantidade de saída maior que o estoque disponível.",
            )
        product.quantity -= payload.quantity

    db.commit()
    db.refresh(product)
    return product