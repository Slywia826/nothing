import os
from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__) #create instance of flask
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SECRET_KEY"] = "687e687ttdf7676syugd7wr76eqwe3schldatabase"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False

db = SQLAlchemy (app)

class User(UserMixin, db.Model):
   id = db.Column (db.Integer,primary_key = True)
   name = db.Column (db.String(100),nullable=False)
   email = db.Column (db.String(100), unique=True, nullable = False)
   password = db.Column (db.Integer)
   def __repr__(self):
      return f'<Classroom {self.name}'

class Classroom(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100), unique = True, nullable = False)
  yearlevel = db.Column(db.String(100), nullable = False)
  capacity = db.Column(db.String(100), nullable = False)
  created_at = db.Column(db.DateTime(timezone=True), server_default = func.now())
  students = db.relationship('Student', backref = 'classroom')
  def __repr__(self):
    return f'<Classroom {self.name}>'

class Student(db.Model):

   id = db.Column(db.Integer, primary_key = True)
   firstname = db.Column(db.String(100), nullable = False)
   lastname = db.Column(db.String(100), nullable = False)
   email = db.Column(db.String(100), unique = True, nullable = False)
   age = db.Column(db.Integer)
   created_at = db.Column(db.DateTime(timezone=True), server_default = func.now())
   bio = db.Column(db.Text)
   classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))

   def __repr__(self):
    return f'<Student {self.name}>'
   
with app.app_context():
     db.create_all()


#routing
@app.route("/")
def index():
  return render_template("index.html")

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

@app.route("/signup")
@login_required
def signup():
   return render_template('signup.html')

@app.route("/signup", methods=['POST'])
@login_required
def signup_post():
   email = request.form['email']
   name = request.form ['name']
   password = request.form ['password']
   user = User.query.filter_by(email=email).first()

   if user:
      flash ('Email address already exists!')
      return redirect(url_for('signup'))
   
   new_user = User(email=email, name=name,password=generate_password_hash(password,method='pbkdf2:sha256'))
   db.session.add(new_user)
   db.session.commit()
   return redirect (url_for('success'))

@app.route ("/login")
def login():
   return render_template("login.html")

@app.route ("/login", methods=['POST'])
def login_post():
   email = request.form['email']
   password = request.form ['password']
   remember = request.form.get('remember')
   user = User.query.filter_by(email=email).first()

   if not user or not check_password_hash(user.password, password):
      flash('Please check your login details and try again!')
      return redirect(url_for('login'))
   
   login_user(user,remember=remember)
   return redirect(url_for('profile'))

@app.route("/profile")
@login_required
def profile():
   return render_template("profile.html", name=current_user.name, email=current_user.email)

@app.route ("/logout")
@login_required 
def logout():
   logout_user()
   return redirect(url_for("index"))

@app.route("/create", methods = ("GET","POST"))
@login_required
def create():
   if request.method == "POST":
      name = request.form["name"]
      yearlevel = request.form["yearlevel"]
      capacity = request.form ["capacity"]
      classroom = Classroom(name=name, yearlevel=yearlevel, capacity=capacity)
      db.session.add(classroom)
      db.session.commit()
      return redirect(url_for("viewclassrooms"))
   return render_template("create.html")

@app.route('/viewanimals')
@login_required
def viewclassrooms():
   classrooms = Classroom.query.all()
   return render_template('animallist.html', classrooms=classrooms)

@app.route('/zookeepers')
@login_required
def zookeepers():
   students = Student.query.all()
   return render_template('zookeeperlist.html', students=students)

@app.route('/<int:classroom_id>/addzookeeper', methods= ('GET', 'POST'))
@login_required
def studentcreate(classroom_id):
   classroom = Classroom.query.get_or_404(classroom_id)
   if request.method == 'POST':
      firstname = request.form['firstname']
      lastname = request.form['lastname']
      email = request.form['email']
      age = int(request.form['age'])
      bio = request.form['bio']
      student = Student(firstname=firstname, lastname=lastname, email=email, age=age, bio=bio, classroom_id=classroom_id)
      db.session.add(student)
      db.session.commit()
      return redirect(url_for("viewclassrooms"))
  
   return render_template("zookeeperadd.html",classroom = classroom)

@app.route('/account=added')
@login_required
def success():
   return render_template('success.html')

#run the app in development app
if __name__ == "main":
    app.run(host="0.0.0.0", debug= True,port="433")
# run: python -m flask run --port 433 (mandatory to use port 433, default port doesn't work)
# port 433: info encrypted, safer for use
