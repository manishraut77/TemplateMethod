import os
import numpy as np

INPUT_DIR="./processed_npys"
FILE_NAME='ct_case_0001.npy'

TOP_PERCENTILE=99.5

def load_npy_points(npy_path):
    points=np.load(npy_path)
    return points
