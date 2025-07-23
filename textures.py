import pygame
import math
import pygame.gfxdraw
import pygame.surfarray as surfarray

import pygame
import math

class Texture:
    def __init__(self, file_name):
        self.file_name = file_name
        self.texture = pygame.image.load(self.file_name).convert_alpha()

    @staticmethod
    def edge_function(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    def triangle_texture(self, cords: tuple, texture_cords: tuple, display: pygame.Surface):
        A, B, C = cords
        frame = surfarray.pixels3d(display)

        ABC = self.edge_function(A, B, C)
        if ABC >= 0:
            return

        width, height = display.get_size()

        minX = max(math.floor(min(A[0],B[0],C[0])), 0)
        maxX = min(math.ceil(max(A[0],B[0],C[0])), width)

        minY = max(math.floor(min(A[1],B[1],C[1])), 0)
        maxY = min(math.ceil(max(A[1],B[1],C[1])), height)

        AB = (B[0] - A[0], B[1] - A[1])
        BC = (C[0] - B[0], C[1] - B[1])
        CA = (A[0] - C[0], A[1] - C[1])

        def is_inside(w, dx, dy):
            return (w < 0) or (w == 0 and (dy > 0 or (dy == 0 and dx < 0)))

        for y in range(minY, maxY):
            for x in range(minX, maxX):
                P = (x, y)

                ABP = self.edge_function(A, B, P)
                BCP = self.edge_function(B, C, P)
                CAP = self.edge_function(C, A, P)

                if (
                    is_inside(ABP, *AB) and
                    is_inside(BCP, *BC) and
                    is_inside(CAP, *CA)
                ):
                    frame[P[0],P[1]] = (255,0,0)
