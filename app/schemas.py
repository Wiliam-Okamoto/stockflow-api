from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    sku: str = Field(..., min_length=2, max_length=50)
    quantity: int = Field(..., ge=0, description="Quantidade inicial não pode ser negativa")
    price: float = Field(..., gt=0, description="Preço unitário deve ser maior que zero")


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    sku: str | None = Field(default=None, min_length=2, max_length=50)
    quantity: int | None = Field(default=None, ge=0)
    price: float | None = Field(default=None, gt=0)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku: str
    quantity: int
    price: float


class StockMovementCreate(BaseModel):
    movement_type: Literal["in", "out"] = Field(..., description="'in' para entrada ou 'out' para saída")
    quantity: int = Field(..., gt=0, description="Quantidade movimentada deve ser maior que zero")