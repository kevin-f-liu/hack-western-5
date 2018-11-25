
from flask import Flask, render_template, request, redirect, make_response, jsonify
from flask_cors import CORS
from werkzeug import secure_filename
import hashlib
# import cv2
# import pdfkit
import os

# from flask_mail import Mail, Message

import cloudstorage as gcs

import weaknesses
from pose_processing_manager import PoseProcessingManager
from json_aggregator import JsonAggregator
from form_check import FormCheck
from firebase_worker import FirebaseWorker

app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})
# mail = Mail(app)

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


# @app.route('/', methods = ['GET', 'POST'])
# def upload_file():
#     if request.method == "POST":
#         return redirect("/uploader")
#     # Delete everything
#     for filename in os.listdir("input_video"):
#         full_path_to_file = os.path.join('./input_video', filename)
#         os.unlink(full_path_to_file)
#     for filename in os.listdir("input_data"):
#         full_path_to_file = os.path.join('./input_data', filename)
#         os.unlink(full_path_to_file)
#     for filename in os.listdir("output_video"):
#         full_path_to_file = os.path.join('./output_video', filename)
#         os.unlink(full_path_to_file)
#     return render_template('index.html')

# get tips from data base
def tips_for_exercises(errors):
    tips = []
    failures = []
    good_lift = ""
    for somestring in errors:
        somestring = somestring.lower()
        if "weak" in somestring: 
            tips = []
            new_string = somestring[somestring.find("weak"):]
            if len(new_string) > 0:
                for exercise in weaknesses.weaknesses.keys():
                    for bodypart in weaknesses.weaknesses[exercise].keys():
                        if new_string.find(bodypart) > 0:
                            tips.append({bodypart: weaknesses.weaknesses[exercise][bodypart]})
        if "no" in somestring: 
            failures = []
            new_string = somestring[somestring.find("no"):]
            if len(new_string) > 0:
                for e in weaknesses.failures.keys():
                    if new_string.find(e) > 0:
                        failures.append([e, weaknesses.failures[e]])
        if "good" in somestring: 
            new_string = somestring[somestring.find("good"):]
            good_lift = ""
            if len(new_string) > 0:
                for g in weaknesses.good_lifts.keys():
                    if new_string.find(g) > 0:
                        good_lift = weaknesses.good_lifts[g]
    return tips, failures, good_lift

def transfer_results(ppm):
    """
    Poll for completed data then pull it and store it into database of user
    """
    fw = FirebaseWorker()

    [data_content, video_content] = ppm.poll()
    ppm.transfer_processed_data(data_content)
    ppm.transfer_latest_video_ref(video_content)
    fw.add('', {'state': 2})

@app.route('/uploader', methods = ['GET', 'POST'])
def uploaded_file():
    print("UPLOAD REQUEST")
    if request.method == 'POST':
     
        f = request.files['file']
        print("GOT A FILE!")
        fw = FirebaseWorker()
        fw.add('', {'state': 1})
        video = f.filename
        if video:
            video_hash = str(int(hashlib.sha1(str(video).encode()).hexdigest(), 16) % (10 ** 8))
            vid_path = os.path.join("output_video", video)
            #f.save(vid_path)
            #select_value = request.form.get('select_value')
            #vidcap = cv2.VideoCapture(vid_path)

            # width = 0
            # height = 0
            #if vidcap.isOpened():
            #    width = vidcap.get(3)
            #    height = vidcap.get(4)

            # ja = JsonAggregator("input_data")
            ppm = PoseProcessingManager()
            # fc = FormCheck(int(width), int(height))

            ppm.send_stream(video, f)
            
            transfer_results(ppm)

            # analyzed_video = ""
            # for filename in os.listdir("input_video"):
            #     analyzed_video = os.path.join("input_video", filename)
            #     print("GOT THE VIDEO ANALYZED %s" % analyzed_video)

            # frames_dict = ja.get_new_data()

            #lift_errors = fc.check_form(len(frames_dict[0]), frames_dict, exercise=select_value)
            #print(lift_errors)
            
            #vidcap = cv2.VideoCapture(analyzed_video)
            #success,image = vidcap.read()
            # count = 0

            #while success:  
            #    success,image = vidcap.read()
            #    if count % 10 == 0:
            #        cv2.imwrite("./static/" + video_hash + "frame%d.jpg" % int(count / 10), image)

            #    count += 1
            
            #tips, failures, good_lift = tips_for_exercises(lift_errors)

            #return render_template('upload.html', video=video_hash, select_value=select_value, count=count, tips=tips, failures=failures, good_lift=good_lift)

    return render_template('index.html', error="Please Submit A File!")

@app.route('/report', methods = ['GET'])
def get_report():
    """
    Returns the report json from Firebase if available, otherwise return dummy
    """
    fw = FirebaseWorker()
    state = fw.get('state')
    #print(request.args)
    if request.args.get('ready-check'):
        # state is processing when 1
        return jsonify(state == 1)

    elif request.args.get('data-request'):
        # state is 2 when done
        if state == 2:
            data_json = fw.get("data/report")
            return jsonify(data_json)
        else:
            return jsonify(False)
    return jsonify(-1)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
