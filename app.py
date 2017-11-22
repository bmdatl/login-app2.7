import os
import bcrypt
from flask import *
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta


app = Flask(__name__)
app.secret_key = os.urandom(10)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


# serializes SQLAlchemy result to JSON
class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data)  # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


#
# helper functions
#


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if session['logged_in']:
            return test(*args, **kwargs)
        else:
            return redirect(url_for('home'))
    return wrap


def get_hashed_pass(raw_pass):
    return bcrypt.hashpw(raw_pass.encode('utf8'), bcrypt.gensalt())


def verify_pass(raw_pass, hashed_pass):
    return bcrypt.checkpw(raw_pass.encode('utf8'), hashed_pass.encode('utf8'))


#
# routed functions
#

@app.route('/')
def home(error=None):
    if not session.get('logged_in'):
        session['logged_in'] = False
    return render_template('home.html', error=error)


@app.route('/register')
def register(error=None):
    return render_template('register.html', error=error)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user:
        password_hashed = user.password
        if verify_pass(password, password_hashed):
            session['logged_in'] = True
            session['user'] = json.dumps(user, cls=AlchemyEncoder)
            return redirect(url_for('success'))
        else:
            error = "Incorrect password."
            return home(error)
    else:
        error = "User cannot be found. Please register for a new account."
        return home(error)


@app.route('/create', methods=['POST'])
def create_account():
    # check if user exists
    user = User.query.filter_by(username=request.form['username']).first()

    # if username is already taken, refresh register page with error
    if user:
        error = "Username already exists. Please enter a new username."
        return register(error)
    else:
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        # hash & salt password
        password_hashed = get_hashed_pass(password)
        newuser = User(name=name, username=username, password=password_hashed)

        # add user to database, redirect to success page with new user details
        db.session.add(newuser)
        db.session.commit()
        user = User.query.filter_by(username=username).first()
        session['logged_in'] = True

        # send user object to session for property retrieval throughout the app
        session['user'] = json.dumps(user, cls=AlchemyEncoder)
        return redirect(url_for('success'))


@app.route('/success')
@login_required
def success():
    user = json.loads(session['user'])
    return render_template('success.html', user=user)


@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug=True, port=5000)

