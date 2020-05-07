from flask import Flask
from flask import render_template, url_for, request, redirect, session, flash, jsonify
#from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from crypt import pwd_context
import json
import os
from twilio.rest import Client

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

app = Flask(__name__)
#sess = Session()

app.debug = True
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://kjmuultbvkoaqd:56ac542cebad0a7473deb0c24d9a87daab81dd0511b4925f9e552fe834d1f1fd@ec2-34-193-42-173.compute-1.amazonaws.com:5432/d76s1h363rpp0'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ryehoqoimamdpg:7420762e6c90e7ffadefb487e90e9844769d64b7b03035d8c86ec004954dda05@ec2-34-199-149-157.compute-1.amazonaws.com:5432/d11d2f8nejvhgg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
#sess.init_app(app)
# TODO: fix these to move onto heroku
SENDGRID_API_KEY = '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'

db = SQLAlchemy(app)
from models import *

loggedIn=False

#login and register
# TODO: make the control flow a bit cleaner
# TODO: make sure the get and post is clear so authentication actually means something
# TODO: screenreader accessibility
# TODO: changing the exception handling
# TODO: I don't think messages are happening
# TODO: Fix xss vulnerabilities
# TODO: PROPER COMPLAINING
# TODO: cascade on database
# TODO: access control

@app.route('/', methods=['GET','POST'])
def home():
    if request.method=='POST':
        session.pop('userID', None)
        userID = request.form['userID']
        matching_ids = User.query.filter_by(id=userID)
        if matching_ids.count() != 1:
            return redirect(url_for('home'))
        else:
            session['userID'] = userID
            password = request.form['password']
            verify_password = matching_ids.with_entities(User.password).all()[0][0]
            if pwd_context.verify(password, verify_password):
                print(matching_ids.with_entities(User.userRole).all()[0][0])
                session['role'] = matching_ids.with_entities(User.userRole).all()[0][0]
                return redirect(url_for('landing'))
            else:
                return redirect(url_for('home'))            
    else:
        return render_template('login.html')

@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgotpassword.html')

@app.route('/forgotnotificationsent', methods=["POST"])
def forgotnotificationsent():
    userId = request.form['userId']
    admin_email = 'gfa2111@cumc.columbia.edu'
    from_email = 'wjang20@amherst.edu'
    subject = 'Forgotten Password'
    message_body = userId + ' has forgotten their password.'
    send_email(admin_email, from_email, subject, message_body)
    return render_template('forgotpasswordsuccess.html')

@app.route('/forgotpasswordsuccess')
def forgotpasswordsuccess():
    return render_template('forgotpasswordsuccess.html')

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
        userID = request.form['userId']
        userRole = request.form['userRole']
        phoneNumber = request.form['phoneNumber']
        #targetBehavior=request.form['targetBehavior']
        #homeSchoolGoal=request.form['homeSchoolGoal']
        targetBehavior="Not set"
        homeSchoolGoal="Not set"
        # TODO: check if passwords are the same in javascript or jquery
        password = request.form['password']
        hashed = pwd_context.hash(password)
        try:
            #new_user = User(userID,userRole, hashed, targetBehavior, homeSchoolGoal,email)
            new_user = User(userID, userRole, hashed, targetBehavior, homeSchoolGoal, email, phoneNumber)
            db.session.add(new_user)
            db.session.commit()
            return render_template('newaccountsuccess.html')
        except Exception as e:
            print(str(e))
            return redirect(url_for('newaccount'))
    else:
        # TODO: CHANGE THIS
        return render_template('newaccountsuccess.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/contactussent', methods=["POST"])
def contactussent():
    body = request.form['message']
    current_user = User.query.filter_by(id=session['userID']).all()[0]
    from_email = current_user.email[0]
    send_email('gfa2111@cumc.columbia.edu', from_email, 'Contact request', body)
    return "success"
    
@app.route('/notecalendar')
def notecalendar():
    current_user = User.query.filter_by(id=session['userID']).all()[0]
    entry_data = {'date' : [e.date for e in current_user.entries]}
    return render_template('notecalendar.html', data=entry_data)

