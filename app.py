from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from flask import Flask, render_template, flash, request, url_for, redirect, session ,make_response,jsonify
from dbcon import Connection
from passlib.hash import sha256_crypt
from pymysql import escape_string as es

import gc
import time
import datetime

#FR Libs
from packages.preprocess import preprocesses
from packages.classifier import training


app = Flask(__name__)
app.secret_key = "super secret key"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
#NN initializations
TRAIN_FOLDER = './uploads/train/'
PRE_FOLDER = './uploads/pre/'
CLASSIFIER = './class/classifier.pkl'
MODEL_DIR = './model'



@app.route('/train/')
def train():
    print("Training Start")
    obj = training(PRE_FOLDER, MODEL_DIR, CLASSIFIER)
    get_file = obj.main_train()
    print('Saved classifier model to file "%s"' % get_file)
    return 'train end'


@app.route('/init/')
def init():
    obj = preprocesses(TRAIN_FOLDER, PRE_FOLDER)
    nrof_images_total, nrof_successfully_aligned = obj.collect_data()

    print('Total number of images: %d' % nrof_images_total)
    print('Number of successfully aligned images: %d' % nrof_successfully_aligned)
    return 'init align images'

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

                #saves user images

                target = os.path.join(APP_ROOT, 'uploads/'+nic)
                print(target)
                if not os.path.isdir(target):
                    os.mkdir(target)


                count = 0
                for file in request.files.getlist('img'):
                    print(file)
                    count = count + 1
                    filename = file.filename
                    print(filename)
                    destination = "/".join([target, filename])
                    print(destination)
                    file.save(destination)

                # ttt
                obj = preprocesses(TRAIN_FOLDER, PRE_FOLDER)
                nrof_images_total, nrof_successfully_aligned = obj.collect_data()

                print('Total number of images: %d' % nrof_images_total)
                print('Number of successfully aligned images: %d' % nrof_successfully_aligned)

                print("Training Start")
                obj = training(PRE_FOLDER, MODEL_DIR, CLASSIFIER)
                get_file = obj.main_train()
                print('Saved classifier model to file "%s"' % get_file)
                # tttt

                conn.commit()
                c.close()
                conn.close()
                gc.collect()

                return redirect(url_for("dash"))

        return render_template(render_template("register.html"))

    except Exception as e:
        return(str(e))




    return render_template("register.html")


#Checkin

@app.route('/checkin/')
def checkin():

    error = 'Please place Your face and press checkin'
    return render_template("checkin.html", error =error)

    #
    # email = "324324324V"  # Have to add request from username
    #
    # c, conn = Connection()
    #
    # c.execute("SELECT * FROM status WHERE email = (%s)", (es(email)))
    #
    # state = c.fetchone()[2]
    #
    # if state == False:
    #
    #  return redirect(url_for("dash"))
    #
    # else:


#Settings

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


# Login

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

                return render_template("register.html")


            else:
                error = "Invalid Credentials. Try Again!"
                gc.collect()

                return render_template("index.html", error = error)




        return render_template("index.html", error = error)

    except Exception as e:
        # flash(e)
        error = "Invalid Credentials. Try Again!"
        return render_template("index.html", error = error)


@app.route('/getfilldetail', methods=['POST'])

def getfillDetail():


    # nic = "324324324V" # Test

    nic = request.form['nic']

    out = []

    c, conn = Connection()

    c.execute("SELECT * FROM members WHERE nic = (%s)", (es(nic)))

    result = c.fetchall()


    for row in result:

        out.append({'name': row[2], 'lname': row[3]})

    conn.commit()
    c.close()
    conn.close()
    gc.collect()

    return jsonify(out=out)



@app.route('/filldetail', methods=['GET'])

def fillDetail():

    return render_template("insertDetails.html")



# Save Member Daily Details

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


# Getting Progress Route for Charts

@app.route('/getprogress', methods=['POST'])

def getProgress():

    #nic = "951324844V" #Test

    nic = request.form['nic']

    out =[]

    c, conn = Connection()

    c.execute("SELECT * FROM memberprogress WHERE nic = (%s)", (es(nic)))

    result = c.fetchall()

    for row in result:

        out.append({ 'weight' : row[1] , 'height' : row[2] , 'chest' : row[3] , 'fat' : row[4] , 'date' : row[6]})


    conn.commit()
    c.close()
    conn.close()
    gc.collect()

    return jsonify(out=out)

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    target = os.path.join(APP_ROOT, 'uploads/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)

    if request.method == 'POST':
        count = 0
        for file in request.files.getlist('img'):
            print(file)
            count = count + 1
            # filename = '00' + str(count) + '.png'
            filename = file.filename
            print(filename)
            destination = "/".join([target, filename])
            print(destination)
            file.save(destination)

        return "file uploaded"

    return "ooooooppppppssss"

if __name__ == "__main__":
    app.run()
