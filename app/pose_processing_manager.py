import json
import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess
import time
from io import BytesIO, StringIO
from firebase_worker import FirebaseWorker

class PoseProcessingManager:
    def __init__(self):
        self.secrets = json.load(open("secrets.json"))
        self.account_key = self.secrets.get("azure_account_key")
        self.account_name = self.secrets.get("azure_account_name")
        self.block_blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        self.fw = FirebaseWorker()

    def send_stream(self, filename, file):
        """
        Send video file stream
        """
        self.block_blob_service.create_blob_from_stream("inputvideo", filename, file)
    
    def send(self, localpath):
        """
        Send a video file, 
        """
        for filename in os.listdir(localpath):
            print("Sending %s" % filename)
            full_path_to_file = os.path.join(localpath, filename)            
            self.block_blob_service.create_blob_from_path("inputvideo", filename, full_path_to_file)
    
    def poll(self):
        """
        Returns after successfully polling for data in azure
        """
        data_content = []
        print("Polling data")
        while not data_content:
            time.sleep(1)
            generator = self.block_blob_service.list_blobs("outputdata")
            for b in generator:
                data_content.append(b)
        images_content = []
        # print("Polling images")
        # while not images_content:
        #     time.sleep(1)
        #     generator = self.block_blob_service.list_blobs("outputimages")
        #     for b in generator:
        #         images_content.append(b)
        video_content = [] # All video files, last one is most recent
        print("Polling video")
        while not video_content:
            time.sleep(1)
            generator = self.block_blob_service.list_blobs("outputvideo")
            for b in generator:
                video_content.append(b)
        
        return (data_content, video_content[-1])

    def transfer_processed_data(self, data_content):
        # Get all the processed data json, delete, and save somewhere
        # Get filename of the processed video
        print("Getting data")
        for blob in data_content:
            with BytesIO() as input_blob:
                self.block_blob_service.get_blob_to_stream("outputdata", blob.name, input_blob) # get it to stream
                myjson = json.loads(input_blob.getvalue().decode("utf-8"))
            self.fw.add_list('data/historical', myjson)
            self.fw.add('data/report', myjson)

        # for blob in images_content:
        #     full_path_to_file = os.path.join('./input_images', blob.name)
        #     self.block_blob_service.get_blob_to_path("outputimages", blob.name, full_path_to_file)
        #     self.block_blob_service.delete_blob("outputimages", blob.name)
        # print("Getting video")
        # for blob in video_content:
        #     time.sleep(5)
        #     full_path_to_file = os.path.join('./input_video', blob.name)
        #     self.block_blob_service.get_blob_to_path("outputvideo", blob.name, full_path_to_file)

        print("Deleting data on azure")
        for blob in data_content:
            self.block_blob_service.delete_blob("outputdata", blob.name)

        # print("Deleting video on azure")
        # print(video_content)
        # for blob in video_content:
        #     self.block_blob_service.delete_blob("outputvideo", blob.name)

    def transfer_latest_video_ref(self, video_content):
        self.fw.add('data', {'processed_video': video_content.name})


if __name__ == "__main__":
    ppm = PoseProcessingManager()
    [data, vid] = ppm.poll()
    ppm.transfer_processed_data(data)
    ppm.transfer_latest_video_ref(vid)