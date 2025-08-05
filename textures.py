import pygame
import math
import numba as nm
import numpy as np

@nm.njit(fastmath=True)
def edge_func(a, b, c):
    return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

class Texture:
    def __init__(self, display: pygame.surface.Surface, texture):
        self.display = display
        self.texture = texture
        self.tex_array = pygame.surfarray.array3d(texture).swapaxes(0, 1)
        self.width, self.height = display.get_width(), display.get_height()
        self.z_buffer = np.full((self.width, self.height), np.inf, dtype=np.float32)  # Z-buffer


    def triangle_texture(self, cords: tuple, texture_coords: tuple, tint, z):
        tex_pixels = self.tex_array
        tex_w, tex_h = self.texture.get_width(), self.texture.get_height()
        frame_array = pygame.surfarray.pixels3d(self.display)

        self.draw_triangle_affine(
            frame_array, self.z_buffer, tex_pixels,
            cords[0], cords[1], cords[2],
            texture_coords[0], texture_coords[1], texture_coords[2],
            tex_w, tex_h,
            tint,
            z[0],z[1],z[2]
        )

    def clear_z(self):
        self.z_buffer[:,:] = np.inf

    @staticmethod
    @nm.njit(parallel=True, fastmath=True)
    def draw_triangle_affine(frame, zbuf, tex, p0, p1, p2, uv0, uv1, uv2, tex_w, tex_h, tint, z1,z2,z3):
        p0 = np.array(p0, dtype=np.float32)
        p1 = np.array(p1, dtype=np.float32)
        p2 = np.array(p2, dtype=np.float32)

        z1 = np.float32(z1)
        z2 = np.float32(z2)
        z3 = np.float32(z3)

        uv0 = np.array(uv0, dtype=np.float32)
        uv1 = np.array(uv1, dtype=np.float32)
        uv2 = np.array(uv2, dtype=np.float32)

        min_x = max(int(min(p0[0], p1[0], p2[0])), 0)
        max_x = min(int(max(p0[0], p1[0], p2[0])) + 1, frame.shape[0])
        min_y = max(int(min(p0[1], p1[1], p2[1])), 0)
        max_y = min(int(max(p0[1], p1[1], p2[1])) + 1, frame.shape[1])

        area = edge_func(p0, p1, p2)

        if area < 0:
            return

        for y in nm.prange(min_y, max_y):
            for x in range(min_x, max_x):
                p = (x, y)

                w0 = edge_func(p1, p2, p)
                w1 = edge_func(p2, p0, p)
                w2 = edge_func(p0, p1, p)

                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    w0 /= area
                    w1 /= area
                    w2 /= area

                    # Interpolate depth (Z)
                    z = w0*z1 + w1*z2 + w2*z3

                    # Depth test
                    if z < zbuf[x, y]:
                        zbuf[x, y] = z

                        # Interpolate UV
                        u = w0 * uv0[0] + w1 * uv1[0] + w2 * uv2[0]
                        v = w0 * uv0[1] + w1 * uv1[1] + w2 * uv2[1]

                        tx = int(u * tex_w)
                        ty = int(1-v * tex_h)  # flip V if necessary

                        pixel = tex[ty, tx]

                        r = min(max(pixel[0] + tint[0], 0), 255)
                        g = min(max(pixel[1] + tint[1], 0), 255)
                        b = min(max(pixel[2] + tint[2], 0), 255)

                        frame[x, y] = (r,g,b)
