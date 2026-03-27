from flask import Flask, render_template, redirect, make_response, jsonify
from flask_login import LoginManager, login_user

from data import db_session
from data.jobs import Jobs
import secrets

from data.jobs_api import blueprint
from data.users import User
from forms.login_form import LoginForm
from forms.register_form import RegisterForm

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
app.register_blueprint(blueprint)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        astronaut = db_sess.query(User).filter(User.id == form.astronaut_id.data).first()
        captain = db_sess.query(User).filter(User.id == form.captain_id.data).first()
        if astronaut and astronaut.check_password(form.astronaut_password.data) \
            and captain and captain.check_password(form.captain_password.data):
            login_user(astronaut)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data,
            age=form.age.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/list_prof/<list>', methods=["GET"])
def list_prof(list: str):
    if not list  in ['ol', 'ul']:
        return jsonify({"error": "invalid list format"})
    db_sess = db_session.create_session()
    users = db_sess.query(User)
    return render_template("list_prof.html", list=list, users=users)


@app.route('/training/<prof>', methods=["GET"])
def training(prof: str):
    title = "Инженерные тренажеры" if "инженер" in prof or "строитель" in prof else "Научные симуляторы"
    return render_template("training.html", title=title)


@app.route('/distribution', methods=["GET"])
def distribution():
    db_sess = db_session.create_session()
    users = db_sess.query(User)
    return render_template("distribution.html", users=users)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs)
    return render_template("index.html", jobs=jobs)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(host="127.0.0.1", port=8080, debug=True)