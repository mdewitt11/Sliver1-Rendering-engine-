from render import Core3d,textures,loadFile
import pygame

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

        distance_to_light = Core3d.distance(center, light_cords)

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
        self.secne = Core3d.Secne(SW,SH,FOV)
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
        self.secne.update_screen(SH,SW)

    def sort_objects(self):
        obj = []
        for i in range(len(self.objects)):
            pos = self.objects[i].pos
            obj.append([Core3d.distance(pos,self.zero),self.objects[i]])
        obj.sort(key=lambda x: x[0],reverse=True)
        return obj
    
    def run(self):
        obj = self.sort_objects()
        for i in range(len(obj)):
            obj[i][1].drawModel(self.SW, self.SH, self.FOV,self.secne)

class Object3D:
    def __init__(self,model_path:str,pos,texture:str,display: pygame.Surface):
        self.model = loadFile.LoadObj(model_path)
        self.pos = pos
        self.texture_cords =self.model[1]
        self.tirangles = self.model[3]
        self.texture = textures.Texture(display,pygame.image.load(texture).convert_alpha())
        self.vert = Core3d.Core3d(self.model[0]).translate(pos)
    
    @staticmethod
    def sortTriangles(vert):
        disMap = []
        for i in range(len(vert)):
            tri = vert[i]

            try:
                z1 = tri[0][0][2]
                z2 = tri[0][1][2]
                z3 = tri[0][2][2]
                avg_z = (z1 + z2 + z3) / 3
            except:
                continue

            disMap.append([avg_z, tri[0],tri[1]])

        disMap.sort(key=lambda x: x[0], reverse=True)
        return [(a, b) for _, a, b in disMap]

    
    def move(self, newPos):
        self.pos = [self.pos[0]+newPos[0],self.pos[1]+newPos[1],self.pos[2]+newPos[2]]
        self.vert = Core3d.Core3d(self.vert).translate(newPos)

    def rotate(self, axis, angle):
        if axis=="x":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotX(angle)).translate(self.pos)
        if axis=="y":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotY(angle)).translate(self.pos)
        if axis=="z":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotZ(angle)).translate(self.pos)
    
    def clipTirangles(self,scene):
        NewVert = []
        clipedPos = None

        for y in range(len(self.tirangles)):

            v0 = self.vert[self.tirangles[y][0][0]]
            v1 = self.vert[self.tirangles[y][1][0]]
            v2 = self.vert[self.tirangles[y][2][0]]

            vt0 = self.texture_cords[self.tirangles[y][0][1]]
            vt1 = self.texture_cords[self.tirangles[y][1][1]]
            vt2 = self.texture_cords[self.tirangles[y][2][1]]

            clipedPos = scene.clip_triangle(
                v0,v1,v2
            )

            NewVert.append((clipedPos,(vt0,vt1,vt2)))
        return NewVert

    def drawModel(self,SW,SH,FOV,secne):
        NewVert = self.clipTirangles(secne)
        NewVert = self.sortTriangles(NewVert)

        if self.vert is not None:
            transfromVert = Core3d.Core3d(NewVert).transform2d3(
                FOV, secne.NearPlane, SH, SW
            )
            for x in range(len(transfromVert)):
                face = transfromVert[x]
                Pos = face[0]

                self.texture.triangle_texture(
                    (secne.center_object((Pos[0][0], Pos[0][1])),
                    secne.center_object((Pos[1][0], Pos[1][1])),
                    secne.center_object((Pos[2][0], Pos[2][1]))),
                    face[1]
                )