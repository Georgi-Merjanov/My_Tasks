from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from datetime import date

class Base(DeclarativeBase):
    pass

db=SQLAlchemy(model_class=Base)

class User(Base):
    __tablename__ = "Users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_picture: Mapped[str] = mapped_column(Text, nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "Tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    day_for: Mapped[date] = mapped_column(Date, nullable=False)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id", name="fk_task_user"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="tasks")