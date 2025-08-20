from flask import Flask,render_template,request,redirect,url_for,flash
from reqs import Req
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Integer,String

year=datetime.now().strftime("%Y")
#Initialize DB
class Base(DeclarativeBase):
    pass
db=SQLAlchemy(model_class=Base)
app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///user_data.db"
db.init_app(app)
app.secret_key = 'IamNoone00#'

#Creating Table
class DataBase(db.Model):
    __tablename__="User Data"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    name:Mapped[String]=mapped_column(String(250))
    email:Mapped[String]=mapped_column(String(250))
    def __repr__(self):
        return f"<DataBase{self.name}>"

with app.app_context():
    db.create_all()



@app.route("/",methods=['GET','POST'])
def index():
    if request.method=='POST':
        name=str(request.form['name'])
        email=str(request.form['email'])
        message=str(request.form['msg'])
        
        with app.app_context():
            new_data=DataBase(name=name,email=email)
            db.session.add(new_data)
            db.session.commit()
        flash('Thank you for Contacting', 'success')
        print(f"{name}\n{email}\n{message}")
        return redirect(url_for('index'))
    req_quote=Req()
    return render_template('index.html',quote=req_quote.quote,author=req_quote.author,current_year=year)

@app.route("/projects/<int:project_id>")
def projects(project_id):
    
    return render_template('projects.html',id=project_id)

if __name__=="__main__":
    app.run(debug=True)
