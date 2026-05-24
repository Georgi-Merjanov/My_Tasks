from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from flask_migrate import Migrate
from password import password
import os

app=Flask(__name__)
app.secret_key="taen_kluch"

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{password}@localhost:5432/python_project_tasks"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(model_class=Base)
db.init_app(app)
migrate=Migrate(app, db)


class User(Base):
    __tablename__ = "Users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_picture: Mapped[str] = mapped_column(String(255), nullable=True)
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "Tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    day_for: Mapped[str] = mapped_column(String(10), nullable=False)
    is_finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id", name="fk_task_user"), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="tasks")


with app.app_context():
    db.create_all()


def get_user():
    user_id=session.get("user_id")
    user=db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
    return user


@app.route("/", methods=["GET", "POST"])
def home():
    if("user_id" not in session):
        return redirect(url_for("login"))
    return render_template("index.html", user=get_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if(request.method=="GET"):
        return render_template("register.html")
    
    new_username=request.form.get("username")
    new_email=request.form.get("email")
    new_password=request.form.get("password")
    if(not new_username or not new_email or not new_password):
        return render_template("register.html", error="Моля попълнете всички полета!")
    
    if(db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()):
        return render_template("register.html", error="Това потребителско име вече е заето!")
    
    if(db.session.execute(db.select(User).filter_by(email=new_email)).scalar_one_or_none()):
        return render_template("register.html", error="Този имейл вече е зает!")
    
    new_user=User(username=new_username, email=new_email, password=new_password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method=="GET"):
        return render_template("login.html")

    login_username=request.form.get("username")
    login_password=request.form.get("password")
    if(not login_username or not login_password):
        return render_template("login.html", error="Моля попълнете всички полета!")
    
    user=db.session.execute(db.select(User).filter_by(username=login_username)).scalar_one_or_none()
    if(not user):
        return render_template("login.html", error="Грешно потребителско име!")
    if(user.password==login_password):
        session["user_id"]=user.id
        return redirect(url_for("home"))
    else:
        return render_template("login.html", error="Грешна парола!")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if(request.method=="GET"):
        return render_template("profile.html", user=get_user())
    
    user=get_user()
    action=request.form.get("action")

    if(action=="update_avatar"):
        file=request.files.get("profile_picture")
        file.filename=f"{user.id}.png"
        path=os.path.join(app.root_path, "static", "profile_pictures", file.filename)
        file.save(path)
        user.profile_picture=file.filename
        db.session.commit()
        return redirect(url_for('profile'))
    
    elif(action=="remove_avatar"):
        file_path=os.path.join(app.root_path, "static", "profile_pictures", user.profile_picture)
        if(os.path.exists(file_path)):
            os.remove(file_path)
        user.profile_picture=None
        db.session.commit()
        return redirect(url_for('profile'))
    
    elif(action=="update_username"):
        new_username=request.form.get("username")
        if new_username==user.username:
            return redirect(url_for('profile'))
        existing_user=db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()
        if(existing_user and existing_user.id!=user.id):
            return render_template("profile.html", user=user, error="Това потребителско име вече е заето!")
        user.username=new_username
        db.session.commit()
        return render_template("profile.html", user=user, success="Успешно променихте потребителското си име!")


@app.route("/logout", methods=["GET","POST"])
def logout():
    if(request.method=="POST"):
        db.session.delete(get_user())
        db.session.commit()
    session.clear()
    return redirect(url_for("login"))


@app.route("/statistics", methods=["GET"])
def statistics():
    return render_template("statistics.html", user=get_user())


if(__name__ == "__main__"):
    app.run(debug=True)