from flask import Flask
from flask import render_template, url_for, request, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from crypt import pwd_context

app = Flask(__name__)
session = Session()

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kjmuultbvkoaqd:56ac542cebad0a7473deb0c24d9a87daab81dd0511b4925f9e552fe834d1f1fd@ec2-34-193-42-173.compute-1.amazonaws.com:5432/d76s1h363rpp0'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
session.init_app(app)
uincrement=1

db = SQLAlchemy(app)
from models import *

loggedIn=False

#login and register
@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        session.pop('user', None)

    else:
        return render_template('login.html')

@app.route('/newaccount', methods=['POST', 'GET'])
def newaccount():
    return render_template('newaccount.html')

@app.route('/newaccountsuccess', methods=['POST'])
def newaccountsuccess():
    global uincrement
    if request.method=='POST':
        empty = False
        for k,v in request.form.items():
            if request.form[k]=="":
                print(request.form[k])
                empty=True
        if empty:
            print('hit')
            return redirect(url_for('newaccount'))
        email=request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        cfirstName = request.form['childFirstName']
        clastName = request.form['childLastName']
        userRole = request.form['userRole']
        # TODO: check if passwords are the same in javascript or jquery
        password = request.form['password']
        hashed = pwd_context.hash(password)
        try:
            new_user = User(uincrement, firstName, lastName, cfirstName, clastName, userRole, hashed)
            db.session.add(new_user)
            db.session.commit()
            uincrement += 1
            return render_template('newaccountsuccess.html')
        except Exception as e:
            print(str(e))
            return redirect(url_for('newaccount'))

@app.route('/addentry') # add required message here?
def addentry():
    if loggedIn:
        return render_template('addentry.html')
    else:
        return "not logged in"

@app.route('/submitted', methods=['POST'])
def submitted():
    if request.method=='POST':
        firstName=request.form['firstName']
        lastName=request.form['lastName']
        targetBehavior=request.form['targetBehavior']
        homeSchoolGoal=request.form['homeSchoolGoal']
        actionPlans=request.form.getlist('actionPlan')
        goalRangeTeacher=request.form['goalRangeTeacher']
        if firstName=='' or lastName=='' or targetBehavior=='' or homeSchoolGoal=='' or actionPlans==None:
            #return render_template('addentry.html', message="*Please fill out required fields*")
            return redirect(url_for('addentry'))
        else:
            print(actionPlans)
            entry = Entry(1, 2, 3, actionPlans)
            return render_template('submitted.html')

@app.route('/hello')
def hello():
    return "hello, world"

@app.route('/readdata')
def readdata():
    if loggedIn:
        return render_template('readdata.html')
    else:
        return "not logged in"