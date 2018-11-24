# -*- coding: utf-8 -*-
"""
Processes Form check and spits out image, video, and data.
"""

import subprocess
import os, uuid, sys, time
from azure.storage.blob import BlockBlobService, PublicAccess
import cv2

import weaknesses
from pose_processing_manager import PoseProcessingManager
from json_aggregator import JsonAggregator
from form_check import FormCheck

ACCOUNT_KEY = 'wVCBTMizVM705bh3SG/WCMCWkCeuwtrZ80fgqhAFXBE/RAa+6N8mk7FtramgAu2Bi/O8XL1jt3WS0N+mBZtObA=='
ACCOUNT_NAME = 'formcheck'

def processVid(vidname, block_blob_service):
    print("input_video/"+vidname+'.mp4')
    subprocess.call(["./bin/OpenPoseDemo.exe", "--video", "input_video/"+vidname+'.mp4', "--write_json", "output_data/", "--write_video", "output_video/"+vidname+".avi", "--keypoint_scale", "1", "--display", "0", '--number_people_max', '1'])
    
    process_output("input_video/"+vidname+'.mp4')
    
    cleanse_inputvid()
    #uploadOutput(vidname, block_blob_service)

def cleanse_inputvid():
    

def uploadOutput(vidname, block_blob_service):
    try:
        print('Deleting Existing outputdata...')
        input_container = 'outputdata'
        generator = block_blob_service.list_blobs(input_container)
        for blob in generator:
            block_blob_service.delete_blob(input_container, blob.name)

        container_name ='outputvideo'
        localpath = './output_video'
        for filename in os.listdir(localpath):
            full_path_to_file =os.path.join(localpath, filename)
            # Upload the created file, use local_file_name for the blob name
            block_blob_service.create_blob_from_path(container_name, filename, full_path_to_file)
            os.unlink(full_path_to_file)
        
#        container_name='outputimages'
#        localpath = './output_images'
#        for filename in os.listdir(localpath):
#            full_path_to_file =os.path.join(localpath, filename)
#            # Upload the created file, use local_file_name for the blob name
#            block_blob_service.create_blob_from_path(container_name, filename, full_path_to_file)
#            os.unlink(full_path_to_file)
        
                
        container_name='outputdata'
        localpath = './output_data'
        #lease_id = block_blob_service.acquire_container_lease(container_name, lease_duration=-1)
        for filename in os.listdir(localpath):
            full_path_to_file =os.path.join(localpath, filename)
            # Upload the created file, use local_file_name for the blob name
            block_blob_service.create_blob_from_path(container_name, filename, full_path_to_file)
            os.unlink(full_path_to_file)
        #block_blob_service.break_container_lease(container_name, lease_break_period=0)

    except Exception as e:
        print(e)


def process_output(vid_path):
    ja = JsonAggregator("ouput_data")
    ppm = PoseProcessingManager()
    height = 0
    width = 0

    vidcap = cv2.VideoCapture(vid_path)

    if vidcap.isOpened():
        width = vidcap.get(3)
        height = vidcap.get(4)

    fc = FormCheck(int(width), int(height))

    frames_dict = ja.get_new_data()

    lift_errors = fc.check_form(len(frames_dict[0]), frames_dict, exercise="SQUAT")
    print(lift_errors)


def main():
    input_container = 'inputvideo'
    block_blob_service = BlockBlobService(account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY)
    while(True):
        print('Waiting for input video...')
        generator = block_blob_service.list_blobs(input_container)

        for blob in generator:
            print('Input Video found, Processing Input Video...')
            full_path_to_file = os.path.join('./input_video',blob.name)
            block_blob_service.get_blob_to_path(input_container, blob.name, full_path_to_file)
            vid_name = blob.name[0:-4]
            processVid(vid_name, block_blob_service)
            os.unlink(full_path_to_file)
            block_blob_service.delete_blob(input_container, blob.name)
            print('Input Video Processing Finished.')
        time.sleep(1)
        
if __name__ == '__main__':
    main()