from flask import Flask, render_template, flash, request, url_for, redirect, session
from dbcon import Connection
from passlib.hash import sha256_crypt
from pymysql import escape_string as es

import gc
import time
import datetime


app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/dash/', methods=['GET', 'POST'])
def dash():
    error = ''
    try:
        if request.method == "POST":
            nic = request.form['nic']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            mobile = request.form['mobile']
            dob = request.form['dob']
            weight = request.form['weight']
            height = request.form['height']
            chest = request.form['chest']
            password = sha256_crypt.encrypt((str(request.form['password'])))

            c, conn = Connection()

            x = c.execute("SELECT * FROM members WHERE nic = (%s)", (es(nic)))

            if int(x) > 0:
                error = "already exists"
                return render_template("register.html", error = error)

            else:


                c.execute("INSERT INTO members (nic, fname, lname, email, mobile, dob, weight, height, chest, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(es(nic), es(fname), es(lname), es(email), es(mobile), es(dob), es(weight),es(height), es(chest), es(password)))

                conn.commit()
                c.close()
                conn.close()
                gc.collect()

                return redirect(url_for("dash"))

        return render_template(render_template("register.html"))

    except Exception as e:
        return(str(e))




    return render_template("register.html")


@app.route('/checkin/')
def checkin():
    error = 'Please place Your face and press checkin'
    return render_template("checkin.html", error =error)

@app.route('/settings/', methods=['GET', 'POST'])
def settings():
    error = 'Create a New Admin Account'
    try:
        if request.method == "POST":
            fname = request.form['name']
            email = request.form['email']
            password = request.form['password']
            password_con = request.form['password_con']

            c, conn = Connection()

            x = c.execute("SELECT * FROM users WHERE email = (%s)", (es(email)))

            if password != password_con:
                error = "Passwords don't Match"
                return render_template("settings.html", error=error)

            else:

                if int(x) > 0:
                    error = "Email Already Exists"

                    return render_template("setttings.html", error=error)


                else:

                    password = sha256_crypt.encrypt(password)

                    c.execute(
                        "INSERT INTO users (fname, email, password) VALUES (%s, %s, %s)",
                        (es(fname), es(email), es(password)))

                    conn.commit()
                    c.close()
                    conn.close()
                    gc.collect()

                    return redirect(url_for("settings"))

        return render_template(render_template("settings.html", error=error))

    except Exception as e:
        return (str(e))



    return render_template("settings.html", error = error)

@app.route('/', methods=['GET', 'POST'])
def index():
    error = 'Type your Username and Password.'
    try:
        c, conn = Connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE email = (%s)", es(request.form['username']))

            data = c.fetchone()[3]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in']  = True
                session['email'] = request.form['username']

                return redirect(url_for("dash"))


            else:
                error = "Invalid Credentials. Try Again!"
                gc.collect()

                return render_template("index.html", error = error)




        return render_template("index.html", error = error)

    except Exception as e:
        # flash(e)
        error = "Invalid Credentials. Try Again!"
        return render_template("index.html", error = error)



# New Codes

@app.route('/filldetail', methods=['GET'])

def fillDetail():


      # email = request.form['email']
      #
      # # return 'Here'
      #
      # c, conn = Connection()
      #
      # c.execute("SELECT * FROM members WHERE email = (%s)", (es(email)))
      #
      # name = c.fetchall()[2]
      # lname = 'asdasd' #c.fetchone()[3]
      # doj = '2018-01-01' #c.fetchone()[7]

      nic = "951324844V"
      name = 'test'
      lname = 'test'
      doj = '2018-01-01'


      return render_template("insertDetails.html" , nic = nic , name = name , lname = lname , doj = doj )

@app.route('/savedetail', methods=['POST'])

def saveDetail():

    # return 'Yes'



    nic = request.form['nic']
    bodyWeight = request.form['weight']
    bodyHeight = request.form['height']
    bodyChest  = request.form['chest']
    bodyFat    = request.form['fat']

    times = time.time()
    ts = datetime.datetime.fromtimestamp(times).strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO memberprogress (nic,weight, height, chest ,fat ,updated) VALUES (%s, %s, %s ,%s, %s,%s)"

    val = (nic , bodyWeight ,bodyHeight ,bodyChest,bodyFat ,ts )

    mysql, conn = Connection()

    mysql.execute(sql,val)

    conn.commit()
    mysql.close()
    conn.close()
    gc.collect()

    return 'Ok Done'

@app.route('/myprogress', methods=['GET'])

def myProgress():

    return render_template("progress.html")

if __name__ == "__main__":
    app.run()
