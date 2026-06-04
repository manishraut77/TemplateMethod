import os
import numpy as np

INPUT_DIR = "./processed_npys"
OUTPUT_DIR = "./normalized_csvs"


def convert_one_npy_to_csv(npy_path):
    points = np.load(npy_path)

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError(f"Expected Nx3 array, got shape {points.shape} in {npy_path}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_name = os.path.basename(npy_path)
    base_name = os.path.splitext(file_name)[0]

    output_path = os.path.join(OUTPUT_DIR, base_name + ".csv")

    np.savetxt(
        output_path,
        points,
        delimiter=",",
        header="X,Y,Z",
        comments=""
    )

    print("saved:", output_path)
    print("shape:", points.shape)

    return output_path


def convert_all_npys_to_csv():
    npy_files = sorted(os.listdir(INPUT_DIR))

    for file_name in npy_files:
        if file_name.endswith(".npy"):
            npy_path = os.path.join(INPUT_DIR, file_name)
            convert_one_npy_to_csv(npy_path)


if __name__ == "__main__":
    convert_all_npys_to_csv()