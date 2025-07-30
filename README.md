# Sliver1 Rendering Engine

The **Sliver1 Rendering Engine** is a CPU-based 3D rendering engine inspired by the techniques used in early game engines like Quake. It emphasizes low-level control and software rendering, using libraries like `pygame` and `numba` for performance and visualization.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)

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
## Requirements

- Pygame
- Numba

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
```

## Usage

- Initialize Pygame and the Display
```python
from render import object
import pygame

pygame.init()

display = pygame.display.set_mode(
    (1000, 900),
    pygame.SRCALPHA,
    32
)
```

- Initialize main group
```python
scene = object.Group(
    [],
    display.get_width(),
    display.get_height()
)
```

- add your model
```python
scene.append('path/to/your/model', [Pos], 'path/to/your/texture', display)
```

- add mainloop
```python
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    display.fill((35, 35, 35))

    group.run() # main run funtion
    group.update_screen(display.get_height(), display.get_width()) # this is use to correct the warping when the screen is resized

    pygame.display.update()
```
---
