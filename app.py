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

from sqlalchemy import exc

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ryehoqoimamdpg:7420762e6c90e7ffadefb487e90e9844769d64b7b03035d8c86ec004954dda05@ec2-34-199-149-157.compute-1.amazonaws.com:5432/d11d2f8nejvhgg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = 'super secret key'
# TODO: HAVE TO CHANGE THE HEROKU STUFF TO WORK REGARDLESS. MOVING ENVIRONMENT VARIABLES
# TODO: fix these to move onto heroku
SENDGRID_API_KEY = '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'
ADMIN_EMAIL = 'gfa2111@cumc.columbia.edu'
ADMINROLE = "Admin"

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
    #logging in
    if request.method=='POST':
        logout_user()
        userID = request.form['userID']
        test_password = request.form['password']

        error = None
        try:
            user = get_user(userID)
        except IndexError:
            error = "No User found with that ID."
        else:
            if verify_password(test_password, user.password):
                login_user(user.id, user.userRole)

                if user.userRole == ADMINROLE:
                    return redirect(url_for('adminlanding'))
                else:
                    return redirect(url_for('landing'))
            else:
                error = "Incorrect Password. Click the Forgot Password button if you have forgotten."
        return render_template('login.html', error=error)
    else:
        #maybe logout_user if they go here.
        return render_template('login.html')

def get_user(userID):
    return User.query.filter_by(id=userID).all()[0]

def logout_user():
    session.pop('userID', None)
    session.pop('role', None)

def login_user(userID, role):
    session['userID'] = userID
    session['role'] = role

def verify_password(test_password, real_password):
    return pwd_context.verify(test_password, real_password)

@app.route('/forgotpassword', methods=['POST', 'GET'])
def forgotpassword():
    if request.method == 'POST':
        userId = request.form['userId']
        # TODO: Keeping it as this email because the user may have also forgotten their id. Ask Dr. Azad what she wants.
        from_email = 'wjang20@amherst.edu'
        subject = 'Forgotten Password'
        message_body = userId + ' has forgotten their password.'
        try:
            send_email(ADMIN_EMAIL, from_email, subject, message_body)
        except:
            return redirect(url_for('failure'))
        return render_template('forgotpasswordsuccess.html')
    else:
        return render_template('forgotpassword.html')

@app.route('/forgotnotificationsent')
def forgotnotificationsent():
    return render_template('forgotpasswordsuccess.html')

@app.route('/failure')
def failure():
    return "Something went wrong. Contact administrator."

@app.route('/forgotpasswordsuccess')
def forgotpasswordsuccess():
    return render_template('forgotpasswordsuccess.html')

@app.route('/newaccount', methods=['POST', 'GET'])
def newaccount():
    if request.method == 'POST':
        email = request.form['email']
        userID = request.form['userId']
        userRole = request.form['userRole']
        phoneNumber = request.form['phoneNumber']
        targetBehavior = "Not set"
        homeSchoolGoal = "Not set"

        password = request.form['password']
        hashedPassword = hash_password(password)
        try:
            create_new_user(userID, userRole, hashedPassword, targetBehavior, homeSchoolGoal, email, phoneNumber)
            return render_template('newaccountsuccess.html')
        except exc.IntegrityError as e:
            # ID already used, wrong format, too long of an input
            error = str(e)
            return render_template('newaccount.html', error=error)
    else:
        return render_template('newaccount.html')

@app.route('/newaccountsuccess')
def newaccountsuccess():
    return render_template('newaccountsuccess.html')

def hash_password(password):
    return pwd_context.hash(password)

def create_new_user(userID, userRole, hashedPassword, targetBehavior, homeSchoolGoal, email, phoneNumber):
    new_user = User(userID, userRole, hashedPassword, targetBehavior, homeSchoolGoal, email, phoneNumber)
    db.session.add(new_user)
    db.session.commit()

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/contactus', methods=['POST', 'GET'])
def contactus():
    if request.method == 'POST':
        body = request.form['message']
        #current_user = User.query.filter_by(id=session['userID']).all()[0]
        user = get_user(session['userID'])
        from_email = user.email
        send_email(ADMIN_EMAIL, from_email, 'Contact request', body)
        return redirect(url_for('contactussuccess'))
    else:
        return render_template('contactus.html')

@app.route('/contactussuccess')
def contactussuccess():
    return render_template('contactussuccess.html')

#'gfa2111@cumc.columbia.edu'
@app.route('/notecalendar')
def notecalendar():
    current_user = User.query.filter_by(id=session['userID']).all()[0]
    entry_data = {'date' : [e.date for e in current_user.entries]}
    return render_template('notecalendar.html', data=entry_data)

# TODO: Breaks if Dr. Azad doesn't enter in action plans first. But that shouldn't happen.