# TODO: There is an ordering that must be followed--does something break if Gazi doesn't enter in the values in time first?

# adding entry and viewing data
@app.route('/addentry') # add required message here?
def addentry():
    try:
        if session['userID'] != None:
            print(session.get('userID'))
            print(session.get('role'))
            current_user = User.query.filter_by(id=session['userID']).all()[0]
            #return render_template('addentry.html', data=session.get('role', None)
            user_data = {'userID' : current_user.id, 'role' : current_user.userRole, 'targetBehavior' : current_user.targetBehavior,
                        'homeSchoolGoal' : current_user.homeSchoolGoal, 'actionPlans' : [ap.stepName for ap in current_user.actionplans]}
            return render_template('addentry.html', data=user_data)
    except:
        return "To fill in later. Redirect to login."

@app.route('/submitted', methods=['POST'])
def submitted():
    if request.method=='POST':
        userID=request.form['userID']
        date=request.form['date']
        targetBehavior=request.form['targetBehavior']
        homeSchoolGoal=request.form['homeSchoolGoal']
        actionPlans=request.form.getlist('actionPlan')
        print('hey')
        print(actionPlans)
        # TEMP FIX
        goalRange=None
        if session['role'] == 'Teacher':
            goalRange = request.form['goalRangeTeacher']
        else:
            goalRange = request.form['goalRangeParent']
        print(userID)
        print(goalRange)
        print(targetBehavior)
        print(homeSchoolGoal)
        #print(actionPlans)
        if userID=='' or goalRange==None or targetBehavior=='' or homeSchoolGoal=='':
            #return render_template('addentry.html', message="*Please fill out required fields*")
            flash("Must fill out all fields")
            return redirect(url_for('addentry'))
        else:
            print(date)
            current_user = User.query.filter_by(id=session['userID']).all()[0]
            mapping = {"Situation significantly worse":-2, "Situation somewhat worse":-1, "No progress":0, "Situation somewhat better": 1, "Situation significantly better":2}
            new_entry = Entry(userId=current_user.id, goalRating=mapping[goalRange], date=date, targetBehavior=current_user.targetBehavior, homeSchoolGoal=current_user.targetBehavior)
            # TODO: more elegant way to do this. FOR TESTING PURPOSES ONLY
            
            new_entry.actionPlanOne = actionPlans[0]
            if(len(actionPlans) > 1):
                new_entry.actionPlanTwo = actionPlans[1]
            if(len(actionPlans) > 2):
                new_entry.actionPlanThree = actionPlans[2]
            if(len(actionPlans) > 3):
                new_entry.actionPlanFour = actionPlans[3]
            if(len(actionPlans) > 4):
                new_entry.actionPlanFive = actionPlans[4]
            
            current_user.entries.append(new_entry)
            db.session.add(new_entry)
            db.session.add(current_user)
            db.session.commit()
            return render_template('submitted.html')

@app.route('/readdata')
def readdata():
    try:
        if session['userID'] != None:
            current_user = User.query.filter_by(id=session['userID']).all()[0]
            all_entries = current_user.entries
            table_data = json.dumps([entry.serialize() for entry in all_entries])
            # TODO: IF targetbehavior fixed, have to change this
            targetBehavior = {'targetBehavior' : current_user.targetBehavior}
            return render_template('readdata.html', data=table_data, behavior=targetBehavior)
    except KeyError:
        return "To fill in later. Redirect to login."

@app.route('/logout')
def logout():
    try:
        if session['userID'] != None:
            session.pop('userID', None)
            session.pop('role', None)
            return redirect(url_for('home'))
    except KeyError:
        return redirect(url_for('home'))

@app.route('/adminlanding')
def adminlanding():
    return render_template('adminlanding.html')

# TODO: finish these after config the db again
# TODO: no data yet.

@app.route('/adminnotifications')
def adminnotifications():
    all_users = User.query.all()
    all_data = []
    for user in all_users:
        user_entry = {'userId' : user.id, 'targetBehavior' : user.targetBehavior, 'homeSchoolGoal': user.homeSchoolGoal, 'actionPlans' : [ap.stepName for ap in user.actionplans]}
        all_data.append(user_entry)
    return render_template('adminnotifications.html', data=all_data)

