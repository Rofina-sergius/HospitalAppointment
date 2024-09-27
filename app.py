from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.secret_key = '12345'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ADMIN_CREDENTIALS = {
    'Admin': 'rofina',
    'rofina': 'sergius'
}

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usr(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           name TEXT NOT NULL,
           mail TEXT NOT NULL,
           date TEXT NOT NULL)""")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    mail = request.form['mail']
    date = request.form['date']
    
    # Parse the appointment date
    app_date = datetime.strptime(date, '%Y-%m-%d')
    current_date = datetime.now()

    # Check if the appointment date is in the past
    if app_date < current_date:
        flash("Error: The appointment date can't be in the past")
        return redirect(url_for('index'))

    # Connect to the database and save the appointment
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO usr (name, mail, date) VALUES (?, ?, ?)", (name, mail, date))
    conn.commit()
    conn.close()

    flash('Appointment submitted successfully!')
    return redirect(url_for('index'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
    
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['logged_in'] = True
            flash("Login successful!")
            return redirect(url_for('result'))  # Redirect to the index page or admin dashboard
        else:
            flash("Invalid username or password!")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('you have been logged out')
    return redirect(url_for('login'))
@app.route('/result')
def result():
    if not session.get('logged_in'):
        flash('you need to login to acces this page')
        return redirect(url_for('login'))
    conn=sqlite3.connect('database.db')
    c=conn.cursor()
    c.execute('select * from usr')
    data=c.fetchall()
    conn.close()
    return render_template('result.html',data=data)
if __name__ == '__main__':
    init_db()  # Ensure the database is initialized on startup
    app.run(debug=True, host='0.0.0.0', port=8000)
