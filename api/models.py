from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    price = Column(Integer)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    product_id = Column(Integer, index=True)
    customer_id = Column(Integer, index=True)
    payment_status = Column(String)
    transaction_date = Column(DateTime, default=datetime.now, index=True)

    @staticmethod
    def generate_order_number(db_session):
        last_order = db_session.query(Order).order_by(Order.id.desc()).first()
        if last_order:
            last_order_number = int(last_order.order_number[3:])
            new_order_number = f"ORD{last_order_number + 1:06d}"
        else:
            new_order_number = "ORD000001"
        return new_order_number