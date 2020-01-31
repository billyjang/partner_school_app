from flask import Flask
from flask import render_template, url_for, request, redirect, session, flash
#from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from crypt import pwd_context

app = Flask(__name__)
#sess = Session()

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kjmuultbvkoaqd:56ac542cebad0a7473deb0c24d9a87daab81dd0511b4925f9e552fe834d1f1fd@ec2-34-193-42-173.compute-1.amazonaws.com:5432/d76s1h363rpp0'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
#sess.init_app(app)

db = SQLAlchemy(app)
from models import *

loggedIn=False

#login and register
# TODO: make the control flow a bit cleaner
# TODO: make sure the get and post is clear so authentication actually means something
# TODO: screenreader accessibility
@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        session.pop('email', None)
        user_email = request.form['email']
        matching_emails = User.query.filter_by(email=user_email)
        if matching_emails.count() != 1:
            return redirect(url_for('home'))
        else:
            session['email'] = user_email
            password = request.form['password']
            verify_password = matching_emails.with_entities(User.password).all()[0][0]
            if pwd_context.verify(password, verify_password):
                print(matching_emails.with_entities(User.userRole).all()[0][0])
                session['role'] = matching_emails.with_entities(User.userRole).all()[0][0]
                return redirect(url_for('addentry'))
            else:
                return redirect(url_for('home'))            
    else:
        return render_template('login.html')

@app.route('/newaccount', methods=['POST', 'GET'])
def newaccount():
    return render_template('newaccount.html')

@app.route('/newaccountsuccess', methods=['POST', 'GET'])
def newaccountsuccess():
    if request.method=='POST':
        empty = False
        for k,v in request.form.items():
            if request.form[k]=="":
                print(request.form[k])
                empty=True
        if empty:
            flash('Must fill out all required fields')
            return redirect(url_for('newaccount'))
        if request.form['password'] != request.form['passwordAgain']:
            flash('Passwords must match')
            return redirect(url_for('newaccount'))
        email=request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        cfirstName = request.form['childFirstName']
        clastName = request.form['childLastName']
        userRole = request.form['userRole']
        email = request.form['email']
        # TODO: check if passwords are the same in javascript or jquery
        password = request.form['password']
        hashed = pwd_context.hash(password)
        try:
            new_user = User(firstName, lastName, cfirstName, clastName, userRole, email, hashed)
            db.session.add(new_user)
            db.session.commit()
            return render_template('newaccountsuccess.html')
        except Exception as e:
            print(str(e))
            return redirect(url_for('newaccount'))
    else:
        # TODO: CHANGE THIS
        return render_template('newaccountsuccess.html')
    
# adding entry and viewing data
@app.route('/addentry') # add required message here?
def addentry():
    if session['email'] != None:
        print(session.get('email'))
        print(session.get('role'))
        return render_template('addentry.html', data=session.get('role', None))
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
        goalRange=None
        if session['role'] == 'Teacher':
            goalRange = request.form.getlist('goalRangeTeacher')
        else:
            goalRange = request.form.getlist('goalRangeParent')
        if firstName=='' or lastName=='' or targetBehavior=='' or homeSchoolGoal=='' or actionPlans==None:
            #return render_template('addentry.html', message="*Please fill out required fields*")
            flash("Must fill out all fields")
            return redirect(url_for('addentry'))
        else:
            print(actionPlans)
            print(goalRange)
            entry = Entry()
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