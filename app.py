from Tool import app, db, login_manager
from Tool.models import User, Club
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/null-club')
def null_club():
    nc = Club(name = 'null')
    db.session.add(nc)
    db.session.commit()
    return 'Added succesfully'


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        passw = request.form['password']
        new_user = User(name=name, email=email, password=passw)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        passw = request.form['password']
        user = User.query.filter_by(email=email).first()
        if (user.check_password(passw)):
            login_user(user)

        return redirect(url_for('index'))
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    print('hi')
    app.run(debug=True)
