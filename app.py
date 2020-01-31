from flask import Flask
from flask import render_template, url_for, request, redirect, session, flash
#from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from crypt import pwd_context
import json

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
# TODO: changing the exception handling

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
        session.pop('email', None)
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
    try:
        if session['email'] != None:
            print(session.get('email'))
            print(session.get('role'))
            return render_template('addentry.html', data=session.get('role', None))
    except:
        return "To fill in later. Redirect to login."

@app.route('/submitted', methods=['POST'])
def submitted():
    if request.method=='POST':
        firstName=request.form['firstName']
        lastName=request.form['lastName']
        targetBehavior=request.form['targetBehavior']
        homeSchoolGoal=request.form['homeSchoolGoal']
        actionPlans=request.form.getlist('actionPlan')
        date=request.form['date']
        goalRange=None
        if session['role'] == 'Teacher':
            goalRange = request.form['goalRangeTeacher']
        else:
            goalRange = request.form['goalRangeParent']
        if firstName=='' or lastName=='' or targetBehavior=='' or homeSchoolGoal=='' or actionPlans==None:
            #return render_template('addentry.html', message="*Please fill out required fields*")
            flash("Must fill out all fields")
            return redirect(url_for('addentry'))
        else:
            print(date)
            current_user = User.query.filter_by(email=session['email']).all()[0]
            mapping = {"Situation significantly worse":-2, "Situation somewhat worse":-1, "No progress":0, "Situation somewhat better": 1, "Situation significantly better":2}
            new_entry = Entry(user_id=current_user.userid, target_behavior=targetBehavior, home_school_goal=homeSchoolGoal, goal_rating=mapping[goalRange], date=date)
            # TODO: more elegant way to do this. FOR TESTING PURPOSES ONLY
            new_entry.action_plan_one = actionPlans[0]
            if(len(actionPlans) > 1):
                new_entry.action_plan_two = actionPlans[1]
            if(len(actionPlans) > 2):
                new_entry.action_plan_three = actionPlans[2]
            if(len(actionPlans) > 3):
                new_entry.action_plan_four = actionPlans[3]
            if(len(actionPlans) > 4):
                new_entry.action_plan_five = actionPlans[4]
            current_user.entries.append(new_entry)
            db.session.add(new_entry)
            db.session.add(current_user)
            db.session.commit()
            return render_template('submitted.html')

@app.route('/readdata')
def readdata():
    try:
        if session['email'] != None:
            current_user = User.query.filter_by(email=session['email']).all()[0]
            all_entries = current_user.entries
            table_data = json.dumps([entry.serialize() for entry in all_entries])
            return render_template('readdata.html', data=table_data)
    except KeyError:
        return "To fill in later. Redirect to login."

@app.route('/logout')
def logout():
    try:
        if session['email'] != None:
            session.pop('email', None)
            session.pop('role', None)
            return redirect(url_for('home'))
    except KeyError:
        return redirect(url_for('home'))