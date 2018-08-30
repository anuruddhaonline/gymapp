from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
from flask import Flask, render_template, flash, request, url_for, redirect, session, make_response, jsonify
from dbcon import Connection
from passlib.hash import sha256_crypt, md5_crypt
from pymysql import escape_string as es

import gc
import time
import datetime

# FR Libs
from packages.preprocess import preprocesses
from packages.classifier import training
import pickle
import time
import cv2
import numpy as np
import tensorflow as tf
from scipy import misc
from packages import facenet, detect_face

app = Flask(__name__)
app.secret_key = "super secret key"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# NN initializations
TRAIN_FOLDER = './uploads/train/'
TEST_FOLDER = './uploads/test/'
PRE_FOLDER = './uploads/pre/'
CLASSIFIER = './class/classifier.pkl'
MODEL_DIR = './model'
npy = ''


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

@app.route('/recognize/')
def recognize(filename="img.png"):
    image_path = TEST_FOLDER + filename
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, npy)

            minsize = 20  # minimum size of face
            threshold = [0.6, 0.6, 0.6]  # three steps's threshold
            factor = 0.709  # scale factor
            frame_interval = 3
            image_size = 182
            input_image_size = 160

            HumanNames = os.listdir(TRAIN_FOLDER)
            HumanNames.sort()

            print('Loading feature extraction model')
            facenet.load_model(MODEL_DIR)

            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]

            classifier_filename_exp = os.path.expanduser(CLASSIFIER)
            with open(classifier_filename_exp, 'rb') as infile:
                (model, class_names) = pickle.load(infile)

            c = 0

            print('Start Recognition!')
            frame = cv2.imread(image_path, 0)

            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # resize frame (optional)

            timeF = frame_interval

            if (c % timeF == 0):

                if frame.ndim == 2:
                    frame = facenet.to_rgb(frame)
                frame = frame[:, :, 0:3]
                bounding_boxes, _ = detect_face.detect_face(frame, minsize, pnet, rnet, onet, threshold, factor)
                nrof_faces = bounding_boxes.shape[0]
                print('Face Detected: %d' % nrof_faces)

                if nrof_faces > 0:
                    det = bounding_boxes[:, 0:4]

                    cropped = []
                    scaled = []
                    scaled_reshape = []
                    bb = np.zeros((nrof_faces, 4), dtype=np.int32)

                    for i in range(nrof_faces):
                        emb_array = np.zeros((1, embedding_size))

                        bb[i][0] = det[i][0]
                        bb[i][1] = det[i][1]
                        bb[i][2] = det[i][2]
                        bb[i][3] = det[i][3]

                        # inner exception
                        if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
                            print('face is too close')
                            continue

                        cropped.append(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
                        cropped[i] = facenet.flip(cropped[i], False)
                        scaled.append(misc.imresize(cropped[i], (image_size, image_size), interp='bilinear'))
                        scaled[i] = cv2.resize(scaled[i], (input_image_size, input_image_size),
                                               interpolation=cv2.INTER_CUBIC)
                        scaled[i] = facenet.prewhiten(scaled[i])
                        scaled_reshape.append(scaled[i].reshape(-1, input_image_size, input_image_size, 3))
                        feed_dict = {images_placeholder: scaled_reshape[i], phase_train_placeholder: False}
                        emb_array[0, :] = sess.run(embeddings, feed_dict=feed_dict)
                        # print("emb_array",emb_array)
                        predictions = model.predict_proba(emb_array)
                        print("Predictions ", predictions)
                        best_class_indices = np.argmax(predictions, axis=1)
                        best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                        print("Best Predictions ", best_class_probabilities)

                        if best_class_probabilities[0] > 0.6:
                            print('Result Indices: ', best_class_indices[0])
                            print(HumanNames)
                            for H_i in HumanNames:
                                # print(H_i)
                                if HumanNames[best_class_indices[0]] == H_i:
                                    result_names = HumanNames[best_class_indices[0]]
                                    print("Face Recognized: ", result_names)
                                    return str(result_names)
                        else:
                            print('Not Recognized')
                            return False
                else:
                    print('Unable to align')
                    return False

    return False

def random_name():
    name = md5_crypt.encrypt(str(time.time())).split("$")[2]
    return name

@app.route('/authenticateuser/', methods=['POST'])
def authenticateUser():

    target = os.path.join(APP_ROOT, 'uploads/test/')
    if not os.path.isdir(target):
        os.mkdir(target)

    filename = random_name() + ".png"
    destination = "/".join([target, filename])

    for file in request.files.getlist('img'):
        print(filename)
        file.save(destination)

    result = recognize(filename)
    os.remove(destination)

    return 'test'


@app.route('/dash/', methods=['GET', 'POST'])
def dash():

    error = ''
    try:
        if request.method == "POST":

            nic = request.form.get('nic')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            email = request.form.get('email')
            mobile = request.form.get('mobile')
            dob = request.form.get('dob')
            weight = request.form.get('weight')
            height = request.form.get('height')
            chest = request.form.get('chest')
            password = sha256_crypt.encrypt((str(request.form.get('password'))))
            print("here")

            c, conn = Connection()


            print('nic',nic)


            x = c.execute("SELECT * FROM members WHERE nic = (%s)", (es(nic)))

            print('user x', x)


            if int(x) > 0:
                error = "already exists"
                return jsonify(error=error)

            else:

                c.execute(
                    "INSERT INTO members (nic, fname, lname, email, mobile, dob, weight, height, chest, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (es(nic), es(fname), es(lname), es(email), es(mobile), es(dob), es(weight), es(height), es(chest),
                     es(password)))

                # saves user images

                target = os.path.join(APP_ROOT, 'uploads/train/' + nic)
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



                return jsonify(sucess="Registration success", value=True)

        return render_template(render_template("register.html"))

    except Exception as e:
        return str(e)

    return render_template(render_template("register.html"))


