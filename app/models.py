from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name_ar = Column(String, nullable=False)
    name_en = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    items = relationship("MenuItem", back_populates="category")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    name_ar = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    description_ar = Column(String, nullable=True)
    description_en = Column(String, nullable=True)

    popular = Column(Boolean, default=False)
    available = Column(Boolean, default=True)

    category = relationship("Category", back_populates="items")
    prices = relationship("ItemPrice", back_populates="item")


class ItemPrice(Base):
    __tablename__ = "item_prices"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)

    size_ar = Column(String, nullable=False)
    size_en = Column(String, nullable=True)
    price_lbp = Column(Integer, nullable=False)

    item = relationship("MenuItem", back_populates="prices")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    status = Column(String, default="confirmed")
    total_price = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)

    quantity = Column(Integer, nullable=False)
    size_ar = Column(String, nullable=False)
    size_en = Column(String, nullable=True)
    unit_price = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")