@app.route('/notificationsent', methods=["POST"])
def notificationsent():
    message_type = request.form['message-type']
    body = request.form['message']
    # TODO: Test emails more, and send one at a time.
    if message_type == "Email":
        all_emails = []
        if request.form['audience'] == 'All':
            all_emails = User.query.with_entities(User.email).all()
        elif request.form['audience'] == 'Parents':
            all_emails = User.query.filter_by(userRole='Parent').with_entities(User.email).all()
        elif request.form['audience'] == 'Teachers':
            all_emails = User.query.filter_by(userRole='Teacher').with_entities(User.email).all()

        to_send_emails = [email[0] for email in all_emails]
        #send_email(to_send_emails, 'wjang20@amherst.edu', 'Reminder', body)
        for to_email in to_send_emails:
            send_email(to_email, 'wjang20@amherst.edu', 'Reminder', body)
    elif message_type == "SMS":
        #send_sms('+17153796650', body)
        # MAKE THIS CLEANER
        # test and do config vigs
        all_sms = []
        if request.form['audience'] == 'All':
            all_sms = User.query.with_entities(User.phoneNumber).all()
        elif request.form['audience'] == 'Parents':
            all_sms = User.query.filter_by(userRole='Parent').with_entities(User.phoneNumber).all()
        elif request.form['audience'] == 'Teachers':
            all_sms = User.query.filter_by(userRole='Teacher').with_entities(User.phoneNumber).all()
        
        to_send_sms = [sms[0] for sms in all_sms]
        for to_sms in to_send_sms:
            send_sms(to_sms, body)
    
    return render_template('notificationsentsuccess.html')
'''
def send_email(to_emails, from_email, subject, message_body):
    to_list = Personalization()
    for email in to_emails:
        to_list.add_to(Email(email))
    message = Mail(
        from_email = from_email, 
        subject = subject, 
        html_content = '<strong>' + message_body + '</strong>'
        )
    message.add_personalization(to_list)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
'''
def send_email(to_email, from_email, subject, message_body):
    message = Mail(
        from_email = from_email,
        to_emails = to_email,
        subject = subject,
        html_content = '<strong>' + message_body + '</strong>'
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

def send_sms(to_phone, body):
    account_sid = 'AC0a28d8b2df04587f7e4ae71d4830c249'
    auth_token = '734fbc7c2ebdfe63b5cd7de0deacae52'
    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=body,
                     from_='+12018013260',
                     to=to_phone
                 )

@app.route('/notificationsentsuccess')
def notificationsentsuccess():
    return render_template('notificationsentsuccess.html')

@app.route('/adminentry')
def adminentry():
    all_users = User.query.all()
    all_data = []
    for user in all_users:
        user_entry = {'userID' : user.id, 'targetBehavior' : user.targetBehavior, 'homeSchoolGoal': user.homeSchoolGoal, 'actionPlans' : [ap.stepName for ap in user.actionplans]}
        all_data.append(user_entry)
    return render_template('adminentry.html', data=all_data)

@app.route('/adminpost', methods=["POST"])
def adminpost():
    req = request.form.to_dict()
    req_keys = list(req.keys())
    #req_action_plan = request.form.to_dict()
    #req_action_plan_keys = list(req_action_plan.keys())
    print(req)
    userId = req_keys[0].split("-")[1]
    current_user = User.query.filter_by(id=userId).all()[0]
    # todo: add targetbehavior and homeschoolgoal
    new_aps = []
    for i in range(5):
        if req[req_keys[i]] == "":
            continue
        new_ap = ActionPlan(order=i, stepName=req[req_keys[i]])
        new_aps.append(new_ap)
        db.session.add(new_ap)

    current_user.targetBehavior=req[req_keys[5]]
    current_user.homeSchoolGoal=req[req_keys[6]]
    
    current_user.actionplans=new_aps
    db.session.add(current_user)
    db.session.commit()
    #current_action_plans = [action_plan[key] for key in action_plan_keys]
    return "Information for User: " + current_user.id + " was saved successfully!"