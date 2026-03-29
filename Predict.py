from flask import Flask, render_template, flash, request, session
import mysql.connector

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from keras.applications.xception import preprocess_input

import warnings
import os
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

model = load_model("Xception.h5")

# Image size
img_width = 200
img_height = 200

# Class names (change according to your dataset folders)
classes = ["COVID19", "NORMAL", "PNEUMONIA", "Tuberculosis",]


@app.route("/")
def homepage():
    return render_template('index.html')


@app.route("/Home")
def Home():
    return render_template('index.html')


@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')


@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')


@app.route("/AdminHome")
def AdminHome():
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb ")
            data = cur.fetchall()
            flash("Login successfully")
            return render_template('AdminHome.html', data=data)

        else:
            flash("UserName Or Password Incorrect!")
            return render_template('AdminLogin.html')


@app.route("/AURemove")
def AURemove():
    id = request.args.get('id')
    conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
    cursor = conn.cursor()
    cursor.execute(
        "delete from regtb where id='" + id + "'")
    conn.commit()
    conn.close()

    flash('User  info Remove Successfully!')

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb  ")
    data = cur.fetchall()
    return render_template('AdminHome.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']

        email = request.form['email']

        address = request.form['address']

        uname = request.form['uname']
        password = request.form['password']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO regtb VALUES ('','" + name + "','" + email + "','" + mobile + "','" + address + "','" + uname + "','" + password + "')")
        conn.commit()
        conn.close()
        flash('User Register successfully')

    return render_template('UserLogin.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = request.form['uname']

        conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username='" + username + "' and Password='" + password + "'")
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('UserLogin.html')
        else:

            conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username='" + username + "' and Password='" + password + "'")
            data = cur.fetchall()
            flash("Login successfully")

            return render_template('UserHome.html', data=data)


@app.route("/UserHome")
def UserHome():
    uname = session['uname']

    conn = mysql.connector.connect(user='root', password='', host='localhost', database='lungdb')
    # cursor = conn.cursor()
    cur = conn.cursor()
    cur.execute("SELECT * FROM  regtb where username='" + uname + "'  ")
    data = cur.fetchall()
    return render_template('UserHome.html', data=data)




@app.route("/Predict")
def Predict():
    return render_template('Predict.html')


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        import tensorflow as tf



        if 'file' not in request.files:
            return "No file uploaded"

        file = request.files['file']
        file.save('static/upload/Test.jpg')
        fname = 'static/upload/Test.jpg'

        # Load image
        img = image.load_img(fname, target_size=(img_width, img_height))
        img = image.img_to_array(img)

        img = preprocess_input(img)

        img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)[0]
    confidence = np.max(prediction)
    sorted_pred = np.sort(prediction)
    second = sorted_pred[-2]
    print("Prediction:", prediction)
    print("Confidence:", confidence)
    print("Second:", second)

    # Check if valid image

    if confidence < 0.99 or (confidence - second) < 0.5:
        out = "Invalid Image (Not Lung X-ray)"
        pre = " "

    else:
        pred_class = classes[np.argmax(prediction)]

        if pred_class == "COVID19":
            out = "Covid"
            pre = "Ivermectin, Hydroxychloroquine"

        elif pred_class == "NORMAL":
            out = "Normal"
            pre = " "

        elif pred_class == "PNEUMONIA":
            out = "Pneumonia"
            pre = "levofloxacin, clarithromycin"

        elif pred_class == "Tuberculosis":
            out = "Tuberculosis"
            pre = "isoniazid / pyrazinamide / rifampin"

    return render_template('Predict.html', pre=pre, result=out, org=fname, conf=confidence)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)


