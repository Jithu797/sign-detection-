import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from flask import Flask, request, render_template, jsonify,session,redirect,g,url_for
import os
import os
import pyrebase
from flask import Flask, request, jsonify, redirect, render_template, session, abort
from datetime import timedelta
from firebase_admin import credentials, firestore, initialize_app, auth
from firebase_admin import credentials

cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
app = Flask(__name__, static_folder='static')

config = {
  "apiKey": "AIzaSyD3v0bEZOm6Kb8EQsd_lUk3lNwhMQmICKU",
  "authDomain": "neurovision-6c4d4.firebaseapp.com",
  "projectId": "neurovision-6c4d4",
  "storageBucket": "neurovision-6c4d4.appspot.com",
  "messagingSenderId": "884617802430",
  "appId": "1:884617802430:web:1d329716f746635dad64ef",
  "measurementId": "G-0X7R4TRKY2",
  "databaseURL": ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
app.secret_key = "secret"

# model = load_model("VGG19-eye_disease-95.73.h5", compile=False)


users = {'username': 'password', 'user2': 'password2'}
@app.route('/', methods=['GET', 'POST'])
def landing():
    return render_template('landing.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html',msg="")


@app.route('/aboutus', methods=['GET', 'POST'])
def aboutus():
    return render_template('aboutus.html')

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    return render_template('contactus.html')

@app.route('/diseases', methods=['GET', 'POST'])
def diseases():
    return render_template('diseases.html')

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form['user_name']
        email = request.form['email']
        dateofbirth = request.form['dateofbirth']
        password = request.form['password']
        print(user_name)
        db = firestore.client()
        # Specify the 'users' collection
        users_ref = db.collection('users')
        # Check if the user already exists in the database
        user_doc = users_ref.document(email).get()
        if not user_doc.exists:
            # If the user doesn't exist, insert new data
            user_data = {
                'user_name': user_name,
                'email': email,
                'dateofbirth': dateofbirth,
                'password' :password,
            }
            # Add the user data to the document
            users_ref.document(email).set(user_data)
            return render_template('index.html')
        else:
            return render_template('signup.html',msg="")
    else:
        return "baba"

@app.route('/sign_in', methods=['POST','GET'])
def sign_in():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = firestore.client()
        # Specify the 'users' collection
        users_ref = db.collection('users')
        # Check if the user already exists in the database
        user_doc = users_ref.document(email).get()
        if user_doc.exists:
            existing_data =user_doc.to_dict()
            user_id_dict = existing_data.get('password')
            print(user_id_dict)
            if user_id_dict==password:
            # return jsonify({"password":pwd})
                return render_template('index.html')
            else:
                return render_template('signup.html',msg="password didn't matched")
        else:
            return render_template('signup.html',msg="Doesn't Account ? Please SignUp")


# @app.route('/mee', methods=['GET', 'POST'])
# def index():
#     if 'username' in session:
#         return redirect(url_for('protected'))

#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         if username in users and users[username] == password:
#             session['username'] = username
#             return redirect(url_for('protected'))

#     return render_template('login.html')

# @app.route('/protected')
# def protected():
#     if 'username' in session:
#         return render_template('home.html', user=session['username'])
#     return redirect(url_for('login'))
@app.route('/login.html')
def login():
        return render_template('login.html')

@app.route('/index.html')
def indexing():
        return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['image']
        print("current path")
        basepath = os.path.dirname(__file__)
        print("current path", basepath)
        filepath = os.path.join(basepath, 'uploads', f.filename)
        print("upload folder is ", filepath)
        f.save(filepath)

        img = image.load_img(filepath, target_size=(64, 64))
        img = image.load_img(filepath, target_size=(224, 224))

        x = image.img_to_array(img)
        print(x)
        x = np.expand_dims(x, axis=0)
        print(x)
        y = model.predict(x)
        preds = np.argmax(y, axis=1)
        print("prediction", preds)

        index = ['Cataract', 'diabetic_retinopathy', 'Glaucoma','Normal']
        prediction_result = index[preds[0]]

        if prediction_result == 'Normal':
            text = "<b>You have normal vision.<b>"
        elif prediction_result == 'Cataract':
            text = '''<b>You have <i>Cataract</i>. Consult with an eye specialist for further evaluation.</b>
            <br><br>
            Cataracts are a common eye condition that can affect people of all ages, but they are most commonly associated with aging. Cataracts occur when the lens of the eye becomes cloudy, causing blurred vision and other visual problems. Here is some information to help raise awareness about cataracts:
            <br><br>
            <b><u>Treatment:</u></b> The primary treatment for cataracts is surgery. Cataract surgery is a highly successful and safe procedure in which the cloudy lens is removed and replaced with an artificial intraocular lens (IOL). This surgery can significantly improve vision and quality of life.
            <br><br>
            <b><u>Prevention:</u></b> While cataracts are often associated with aging and genetic factors, you can take steps to reduce your risk. These include protecting your eyes from excessive sunlight, not smoking, managing chronic conditions like diabetes, and maintaining a healthy diet rich in antioxidants.
            '''
        elif prediction_result == 'diabetic_retinopathy':
            text = '''<b>You may have <i>Diabetic Retinopathy</i>. It is recommended to consult with an eye specialist.</b>
            <br><br>
            Diabetic retinopathy is a serious eye condition that affects people with diabetes, primarily those who have had the disease for a long time or have poorly managed their blood sugar levels. It can lead to vision impairment and even blindness if not properly diagnosed and treated. Here is some information to raise awareness about diabetic retinopathy:
            <br><br>
            <b><u>Treatment:</u></b> Treatment options for diabetic retinopathy depend on the stage and severity of the disease. They can include laser therapy to seal leaking blood vessels, medications injected into the eye, and surgery to remove blood from the vitreous gel. Effective management of diabetes through blood sugar control and other health measures is also essential to slow or prevent the progression of diabetic retinopathy.
            <br><br>
            <b><u>Prevention and awareness:</u></b> Raising awareness about diabetic retinopathy is crucial, as early detection and management are key to preserving vision. People with diabetes should be educated about the importance of regular eye exams and good diabetes management to reduce the risk of diabetic retinopathy.
            '''
        elif prediction_result == 'Glaucoma':
            text = '''<b>You may have <i>Glaucoma</i>. Please consult with an eye specialist for further evaluation.</b>
            <br><br>
            Glaucoma is a group of eye conditions that can cause damage to the optic nerve, leading to vision loss and, if left untreated, even blindness. It is often associated with increased intraocular pressure (IOP), but it can also occur with normal or low IOP. Here's some information to raise awareness about glaucoma:
            <br><br>
            <b><u>Treatment:</u></b> While glaucoma is not curable, it can be managed effectively to prevent further vision loss. Treatment options may include:
            <br>
            - Prescription eye drops to reduce IOP.
            - Oral medications.
            - Laser therapy (laser trabeculoplasty or iridotomy).
            - Surgical procedures (trabeculectomy or implantation of drainage devices).
            <br><br>
            <b><u>Prevention and Awareness:</u></b> Early detection is key to managing glaucoma. Regular eye check-ups, especially for those with risk factors like family history of the disease, are important. Raising awareness about the importance of routine eye exams is crucial in preventing vision loss from glaucoma.
            '''
        else:
            text = "<b>Unable to determine the eye condition.</b>"

        return jsonify({'result': text})
        # return    

if __name__ == '__main__':
    app.run(debug=False, threaded=False)
