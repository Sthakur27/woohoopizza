import configparser
from flask import Flask, render_template, request, redirect, session 
import mysql.connector

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

# Set up application server.
app = Flask(__name__)

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql):
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


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
       #todo, try to login user, redirect if successful, error msg if bad creds
        if "email" in request.form:
            print(request.form)
			#print(request.form["email"])
            #print(request.form["password"])
            #book_id = int(request.form["buy-book"])
            #sql = "delete from book where id={book_id}".format(book_id=book_id)
            #sql_execute(sql)
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
    app.run(**config['app'])

