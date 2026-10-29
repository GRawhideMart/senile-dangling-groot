# Industrial SDG Pipeline

[![Blender](https://img.shields.io/badge/Blender-5.1.1-orange.svg?logo=blender&logoColor=white)](https://www.blender.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![DevContainer](https://img.shields.io/badge/Dev_Containers-Supported-blueviolet.svg?logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com/docs/devcontainers/containers)
[![Render Engine](https://img.shields.io/badge/Render_Engine-Cycles-brightgreen.svg)]()

A procedural Blender-based **Synthetic Data Generation (SDG)** pipeline engineered for machine learning and computer vision tasks in industrial and logistics environments.

The pipeline procedurally creates realistic 3D assets (cardboard packages, wooden pallets, factory structures, and geometric clutter), introduces rich domain randomization (lighting, camera angles, materials, warping, and dents), and renders multi-modal ground truth datasets containing RGB imagery, mathematical amodal segmentation masks, 32-bit floating-point depth maps, and 2D/3D bounding box annotations.

---

## Visual Outputs

Each iteration of the generation pipeline automatically produces aligned modalities and ground truth annotations:

| RGB Synthetic Render | Binary Segmentation Mask | 2D/3D Bounding Box Debug |
| :---: | :---: | :---: |
| ![RGB Render](docs/images/sample_rgb.png) | ![Binary Mask](docs/images/sample_mask.png) | ![Bounding Box Debug](docs/images/sample_debug.png) |
| *Photorealistic Cycles render with procedural textures and clutter* | *Pristine mathematical amodal mask of the target package* | *Projected 3D corners (green) and tight 2D bounding box (red)* |

### Domain & Environment Variations

The generator dynamically alters indoor and outdoor industrial contexts, camera angles, sun positions, and distractor clutter:

| Indoor Setting (Pallet & Concrete) | Outdoor Setting (Dynamic Sky & Sunlight) |
| :---: | :---: |
| ![Indoor Environment](docs/images/sample_indoor.png) | ![Outdoor Environment](docs/images/sample_outdoor.png) |
| *Simulated warehouse setting on wooden pallets with industrial lighting* | *Outdoor environment with atmospheric scattering and terrain variation* |

---

## Core Capabilities

- **Procedural Package Generation (`src/generators/box.py`)**:
  - **Geometric Scaling**: Randomized dimensions $`s_x, s_y \in [0.6, 0.9]\text{ m}`$ and height $`s_z \in [0.1, 0.8]\text{ m}`$.
  - **Procedural Cardboard Shader**: Synthesized Cycles shader with base brown color sampled in HSV space ($`H \in [0.06, 0.10]`$, $`S \in [0.40, 0.60]`$, $`V \in [0.40, 0.60]`$).
  - **Shipping Labels & Barcodes**: Voronoi noise thresholding for rectangular label patches combined with high-frequency noise textures for simulated printed text and barcodes.
  - **Surface Imperfections & Damage**: Bevel modifier with edge width $`w \in [2, 10]\text{ mm}`$ and angle limit $`\theta_{\text{bevel}} = 30^{\circ}`$, coupled with displacement surface warping ($`d_{\text{warp}} \in [5, 15]\text{ mm}`$).
  - **Orientation Randomization**: In-plane yaw rotation $`\psi \in [0, 2\pi)`$ and discrete tilt angles $`\psi_{\text{tilt}} \in \{0^{\circ}, 90^{\circ}, 180^{\circ}\}`$.

- **Domain & Environment Randomization (`src/generators/environment.py`)**:
  - **Indoor Warehouses**: Procedural multi-slat wooden pallets, concrete flooring with surface roughness $`R_{\text{floor}} \in [0.02, 0.06]`$, structural steel pillars, and ceiling beams illuminated by randomized overhead area lighting ($`E \in [300, 600]\text{ W}`$ at height $`z \in [4, 6]\text{ m}`$).
  - **Outdoor Loading Docks**: Dynamic sky scattering model (`MULTIPLE_SCATTERING`) with sun azimuth $`\phi_{\text{sun}} \in [0^{\circ}, 360^{\circ}]`$, sun elevation $`\theta_{\text{sun}} \in [15^{\circ}, 45^{\circ}]`$, and solar intensity $`I_{\text{sun}} \in [0.002, 0.005]`$, paired with grass and dirt terrain shaders.
  - **Camera Spherical Randomization**: Camera position $`\mathbf{p}_{\text{cam}} = (r\cos\theta\cos\phi, \; r\cos\theta\sin\phi, \; r\sin\theta + 0.5)^{\top}`$ targeting scene origin $`\mathbf{p}_0 = (0, 0, 0)^{\top}`$, with azimuth $`\phi \in [0^{\circ}, 360^{\circ}]`$, elevation $`\theta \in [15^{\circ}, 50^{\circ}]`$, and radius $`r \in [3.5\text{ m}, 5.5\text{ m}]`$.

- **Visual Distractors & Clutter (`src/generators/clutter.py`)**:
  - Spawns $`N \in [5, 12]`$ primitive objects (cubes, cylinders, spheres, toruses) distributed in a radial ring at position $`\mathbf{p}_{\text{clutter}} = (d\cos\alpha, \; d\sin\alpha, \; z_0)^{\top}`$, with radius $`d \in [1.5\text{ m}, 4.0\text{ m}]`$, polar angle $`\alpha \in [0, 2\pi)`$, and height $`z_0 \in [0.05\text{ m}, 0.8\text{ m}]`$.
  - Randomized distractor scale $`s \in [0.1\text{ m}, 0.6\text{ m}]`$ and materials with segmentation pass index $0$ to guarantee exclusion from target masks.

- **Multi-Modal Ground Truth Extraction**:
  - **RGB Image**: High-fidelity Cycles path-traced rendering with 64 samples per pixel at 1024 × 1024 resolution.
  - **Depth Map (EXR)**: Single-channel 32-bit floating-point depth buffer $`Z \in \mathbb{R}^{H \times W}`$ extracted via Compositor output nodes.
  - **2D/3D Bounding Box Extraction (`src/core/bounding_box.py`)**: Transforms 8 object-space bounding box vertices into world coordinates using evaluated depsgraph matrices ($`\mathbf{v}_{\text{world}} = \mathbf{M} \mathbf{v}_{\text{local}}`$), projects them to 2D pixel coordinates $`(x, y) \in [0, W] \times [0, H]`$ via camera perspective projection, and extracts the tight axis-aligned bounding box $`[x_{\min}, y_{\min}, x_{\max}, y_{\max}]`$.
  - **Amodal Segmentation Mask**: Computes the 2D convex hull $`\mathcal{H} = \text{Conv}(\{(x_i, y_i)\}_{i=1}^8)`$ from the projected corners and rasterizes a pristine binary amodal mask $`\mathcal{M}(u, v) \in \{0, 255\}`$.

---

## Architecture & Codebase

```text
sdg_project/
├── .devcontainer/             # Dev container configuration for VS Code & Docker
│   ├── Dockerfile             # Ubuntu 22.04 + Blender 5.1.1 + PyTorch + OpenCV
│   └── devcontainer.json      # VS Code extensions and interpreter configurations
├── docs/                      # Documentation assets and sample outputs
│   └── images/
├── src/
│   ├── core/                  # Engine, compositing, and annotation extraction
│   │   ├── engine.py          # Cycles render engine setup, samples, and resolution
│   │   ├── compositor.py      # Compositor node tree for depth pass extraction
│   │   ├── bounding_box.py    # 3D bounding box corners and 2D camera projections
│   │   └── exporter.py        # Coordinates exporter and OpenCV debug visualizer
│   ├── generators/            # Procedural asset and environment generators
│   │   ├── box.py             # Procedural cardboard box, labels, and dents
│   │   ├── clutter.py         # Visual distractors and background clutter
│   │   └── environment.py     # Camera, lighting, pallets, and indoor/outdoor worlds
│   └── main.py                # Main pipeline orchestrator and execution loop
├── .gitignore                 # Excludes heavy caches, temporary renders, and EXRs
└── README.md                  # Project overview and documentation
```

---

## Spin Up the Dev Container

Blender 5.1.1 bundles its own internal C++ runtime and embedded Python 3.13 environment. To guarantee reproducible execution without manual system dependency installation, this repository is configured to run inside a **VS Code Dev Container**.

### Prerequisites

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine on Linux).
2. Install [Visual Studio Code](https://code.visualstudio.com/).
3. Install the [Dev Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code.

### Launching with VS Code (Recommended)

1. Clone the repository and open the root folder in VS Code:
   ```bash
   git clone https://github.com/GRawhideMart/senile-dangling-groot.git
   cd senile-dangling-groot
   code .
   ```
2. When the pop-up notification appears in the lower-right corner asking to **"Reopen in Container"**, click it.
   - *Alternatively:* Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS), type `Dev Containers: Reopen in Container`, and press `Enter`.
3. VS Code will build the Docker container (installing Blender 5.1.1, Python 3.13, PyTorch, Albumentations, and `fake-bpy-module-latest` for IntelliSense/Pylance autocomplete).
4. Once connected, open an integrated terminal in VS Code (`Ctrl+\``) — all environment variables and paths are automatically configured.

### Launching with Dev Container CLI

If you prefer the command line:

```bash
# Install Dev Containers CLI if not already present
npm install -g @devcontainers/cli

# Build and start container
devcontainer up --workspace-folder .

# Execute the pipeline directly
devcontainer exec --workspace-folder . blender --background --python src/main.py
```

### Standalone Docker Execution

You can also build and run the Docker container directly without VS Code:

```bash
# Build Docker image
docker build -t industrial-sdg -f .devcontainer/Dockerfile .

# Run the generation pipeline and mount the output
docker run -it --rm -v $(pwd):/workspace industrial-sdg blender --background --python src/main.py
```

---

## Running the Pipeline

Inside the container environment, execute the main entry point via Blender:

```bash
blender --background --python src/main.py
```

> **Tip:** Omit the `--background` flag if you have an X11/VNC display server running and wish to inspect the generated 3D scene and materials interactively inside Blender's viewport.

### Generated Dataset Structure

When execution finishes, the pipeline writes output data to `output/`:

```text
output/
├── images/                    # Rendered RGB frames (PNG, 1024x1024)
│   ├── frame_0000.png
│   └── frame_0001.png
├── masks/                     # Binary amodal segmentation masks (PNG, 1024x1024)
│   ├── frame_0000_mask.png
│   └── frame_0001_mask.png
├── depth/                     # Single-channel 32-bit float depth maps (OpenEXR)
│   ├── frame_0000_depth.exr
│   └── frame_0001_depth.exr
└── debug/                     # Bounding box labels and visual overlays
    ├── frame_0000.txt         # 2D coordinates (x_min, y_min, x_max, y_max)
    └── frame_0000_debug.png   # Verification image with bounding box overlay
```

---

## Development Conventions

All contributions and extensions should adhere to the project conventions:

- **SOLID Principles:** Strictly adhere to SOLID design principles for modularity and separation of concerns.
- **Documentation:** Use **Google-style docstrings** for all classes, methods, and functions.
- **Vertical Alignment:** For code readability, align `=`, `:`, and function parameters vertically:
  ```python
  self.render_path = render_path
  self.resolution  = resolution
  self.samples     = samples
  ```
- **Imports:** Use absolute imports relative to the `src` directory. `src/main.py` prepends its directory to `sys.path`.
- **Stateless Execution:** Generators must clean up orphaned meshes, materials, and textures between iterations to prevent GPU memory leaks across long generation runs.

---

## Roadmap & Planned Features

- [x] Camera randomization (spherical coordinates, distance, elevation).
- [x] 3D bounding box extraction and 2D perspective projection.
- [x] Procedural indoor/outdoor environment randomization.
- [ ] Export formats for popular detection/segmentation frameworks (YOLOv8/YOLOv11, COCO JSON, Pascal VOC).
- [ ] Occlusion metrics and multi-instance generation (stacking pallets and multiple packages).
- [ ] Additional industrial packaging types (cylindrical drums, shrink-wrapped bundles, pallet wrap).
