# Sliver1 Rendering Engine

The **Sliver1 Rendering Engine** is a CPU-based 3D rendering engine inspired by the techniques used in early game engines like Quake. It emphasizes low-level control and software rendering, using libraries like `pygame` and `numba` for performance and visualization.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Screenshots](#screenshots)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

---

## About

Sliver1 is a lightweight software renderer that runs entirely on the CPU. It's designed for learning, experimentation, and exploring how 3D rendering worked in early-era engines before widespread GPU acceleration.

It includes basic rasterization, texture mapping, triangle rendering, and affine transformations.

---

## Features

- Pure software rendering (no OpenGL or DirectX)
- 2D framebuffer using `pygame`
- Triangle rasterization
- Texture mapping (affine)
- Backface culling
- `numba`-accelerated math routines

---
## libraries

- Pygame
- numba

---

## Installation

```bash
pip install -r requirements.txt
```

---
### Clone the repository

```bash
git clone https://github.com/mdewitt11/Sliver1-Rendering-engine-.git
cd Sliver1-Rendering-engine-
