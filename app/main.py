from fastapi import FastAPI, HTTPException, status

from app.schemas import ProductCreate, ProductResponse

app = FastAPI(
    title="StockFlow API",
    description="API REST para controle de estoque com FastAPI",
    version="0.1.0",
)

products_db: list[ProductResponse] = []
next_id = 1


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate) -> ProductResponse:
    global next_id

    if any(item.sku.lower() == payload.sku.lower() for item in products_db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um produto cadastrado com esse SKU.",
        )

    product = ProductResponse(id=next_id, **payload.model_dump())
    next_id += 1
    products_db.append(product)
    return product


@app.get("/products", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def list_products() -> list[ProductResponse]:
    return products_db


@app.get("/", status_code=status.HTTP_200_OK)
def root() -> dict[str, str]:
    return {"message": "StockFlow API rodando. Acesse /docs para testar."}