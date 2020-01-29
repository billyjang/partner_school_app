from flask import Flask
from flask import render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from crypt import pwd_context

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kjmuultbvkoaqd:56ac542cebad0a7473deb0c24d9a87daab81dd0511b4925f9e552fe834d1f1fd@ec2-34-193-42-173.compute-1.amazonaws.com:5432/d76s1h363rpp0'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from models import *


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/addentry') # add required message here?
def addentry():
    return render_template('addentry.html')

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
    return render_template('readdata.html')