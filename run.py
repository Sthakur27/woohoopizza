import configparser
from flask import Flask, render_template, request, redirect, session 
import hashlib
import random
import mysql.connector

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

# Set up application server.
app = Flask(__name__)

# Create a function for fetching data from the database.
def sql_query(sql):
    print("ATTEMPTING QUERY:")
    print(sql)
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql):
    print("ATTEMPTING EXECUTE:")
    print(sql)
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

#@app.route('/')
def template_response():
    return render_template('home.html')

def login_redirect():
    if not is_logged_in():
        redirect('/login')

@app.route('/logout',methods=['GET'])
def logout():
    session['logged_in']=False
    redirect('/login')

def is_logged_in():
    if not session.get('logged_in'):
        return False
    else:
        return session['logged_in']

@app.route('/newuser',methods=['GET','POST'])
def newuser():
    if request.method=='POST':
        #todo check if correct, create user, add to db
        session['logged_in']=True
        return redirect('/login')
    if request.method=='GET':
        #return page for creating user
        return render_template('createuser.html')

def myhash(password):
    '''
    algo = 'sha256'
    hsh = get_hexdigest(algo,"",password)
    return hsh;
    '''
    hasher = hashlib.sha256()
    bpass = password.encode('ascii')
    hasher.update(bpass)
    bhash = hasher.hexdigest()
    #return bhash.decode('unicode_escape')
    return bhash


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        print(request.form)
        if(request.form['submit_button'] == "Sign Up"):
            email = request.form["email"]
            sql = "select * from User where email='{}';".format(email)
            existing_user = sql_query(sql)
            if(existing_user!=[]):
                print("existing user found: {}".format(existing_user))
            else:
                password = request.form["password"]
                print(password)
                passwordhash = myhash(password)
                print(passwordhash)
                sql = "insert into User (email,password_hash) values ('{}','{}');".format(email,passwordhash)
                sql_execute(sql)
        else:
            email = request.form["email"]
            passwordhash = myhash(request.form["password"])
            sql = "SELECT password_hash from User where email='{}'".format(email)
            real_phash = sql_query(sql)[0][0]
            print(real_phash)
            print(passwordhash)
            if(passwordhash == real_phash):
                print("match")
                session['logged_in']=True
                return redirect('/menu')
            else:
                print("incorrect password")
            
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
def home():
    login_redirect() #ensure user logged in
    return render_template('home.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    login_redirect() #ensure user logged in
    print("at menu")
    return render_template('home.html')

@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_summary(order_id):
    login_redirect() #ensure user logged in
    return render_template('ordersummary.html')

@app.route('/user/history/<int:user_id>', methods=['GET', 'POST'])
def order_history(user_id):
    login_redirect() #ensure user logged in
    return render_template('userhistory.html')

if __name__ == '__main__':
    app.secret_key = 't13rulzlol'
    app.run(**config['app'])
