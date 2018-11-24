import numpy as np
import vector_helper as vh
import math

from data_processors.squat_data_processor import process_squat_data

class FormCheck:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.orientation = None
        self.exercises = {
            "LUNGE": self.check_squat,
            "DEADLIFT": self.check_deadlift,
            "BENCH": self.check_bench
        }

    def check_form(self, frames, data, exercise=None):
        """
        data: dict with keys based on https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/output.md
              Each key maps to a list of positions (x, y)
        """
        if not exercise:
            # TODO predict exercise from timeseries data
            return
        data = self.normalize_data(frames, data)
        return self.exercises[exercise](frames, data)
    
    def normalize_data(self, frames, data):
        """ Return data that is reasonably oriented, and so the person is facing the right way."""
        # Find orientation with neck and mid hips
        num_samples = 3
        avg_neck_x = sum([val[0] for val in data[1][:num_samples]]) / num_samples
        avg_hip_x = sum([val[0] for val in data[8][:num_samples]]) / num_samples

        if avg_neck_x > avg_hip_x:
            # Facing right
            self.orientation = "r"
            for key, time_list in data.items():
                for datum in time_list:
                    datum[1] = self.height - datum[1] - 1
        else:
            # Facing Left. Invert
            self.orientation = "l"
            for key, time_list in data.items():
                for datum in time_list:
                    datum[1] = self.height - datum[1] - 1
                    datum[0] = self.width - datum[0] - 1
        return data

    def check_squat(self, frames, data):
        """
        Major data points:
        {1,  "Neck"},
        {8,  "MidHip"},
        {9,  "RHip"},
        {10, "RKnee"},
        {11, "RAnkle"},
        {12, "LHip"},
        {13, "LKnee"},
        {14, "LAnkle"},
        """
        important_anatomy_features, \
        important_anatomy_joints, \
        joint_first_angular_derivatives,\
        joint_second_angular_derivatives = process_squat_data(frames, data)
        lift_errors = []
        # Find bottom out frame
        hip_y_vals = [coor[1] for coor in data[8]]
        lowest_hip = min(hip_y_vals)
        lowest_hip_frame = hip_y_vals.index(lowest_hip)
        depth_tol = 5
        if lowest_hip > min([data[10][lowest_hip_frame][1], data[13][lowest_hip_frame][1]]) + depth_tol:
            lift_errors.append("NODEPTH")
            lift_errors.append("WEAKQUADS") 

        # Check rate of acceleration after bottom out
        # Use average of second derivatives
        tolerance = 5
        avg_rising_sd = 10* sum(joint_second_angular_derivatives["leg-back"][(lowest_hip_frame + 1):]) / (len(joint_second_angular_derivatives["leg-back"][(lowest_hip_frame + 1):]) + 1)
        print(joint_second_angular_derivatives["leg-back"])
        print("AVG RISING %s" % avg_rising_sd)
        if avg_rising_sd < -1 * tolerance:
            lift_errors.append("WEAKHIPS")
        elif avg_rising_sd > tolerance:
            lift_errors.append("WEAKQUADS")
        
        # Check for "goodmorning-ing"
        print(len(lift_errors))

        if len(lift_errors) == 0:
            lift_errors.append("GOODSQUAT")

        return lift_errors

    
    def check_deadlift(self, frames, data):
        lift_errors = []
        if len(lift_errors) == 0:
            lift_errors.append("GOODDEADLIFT")

        return lift_errors
    
    def check_bench(self, frames, data):
        lift_errors = []
        if len(lift_errors) == 0:
            lift_errors.append("GOODBENCH")

        return lift_errors
        

if __name__ == "__main__":
    fc = FormCheck(10, 10)
    data = {
        1: [[9, 5], [6, 6],[9, 5], [6, 6]],
        8: [[5, 5], [6, 5],[5, 5], [6, 5]],
        9: [[5, 7], [6, 7],[5, 7], [6, 7]],
        10: [[7, 7], [7, 7],[7, 7], [7, 7]],
        11: [[9, 7], [9, 7],[9, 7],[9, 7]],
        12: [[5, 3], [6, 3],[5, 3],[5, 3]],
        13: [[7, 3], [7, 3],[7, 3],[7, 3]],
        14: [[9, 3], [9, 3],[9, 3], [9, 3]]
    }
    frames = 4

    fc.check_form(frames, data, exercise="SQUAT")

