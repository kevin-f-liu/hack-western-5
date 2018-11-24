import glob
import json

class JsonAggregator:
    def __init__(self, subdirectory):
        self.subdirectory = subdirectory
        self.files = None
        self.raw_keypoints = []

    def get_new_data(self, subdirectory=None):
        if subdirectory:
            self.subdirectory = subdirectory
        self.raw_keypoints = []
        self.fetch_raw_keypoints()

        keypoint_dict = {}
        for frame in self.raw_keypoints:
            for i in range(0, len(frame), 3):
                if keypoint_dict.get(int(i/3)):
                    keypoint_dict[int(i/3)].append([frame[i], frame[i+1]])
                else:
                    keypoint_dict[int(i/3)] = [[frame[i], frame[i+1]]]

        return keypoint_dict
        

    def fetch_raw_keypoints(self):
        self.pull_files()
        for f in self.files:
            file = json.load(open(f))
            self.raw_keypoints.append(file['people'][0]["pose_keypoints_2d"])
    
    def pull_files(self):
        self.files = [f for f in glob.glob("%s/*.json" % self.subdirectory)]


if __name__ == "__main__":
    ja = JsonAggregator("output_data")
    frame_dict = ja.get_new_data()

    from form_check import FormCheck

    fc = FormCheck(579, 837)
    fc.check_form(6, frame_dict, exercise="SQUAT")
