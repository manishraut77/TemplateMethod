"""
Extract just the LV and RV myocardium (labels 1 and 2) from each mesh in the
KCL dataset and save the result.

Folder layout expected (run from the parent directory containing all three):

    ./CardiacShapeModel-master/   <- official repo (Mesh.py, ...)
    ./KCL Dataset/                <- 01.vtk, 02.vtk, ..., 20.vtk
    ./Final Dataset/              <- output written here as 01.vtk, ..., 20.vtk

Labels extracted:
    1 = LV myocardium
    2 = RV myocardium
"""

import os
import sys
import glob
import traceback
import vtk

REPO_DIR = './CardiacShapeModel-master'
sys.path.insert(0, REPO_DIR)

from Mesh import Model

INPUT_DIR = './KCL Dataset'
OUTPUT_DIR = './Final Dataset'

LV, RV = 1, 2


def threshold_compat(model, low, high, array_name='ID'):
    """
    Model.threshold() calls vtkThreshold.ThresholdBetween(), which was
    removed in newer VTK versions, AND relies on an ambiguous "active
    scalar" default that can silently pick the wrong array (e.g. a
    POINT_DATA UVC field instead of the CELL_DATA label array). This
    explicitly targets the named cell-data array to avoid both problems.
    """
    th = vtk.vtkThreshold()
    th.SetInputConnection(model.mesh.GetOutputPort())
    th.SetInputArrayToProcess(
        0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_CELLS, array_name)
    if hasattr(th, 'ThresholdBetween'):
        th.ThresholdBetween(low, high)
    else:
        th.SetLowerThreshold(low)
        th.SetUpperThreshold(high)
        th.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
    th.Update()
    return th


def process_case(vtk_path):
    print('\n--- Processing {} ---'.format(vtk_path))

    # Model.__init__ splits the filename on '.', so pass an absolute path
    # to avoid the leading './' being mistaken for part of the filename.
    vtk_path = os.path.abspath(vtk_path)
    model = Model(vtk_path)

    # Labels 1 and 2 are contiguous, so a single threshold covers both
    th = threshold_compat(model, LV, RV)
    n_cells = th.GetOutput().GetNumberOfCells()
    n_points = th.GetOutput().GetNumberOfPoints()
    print('  -> threshold result: {} cells, {} points'.format(n_cells, n_points))
    if n_cells == 0:
        print('  !!! WARNING: threshold produced zero cells -- nothing will be written')
    model.mesh = th
    return model


def find_case_files(input_dir):
    files = glob.glob(os.path.join(input_dir, '*.vtk'))
    files.sort()
    return files


def run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    case_files = find_case_files(INPUT_DIR)
    if not case_files:
        raise FileNotFoundError('No .vtk files found under "{}"'.format(INPUT_DIR))

    print('Found {} .vtk files:'.format(len(case_files)))
    for f in case_files:
        print('  ', f)

    for vtk_path in case_files:
        case_id = os.path.splitext(os.path.basename(vtk_path))[0].strip()

        try:
            result = process_case(vtk_path)
        except Exception as e:
            print('!!! Failed on {}: {}'.format(vtk_path, e))
            traceback.print_exc()
            continue

        result.filename = os.path.join(os.path.abspath(OUTPUT_DIR), case_id)
        result.write_vtk(postscript='', type_='UG')

        expected_path = result.filename + '.vtk'
        if os.path.isfile(expected_path):
            size = os.path.getsize(expected_path)
            print('  -> confirmed on disk: {} ({} bytes)'.format(expected_path, size))
        else:
            print('  !!! write_vtk reported success but file not found at: {}'.format(expected_path))

    print('\nDone. LV+RV meshes written to: {}'.format(OUTPUT_DIR))


if __name__ == '__main__':
    run()