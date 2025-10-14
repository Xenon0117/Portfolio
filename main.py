#Import Modules

from flask import Flask,render_template,request,redirect,url_for,flash,abort,send_from_directory
from reqs import Req
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Integer,String
from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
load_dotenv()

#Getting Current Year
year=datetime.now().strftime("%Y")

#Initialize 
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['DB_URI']
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,        # ← Critical: validates connection before use
    "pool_recycle": 300,          # Recycle connections every 5 minutes
    "connect_args": {
        "sslmode": "require"      # Explicitly enforce SSL (redundant but safe)
    }
}
DOWNLOAD_FOLDER = 'Downloadables'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config["SECRET_KEY"] = os.environ['FLASK_KEY']

#Initialize DB
class Base(DeclarativeBase):
    pass
db=SQLAlchemy(model_class=Base)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

#Creating Table
class DataBase(db.Model):
    __tablename__="User Data"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[str]=mapped_column(String(250))
    email:Mapped[str]=mapped_column(String(250))
    message:Mapped[str]=mapped_column(String(1000))
    def __repr__(self):
        return f"<DataBase{self.name}>"

#Create DataBase
with app.app_context():
    db.create_all()

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User,int(user_id))

#Create admin-only decorator
def admin_only(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        #Otherwise continue with the route function
        return f(*args, **kwargs)        
    return decorated_function

@app.route("/",methods=['GET','POST'])
def index():
    if request.method=='POST':
        _email=os.environ["EMAIL"]
        password=os.environ["PASS"]
        name=str(request.form['name'])
        email=str(request.form['email'])
        message=str(request.form['msg'])
        
        with app.app_context():
            new_data=DataBase(name=name,email=email,message=message)
            db.session.add(new_data)
            db.session.commit()
        new_letter=f"Name: {name}\nEmail Id: {email}\nMessage:{message}"
        
        # email_message = MIMEText(new_letter)
        # email_message['Subject'] = f"Feedback from {name}"
        # email_message['From'] = _email
        # email_message['To'] = "devilsayan16@gmail.com"

        # try:
        #     with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        #         connection.starttls()
        #         connection.login(user=_email, password=password)
        #         connection.sendmail(from_addr=_email, to_addrs=[os.environ['SEND_TO_MAIL_ID']],
        #                             msg=email_message.as_string())
        #     flash('Thank you for Contacting', 'success')
        #     print(f"{name}\n{email}\n{message}")
        #     return redirect(url_for('index'))
        # except smtplib.SMTPAuthenticationError:
        #     print("Authentication error. Check your email and password (or App Password).")
        #     flash("Something Went Wrong","danger")
        # except smtplib.SMTPDataError as e:
        #     print(f"SMTP Data Error: {e}")
        #     flash("Something Went Wrong","danger")
        # except Exception as e:
        #     print(f"An error occurred: {e}")
        #     flash("Something Went Wrong","danger")  

    req_quote=Req()
    return render_template('index.html',quote=req_quote.quote,author=req_quote.author,current_year=year)

@app.route("/projects/<int:project_id>")
def projects(project_id):
    return render_template('projects.html',id=project_id)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email_form = request.form.get('email')
        name_form = request.form.get('name')
        pw = request.form.get('password')  
        # Validate that all fields are provided
        if not all([email_form, name_form, pw]):
            flash("Please fill in all fields", "danger")
            return redirect(url_for('register'))
        # Check if user already exists
        duplicate_entry = db.session.execute(db.select(User).where(User.email == email_form)).scalar()
        if duplicate_entry:
            flash("User already present. Please Login instead", "warning")
            return redirect(url_for('login'))

        # Create new user
        hashed_and_salted_password = generate_password_hash(password=pw, method="pbkdf2:sha256", salt_length=8)
        new_user = User(
            email=email_form,
            password=hashed_and_salted_password,
            name=name_form
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("Registered and Logged In", "success")
        return redirect(url_for("index"))
    
    return render_template("register.html", logged_in=current_user.is_authenticated)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email_login = request.form.get('email')
        password_login = request.form.get('password')
        
        if not all([email_login, password_login]):
            flash("Please fill in all fields", "danger")
            return redirect(url_for('login'))
        
        user_data = db.session.execute(db.select(User).where(User.email == email_login)).scalar()
        if user_data:
            if check_password_hash(user_data.password, password_login):
                login_user(user_data)
                flash("You're Successfully Logged In", "success")
                return redirect(url_for("view"))
            else:
                flash("Invalid Email or Password", "danger")
                return redirect(url_for('login'))
        else:
            flash("Only Admin Accessible. Need Admin Credentials", "warning")
            return redirect(url_for('login'))
    
    return render_template("login.html", logged_in=current_user.is_authenticated)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Successfully Logged Out","info")
    return redirect(url_for('index'))

@app.route('/view')
@login_required
@admin_only
def view():
    with app.app_context():
        # Get all records from DataBase table
        all_data = db.session.execute(db.select(DataBase).order_by(DataBase.id)).scalars().all()
    return render_template('view.html', data=all_data, current_year=year)

@app.route('/download/<filename>')
def download_file(filename):
    # Construct the full path to the file
    return send_from_directory(
        app.config['DOWNLOAD_FOLDER'],
        filename,
        as_attachment=True  # This makes the browser download the file
    )

if __name__=="__main__":
    app.run(debug=False)
