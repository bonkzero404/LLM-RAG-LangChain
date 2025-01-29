from typing import Dict, List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db, engine
from fastapi.staticfiles import StaticFiles
import requests
from config import XENDIT_API_KEY

models.Base.metadata.create_all(bind=engine)

app = FastAPI(swagger_ui_parameters={"syntaxHighlight": False})
app.mount("/storages", StaticFiles(directory="../storages"), name="static")

# Customer CRUD
@app.post("/customers/", response_model=schemas.CustomerSchema)
def create_customer(customer: schemas.CustomerSchema, db: Session = Depends(get_db)):
    db_customer = models.Customer(email=customer.email, full_name=customer.full_name)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.get("/customers/", response_model=List[schemas.CustomerSchema])
def read_customers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    customers = db.query(models.Customer).offset(skip).limit(limit).all()
    return customers

@app.get("/customers/{customer_id}", response_model=schemas.CustomerSchema)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=schemas.CustomerSchema)
def update_customer(customer_id: int, customer: schemas.CustomerSchema, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db_customer.email = customer.email
    db_customer.full_name = customer.full_name
    db.commit()
    db.refresh(db_customer)
    return db_customer

@app.delete("/customers/{customer_id}", response_model=schemas.CustomerSchema)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(db_customer)
    db.commit()
    return db_customer

# Product CRUD
@app.post("/products/", response_model=schemas.ProductSchema)
def create_product(product: schemas.ProductSchema, db: Session = Depends(get_db)):
    db_product = models.Product(sku=product.sku, name=product.name, price=product.price)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/", response_model=List[schemas.ProductSchema])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@app.get("/products/{product_id}", response_model=schemas.ProductSchema)
def read_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}", response_model=schemas.ProductSchema)
def update_product(product_id: int, product: schemas.ProductSchema, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db_product.sku = product.sku
    db_product.name = product.name
    db_product.price = product.price
    db.commit()
    db.refresh(db_product)
    return db_product

@app.delete("/products/{product_id}", response_model=schemas.ProductSchema)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return db_product

# Pencarian product berdasarkan SKU atau nama
@app.get("/products/search/", response_model=List[schemas.ProductSchema])
def search_products(query: str, db: Session = Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.sku.ilike(f"%{query}%") | models.Product.name.ilike(f"%{query}%")).all()
    return products

# Order CRUD
# Order CRUD
@app.post("/orders/", response_model=schemas.OrderSchemaResponse)
def create_order(order: schemas.OrderSchemaRelation, db: Session = Depends(get_db)):
    # debug order
    print("FIELD", order)

    # Search for product by SKU
    product = db.query(models.Product).filter(models.Product.sku == order.sku).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Search for customer by email
    customer = db.query(models.Customer).filter(models.Customer.email == order.email).first()
    if customer is None:
        # Insert customer if not found
        db_customer = models.Customer(email=order.email, full_name=order.full_name)
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        customer_id = db_customer.id
        customer = db_customer
    else:
        customer_id = customer.id

    order_number = models.Order.generate_order_number(db)
    db_order = models.Order(order_number=order_number, product_id=product.id, customer_id=customer_id, payment_status="pending")
    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Send data to Xendit API
    xendit_api_url = "https://api.xendit.co/v2/invoices"
    headers = {
        "Content-Type": "application/json"
    }
    # full_name_parts = customer.full_name.split()
    # given_names = full_name_parts[0]
    # surname = " ".join(full_name_parts[1:]) if len(full_name_parts) > 1 else ""
    data = {
        "external_id": order_number,
        "amount": product.price,
        "description": f"Invoice for order {order_number}",
        "invoice_duration": 86400,
        "customer": {
            "given_names": customer.full_name,
            # "surname": surname,
            "email": customer.email
        },
        "currency": "IDR",
        "items": [
            {
                "name": product.name,
                "quantity": 1,
                "price": product.price,
                "category": "Electronic",
            }
        ]
    }
    response = requests.post(xendit_api_url, headers=headers, json=data, auth=(XENDIT_API_KEY, ''))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to create invoice with Xendit")

    invoice_url = response.json().get("invoice_url")

    return schemas.OrderSchemaResponse(
        id=db_order.id,
        order_number=db_order.order_number,
        product=schemas.ProductSchema(
            sku=product.sku,
            name=product.name,
            price=product.price
        ),
        customer=schemas.CustomerSchema(
            email=customer.email,
            full_name=customer.full_name
        ),
        payment_status=db_order.payment_status,
        invoice_url=invoice_url,
        transaction_date=db_order.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.get("/orders/{order_number}", response_model=schemas.OrderSchema)
def read_order(order_number: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_number == order_number).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/order-report", response_model=Dict[str, List[int]])
def order_report(year: str, db: Session = Depends(get_db)):
    from sqlalchemy import extract, func

    orders_per_month = db.query(
        extract('month', models.Order.transaction_date).label('month'),
        func.count(models.Order.id).label('order_count')
    ).filter(
        extract('year', models.Order.transaction_date) == year
    ).group_by(
        extract('month', models.Order.transaction_date)
    ).all()

    print(f"Orders per month: {orders_per_month}")  # Debug statement

    months = [int(order.month) for order in orders_per_month]
    order_counts = [order.order_count for order in orders_per_month]

    return {"months": months, "order_counts": order_counts}