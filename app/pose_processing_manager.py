import json
import os, uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess
import time

class PoseProcessingManager:
    def __init__(self):
        self.secrets = json.load(open("secrets.json"))
        self.account_key = self.secrets.get("azure_account_key")
        self.account_name = self.secrets.get("azure_account_name")
        self.block_blob_service = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
    
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
        video_content = []
        print("Polling video")
        while not video_content:
            time.sleep(1)
            generator = self.block_blob_service.list_blobs("outputvideo")
            for b in generator:
                video_content.append(b)
        print("Getting data")
        for blob in data_content:
            full_path_to_file = os.path.join('./input_data', blob.name)
            self.block_blob_service.get_blob_to_path("outputdata", blob.name, full_path_to_file)
        # for blob in images_content:
        #     full_path_to_file = os.path.join('./input_images', blob.name)
        #     self.block_blob_service.get_blob_to_path("outputimages", blob.name, full_path_to_file)
        #     self.block_blob_service.delete_blob("outputimages", blob.name)
        print("Getting video")
        for blob in video_content:
            time.sleep(5)
            full_path_to_file = os.path.join('./input_video', blob.name)
            self.block_blob_service.get_blob_to_path("outputvideo", blob.name, full_path_to_file)

        print("Deleting data on azure")
        print(data_content)
        for blob in data_content:
            self.block_blob_service.delete_blob("outputdata", blob.name)
        print("Deleting video on azure")
        print(video_content)
        for blob in video_content:
            self.block_blob_service.delete_blob("outputvideo", blob.name)
            

if __name__ == "__main__":
    ppm = PoseProcessingManager()
    ppm.poll()