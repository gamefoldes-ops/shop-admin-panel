import os
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


def get_database_url():
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url

    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'telegram_shop')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    return f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}'


engine = create_engine(get_database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    orders: Mapped[list['Order']] = relationship(back_populates='user')


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    quantity_in_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default='pending')
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User | None] = relationship(back_populates='orders')
