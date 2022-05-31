import os
from flask import Flask, render_template, send_from_directory, redirect, url_for, request, Response
from werkzeug.utils import secure_filename
import subprocess
import cv2

app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'mp4'])
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['STATIC_FOLDER'] = 'static/'

camera = cv2.VideoCapture(0)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET','POST'])
def predict():
    file = request.files['file']
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
    print(file)
    subprocess.run("ls")
    subprocess.run(['python', 'detect.py', '--source', os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))], shell=True)
    return redirect(url_for('download_file', name=file.filename))

@app.route('/static/<name>')
def download_file(name):
    return send_from_directory(app.config['STATIC_FOLDER'], name)

def gen_frames():
    while True:
        subprocess.run(['python', 'detect.py', '--source', '0'], shell=True)
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/livestream')
def livestream():
    return render_template('livestream.html')

@app.route('/video_feed')
def video_feed():
	return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')