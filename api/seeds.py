from sqlalchemy.orm import Session
from random import choice
from datetime import datetime, timedelta
from faker import Faker
from models import Customer, Order
from database import SessionLocal
import random

def generate_random_date_in_2024():
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def create_orders(db: Session, num_orders: int):
    fake = Faker()
    order_number_prefix = 'ORD'
    product_ids = [1, 2, 3, 4]
    payment_status_options = ['pending', 'paid']

    for i in range(1, num_orders + 1):
        customer_email = fake.email()
        customer_name = fake.name()

        customer = db.query(Customer).filter(Customer.email == customer_email).first()

        if not customer:
            customer = Customer(email=customer_email, full_name=customer_name)
            db.add(customer)
            db.commit()
            db.refresh(customer)

        order_number = f"{order_number_prefix}{i:08d}"

        payment_status = choice(payment_status_options)
        transaction_date = generate_random_date_in_2024()

        order = Order(
            order_number=order_number,
            product_id=choice(product_ids),
            customer_id=customer.id,
            payment_status=payment_status,
            transaction_date=transaction_date
        )
        db.add(order)

        if i % 100 == 0:
            db.commit()
            db.refresh(order)
            print(f"Created {i} orders so far.")

    db.commit()

def seed_database(db: Session, num_orders: int = 500000):
    print(f"Seeding {num_orders} orders...")
    create_orders(db, num_orders)
    print("Seeding completed.")


db = SessionLocal()
seed_database(db)
db.close()