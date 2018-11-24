import hashlib
import cv2
# import pdfkit
import os

# from flask_mail import Mail, Message

import weaknesses
from pose_processing_manager import PoseProcessingManager
from json_aggregator import JsonAggregator
from form_check import FormCheck
import os

analyzed_video = ""
for filename in os.listdir("input_video"):
    analyzed_video = os.path.join("input_video", filename)
    print("GOT THE VIDEO ANALYZED %s" % analyzed_video)

vidcap = cv2.VideoCapture(analyzed_video)
success,image = vidcap.read()
count = 0

while success:  
    success,image = vidcap.read()
    if count % 25 == 0:
        cv2.imwrite("./static/" + "asdfasdfasdf" + "frame%d.jpg" % int(count / 25), image)

    count += 1