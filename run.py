import configparser
from flask import Flask, render_template, request, redirect, session, flash 
import hashlib
import random
import mysql.connector
from flask_bootstrap import Bootstrap
import json
import time

# Read configuration from file to connect to database
config = configparser.ConfigParser()
config.read('config.ini')

# Set up application server.
app = Flask(__name__)
bootstrap = Bootstrap(app)

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def sql_execute(sql, returnId = False):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    if(returnId):
        newId = cursor.lastrowid
    db.commit()
    cursor.close()
    db.close()
    if(returnId):
        return newId

# Logout redirects to login page
@app.route('/logout',methods=['GET'])
def logout():
    session['logged_in']=False
    return redirect('/login')

# Helper function to test whether user is logged in
def is_logged_in():
    if(session.get('username') is None):
        return False
    if (not session.get('logged_in')) or (not session.get('username')) or session.get('username') is None:
        return False
    else:
        return session['logged_in']


# Helper function that hashes password to send to backend
def myhash(password):
    hasher = hashlib.sha256()
    bpass = password.encode('ascii')
    hasher.update(bpass)
    bhash = hasher.hexdigest()
    return bhash

# Login page
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        if(request.form['submit_button'] == "Sign Up"):

            #create user
            email = request.form["email"]
            sql = "select * from User where email='{}';".format(email)
            existing_user = sql_query(sql)

            #check for existing user, else add to database
            if(existing_user!=[]):
                flash("Error adding user, email \"{}\"already in use".format(email),"bg-danger")
                return redirect('/login')
            else:
                password = request.form["password"]
                passwordhash = myhash(password)
                sql = "insert into User (email,password_hash) values ('{}','{}');".format(email,passwordhash)
                sql_execute(sql)
                flash("User \"{}\" added".format(email),"bg-success")

        else:

            #sign in existing user after various checks
            email = request.form["email"]
            passwordhash = myhash(request.form["password"])
            sql = "SELECT password_hash,id from User where email='{}'".format(email)
            real_phash = sql_query(sql)
            if(real_phash == []):
                flash("No user \"{}\" found".format(email),"bg-danger")
                return redirect('/login')
            elif(passwordhash == real_phash[0][0]):
                flash("Successfully Logged in","bg-success")
                session['logged_in'] = True
                session['username'] = email
                session['uid'] = real_phash[0][1]
                return redirect('/menu')
            else:
                flash("Incorrect password for \"{}\"".format(email),"bg-danger")
                return redirect('/login')
        return redirect('/login')
    else:
        return render_template('login.html')

# The main menu page
@app.route('/', methods=['GET', 'POST'])
@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if not is_logged_in(): #ensure user logged in
        return redirect('/login')
    # Load in the POST request data containing order
    if request.method=='POST':
        data = json.loads(request.data.decode('ascii'))
        pizzas = data[0]
        breadsticks = data[1]
        drinks = data[2]
        
        #create user order
        sql = "INSERT INTO UserOrder (user_id,placed_on) values ({},'{}');".format(session['uid'],time.strftime('%Y-%m-%d %H-%M-%S'))
        order_id = sql_execute(sql,returnId=True) #get id of row inserted

        # Generating the SQL pizza order to send to backend
        psizes = {"Small":1,"Medium":2,"Large":3}
        toppings = {'pepperoni':5,'mushroom':6,"olive":7,"bacon":8,'sausage':9}
        for p in pizzas:
            sql = "INSERT into Pizza_Order (pizza_id,order_id,quantity) values ({},{},{});".format(psizes[p['size']]+1,order_id,p['amount'])
            last_pizza_id = sql_execute(sql,returnId=True)
            for t in toppings:
                if(p[t]): #pizza has topping
                    sql = "INSERT into Pizza_Topping (pizza_order_id,topping_id) values ({},{});".format(last_pizza_id,toppings[t])
                    sql_execute(sql)

        # Generating the SQL breadstick order to send to backend
        btypes = {"Original Breadsticks":13,"Cheesy Breadsticks":14,"Cheesy Garlic Breadsticks":15}   
        for b in breadsticks:
            print(b)
            sql = "INSERT into BreadStick_Order (breadstick_id,order_id,quantity) values ({},{},{});".format(btypes[b['type']],order_id,b['amount'])
            sql_execute(sql) 

        # Generating the SQL drink order to send to backend
        dsizes = {'Small':0,'Medium':1,'Large':2}
        dtypes = {"Crush":13,"Mountain Dew":16,"Coke":10}
        for d in drinks:
            sql = "INSERT into Drink_Order (drink_id,order_id,quantity) values ({},{},{});".format(dtypes[d['typeText']]+dsizes[d['size']],order_id,d['amount'])
            sql_execute(sql)
        flash("Order added successfully","bg-success")     
    return render_template('food_menu.html',username = session['username'])


