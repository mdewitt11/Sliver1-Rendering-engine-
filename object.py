from render import Math3d
import pygame
import math

class Light3D:
    def __init__(self,pos=(0,0,0)):
        self.pos = pos
    
    def change_pos(self,NewPos):
        self.pos = NewPos
    
    @staticmethod
    def triangle_center(v0, v1, v2):
        return [
            (v0[0] + v1[0] + v2[0]) / 3,
            (v0[1] + v1[1] + v2[1]) / 3,
            (v0[2] + v1[2] + v2[2]) / 3,
        ]
    
    @staticmethod
    def normalize(vec):
        length = sum(x**2 for x in vec) ** 0.5
        if length == 0:
            return [0, 0, 0]
        return [x / length for x in vec]
    
    def get_light_dir(self,surface_pos):
        surface_pos = self.triangle_center(surface_pos[0],surface_pos[1],surface_pos[2])
        return self.normalize([
            self.pos[0] - surface_pos[0],
            self.pos[1] - surface_pos[1],
            self.pos[2] - surface_pos[2]
        ])
    
    def add_fog(self, light_cords, surface_cords, light_radius, base_color):
        center = self.triangle_center(surface_cords[0], surface_cords[1], surface_cords[2])

        distance_to_light = Math3d.distance(center, light_cords)

        brightness = max(0, 1 - (distance_to_light / light_radius))
        brightness = brightness ** 2

        return tuple(
            min(255, int(base_color[i] * brightness))
            for i in range(3)
        )


class Group:
    def __init__(self, objects=[],SW=900,SH=1000,FOV=0.5):
        self.objects = objects
        self.light = Light3D()
        self.camera = Math3d.Camera(SW,SH,FOV)
        self.zero = (0,0,0)
        self.SW = SW
        self.SH = SH
        self.FOV = FOV * self.SH

    def append(self, object3d):
        self.append(object3d)

    def move(self, pos):
        for i in range(len(self.objects)):
            self.objects[i].move(pos)
            self.move_light(pos)
             
    def move_light(self,pos):
        self.light.change_pos(
            (
                self.light.pos[0] + pos[0],
                self.light.pos[1] + pos[1],
                self.light.pos[2] + pos[2]
            )
        )
    
    def rotate(self, axis, a):
        for i in range(len(self.objects)):
            self.objects[i].rotate(axis,a)
    
    def update_screen(self,SH,SW):
        self.camera.update_screen(SH,SW)

    def sort_objects(self):
        obj = []
        for i in range(len(self.objects)):
            pos = self.objects[i].pos
            obj.append([Math3d.distance(pos,self.zero),self.objects[i]])
        obj.sort(key=lambda x: x[0],reverse=True)
        return obj
    
    def run(self, display):
        obj = self.sort_objects()
        for i in range(len(obj)):
            obj[i][1].drawTriangle(display, self.SW, self.SH, self.FOV,self.light,self.camera)

class Object3D:
    def __init__(self, vert, tirangles, pos,color,texture:str):
        self.pos = pos
        self.max_darkness = 0
        self.max_brightness = 255
        self.color = color
        self.tirangles = tirangles
        self.texture = texture
        self.vert = Math3d.Transform(vert).translate(pos)
    
    def sortTriangles(self, vert):
        disMap = []
        for i in range(len(vert)):
            tri = vert[i]

            try:
                z1 = tri[0][2]
                z2 = tri[1][2]
                z3 = tri[2][2]
                avg_z = (z1 + z2 + z3) / 3
            except:
                continue

            disMap.append([avg_z, tri])

        disMap.sort(key=lambda x: x[0], reverse=True)
        return [tri for _, tri in disMap]
    
    def move(self, newPos):
        self.pos = [self.pos[0]+newPos[0],self.pos[1]+newPos[1],self.pos[2]+newPos[2]]
        self.vert = Math3d.Transform(self.vert).translate(newPos)

    def rotate(self, axis, angle):
        if axis=="x":self.vert=Math3d.Transform(Math3d.Transform(Math3d.Transform(self.vert).translateFliped(self.pos)).RotX(angle)).translate(self.pos)
        if axis=="y":self.vert=Math3d.Transform(Math3d.Transform(Math3d.Transform(self.vert).translateFliped(self.pos)).RotY(angle)).translate(self.pos)
        if axis=="z":self.vert=Math3d.Transform(Math3d.Transform(Math3d.Transform(self.vert).translateFliped(self.pos)).RotZ(angle)).translate(self.pos)
    
    def clipTirangles(self,cam):
        NewVert = []
        clipedPos = None

        for y in range(len(self.tirangles)):

            v0 = self.vert[self.tirangles[y][0][0]]
            v1 = self.vert[self.tirangles[y][1][0]]
            v2 = self.vert[self.tirangles[y][2][0]]

            clipedPos = cam.clip_triangle(
                v0,v1,v2
            )

            NewVert.append(clipedPos)
        return NewVert

    def drawTriangle(self, display,SW,SH,FOV,light3d,cam,hasfog=False,fog_radus=None):
        NewVert = self.clipTirangles(cam)
        NewVert = self.sortTriangles(NewVert)

        if self.vert is not None:
            transfromVert = Math3d.Transform(NewVert).transform2d3(
                FOV, cam.NearPlane, SH, SW
            )
            for x in range(len(transfromVert)):
                Pos = transfromVert[x]

                v0, v1, v2 = NewVert[x]

                edge1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
                edge2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

                nx = edge1[1]*edge2[2] - edge1[2]*edge2[1]
                ny = edge1[2]*edge2[0] - edge1[0]*edge2[2]
                nz = edge1[0]*edge2[1] - edge1[1]*edge2[0]

                length = math.sqrt(nx*nx + ny*ny + nz*nz)

                if length == 0: continue

                normal = (nx / length, ny / length, nz / length)

                light_dir = light3d.get_light_dir((v0,v1,v2))
                ld_len = math.sqrt(sum(c*c for c in light_dir))
                light_dir = tuple(c / ld_len for c in light_dir)

                brightness = max(0.2, normal[0]*light_dir[0] + normal[1]*light_dir[1] + normal[2]*light_dir[2])

                shaded_color = tuple(
                    max(self.max_darkness, min(self.max_brightness, int(self.color[i] * brightness)))
                    for i in range(3)
                    )
                
                if hasfog:
                    shaded_color = light3d.add_fog(light3d.pos,(v0,v1,v2),fog_radus,shaded_color)

                pygame.draw.polygon(
                    display,
                    shaded_color,
                    [cam.center_object((Pos[0][0], Pos[0][1])),
                    cam.center_object((Pos[1][0], Pos[1][1])),
                    cam.center_object((Pos[2][0], Pos[2][1]))]
                )