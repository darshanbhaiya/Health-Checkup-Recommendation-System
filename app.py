from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import os
import pandas as pd
from mymodels import main1, main2

# Define Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Define SQLite database URIs
Users_uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'User.db')
Checkup_uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Checkup.db')
CheckupDetails_uri = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Checkupdetails.db')

app.config['SQLALCHEMY_DATABASE_URI'] = Users_uri
app.config['SQLALCHEMY_BINDS'] = {
    'checkup': Checkup_uri,
    'Checkupdetails': CheckupDetails_uri
}

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    Adhaar = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Age = db.Column(db.Integer, nullable=False)
    Gender = db.Column(db.String(7), nullable=False)
    Phoneno = db.Column(db.Integer, nullable=False)
    Address = db.Column(db.Text)
    Username = db.Column(db.String(30), nullable=False, unique=True)
    Password = db.Column(db.String(30), nullable=False)
    doctor = db.Column(db.Integer, nullable=True)

# Define Checkup model
class Checkup(db.Model):
    __bind_key__ = 'checkup'
    id = db.Column(db.Integer, primary_key=True)
    user_adhaar = db.Column(db.Integer, unique=False)
    Checkup_Result = db.Column(db.String(10), nullable=False, unique=False)
    Date = db.Column(db.String(10), default=datetime.datetime.utcnow().strftime("%m/%d/%Y"))

# Define Checkupdetails model
class Checkupdetails(db.Model):
    __bind_key__ = 'Checkupdetails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=False)
    gender = db.Column(db.Integer, nullable=False, unique=False)
    age = db.Column(db.Integer, nullable=False, unique=False)
    sleepDuration = db.Column(db.Float, nullable=False, unique=False)
    qualityOfSleep = db.Column(db.Integer, nullable=False, unique=False)
    physicalActivityLevel = db.Column(db.Float, nullable=False, unique=False)
    stressLevel = db.Column(db.Integer, nullable=False, unique=False)
    bmi = db.Column(db.Float, nullable=False, unique=False)
    bloodPressure = db.Column(db.Float, nullable=False, unique=False)
    heartRate = db.Column(db.Integer, nullable=False, unique=False)
    dailySteps = db.Column(db.Integer, nullable=False, unique=False)
    fever = db.Column(db.Integer, nullable=False, unique=False)
    cough = db.Column(db.Integer, nullable=False, unique=False)
    fatigue = db.Column(db.Integer, nullable=False, unique=False)
    breathingDifficulty = db.Column(db.Integer, nullable=False, unique=False)
    cholesterol = db.Column(db.Integer, nullable=False, unique=False)

# Create database tables
with app.app_context():
    db.create_all()

listuser=[]
listAdhar=[]


# Function to calculate Mean Arterial Pressure (MAP)
def calculate_map(systolic, diastolic):
    map_value = (2 * diastolic + systolic) / 3
    return map_value

# Function to check cholesterol level
def check_cholesterol_level(saturatedTransFats, dietaryCholesterol, omega3FattyAcids, solubleFiber, alcoholConsumption, smoking):
    total_score = saturatedTransFats + dietaryCholesterol + omega3FattyAcids + solubleFiber + alcoholConsumption + smoking

    if total_score >= 8:
        return 2
    elif 4 <= total_score <= 7:
        return 1
    else:
        return 0

# Function to check fever
def has_fever(bodytemp):
    fever_threshold_fahrenheit = 98.6
    return bodytemp > fever_threshold_fahrenheit

# Routes

@app.route('/')
def helloworld():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(Username=username).first()

        if user and username == user.Username and password == user.Password:
            if user.doctor == 0:
                session['logged_in'] = True
                session['adhaar'] = user.Adhaar
                return render_template('dashboard.html', name=user.Name, Age=user.Age, username=user.Username, password=user.Password, adhaar=user.Adhaar)
            else:
                session['logged_in'] = True
                session['adhaar'] = user.Adhaar
                return render_template('doctor.html', name=user.Name, Age=user.Age, username=user.Username, password=user.Password, adhaar=user.Adhaar)
        else:
            return 'Wrong username and password'

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phoneno = request.form['phone']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        adhaar = request.form['aadhaar']
        doctor = int(request.form['doctor'])

        existing_user = 0
        if username in listuser or adhaar in listAdhar:
            existing_user = 1

        if existing_user:
            return render_template('signup.html', error="Username or Aadhaar number already exists. Please choose different ones.")
        else:
            new_user = User(Name=name, Age=age, Gender=gender, Phoneno=phoneno, Address=address, Username=username, Password=password, Adhaar=adhaar, doctor=doctor)
            db.session.add(new_user)
            db.session.commit()
            listuser.append(username)
            listAdhar.append(adhaar)
            session['logged_in'] = True
            session['adhaar'] = new_user.Adhaar

            if doctor == 0:
                return render_template('dashboard.html', name=new_user.Name, Age=new_user.Age, username=new_user.Username, password=new_user.Password, adhaar=new_user.Adhaar)
            else:
                return render_template('doctor.html', name=new_user.Name, Age=new_user.Age, username=new_user.Username, password=new_user.Password, adhaar=new_user.Adhaar)
                
    return render_template('signup.html')

@app.route('/doctoruser', methods=['GET', 'POST'])
def doc():
    id = request.form["loginId"]
    if not session.get('logged_in'):
        return redirect(url_for('helloworld'))
    else:
        user = User.query.filter_by(Adhaar=id).first()
        checkups = Checkup.query.filter_by(user_adhaar=id).all()
        for checkup in checkups:
            print(f"Checkup ID: {checkup.id},  Result: {checkup.Checkup_Result}, Date: {checkup.Date}")
        return render_template('doctorhistory.html', user=user, checkups=checkups)

