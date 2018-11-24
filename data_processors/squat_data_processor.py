import numpy as np
import math

import vector_helper as vh

def process_squat_data(frames, data):
    """
    frames: num frames
    data: dict of lists for each point on COCO model
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
    required_data = {
        "back": [8, 1], #hip to neck
        "hip_plane": [12, 9], #left to right hip plane
        "LFemur": [13, 12], #left femur knee to hip
        "RFemur": [10, 9], #right femur knee to hip
        "LCalf": [13, 14], #left calf knee to ankle
        "RCalf": [10, 11] #right calf knee to ankle
    }
    important_anatomy_features = {
        "back": [],
        "hip_plane": [],
        "LFemur": [],
        "RFemur": [],
        "LCalf": [],
        "RCalf": []
    }
    important_anatomy_joints = {
        "back-hip_plane": [],
        "leg-back": [],
        "LKnee": [],
        "RKnee": []
    }
    # Needs to process vectors for squat, and get either suggestions or critique
    # load anatomy timewise
    for i in range(frames):
        for anat, parts in required_data.items():
            vec = [data[parts[1]][i][0] - data[parts[0]][i][0], data[parts[1]][i][1] - data[parts[0]][i][1]]
            important_anatomy_features[anat].append(vec)
    # print(important_anatomy_features)
    # Generate angles
    for i in range(frames):
        important_anatomy_joints["back-hip_plane"].append(
            vh.angle_between(
                important_anatomy_features["back"][i], 
                important_anatomy_features["hip_plane"][i]
            )
        )
        important_anatomy_joints["leg-back"].append(
            vh.angle_between(
                vh.reverse_vector(
                    vh.average_vector(
                        important_anatomy_features["LFemur"][i],
                        important_anatomy_features["RFemur"][i]
                    )
                ),
                important_anatomy_features["back"][i]
            )
        )
        important_anatomy_joints["LKnee"].append(
            vh.angle_between(
                important_anatomy_features["LFemur"][i],
                important_anatomy_features["LCalf"][i]
            )
        )
        important_anatomy_joints["RKnee"].append(
            vh.angle_between(
                important_anatomy_features["RFemur"][i],
                important_anatomy_features["RCalf"][i]
            )
        )
    # print(important_anatomy_joints)

    # Calculate first differences, second differences
    joint_first_angular_derivatives = {
        "back-hip_plane": [],
        "leg-back": [],
        "LKnee": [],
        "RKnee": []
    }
    joint_second_angular_derivatives = {
        "back-hip_plane": [],
        "leg-back": [],
        "LKnee": [],
        "RKnee": []
    }

    for i in range(frames - 1):
        joint_first_angular_derivatives["leg-back"].append(
            important_anatomy_joints["leg-back"][i + 1] - important_anatomy_joints["leg-back"][i]
        )
        joint_first_angular_derivatives["LKnee"].append(
            important_anatomy_joints["LKnee"][i + 1] - important_anatomy_joints["LKnee"][i]
        )
        joint_first_angular_derivatives["RKnee"].append(
            important_anatomy_joints["RKnee"][i + 1] - important_anatomy_joints["RKnee"][i]
        )
    for i in range(frames - 2):
        joint_second_angular_derivatives["leg-back"].append(
            joint_first_angular_derivatives["leg-back"][i + 1] - joint_first_angular_derivatives["leg-back"][i]
        )
        joint_second_angular_derivatives["LKnee"].append(
            joint_first_angular_derivatives["LKnee"][i + 1] - joint_first_angular_derivatives["LKnee"][i]
        )
        joint_second_angular_derivatives["RKnee"].append(
            joint_first_angular_derivatives["RKnee"][i + 1] - joint_first_angular_derivatives["RKnee"][i]
        )

    # print(joint_first_angular_derivatives)
    # print(joint_second_angular_derivatives)

    return important_anatomy_features, important_anatomy_joints, joint_first_angular_derivatives, joint_second_angular_derivatives