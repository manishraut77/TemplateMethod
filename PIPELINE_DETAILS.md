# Heart Geometry Pipeline: Completed Through Rigid Alignment

## Current status

The project is intentionally complete only through stage 3 of the planning
diagram:

1. Data preprocessing
2. Template selection
3. Rigid alignment

Non-rigid registration and deformation vectors are not part of the current
output. Deformation vectors only make sense after a non-rigid template-to-cloud
registration step.

## 1. Data preprocessing

Input files:

- `geometries/ct_case_XXXX.csv`
- Each file contains one point per row: `x,y,z`

Output files:

- `processed_npys/ct_case_XXXX.npy`
- Shape: `(15000, 3)`

For each raw point cloud `P = {p_i}`, `preprocess.py` does the following.

### Centering

The centroid is:

```text
c = (1/N) sum_i p_i
```

Centered points are:

```text
q_i = p_i - c
```

### RMS scale normalization

The RMS scale is:

```text
s_rms = sqrt((1/N) sum_i ||q_i||^2)
```

Normalized points are:

```text
n_i = q_i / s_rms
```

### PCA orientation

The covariance matrix is:

```text
C = cov(N)
```

Eigenvectors of `C` are sorted by decreasing eigenvalue. Points are rotated into
the PCA basis:

```text
a_i = n_i E
```

where `E` contains the sorted eigenvectors.

### Template-based PCA sign selection

PCA eigenvectors have sign ambiguity: `v` and `-v` are both valid. The old code
used the mean coordinate along each PCA axis, but after centering those means are
approximately zero, so that did not reliably orient the hearts.

The updated code uses `ct_case_0001.csv` as the orientation reference. For each
target, it tries all 8 axis sign combinations:

```text
(+/-x, +/-y, +/-z)
```

For each candidate, it builds a coarse 3D occupancy histogram and chooses the
sign combination whose histogram is closest to the template histogram.

### Fixed-size resampling

Each processed heart is resampled to exactly 15,000 points. The seed is derived
from the filename, so rerunning preprocessing gives stable outputs.

## 2. Template selection

The current template is:

```text
processed_npys/ct_case_0001.npy
```

This template acts as the reference shape for rigid alignment.

## 3. Rigid alignment

Implemented in:

```text
register_template.py
```

For each target point cloud, the script rigidly maps the template into the
target frame:

```text
x_i = R X_i + t
```

where:

- `X_i` is template point `i`
- `x_i` is the rigidly aligned template point
- `R` is a 3x3 rotation matrix
- `t` is a 3D translation vector

Uniform scale is disabled because preprocessing already RMS-normalizes scale.
If scale is intentionally enabled later, the transform becomes:

```text
x_i = alpha R X_i + t
```

### ICP loop

Rigid registration uses ICP:

1. Sample template points.
2. Find nearest target points for the transformed template sample.
3. Estimate the best rigid transform between matched points.
4. Compose that transform into the accumulated rigid transform.
5. Stop when nearest-neighbor error stops improving or the iteration limit is
   reached.

### Kabsch/SVD transform

Given matched source points `A = {a_i}` and target points `B = {b_i}`:

```text
mean_A = (1/N) sum_i a_i
mean_B = (1/N) sum_i b_i
A0 = A - mean_A
B0 = B - mean_B
H = (A0^T B0) / N
```

Compute:

```text
H = U Sigma V^T
```

Then:

```text
D = diag(1, 1, sign(det(U V^T)))
R = U D V^T
t = mean_B - mean_A R
```

The determinant correction prevents reflections.

## Current outputs

Rigid alignment saves:

```text
registered_templates/ct_case_XXXX.npy
rigid_transforms/ct_case_XXXX.npz
registration_metrics.csv
```

`registered_templates/` contains the rigidly aligned template for each target.

`rigid_transforms/` contains:

- `scale`
- `rotation`
- `translation`
- `homogeneous_matrix`
- `template_path`
- `target_path`

`registration_metrics.csv` contains:

- case filename
- ICP iterations
- scale
- mean nearest-neighbor distance
- median nearest-neighbor distance
- max nearest-neighbor distance
- registered template path
- rigid transform path

Latest verified run:

```text
processed_npys: 64 files
registered_templates: 64 files
rigid_transforms: 64 files
array shape: (15000, 3)
all arrays finite: yes
average mean nearest-neighbor distance: ~0.0583
```

## Not done yet

The following stages are intentionally not completed yet:

- Non-rigid registration
- Deformation vector extraction
- PCA/VAE modeling
- Generation

The next valid stage is non-rigid template-to-cloud registration. Only after
that should deformation vectors be computed:

```text
u_i = x_nonrigid_i - X_i
```
