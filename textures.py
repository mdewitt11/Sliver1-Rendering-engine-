import pygame
import numba as nm

class Texture:
    def __init__(self, display, texture):
        self.display = display  # pygame Surface
        self.texture = texture  # pygame Surface
        self.tex_array = pygame.surfarray.array3d(texture).swapaxes(0, 1) 
    
    @staticmethod
    def edge_sort(cords:tuple):
        return sorted(cords,key=lambda x: x[1])
    
    @staticmethod
    @nm.njit()
    def fast_edge_func(a,b,c):
        return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

    def triangle_texture(self, cords: tuple, texture_coords: tuple):
        a, b, c = cords
        if self.fast_edge_func(a, b, c) < 0:
            return

        a, b, c = self.edge_sort(cords)

        tex_pixels = self.tex_array
        tex_w, tex_h = self.texture.get_width(), self.texture.get_height()
        frame_array = pygame.surfarray.pixels3d(self.display)

        draw_triangle_affine(
            frame_array, tex_pixels,
            cords[0], cords[1], cords[2],
            texture_coords[0], texture_coords[1], texture_coords[2],
            tex_w, tex_h
        )



@nm.njit(parallel=True)
def draw_triangle_affine(frame, tex, p0, p1, p2, uv0, uv1, uv2, tex_w, tex_h):
    def edge_func(a, b, c):
        return (c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])

    min_x = max(int(min(p0[0], p1[0], p2[0])), 0)
    max_x = min(int(max(p0[0], p1[0], p2[0]))+1, frame.shape[0])
    min_y = max(int(min(p0[1], p1[1], p2[1])), 0)
    max_y = min(int(max(p0[1], p1[1], p2[1]))+1, frame.shape[1])

    
    area = edge_func(p0, p1, p2)

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

                u = w0 * uv0[0] + w1 * uv1[0] + w2 * uv2[0]
                v = w0 * uv0[1] + w1 * uv1[1] + w2 * uv2[1]

                tx = int(u * tex_w)
                ty = int((1 - v) * tex_h)  # flip V if necessary

                frame[x, y] = tex[ty, tx]