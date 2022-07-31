from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase

config = {
    "apiKey": "AIzaSyDAdVhYNYG7lCpwLTiggSeQ4k6XiwVJ2Nc",
    "authDomain": "authentication-lab-de1af.firebaseapp.com",
    "projectId": "authentication-lab-de1af",
    "storageBucket": "authentication-lab-de1af.appspot.com",
    "messagingSenderId": "607156653908",
    "appId": "1:607156653908:web:f5c07927c3ccfaec3482c1",
    "measurementId": "G-WT5F2HEZJB",
    "databaseURL": "https://authentication-lab-de1af-default-rtdb.firebaseio.com"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'super-secret-key'


@app.route('/', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        user_email = request.form["email"]
        user_password = request.form["password"]

        try:
            login_session['user'] = auth.sign_in_with_email_and_password(user_email, user_password)
            return redirect(url_for('add_tweet'))
        except:
            return render_template("signin.html", error = "Auth Failed")
            # error = "Auth Failed"
    else:
        return render_template("signin.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = ""
    if request.method == 'POST':
        full_name = request.form["full_name"]
        username = request.form["username"]
        bio = request.form["bio"]
        email = request.form["email"]
        pwrd = request.form["password"]
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email,
                                                                             pwrd)
            user = {"full_name": full_name,
                    "username": username,
                    "bio": bio}
            db.child("Users").child(login_session['user']['localId']).set(user)


            return redirect(url_for('signin'))
        except:
            error = "Auth Failed"
    return render_template("signup.html")


@app.route('/add_tweet', methods=['GET', 'POST'])
def add_tweet():
    if request.method == 'POST':
        try:
            tweet = {"title": request.form["title"],
                     "text": request.form["text"],
                     "uid": login_session['user']['localId']}
            db.child("Users").child(login_session['user']['localId']).child("Tweets").push(tweet)
        except:
            return render_template("signin.html")

    return render_template("add_tweet.html")

@app.route('/signout')
def signout():
    login_session['user'] = None
    auth.current_user = None
    return redirect(url_for('signin'))

@app.route('/all_tweets')
def all_tweets():
    return render_template('tweets.html', thing=db.child("Users").child(login_session['user']['localId']).child("Tweets").get().val().values())

if __name__ == '__main__':
    app.run(debug=True)