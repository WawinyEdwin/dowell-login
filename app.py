import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template,flash, redirect, url_for, request, session
import uuid
from functools import wraps

IMAGE_FOLDER = './selfies'
VOICE_FOLDER = './voices'

app = Flask(__name__, template_folder='templates')

#secret key to sign our session
app.secret_key = 'sometimesiwrite'

app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['VOICE_FOLDER'] = VOICE_FOLDER

#  Language detection.
def languageDetection(word):
    try:
        if not word:
            return {
                "message": "String is empty or invalid",
                "success": False,
                "input_string": word
            }
        if len(word) == 0:
            return {
                "message": "String is empty or invalid",
                "success": False,
                "input_string": word
            }
        if not re.search('[a-zA-Z]', word):
            return {
                "message": "String invalid characters",
                "success": False,
                "input_string": word
            }
        detector = google_translator()
        return_data = list()
        language_list = []
        for item in word.split(' '):
            detect_result = detector.detect(item)
            print(detect_result)
            return_data.append(
                {
                    "input_string": item,
                    "short_form": detect_result[0],
                    "long_form": detect_result[1]
                }
            )
            language_list.append(detect_result[0])

        return {
            "data": return_data,
            "success": True,
            "input_string": word,
            "same_language": len(set(language_list)) == 1
        }
    except Exception as e:
        print(e)
        return {
            "message": "String is empty or invalid",
            "success": False
        }
    return 

#We protect our dshaboard Route
def ensure_logged_in(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('id'):
            flash("Unauthorised, please login")
            return redirect(url_for('dowelllogin'))
        return fn(*args, **kwargs)
    return wrapper

#Index Page
@app.route('/')
def index():
    return render_template('index.html')

#Protected Dashboard.
@app.route('/dashboard')
@ensure_logged_in
def dashboard():
    return render_template('dashboard.html')

# Login Validation and user authentication.
@app.route('/login', methods=['GET', 'POST'])
def dowelllogin():

    #Language to choose.
    languages = ['English', 'Swahili', 'Spanish', 'Latin' , 'Greek']
    
    # validate request params
    if request.method == 'POST':
        language = request.form.get('language')

        #ids for the laguages
        if languages == 'English':
            eng_Id = uuid.uuid4()
        elif languages == 'Swahili':
            sw_Id = uuid.uuid4()
        elif languages == 'Spanish':
            span_Id = uuid.uuid4()
        elif languages == 'Latin':
            lat_Id = uuid.uuid4()
        else:
            print("Invalid")

        #login-credentials
        user_name = request.form.get('user_name')
        
        password = request.form.get('password')

        #get voice from request
        voice = request.files['voice']

        #get selfies from request.
        selfie = request.files['selfie']

        #if we have voice in request.
        if voice:
            voice = request.files['voice']
            voice_name = secure_filename(voice.filename)
            voice.save(voice_name)
            dowellvoiceID(voice_name)

        #if we have the selfie in request.
        if selfie:
            # Handle the selfie
            selfie_name = secure_filename(selfie.filename)
            selfie.save(selfie_name)
            dowellfaceID(selfie_name)

        # Check login credentials and sign the session
        if user_name == 'test' and password == 'passw':

            languageDetection(user_name)

            #check rights for projects
            if(dowellconnection() == True):
                # Initialize a user session
                session['Loggedin'] = True
                session['id'] = 1
                session['user_name'] = user_name
                # session['language'] = 

                flash("Authenticated")
                return redirect(url_for('dashboard'))
            else: #rights not available?

                flash("Rights not set, contact admin")
                return
        else:
            flash("Wrong, credentials, Retry or contact admin.")
            return redirect(url_for('dowelllogin'))  
    else:
        return render_template('login.html', languages = languages)

# Check assigned user rights.
def dowellconnection():

    rights = ['locationRight' , 'connectivityRight', 'deviceRight', 'osRight', 'roleRight',  'crudRight']

    if rights:
        allow = True
    
    else:
        allow = False

    return allow

#generate faceID from the selfie image
def dowellfaceID(selfie):

    id = uuid.uuid4()

    faceID =  str(id) + selfie

    return faceID

#generate voiceID from the voice recording
def dowellvoiceID(voice):

    id = uuid.uuid4()

    voiceID = str(id) + voice  


    return voiceID


@app.route('/logout')
def logout():
     # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have signed Out')
    
    # Redirect to login page
    return redirect(url_for('dowelllogin'))


# Error Pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500