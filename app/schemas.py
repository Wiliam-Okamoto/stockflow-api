from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    sku: str = Field(..., min_length=2, max_length=50)
    quantity: int = Field(..., ge=0, description="Quantidade inicial não pode ser negativa")
    price: float = Field(..., gt=0, description="Preço unitário deve ser maior que zero")


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    quantity: int
    price: float