import os
import vtk

# ============================================================
# Directories
# ============================================================

INPUT_DIR = "./Final Dataset"
OUTPUT_DIR = "./AlignedVtkData"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# Final alignment matrix from ParaView
# ============================================================

MATRIX = [
    [-0.6981766095764631, -0.6099980031519487, -0.3747690728848228, 0.0],
    [ 0.1976765177322381, -0.6673777811375955,  0.7180047991351557, 0.0],
    [-0.6880940460268281,  0.4272111110382015,  0.5865298376280054, 0.0],
    [ 0.0,                 0.0,                 0.0,                1.0]
]


# ============================================================
# Create VTK transform
# ============================================================

matrix = vtk.vtkMatrix4x4()

for i in range(4):
    for j in range(4):
        matrix.SetElement(i, j, MATRIX[i][j])

transform = vtk.vtkTransform()
transform.SetMatrix(matrix)


# ============================================================
# Process all VTK files
# ============================================================

vtk_files = sorted(
    f for f in os.listdir(INPUT_DIR)
    if f.lower().endswith(".vtk")
)

print(f"Found {len(vtk_files)} VTK files.")

for filename in vtk_files:

    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)

    print(f"Aligning: {filename}")

    # --------------------------------------------------------
    # Read input VTK
    # --------------------------------------------------------

    reader = vtk.vtkDataSetReader()
    reader.SetFileName(input_path)
    reader.Update()

    mesh = reader.GetOutput()

    if mesh is None or mesh.GetNumberOfPoints() == 0:
        print(f"  WARNING: Could not read points from {filename}")
        continue

    # --------------------------------------------------------
    # Apply transformation
    # --------------------------------------------------------

    transform_filter = vtk.vtkTransformFilter()
    transform_filter.SetInputData(mesh)
    transform_filter.SetTransform(transform)
    transform_filter.Update()

    aligned_mesh = transform_filter.GetOutput()

    # --------------------------------------------------------
    # Write output
    # --------------------------------------------------------

    writer = vtk.vtkDataSetWriter()
    writer.SetFileName(output_path)
    writer.SetInputData(aligned_mesh)
    writer.SetFileTypeToBinary()
    writer.Write()

    print(f"  Saved: {output_path}")


print("\nDone.")