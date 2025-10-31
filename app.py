from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "stockify_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

# ---------------- DATABASE MODEL ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# ---------------- ROUTES ----------------

@app.route('/')
def home():
    return redirect(url_for('login'))


# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check for admin login
        if email == "storeadmin@gmail.com":
            if password == "CSS@123_":
                session['fullname'] = "Admin"
                flash("The admin no longer needs to sign up.")
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Incorrect admin password.")
                return render_template('login.html')

        # Regular crew login
        user = User.query.filter_by(email=email).first()

        if user:
            if user.password == password:
                session['user_id'] = user.id
                session['fullname'] = user.fullname
                return redirect(url_for('crew_dashboard'))
            else:
                flash('Incorrect password.')
        else:
            flash('Email not found. Please sign up first.')

    return render_template('login.html')


# ---------------- SIGNUP ----------------
@app.route('/signup', methods=['POST'])
def signup():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']

    if email == "storeadmin@gmail.com":
        flash("The admin no longer needs to sign up.")
        return redirect(url_for('login'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("The email has an account.")
        return redirect(url_for('login'))

    new_user = User(fullname=fullname, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash("Account created successfully! You can now log in.")
    return redirect(url_for('login'))


# ---------------- CREW DASHBOARD ----------------
@app.route('/crew_dashboard')
def crew_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    name = session.get('fullname', 'Crew')
    return render_template('crew_dashboard.html', name=name)


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('fullname') != "Admin":
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    name = session.get('fullname', 'Crew')
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session.clear()
    return render_template('logout.html', name=name, time=time)


# ---------------- MAIN ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
