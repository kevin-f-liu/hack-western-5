import numpy as np
import math

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in degrees between vectors 'v1' and 'v2'::
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)) * 180 / math.pi

def average_vector(v1, v2):
    return np.add(v1, v2)

def reverse_vector(v1):
    return [-1 * v1[0], -1 * v1[1]]

if __name__ == "__main__":
    print(angle_between([-0.50, 1], [-1, -0.5]))