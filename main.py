from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_migrate import Migrate
from password import password
from models import db, User, Task
from datetime import date, timedelta
import os

app=Flask(__name__)
app.secret_key="taen_kluch"

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{password}@localhost:5432/python_project_tasks"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db.init_app(app)
migrate=Migrate(app, db)

with app.app_context():
    db.create_all()


def get_user():
    user_id=session.get("user_id")
    user=db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()
    return user


def date_to_month(month_number):
    months={
        1: "Януари", 2: "Февруари", 3: "Март", 4: "Април",
        5: "Май", 6: "Юни", 7: "Юли", 8: "Август",
        9: "Септември", 10: "Октомври", 11: "Ноември", 12: "Декември"}
    return months.get(month_number)


def get_current_week(offset=0):
    target_date=date.today()+timedelta(weeks=offset)
    days_after_monday=target_date.weekday()
    monday=target_date-timedelta(days=days_after_monday)
    days=[]
    for i in range(0,7):
        days.append(monday+timedelta(days=i))
    
    first_day=days[0]
    last_day=days[6]
    
    if(first_day.month==last_day.month):
        month=date_to_month(first_day.month)
    else:
        month=f"{date_to_month(first_day.month)}/{date_to_month(last_day.month)}"
        
    if(first_day.year==last_day.year):
        year=str(first_day.year)
    else:
        year=f"{first_day.year}/{last_day.year}"

    dictionary={"monday": days[0],
          "tuesday": days[1],
          "wednesday": days[2],
          "thursday": days[3],
          "friday": days[4],
          "saturday": days[5],
          "sunday": days[6],
          "month": month,
          "year": year}
    
    return dictionary


@app.route("/", methods=["GET", "POST"])
def home():
    if("user_id" not in session):
        return redirect(url_for("login"))
    
    offset=request.args.get("offset", type=int, default=0)
    user=get_user()
    week=get_current_week(offset)
    return render_template("index.html", user=user, week=week, offset=offset, today=date.today())


@app.route("/register", methods=["GET", "POST"])
def register():
    if(request.method=="GET"):
        return render_template("register.html")
    
    new_username=request.form.get("username")
    new_email=request.form.get("email")
    new_password=request.form.get("password")

    if(not new_username or not new_email or not new_password):
        return render_template("register.html", error="Моля попълнете всички полета!")
    
    if(len(new_password)<10):
        return render_template("register.html", error="Паролата трябва да е поне 10 символа!")
    
    if(db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()):
        return render_template("register.html", error="Това потребителско име вече е заето!")
    
    if(db.session.execute(db.select(User).filter_by(email=new_email)).scalar_one_or_none()):
        return render_template("register.html", error="Този имейл вече е зает!")
    
    hashed_password=generate_password_hash(new_password)
    new_user=User(username=new_username, email=new_email, password=hashed_password)
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
    
    if(len(login_password)<10):
        return render_template("login.html", error="Паролата трябва да е поне 10 символа!")
    
    user=db.session.execute(db.select(User).filter_by(username=login_username)).scalar_one_or_none()
    if(not user):
        return render_template("login.html", error="Грешно потребителско име!")
    if(check_password_hash(user.password, login_password)):
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
        if(new_username==user.username):
            return redirect(url_for('profile'))
        existing_user=db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()
        if(existing_user and existing_user.id!=user.id):
            return render_template("profile.html", user=user, error_username="Това потребителско име вече е заето!")
        user.username=new_username
        db.session.commit()
        return render_template("profile.html", user=user, success_username="Успешно променихте потребителското си име!")
    
    elif(action=="update_email"):
        new_email=request.form.get("email")
        if(new_email==user.email):
            return redirect(url_for('profile'))
        existing_user=db.session.execute(db.select(User).filter_by(email=new_email)).scalar_one_or_none()
        if(existing_user and existing_user.id!=user.id):
            return render_template("profile.html", user=user, error_email="Този имейл вече е зает!")
        user.email=new_email
        db.session.commit()
        return render_template("profile.html", user=user, success_email="Успешно променихте имейлът си!")
    
    elif(action=="update_password"):
        old_password=request.form.get("old_password")
        new_password=request.form.get("new_password")
        confirm_password=request.form.get("confirm_password")
        
        if(not old_password or not new_password or not confirm_password):
            return render_template("profile.html", user=user, error_password="Моля попълнете всички полета!")
        
        if(len(new_password)<10):
            return render_template("profile.html", user=user, error_password="Паролата трябва да е поне 10 символа!")
        
        if(not check_password_hash(user.password, old_password)):
            return render_template("profile.html", user=user, error_password="Старата парола е грешна!")
        
        if(new_password!=confirm_password):
            return render_template("profile.html", user=user, error_password="Паролите не съвпадат!")
        
        hashed_password=generate_password_hash(new_password)
        user.password=hashed_password
        db.session.commit()
        return render_template("profile.html", user=user, success_password="Успешно променихте паролата си!")


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