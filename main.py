from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta
from flask_migrate import Migrate
from models import db, User, Task
from dotenv import load_dotenv
import base64
import os

load_dotenv()
app=Flask(__name__)
app.secret_key="taen_kluch"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
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


@app.route("/", methods=["GET"])
def home():
    if("user_id" not in session):
        return redirect(url_for("login"))
    
    user=get_user()
    return render_template("index.html", user=user)


@app.route("/week/data", methods=["GET"])
def get_week_data():
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    offset=request.args.get("offset", type=int, default=0)
    week=get_current_week(offset)

    start_date=week["monday"]
    end_date=week["sunday"]
    
    tasks=db.session.execute(
        db.select(Task).filter(Task.user_id==user.id, Task.day_for>=start_date, Task.day_for<=end_date).order_by(Task.is_finished, Task.id.desc())).scalars().all()

    response_data={
        "month": week["month"],
        "year": week["year"],
        "today_iso": date.today().isoformat(),
        "days": {
            "monday": week["monday"].isoformat(),
            "tuesday": week["tuesday"].isoformat(),
            "wednesday": week["wednesday"].isoformat(),
            "thursday": week["thursday"].isoformat(),
            "friday": week["friday"].isoformat(),
            "saturday": week["saturday"].isoformat(),
            "sunday": week["sunday"].isoformat()},
        "days_numbers": {
            "monday": week["monday"].day,
            "tuesday": week["tuesday"].day,
            "wednesday": week["wednesday"].day,
            "thursday": week["thursday"].day,
            "friday": week["friday"].day,
            "saturday": week["saturday"].day,
            "sunday": week["sunday"].day},
        "tasks": [dictify(task) for task in tasks]}

    return jsonify(response_data), 200


def dictify(task):
    return{
        "id": task.id,
        "name": task.name,
        "day_for": task.day_for.isoformat(),
        "is_finished": task.is_finished}


@app.route("/tasks", methods=["GET", "POST"])
def add_task_or_send_all_tasks():
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    if(request.method=="POST"):
        if(not request.is_json):
            return jsonify({"error": "Невалиден формат на данните!"}), 400

        data=request.get_json()
        task_text=data.get("name")
        task_date=data.get("day_for")

        if(not task_text or task_text.strip() == ""):
            return jsonify({"error": "Името на задачата не може да бъде празно!"}), 400
        
        if(not task_date or task_date.strip() == ""):
            return jsonify({"error": "Датата на задачата не може да бъде празна!"}), 400
        
        try:
            date_object=date.fromisoformat(task_date)
            
            new_task=Task(name=task_text, day_for=date_object, user_id=user.id)
            db.session.add(new_task)
            db.session.commit()
            
            return jsonify(dictify(new_task)), 201
        
        except ValueError:
            return jsonify({"error": "Невалиден формат на датата!"}), 400
    
    elif(request.method=="GET"):
        tasks=db.session.execute(db.select(Task).filter_by(user_id=user.id).order_by(Task.is_finished, Task.id.desc())).scalars().all()
        return jsonify([dictify(task) for task in tasks])


def get_task(task_id):
    task=db.session.execute(db.select(Task).filter_by(id=task_id)).scalar_one_or_none()
    return task


