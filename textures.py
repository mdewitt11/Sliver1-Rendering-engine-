import pygame


class Texture:
    def __init__(self,file_name):
        self.file_name = file_name
        self.load_img = pygame.image.load(self.file_name).convert_alpha()

    def triangle_texture(self,cords:tuple):
        v1,v2,v3 = cords
        return v1,v2,v3
