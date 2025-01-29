from pydantic import BaseModel

class CustomerSchema(BaseModel):
    email: str
    full_name: str

    class Config:
        orm_mode = True

class ProductSchema(BaseModel):
    sku: str
    name: str
    price: int

    class Config:
        orm_mode = True

class OrderSchema(BaseModel):
    id: int
    order_number: str
    product_id: int
    customer_id: int
    payment_status: str

    class Config:
        orm_mode = True


class OrderSchemaRelation(BaseModel):
    sku: str
    email: str
    full_name: str

    class Config:
        orm_mode = True

class OrderSchemaResponse(BaseModel):
    id: int
    order_number: str
    product: ProductSchema
    customer: CustomerSchema
    payment_status: str
    invoice_url: str
    transaction_date: str

    class Config:
        orm_mode = True
