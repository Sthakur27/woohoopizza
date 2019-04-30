import configparser
from flask import Flask, render_template, request, redirect, session, flash 
import hashlib
import random
import mysql.connector
from flask_bootstrap import Bootstrap


# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

# Set up application server.
app = Flask(__name__)
bootstrap = Bootstrap(app)

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


def myhash(password):
    hasher = hashlib.sha256()
    bpass = password.encode('ascii')
    hasher.update(bpass)
    bhash = hasher.hexdigest()
    return bhash


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        if(request.form['submit_button'] == "Sign Up"):
            #create user
            email = request.form["email"]
            sql = "select * from User where email='{}';".format(email)
            existing_user = sql_query(sql)
            if(existing_user!=[]):
                flash("Error adding user, email \"{}\"already in use".format(email),"bg-danger")
            else:
                password = request.form["password"]
                passwordhash = myhash(password)
                sql = "insert into User (email,password_hash) values ('{}','{}');".format(email,passwordhash)
                sql_execute(sql)
                flash("User \"{}\" added".format(email),"bg-success")
        else:
            #sign in existing user
            email = request.form["email"]
            passwordhash = myhash(request.form["password"])
            sql = "SELECT password_hash from User where email='{}'".format(email)
            real_phash = sql_query(sql)
            if(real_phash == []):
                flash("No user \"{}\" found".format(email),"bg-danger")
            elif(passwordhash == real_phash[0][0]):
                flash("Successfully Logged in","bg-success")
                session['logged_in'] = True
                session['username'] = email
                return redirect('/menu')
            else:
                flash("Incorrect password for \"{}\"".format(email),"bg-danger")
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/menu', methods=['GET', 'POST'])
def home():
    login_redirect() #ensure user logged in
    if request.method=='POST':
        #insert order
        #get id of inserted row
        sql = "SELECT id from UserOrder where id = LAST_INSERT_ID()"
        order_id = sql_execute(sql)
        if(order_id!=[] and order_id[0]!=[]):
            order_id=[0][0]
            return redirect("/order/confirm/{}".format(order_id))
        else:
            flash("Error retrieving order","bg-danger")
        
    return render_template('food_menu.html',username = session['username'])

def order_analysis(order_id):
    #get pizzas
    sql = "SELECT po.id,po.quantity,p.pizza_size, SUM(po.quantity*fbd.base_price),SUM(po.quantity*fbd.base_calories)"
    sql += " from Pizza p,Pizza_Order po, FoodBaseData fbd where po.order_id={} and p.id=po.pizza_id and fbd.id = p.base_data_id".format(order_id)
    sql += " group by po.id;"
    pizza_orders = sql_execute(sql)
    #append toppings
    for i in range(len(pizza_orders)):
        sql = "SELECT t.name, SUM({}*fbd.base_price),SUM({}*fbd.base_calories)".format(pizza_orders[i][1],pizza_orders[i][1])
        sql += " from Topping t,Pizza_Topping pt, FoodBaseData fbd"
        sql += " where Pizza_Topping.pizza_order_id={} and Pizza_Topping.topping_id=Topping.id".format(pizza_orders[i][0])
        sql += " group by t.name;"
        toppings = sql_execute(sql)
        pizza_orders[i].append(toppings)
    
    #get drinks
    sql = "SELECT do.id,do.quantity,d.name, SUM(po.quantity*fbd.base_price),SUM(po.quantity*fbd.base_calories)"
    sql += " from Drink d,Drink_Order do, FoodBaseData fbd where do.order_id={} and d.id=do.drink_id and fbd.id = d.base_data_id".format(order_id)
    sql += " group by do.id;"
    drink_orders = sql_execute(sql) 
    
    #get breadsticks
    sql = "SELECT bo.id,bo.quantity,b.name, SUM(bo.quantity*fbd.base_price),SUM(bo.quantity*fbd.base_calories)"
    sql += " from BreadStick b,BreadStick_Order bo, FoodBaseData fbd where bo.order_id={} and b.id=bo.breadstick_id and fbd.id = b.base_data_id".format(order_id)
    sql += " group by bo.id;"
    breadstick_orders = sql_execute(sql)
    
    total_price = 0
    total_calories = 0
    for po in pizza_orders:
        for t in po[-1]:
            total_price+=t[1]
            total_calories+=t[2]
        total_price += po[3]
        total_calories += po[4]
    
    for do in drink_orders:
        total_price += do[3]
        total_calories += do[4]
        
    for bo in breadstick_orders:
        total_price += bo[3]
        total_calories += bo[4]
        
    return ([total_price,total_calories,pizza_orders,drink_orders,breadstick_orders])
    
@app.route('/order/confirm/<int:order_id>', methods=['GET', 'POST'])
def order_confirm(order_id):
    if request.method=='POST':
        #set confirmed = true for order
        redirect("/")
    login_redirect() #ensure user logged in
    order_info = order_analysis(order_id)
    return render_template('order_summary.html',confirm=True,order_info = order_info, username = session['username'])    
    
@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_summary(order_id):
    login_redirect() #ensure user logged in        
    '''
    #get total calories,price
    sql  = "SELECT SUM(po.quantity*,SUM(fbd.base_price)"
    sql += " from Pizza_Order po,Pizza p,Pizza_Topping pt,Topping t,BreadStick_Order bo,BreadStick b,Drink_Order do,Drink d," 
    sql += " FoodBaseData fbd1, FoodBaseData fbd2, FoodBaseData fbd3,FoodBaseData fbd4" 
    sql += " where po.order_id={} and bo.order_id={} and do.order_id={}".format(order_id,order_id,order_id)
    sql += " and po.pizza_id=p.id and p.base_data_id=fbd1.id"
    sql += " and pt.pizza_order_id=po.id and t.id=pt.topping_id and fbd2.id=t.base_data_id"
    sql += " and bo.id=b.id and b.base_data_id=fbd3.id"
    sql += " and do.id=d.id and d.base_data_id=fbd4.id"
    '''
    order_info = order_analysis(order_id)
    return render_template('order_summary.html',confirm=False, order_info = order_info, username = session['username'])

@app.route('/user/history/', methods=['GET', 'POST'])
def order_history():
    login_redirect() #ensure user logged in
    sql = "SELECT uo.id, uo.placed_on from UserOrder uo, User u where u.email=\"{}\" and uo.user_id = u.id".format(session['username'])
    orders = sql_execute(sql)
    return render_template('user_history.html',orders = orders, username = session['username'])

if __name__ == '__main__':
    app.secret_key = 't13rulzlol'
    app.run(**config['app'])

