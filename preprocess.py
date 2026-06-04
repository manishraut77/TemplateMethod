import os
import numpy as np

INPUT_DIR="./geometries"
OUTPUT_DIR='./processed_npys'
TEMPLATE_PATH="./geometries/ct_case_0001.csv"

def load_csv_points(csv_path):
    points=np.loadtxt(csv_path,delimiter=',') #this fucking line loads the csv file into a numpy array. delimeter tells NumPy that values are separated by commas. 
    if points.ndim != 2 or points.shape[1] !=3:
       raise ValueError(f"Expected NX3 CSV, got shape {points.shape}")
    return points

def sample_random_points(points,target_count=15000):
    total_points=points.shape[0]
    indices=np.random.choice(total_points,target_count,replace=False)
    sampled_points=points[indices]
    return sampled_points

def save_points(points,csv_path):
    os.makedirs(OUTPUT_DIR,exist_ok=True)
    file_name=os.path.basename(csv_path)
    base_name=os.path.splitext(file_name)[0]
    output_path=os.path.join(OUTPUT_DIR,base_name + ".npy")
    np.save(output_path,points)
    return output_path

def normalize_sampled_points(points):
    center=np.mean(points,axis=0)
    centered_points=points-center
    squared_distances=np.sum(centered_points**2,axis=1)
    rms_scale=np.sqrt(np.mean(squared_distances))
    normalized_points=centered_points/rms_scale
    sampled_points=sample_random_points(normalized_points)
    return sampled_points

def process_one_file(csv_path):

    points=load_csv_points(csv_path)
    normalized_sampled_points=normalize_sampled_points(points)
    saved_path=save_points(normalized_sampled_points,csv_path)

    print("saved:",saved_path)
    print("shape:", normalized_sampled_points.shape)

    return saved_path

def process_all_files():
    csv_files=sorted(os.listdir(INPUT_DIR))

    for file_name in csv_files:
        if file_name.endswith(".csv"):
            csv_path=os.path.join(INPUT_DIR,file_name)
            saved_path=process_one_file(csv_path)
          
if __name__ == "__main__":

  process_all_files()