# adding entry and viewing data
@app.route('/addentry') # add required message here?
def addentry():
    try:
        if session['userID'] != None:
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
        userID = request.form['userID']
        date = request.form['date']
        targetBehavior = request.form['targetBehavior']
        homeSchoolGoal = request.form['homeSchoolGoal']
        actionPlans = request.form.getlist('actionPlan')
        goalRange=request.form['goalRange']
        signature = request.form['signatureData']

        user = get_user(session['userID'])
        mapping = {"Situation significantly worse":-2, "Situation somewhat worse":-1, "No progress":0, "Situation somewhat better": 1, "Situation significantly better":2}
        new_entry = Entry(userId=user.id, goalRating=mapping[goalRange], date=date, targetBehavior=user.targetBehavior, homeSchoolGoal=user.homeSchoolGoal, signature=signature)
        
        # TODO: Modify db for better solution. Should be a separate table with a position index. FOR TESTING PURPOSES ONLY
        new_entry.actionPlanOne = actionPlans[0]
        if(len(actionPlans) > 1):
            new_entry.actionPlanTwo = actionPlans[1]
        if(len(actionPlans) > 2):
            new_entry.actionPlanThree = actionPlans[2]
        if(len(actionPlans) > 3):
            new_entry.actionPlanFour = actionPlans[3]
        if(len(actionPlans) > 4):
            new_entry.actionPlanFive = actionPlans[4]
        if(len(actionPlans) > 5):
            new_entry.actionPlanSix = actionPlans[5]
        if(len(actionPlans) > 6):
            new_entry.actionPlanSeven = actionPlans[6]
        if(len(actionPlans) > 7):
            new_entry.actionPlanEight = actionPlans[7]
        if(len(actionPlans) > 8):
            new_entry.actionPlanNine = actionPlans[8]
        if(len(actionPlans) > 9):
            new_entry.actionPlanTen = actionPlans[9]

        user.entries.append(new_entry)
        db.session.add(new_entry)
        db.session.add(user)
        try:
            db.session.commit()
        except exc.IntegrityError:
            return "Can't enter two notes for one day! Choose another date for this entry."
        return render_template('submitted.html')

@app.route('/readdata')
def readdata():
    try:
        if session['userID'] != None:
            user = get_user(session['userID'])
            all_entries = user.entries
            table_data = json.dumps([entry.serialize() for entry in all_entries])
            # TODO: IF targetbehavior fixed, have to change this
            targetBehavior = {'targetBehavior' : user.targetBehavior}
            homeSchoolGoal = {'homeSchoolGoal' : user.homeSchoolGoal}
            return render_template('readdata.html', data=table_data, behavior=targetBehavior, homeSchoolGoal=homeSchoolGoal)
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
    if authenticateAdmin(session['role']):    
        return render_template('adminlanding.html')
    else:
        return "Access denied."

def authenticateAdmin(userRole):
    return userRole == ADMINROLE
# TODO: finish these after config the db again
# TODO: no data yet.

@app.route('/adminnotifications')
def adminnotifications():
    if authenticateAdmin(session['role']):
        all_users = User.query.all()
        all_data = []
        for user in all_users:
            user_entry = {'userId' : user.id}
            all_data.append(user_entry)
        return render_template('adminnotifications.html', data=all_data)
    else:
        return "Access denied."

@app.route('/adminnotificationpost', methods=["POST"])
def adminnotificationpost():
    if authenticateAdmin(session['role']):
        try:
            req = request.form.to_dict()
            req_keys = list(req.keys())
            print(req)

            audience = req['audience']
            message_type = req['message-type']
            body = req['message']
            success_message = ""

            query = User.query
            if audience == "Parents":
                query = query.filter_by(userRole='Parent')
                success_message = "all parents"
            elif audience == "Teachers":
                query = query.filter_by(userRole='Teacher')
                success_message = "all teachers"
            elif audience == "Single":
                query = query.filter_by(id=req['single'])
                success_message = "user: " + req['single']
            
            if message_type == "Email":
                query = query.with_entities(User.email)
                all_emails = query.all()
                to_send_emails = [email[0] for email in all_emails]
                print(to_send_emails)
                for to_email in to_send_emails:
                    send_email(to_email, ADMIN_EMAIL, 'Reminder', body)
            elif message_type == "SMS":
                query = query.with_entities(User.phoneNumber)
                all_sms = query.all()
                to_send_sms = [sms[0] for sms in all_sms]
                print(to_send_sms)
                for to_sms in to_send_sms:
                    send_sms(to_sms, body)
            
            return message_type + " was sucessfully sent to " + success_message + "."

        except RuntimeError:
            return "Message sending failed! Try again."
    else:
        return "Access denied." 

def send_email(to_email, from_email, subject, message_body):
    message = Mail(
        from_email = from_email,
        to_emails = to_email,
        subject = subject,
        html_content = '<strong>' + message_body + '</strong>'
    )
    print('init good')
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        print("sg")
        response = sg.send(message)
        print("send")
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print("exception hit")
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
    if authenticateAdmin(session['role']):
        all_users = User.query.all()
        all_data = []
        for user in all_users:
            user_entry = {'userID' : user.id, 'targetBehavior' : user.targetBehavior, 'homeSchoolGoal': user.homeSchoolGoal, 'actionPlans' : [ap.stepName for ap in user.actionplans]}
            all_data.append(user_entry)
        return render_template('adminentry.html', data=all_data)
    else:
        return "Access denied."

@app.route('/adminpost', methods=["POST"])
def adminpost():
    if authenticateAdmin(session['role']):
        req = request.form.to_dict()
        req_keys = list(req.keys())
        #req_action_plan = request.form.to_dict()
        #req_action_plan_keys = list(req_action_plan.keys())
        print(req)
        userId = req_keys[0].split("-")[1]
        current_user = User.query.filter_by(id=userId).all()[0]
        # todo: add targetbehavior and homeschoolgoal
        new_aps = []
        for i in range(10):
            if req[req_keys[i]] == "":
                continue
            new_ap = ActionPlan(order=i, stepName=req[req_keys[i]])
            new_aps.append(new_ap)
            db.session.add(new_ap)

        # TODO: obviously change this, just for testing
        current_user.targetBehavior=req[req_keys[10]]
        current_user.homeSchoolGoal=req[req_keys[11]]
        
        current_user.actionplans=new_aps
        db.session.add(current_user)
        db.session.commit()
        #current_action_plans = [action_plan[key] for key in action_plan_keys]
        return "Information for User: " + current_user.id + " was saved successfully!"
    else:
        return "Access denied."