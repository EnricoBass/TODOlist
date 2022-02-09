from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user, LoginManager, UserMixin, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from forms import Register, LogIn, CreateList


app = Flask(__name__)
app.secret_key = "secretKey"
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    list_items = db.relationship("UserListItem", backref="users")



class UserListItem(db.Model):
    __tablename__ = "user_list_items"
    id = db.Column(db.Integer, primary_key=True)
    list_item = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template("index.html", user=current_user)


@app.route("/Sign-In", methods=["GET", "POST"])
def sign_in():
    form = Register()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256', salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("to_do_list"))
    return render_template("sign-in.html", form=form, user=current_user)


@app.route("/log-in", methods=["GET", "POST"])
def log_in():
    form = LogIn()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("to_do_list"))
    return render_template("log-in.html", form=form, user=current_user)


@app.route("/log-out")
def log_out():
    logout_user()
    return redirect(url_for("home"))


@app.route("/create-your-list", methods=["GET", "POST"])
@login_required
def to_do_list():
    user = current_user
    form = CreateList()
    if form.validate_on_submit():
        data = form.create_list.data
        new_data = data.split("\n")
        for i in new_data:
            n = i.replace("\r", "")
            new_item = UserListItem(
                list_item=n,
                user_id=user.id
            )
            db.session.add(new_item)
            db.session.commit()

        return redirect(url_for("show_list"))
    return render_template("create-to-do-list.html", form=form, user=current_user)


@app.route("/show-your-list", methods=["GET"])
@login_required
def show_list():
    user = current_user

    if request.form.get("Delete"):
        return redirect(url_for("delete"))

    if request.form.get("add"):
        return redirect(url_for("to_do_list"))

    return render_template("show-list.html", user=user)


@app.route("/show-your-list", methods=["GET", "POST"])
@login_required
def delete():
    user = current_user
    list_ = user.list_items
    for items in list_:
        db.session.delete(items)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/delete_item/<int:id>")
def delete_item(id):
    item = UserListItem.query.get(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for("show_list"))


app.run(debug=True)