# Checkin

@app.route('/checkin/')
def checkin():
    error = 'Please place Your face and press checkin'
    return render_template("checkin.html", error=error)

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


# Settings

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

    return render_template("settings.html", error=error)


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
                session['logged_in'] = True
                session['email'] = request.form['username']

                return render_template("register.html")


            else:
                error = "Invalid Credentials. Try Again!"
                gc.collect()

                return render_template("index.html", error=error)

        return render_template("index.html", error=error)

    except Exception as e:
        # flash(e)
        error = "Invalid Credentials. Try Again!"
        return render_template("index.html", error=error)


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


@app.route('/filldetail/', methods=['GET'])
def fillDetail():
    return render_template("insertDetails.html")


# Save Member Daily Details

@app.route('/savedetail', methods=['POST'])
def saveDetail():
    # return 'Yes'

    nic = request.form['nic']
    bodyWeight = request.form['weight']
    bodyHeight = request.form['height']
    bodyChest = request.form['chest']
    bodyFat = request.form['fat']

    times = time.time()
    ts = datetime.datetime.fromtimestamp(times).strftime('%Y-%m-%d %H:%M:%S')

    sql = "INSERT INTO memberprogress (nic,weight, height, chest ,fat ,updated) VALUES (%s, %s, %s ,%s, %s,%s)"

    val = (nic, bodyWeight, bodyHeight, bodyChest, bodyFat, ts)

    mysql, conn = Connection()

    mysql.execute(sql, val)

    conn.commit()
    mysql.close()
    conn.close()
    gc.collect()

    return 'Ok Done'


# Getting Progress Route for Charts

@app.route('/getprogress', methods=['POST'])
def getProgress():
    # nic = "951324844V" #Test

    nic = request.form['nic']

    out = []

    c, conn = Connection()

    c.execute("SELECT * FROM memberprogress WHERE nic = (%s)", (es(nic)))

    result = c.fetchall()

    for row in result:
        out.append({'weight': row[1], 'height': row[2], 'chest': row[3], 'fat': row[4], 'date': row[6]})

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