# Order analysis page
def order_analysis(order_id):

    #retrieve pizza data from backend 
    sql = "SELECT po.id,po.quantity,p.pizza_size, SUM(po.quantity*fbd.base_price),SUM(po.quantity*fbd.base_calories)"
    sql += " from Pizza p,Pizza_Order po, FoodBaseData fbd where po.order_id={} and p.id=po.pizza_id and fbd.id = p.base_data_id".format(order_id)
    sql += " group by po.id;"
    pizza_orders = sql_query(sql)

    #append toppings
    for i in range(len(pizza_orders)):
        sql = "SELECT t.name, SUM({}*fbd.base_price),SUM({}*fbd.base_calories)".format(pizza_orders[i][1],pizza_orders[i][1])
        sql += " from Topping t,Pizza_Topping pt, FoodBaseData fbd"
        sql += " where pt.pizza_order_id={} and pt.topping_id=t.id and t.base_data_id=fbd.id".format(pizza_orders[i][0])
        sql += " group by t.name;"
        toppings = sql_query(sql)
        pizza_orders[i] = list(pizza_orders[i])
        txt = ""
        for t in toppings:
            ttxt = t[0]+" "
            txt = txt + ttxt
        if(txt==""):
            txt="No Toppings"
        pizza_orders[i].append(txt)
        pizza_orders[i].append(toppings)
    
    #get drinks data from backend
    sql = "SELECT do.id,do.quantity,d.name, SUM(do.quantity*fbd.base_price),SUM(do.quantity*fbd.base_calories)"
    sql += " from Drink d,Drink_Order do, FoodBaseData fbd where do.order_id={} and d.id=do.drink_id and fbd.id = d.base_data_id".format(order_id)
    sql += " group by do.id;"
    drink_orders = sql_query(sql) 
    
    #get breadsticks data from backend
    sql = "SELECT bo.id,bo.quantity,b.name, SUM(bo.quantity*fbd.base_price),SUM(bo.quantity*fbd.base_calories)"
    sql += " from BreadStick b,BreadStick_Order bo, FoodBaseData fbd where bo.order_id={} and b.id=bo.breadstick_id and fbd.id = b.base_data_id".format(order_id)
    sql += " group by bo.id;"
    breadstick_orders = sql_query(sql)
    
    #analytics queries to calculate total price and calories
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

    #return all data
    return (["%.2f" % round(total_price, 2),total_calories,pizza_orders,drink_orders,breadstick_orders])

# Refresh page
@app.route("/refresh")
def ref():

    # Wipe the menu clean as order did not get placed
    for t in ['Pizza_Topping','BreadStick_Order','Drink_Order','Pizza_Order','UserOrder','User']:
        sql = "DELETE from {};".format(t)
        sql_execute(sql)
    sql = "UPDATE BreadStick set base_data_id=15 where id=15";
    sql_execute(sql)
    sql = "UPDATE FoodBaseData set base_calories=160,base_price=1.05 where id=13";
    sql_execute(sql)
    sql = "UPDATE FoodBaseData set base_calories=180,base_price=1.20 where id=14";
    sql_execute(sql)
    sql = "UPDATE FoodBaseData set base_calories=190,base_price=1.30 where id=15";
    sql_execute(sql)
    return redirect("/")
    
# For various SQL queries from tables if need be   
@app.route("/query")
def qme():
    sql = "SELECT * from Drink;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    sql = "SELECT * from BreadStick;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    sql = "SELECT * from Pizza;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    sql = "SELECT * from Topping;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    sql = "SELECT * from FoodBaseData;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    sql = "SELECT * from UserOrder;"
    ds = sql_query(sql)
    for d in ds:
        print(d)
    return redirect("/") 

# Page to go to for order analysis
@app.route('/order/<int:order_id>', methods=['GET', 'POST'])
def order_summary(order_id):
    if not is_logged_in(): #ensure user logged in
        return redirect('/login')       
    order_info = order_analysis(order_id)
    return render_template('order_summary.html',confirm=False, order_info = order_info, username = session['username'])

# Page for user order history
@app.route('/user/history/', methods=['GET', 'POST'])
def order_history():
    if not is_logged_in(): #ensure user logged in
        return redirect('/login')
    sql = "SELECT uo.id, uo.placed_on from UserOrder uo, User u where u.email=\"{}\" and uo.user_id = u.id".format(session['username'])
    orders = sql_query(sql)
    return render_template('orderhistory.html',orders = orders, username = session['username'])

# Page that sends SQL queries to delete orders if need be from backend
@app.route('/order/delete/<int:order_id>', methods=['GET', 'POST'])
def order_delete(order_id):
    if not is_logged_in(): #ensure user logged in
        return redirect('/login')
    sql = "DELETE from Pizza_Topping WHERE Pizza_Topping.pizza_order_id in (SELECT id from Pizza_Order where Pizza_Order.order_id={})".format(order_id)
    sql_execute(sql)   
    sql = "DELETE from Pizza_Order WHERE Pizza_Order.order_id={}".format(order_id)
    sql_execute(sql)
    sql = "DELETE from BreadStick_Order WHERE BreadStick_Order.order_id={}".format(order_id)
    sql_execute(sql)
    sql = "DELETE from Drink_Order WHERE Drink_Order.order_id={}".format(order_id)
    sql_execute(sql)
    sql = "DELETE from UserOrder WHERE UserOrder.id={}".format(order_id)
    sql_execute(sql)
    return redirect('/user/history/')

if __name__ == '__main__':
    app.secret_key = 't13rulzlol'
    app.run(**config['app'])

