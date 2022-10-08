from flask import Flask, render_template, request

import mysql.connector as mysql

app=Flask(__name__)
app.secret_key='hari123'

db = mysql.connect(
    host = 'localhost',
    user = 'root',
    password = 'root',
    database='db'
)

cursor = db.cursor()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/admin_login')
def adminLogin():
    return render_template('admin_login.html')

# Collecting data from registration page.
@app.route('/collect',methods=['POST'])
def collectData():
    n = request.form['name']
    m = request.form['mob']
    a = request.form['acnt']

    k = getdetails(n,m)
    if k:
        sql = 'UPDATE customer SET status = NULL, time = NULL WHERE name = %s'
        val = (n,)
        cursor.execute(sql,val)
        db.commit()
        return render_template('register.html',res = (n+" "+"Request Sent"))
    else:
        storedata(n,m,a)
        return render_template('register.html',res = "Data Request Sent")

# Checking data from login page i.e; present in database or not
@app.route('/compare',methods=['POST'])
def checkstatus():
    mobnum = request.form['mob']

    sql = 'SELECT * FROM customer WHERE mobile = %s'
    val = (mobnum,)
    cursor.execute(sql,val)
    result = cursor.fetchone()
    if result:
        #print(result)
        if result[4]== None:
            return render_template('status.html',res1 = "Decision Pending")
        else:
            dt = str(result[3])
            d = dt[8:10]+"-"+dt[5:8]+dt[:4]
            t = dt[11:]
            dt = d+" "+t
            return render_template('status.html',res1 = "Approved",res2 = 'at', res3 = dt)
    else:
        return render_template("login.html",res = 'Invalid Credentials')

# To check data of admin login
@app.route('/collect_admin',methods=['POST'])
def admin():
    r = request.form['mob1']
    p = request.form['psw1']

    result = getDataFromAdmin(r,p)
    if result:
        cursor.execute('SELECT * FROM customer')
        result = cursor.fetchall()
        # This is to print data in table format
        data = []
        for i in result:
            data.append(i)
        return render_template('admin.html',res = data)
    else:
        return render_template('admin_login.html',res = 'Invalid Credentials')
        
# admin is scheduling some date, time for meeting
@app.route('/assign_time_admin',methods=['POST'])
def adminAssignsTime():
    m = request.form['mob']
    t = request.form['time']

    sql = 'SELECT * FROM customer WHERE mobile = %s'
    val = (m,)
    cursor.execute(sql,val)
    result = cursor.fetchone()
    if result:
        sql = "UPDATE customer SET time = %s WHERE mobile = %s"
        val = (t,m)
        cursor.execute(sql,val)
        db.commit()
        return render_template("admin.html",res1 = "Data Updated")
    else:
        return render_template("admin.html",res1 = "Invalid Number")

# To refresh the page and show data
@app.route('/admin_refresh',methods=['POST'])
def resetButttonAdmin():
    cursor.execute("SELECT * FROM customer")
    result = cursor.fetchall()
    db.commit()
    data = []
    for i in result:
        data.append(i)
    return render_template('admin.html',res = data)

# To collect the status i.e; approve, reject, or assign some time by the customer
@app.route('/collect_status',methods=['POST'])
def collectStatus():
    m = request.form['mob']
    st = request.form['status']
    #print(st)
    sql = 'SELECT * FROM customer WHERE mobile = %s'
    val = (m,)
    cursor.execute(sql,val)
    result = cursor.fetchone()
    if result[3] != None:
        if st == 'approve':
            k = 'Approved'
            sql = "UPDATE customer SET status = %s WHERE mobile = %s"
            val = (k,m)
            cursor.execute(sql,val)
            db.commit()
            return render_template('status.html',res1=k)
        elif st == 'reject':
            kn = 'Rejected'
            sql = "UPDATE customer SET status = %s WHERE mobile = %s"
            val = (kn,m)
            cursor.execute(sql,val)
            db.commit()
            return render_template('status.html',res1=kn)
        elif st == "assign":
            dt = request.form['time']
            k = 'Approved'
            sql = "UPDATE customer SET status = %s WHERE mobile = %s"
            val = (k,m)
            cursor.execute(sql,val)
            db.commit()
            sql = "UPDATE customer SET time = %s WHERE mobile = %s"
            val = (dt,m)
            cursor.execute(sql,val)
            db.commit()
            # this is to display at status page if changes made
            dt = str(dt)
            d = dt[8:10]+"-"+dt[5:8]+dt[:4]
            t = dt[11:]
            dt = d+" "+t
            return render_template('status.html',res1 = k,res2 = "at", res3 = dt)
    else:
        return render_template('status.html', res1 = "Still the decision is pending!")

# To check data is present in database or not(customer)
def getdetails(name,mob):
    cursor.execute("SELECT * FROM customer WHERE name = %s AND mobile = %s", (name,mob))
    result = cursor.fetchone()
    return result

# If data is not present in database, then store data(customer)
def storedata(name,mob,account): #Private function not a handler
    sql = "INSERT INTO customer (name,mobile,acntno) VALUES (%s,%s,%s)"
    val = (name,mob,account)
    cursor.execute(sql,val)
    db.commit()

# Check the data entered is correct or not.(admin)
def getDataFromAdmin(mob,psw):
    cursor.execute("SELECT * FROM admin WHERE mobile = %s AND password = %s", (mob,psw))
    result = cursor.fetchone()
    return result

if __name__=="__main__":
    app.run(debug=True)