@app.route("/tasks/<int:task_id>/checkbox", methods=["PATCH"])
def toggle_checkbox(task_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    task=get_task(task_id)
    if(not task):
            return jsonify({"error": "Задачата не е намерена!"}), 404

    task.is_finished=not task.is_finished
    db.session.commit()
    return jsonify(dictify(task)), 200


@app.route("/tasks/<int:task_id>", methods=["PATCH", "DELETE"])
def edit_or_delete_task(task_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    task=get_task(task_id)
    if(not task):
        return jsonify({"error": "Задачата не е намерена!"}), 404

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    if(request.method=="PATCH"):
        if(not request.is_json):
            return jsonify({"error": "Невалиден формат на данните!"}), 400

        data=request.get_json()
        task_text=data.get("name")

        if(not task_text or task_text.strip() == ""):
            return jsonify({"error": "Името на задачата не може да бъде празно!"}), 400
        
        task.name=task_text
        db.session.commit()
        return jsonify(dictify(task)), 200
    
    elif(request.method=="DELETE"):
        db.session.delete(task)
        db.session.commit()
        return "", 204


@app.route("/register", methods=["GET", "POST"])
def register():
    if(request.method=="GET"):
        return render_template("register.html")
    
    data=request.get_json()
    if(not data):
        return jsonify({"error": "Невалиден JSON формат"}), 400
    
    new_username=data.get("username")
    new_email=data.get("email")
    new_password=data.get("password")

    if(not new_username or not new_email or not new_password):
        return jsonify({"error": "Моля попълнете всички полета!"}), 400
    
    if(len(new_password)<10):
        return jsonify({"error": "Паролата трябва да е поне 10 символа!"}), 400
    
    if(db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()):
        return jsonify({"error": "Това потребителско име вече е заето!"}), 400
    
    if(db.session.execute(db.select(User).filter_by(email=new_email)).scalar_one_or_none()):
        return jsonify({"error": "Този имейл вече е зает!"}), 400
    
    hashed_password=generate_password_hash(new_password)
    new_user=User(username=new_username, email=new_email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"success": "Успешна регистрация!"}), 201


@app.route("/login", methods=["GET", "POST"])
def login():
    if(request.method=="GET"):
        return render_template("login.html")

    data=request.get_json()
    if(not data):
        return jsonify({"error": "Невалиден JSON формат"}), 400

    login_username=data.get("username")
    login_password=data.get("password")

    if(not login_username or not login_password):
        return jsonify({"error": "Моля попълнете всички полета!"}), 400
    
    if(len(login_password)<10):
        return jsonify({"error": "Паролата трябва да е поне 10 символа!"}), 400
    
    user=db.session.execute(db.select(User).filter_by(username=login_username)).scalar_one_or_none()
    if(not user):
        return jsonify({"error": "Грешно потребителско име!"}), 400
    if(check_password_hash(user.password, login_password)):
        session["user_id"]=user.id
        return jsonify({"success": "Успешен вход!"}), 200
    else:
        return jsonify({"error": "Грешна парола!"}), 400


@app.route("/profile", methods=["GET"])
def profile():
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    return render_template("profile.html", user=get_user())


@app.route("/users/<int:user_id>/avatar", methods=["PATCH"])
def update_avatar(user_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401
        
    if(session["user_id"]!=user_id):
        return jsonify({"error": "Нямате привилегии за това действие!"}), 403

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    if(request.is_json):
        data=request.get_json()
        if("profile_picture" in data and data.get("profile_picture") is None):
            user.profile_picture=None
            db.session.commit()
            return jsonify({"success": "Снимката беше премахната успешно!"}), 200

    if('profile_picture' in request.files):
        file=request.files['profile_picture']
        
        if(file.filename == ''):
            return jsonify({"error": "Не е избран валиден файл!"}), 400
            
        file_bytes = file.read()
        base64_encoded = base64.b64encode(file_bytes).decode('utf-8')
        file_type = file.content_type
        data_url = f"data:{file_type};base64,{base64_encoded}"
        
        user.profile_picture = data_url
        db.session.commit()
        
        return jsonify({"success": "Снимката беше обновена успешно!"}), 200

    return jsonify({"error": "Невалиден формат на данните!"}), 400


@app.route("/users/<int:user_id>/username", methods=["PATCH"])
def update_username(user_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401
        
    if(session["user_id"]!=user_id):
        return jsonify({"error": "Нямате привилегии за това действие!"}), 403

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    if(not request.is_json):
        return jsonify({"error": "Невалиден формат на данните!"}), 400

    data=request.get_json()
    new_username=data.get("username")

    if(not new_username or new_username.strip() == ""):
        return jsonify({"error": "Потребителското име не може да бъде празно!"}), 400

    if(new_username==user.username):
        return "", 204

    existing_user=db.session.execute(db.select(User).filter_by(username=new_username)).scalar_one_or_none()
    if(existing_user and existing_user.id!=user.id):
        return jsonify({"error": "Това потребителско име вече е заето!"}), 400

    user.username=new_username
    db.session.commit()
    return jsonify({"success": "Успешно променихте потребителското си име!"}), 200


@app.route("/users/<int:user_id>/email", methods=["PATCH"])
def update_email(user_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401
        
    if(session["user_id"]!=user_id):
        return jsonify({"error": "Нямате привилегии за това действие!"}), 403

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    if(not request.is_json):
        return jsonify({"error": "Невалиден формат на данните!"}), 400

    data=request.get_json()
    new_email=data.get("email")

    if(not new_email or new_email.strip() == ""):
        return jsonify({"error": "Имейлът не може да бъде празен!"}), 400

    if(new_email==user.email):
        return '', 204

    existing_user = db.session.execute(db.select(User).filter_by(email=new_email)).scalar_one_or_none()
    if(existing_user and existing_user.id!=user.id):
        return jsonify({"error": "Този имейл вече е зает!"}), 400

    user.email=new_email
    db.session.commit()
    return jsonify({"success": "Успешно променихте имейла си!"}), 200


@app.route("/users/<int:user_id>/password", methods=["PATCH"])
def update_password(user_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401
        
    if(session["user_id"] != user_id):
        return jsonify({"error": "Нямате привилегии за това действие!"}), 403

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    if(not request.is_json):
        return jsonify({"error": "Невалиден формат на данните!"}), 400

    data=request.get_json()
    old_password=data.get("old_password")
    new_password=data.get("new_password")
    confirm_password=data.get("confirm_password")

    if(not old_password or not new_password or not confirm_password):
        return jsonify({"error": "Моля попълнете всички полета!"}), 400

    if(len(new_password) < 10):
        return jsonify({"error": "Новата парола трябва да е поне 10 символа!"}), 400

    if(not check_password_hash(user.password, old_password)):
        return jsonify({"error": "Старата парола е грешна!"}), 400

    if(new_password!=confirm_password):
        return jsonify({"error": "Паролите не съвпадат!"}), 400

    user.password=generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"success": "Успешно променихте паролата си!"}), 200


@app.route("/logout", methods=["POST"])
def logout():
    if("user_id" not in session):
        return jsonify({"error": "Нямате достъп!"}), 401
    session.clear()
    return "", 204


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401
    
    if(session["user_id"]!=user_id):
        return jsonify({"error": "Нямате привилегии за това действие!"}), 403

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404

    db.session.delete(user)
    db.session.commit()
    session.clear()
    return "", 204


@app.route("/statistics", methods=["GET"])
def statistics():
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    return render_template("statistics.html", user=get_user())


def get_week_range(offset=0):
    week=get_current_week(offset)
    week_range={
        "monday": week.get("monday"),
        "sunday": week.get("sunday")}
    return week_range
    

def get_total_finished_tasks_count(user_id):
    total_finished_tasks=db.session.execute(db.select(Task).filter_by(user_id=user_id, is_finished=True)).scalars().all()
    count=len(total_finished_tasks)
    return count


def get_win_streak(user_id):
    win_streak=0
    yesterday=date.today()-timedelta(days=1)
    first_task = db.session.execute(db.select(Task).filter_by(user_id=user_id).order_by(Task.day_for.asc())).scalars().first()
    while True:
        tasks=db.session.execute(db.select(Task).filter_by(user_id=user_id, day_for=yesterday)).scalars().all()
        finished_tasks=[task for task in tasks if(task.is_finished)]
        if(not first_task or yesterday<first_task.day_for):
            break
        if(tasks):
            if(len(tasks)==len(finished_tasks)):
                win_streak+=1
            else:
                break
        yesterday-=timedelta(days=1)
    return win_streak


@app.route("/statistics/data", methods=["GET"])
def statistics_data():
    if("user_id" not in session):
        return jsonify({"error": "Не сте удостоверен в системата!"}), 401

    user=get_user()
    if(not user):
        return jsonify({"error": "Потребителят не е намерен!"}), 404
    
    offset=request.args.get("offset", type=int, default=0)
    week_range=get_week_range(offset)
    week_range_string=f"{(week_range.get('monday')).day:02d}.{(week_range.get('monday')).month:02d} - {(week_range.get('sunday')).day:02d}.{(week_range.get('sunday')).month:02d}"

    total_finished_tasks_count=get_total_finished_tasks_count(user.id)
    win_streak=get_win_streak(user.id)

    weekly_tasks=db.session.execute(db.select(Task).filter(Task.user_id==user.id, Task.day_for>=week_range.get("monday"), Task.day_for<=week_range.get("sunday"))).scalars().all()
    weekly_finished_tasks=len([task for task in weekly_tasks if(task.is_finished)])
    balance_weekly_finished_tasks=f"{weekly_finished_tasks} / {len(weekly_tasks)}"
    if(len(weekly_tasks)==0):
        percent_balance_weekly_finished_tasks_int=0
        percent_balance_weekly_finished_tasks="0%"
    else:
        percent_balance_weekly_finished_tasks_int=(100/len(weekly_tasks))*weekly_finished_tasks
        percent_balance_weekly_finished_tasks=f"{((100/len(weekly_tasks))*weekly_finished_tasks):.2f}%"

    last_week_range=get_week_range(offset-1)
    last_week_tasks=db.session.execute(db.select(Task).filter(Task.user_id==user.id, Task.day_for>=last_week_range.get("monday"), Task.day_for<=last_week_range.get("sunday"))).scalars().all()
    last_week_finished_tasks=len([task for task in last_week_tasks if(task.is_finished)])
    if(len(last_week_tasks)==0):
        last_week_percent_balance_finished_tasks_int=0
    else:
        last_week_percent_balance_finished_tasks_int=(100/len(last_week_tasks))*last_week_finished_tasks

    percent_balance_weekly_finished_tasks_compared_to_last_week_int = percent_balance_weekly_finished_tasks_int - last_week_percent_balance_finished_tasks_int
    if(percent_balance_weekly_finished_tasks_compared_to_last_week_int>0):
        percent_balance_weekly_finished_tasks_compared_to_last_week = f"С {percent_balance_weekly_finished_tasks_compared_to_last_week_int:.2f}% по-добре от миналата седмица"
    elif(percent_balance_weekly_finished_tasks_compared_to_last_week_int<0):
        percent_balance_weekly_finished_tasks_compared_to_last_week = f"С {-percent_balance_weekly_finished_tasks_compared_to_last_week_int:.2f}% по-зле от миналата седмица"
    else:
        percent_balance_weekly_finished_tasks_compared_to_last_week = f"Същото като миналата седмица"
    
    days_finished_from_total_tasks=[]
    for i in range(7):
        current_date=week_range.get("monday")+timedelta(days=i)
        day_total_tasks = [task for task in weekly_tasks if(task.day_for==current_date)]
        day_finished_tasks=[task for task in day_total_tasks if(task.is_finished)]
        days_finished_from_total_tasks.append({"finished": len(day_finished_tasks), "total": len(day_total_tasks)})
    
    dictionary={
        "win_streak": win_streak,
        "total_finished_tasks_count": total_finished_tasks_count,
        "week_range": week_range_string,
        "balance_weekly_finished_tasks": balance_weekly_finished_tasks,
        "percent_balance_weekly_finished_tasks": percent_balance_weekly_finished_tasks,
        "percent_balance_weekly_finished_tasks_compared_to_last_week": percent_balance_weekly_finished_tasks_compared_to_last_week,
        "days_finished_from_total_tasks": days_finished_from_total_tasks}
    
    return jsonify(dictionary), 200


app = app
if(__name__ == "__main__"):
    app.run(debug=True)