@app.route('/review/<int:checkup_id>', methods=['GET', 'POST'])
def review(checkup_id):
    details = Checkupdetails.query.filter_by(id=checkup_id).all()
    return render_template('review.html', data=details[0])

@app.route('/history')
def history():
    if not session.get('logged_in'):
        return redirect(url_for('helloworld'))
    else:
        adhaar = session.get('adhaar')
        user = User.query.filter_by(Adhaar=adhaar).first()
        checkups = Checkup.query.filter_by(user_adhaar=adhaar).all()
        for checkup in checkups:
            print(f"Checkup ID: {checkup.id},  Result: {checkup.Checkup_Result}, Date: {checkup.Date}")
        return render_template('history.html', user=user, checkups=checkups)

@app.route('/checkup-form', methods=['GET', 'POST'])
def checkupform():
    if not session.get('logged_in'):
        return redirect(url_for('helloworld'))
    if request.method == 'POST':
        name = str(request.form['name'])
        gender = int(request.form['gender'])
        age = int(request.form['age'])
        sleepduration = float(request.form['sleepDuration'])
        qualityOfSleep = int(request.form['qualityOfSleep'])
        physicalActivity = float(request.form['physicalActivity']) * 10
        stresslevel = int(request.form['stressLevel'])
        bmi = float(request.form['bmi'])

        bloodpressure = str(request.form['bloodPressure'])
        bp = bloodpressure.split('/')
        bloodpressure = round(calculate_map(int(bp[0]), int(bp[1])), 2)

        heartrate = int(request.form['heartRate'])
        daily_steps = int(request.form['dailySteps'])

        bodytemp = float(request.form['bodytemp'])
        Fever = has_fever(bodytemp)

        cough = int(request.form['cough'])
        fatigue = int(request.form['fatigue'])
        Breathing_difficulty = int(request.form['difficultyBreathing'])

        saturatedTransFats = int(request.form['saturatedTransFats'])
        dietaryCholesterol = int(request.form['dietaryCholesterol'])
        omega3FattyAcids = int(request.form['omega3FattyAcids'])
        solubleFiber = int(request.form['solubleFiber'])
        alcoholConsumption = int(request.form['alcoholConsumption'])
        smoking = int(request.form['smoking'])
        cholesterolLevel = check_cholesterol_level(saturatedTransFats, dietaryCholesterol, omega3FattyAcids, solubleFiber, alcoholConsumption, smoking)

        details_tuple = Checkupdetails(name=name, gender=gender, age=age, sleepDuration=sleepduration, qualityOfSleep=qualityOfSleep, physicalActivityLevel=physicalActivity, stressLevel=stresslevel, bmi=bmi, bloodPressure=bloodpressure, heartRate=heartrate, dailySteps=daily_steps, fever=Fever, cough=cough, fatigue=fatigue, breathingDifficulty=Breathing_difficulty, cholesterol=cholesterolLevel)
        db.session.add(details_tuple)
        db.session.commit()

        session['name'] = name
        session['gender'] = gender
        session['age'] = age
        session['sleepduration'] = sleepduration
        session['qualityOfSleep'] = qualityOfSleep
        session['physicalActivity'] = physicalActivity
        session['stresslevel'] = stresslevel
        session['bmi'] = bmi
        session['bloodpressure'] = bloodpressure
        session['heartrate'] = heartrate
        session['daily_steps'] = daily_steps
        session['Fever'] = Fever
        session['cough'] = cough
        session['fatigue'] = fatigue
        session['Breathing_difficulty'] = Breathing_difficulty
        session['cholesterolLevel'] = cholesterolLevel

        if bmi < 18.5:
            bmi = 0
        elif 18.5 <= bmi < 25:
            bmi = 1
        elif bmi >= 25:
            bmi = 2

        output1 = main2(gender, age, sleepduration, qualityOfSleep, physicalActivity, stresslevel, bmi, bloodpressure, heartrate, daily_steps)
        output2 = main1(Fever, cough, fatigue, Breathing_difficulty, age, gender, bloodpressure, cholesterolLevel)

        if output1 == 1 or output2 == 1:
            session['Output'] = 1
            result = 'Must visit'
        else:
            session['Output'] = 0
            result = 'Visit Not required'

        new_tuple = Checkup(user_adhaar=session['adhaar'], Checkup_Result=result)
        db.session.add(new_tuple)
        db.session.commit()

        return render_template('try.html')

    return render_template('newform.html')

@app.route('/get_health_data')
def get_health_data():
    health_data = {
        "name": session.get('name'),
        "gender": session.get('gender'),
        "age": session.get('age'),
        "sleepDuration": session.get('sleepduration'),
        "qualityOfSleep": session.get('qualityOfSleep'),
        "physicalActivityLevel": session.get('physicalActivity'),
        "stressLevel": session.get('stresslevel'),
        "bmi": session.get('bmi'),
        "bloodPressure": session.get('bloodpressure'),
        "heartRate": session.get('heartrate'),
        "dailySteps": session.get('daily_steps'),
        "fever": session.get('Fever'),
        "cough": session.get('cough'),
        "fatigue": session.get('fatigue'),
        "breathingDifficulty": session.get('Breathing_difficulty'),
        "cholesterol": session.get('cholesterolLevel'),
        "result": session['Output']
    }
    return jsonify(health_data)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('prob', None)
    session.pop('Output', None)
    session.pop('adhaar', None)
    return redirect(url_for('helloworld'))

if __name__ == '__main__':
    app.run(debug=True)
