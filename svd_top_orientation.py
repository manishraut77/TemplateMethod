import os
import numpy as np

INPUT_DIR="./normalized_csvs"
OUTPUT_NPY_DIR="./svd_oriented_npys"
OUTPUT_CSV_DIR="./svd_oriented_csvs"
TOP_PERCENTILE=99.5


def load_csv_points(csv_path):
    points=np.loadtxt(csv_path,delimiter=",")
    if points.ndim != 2 or points.shape[1]!=3:
        raise ValueError(f"Expected N*3 CSV, got shape {points.shape}")
    return points

def get_top_plane_points(points):
    z_values=points[:,2]
    z_threshold=np.percentile(z_values,TOP_PERCENTILE)
    top_points=points[z_values>=z_threshold]
    return top_points, z_threshold


def fit_plane_normal_svd(top_points):
     center=np.mean(top_points,axis=0)
     centered_top_points=top_points - center
     _, _, vh = np.linalg.svd(centered_top_points)
     normal = vh[-1]
     normal= normal/np.linalg.norm(normal)
     if normal[2]<0:
         normal=-normal
     return normal

def rotation_matrix_from_vectors(source,target):
    source =source/np.linalg.norm(source)
    target=target/np.linalg.norm(target)
    axis=np.cross(source,target)
    axis_norm=np.linalg.norm(axis)
    dot=np.dot(source,target)
    dot=np.clip(dot,-1.0,1.0)
    if axis_norm < 1e-12 and dot < 0:
        axis = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(axis, source)) > 0.9:       # if too parallel choose another axis
            axis = np.array([0.0, 1.0, 0.0])
        axis = axis - np.dot(axis, source) * source
        axis = axis / np.linalg.norm(axis) 
        angle=np.pi

    else:
        axis= axis/axis_norm
        angle=np.arccos(dot)

    x, y, z = axis                                # unpack axis coordinates

    K = np.array([
        [0.0, -z, y],
        [z, 0.0, -x],
        [-y, x, 0.0]
    ])                                            # skew-symmetric matrix used in Rodrigues formula

    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * (K @ K)  # Rodrigues rotation matrix

    return R

def align_heart(points):
    top_points, z_threshold = get_top_plane_points(points)
    normal_before = fit_plane_normal_svd(top_points)
    z_axis=np.array([0.0,0.0,1.0])
    angle_before = np.degrees(np.arccos(np.clip(np.dot(normal_before,z_axis),-1.0,1.0)))
    R=rotation_matrix_from_vectors(normal_before,z_axis)
    aligned_points = points @ R.T
    new_top_points ,_ = get_top_plane_points(aligned_points)
    normal_after=fit_plane_normal_svd(new_top_points)

    angle_after=np.degrees(np.arccos(np.clip(np.dot(normal_after,z_axis),-1.0,1.0)))
    return aligned_points,normal_before,normal_after,angle_before, angle_after,z_threshold

def save_outputs(points,original_csv_path):
    os.makedirs(OUTPUT_NPY_DIR,exist_ok=True)
    os.makedirs(OUTPUT_CSV_DIR,exist_ok=True)
    file_name=os.path.basename(original_csv_path)
    base_name=os.path.splitext(file_name)[0]
    npy_path=os.path.join(OUTPUT_NPY_DIR,base_name+".npy")
    csv_path=os.path.join(OUTPUT_CSV_DIR,base_name+".csv")
    np.save(npy_path,points)
    np.savetxt(csv_path,points,delimiter=',')
    return npy_path, csv_path
def process_one_file(csv_path):
    points=load_csv_points(csv_path)
    aligned_points,normal_before,normal_after,angle_before,angle_after,z_threshold=align_heart(points)
    npy_path,csv_output_path=save_outputs(aligned_points,csv_path)
    print("--------------------------------------------------------------------------")
    print("File:",os.path.basename(csv_path))
    print("Shape:",points.shape)
    print("top plane threshold:" ,z_threshold)
    print("Normal befroe: ", normal_before)
    print("Angle before:", angle_before)
    print("normal after: ", normal_after)
    print("Angle after: ", angle_after)
    print("Saved NPY:", npy_path)
    print("Saved CSV:", csv_path)

def process_all_files():
    csv_files=sorted(os.listdir(INPUT_DIR))
    for file_name in csv_files:
        if file_name.endswith(".csv"):
            csv_path=os.path.join(INPUT_DIR,file_name)
            process_one_file(csv_path)

if __name__=="__main__":
    process_all_files()


    





    
     

