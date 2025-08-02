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
    
    def lighting(self,Normals,face):
        light_dir = self.get_light_dir(face)

        # Average the normals for flat lighting
        nx = (Normals[0][0] + Normals[1][0] + Normals[2][0]) / 3
        ny = (Normals[0][1] + Normals[1][1] + Normals[2][1]) / 3
        nz = (Normals[0][2] + Normals[1][2] + Normals[2][2]) / 3

        length = (nx**2 + ny**2 + nz**2) ** 0.5
        if length != 0:
                nx /= length
                ny /= length
                nz /= length

            # Dot product for diffuse lighting
        light = max(0.0, nx * light_dir[0] + ny * light_dir[1] + nz * light_dir[2])

            # Base tint color (example: pale gold)
        base_tint = (255, 200, 100)

            # Apply lighting to tint
        lit_tint = (
                int(base_tint[0] * light),
                int(base_tint[1] * light),
                int(base_tint[2] * light)
            )
        return lit_tint


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
        self.objects.append(object3d)

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
    
    def rotate_object(self, axis, a):
        for i in range(len(self.objects)):
            self.objects[i].rotate_object(axis,a)

    def rotate_camera(self, axis, a):
        for i in range(len(self.objects)):
            self.objects[i].rotate_camera(axis,a)
    
    def update_screen(self,SH,SW):
        self.secne.update_screen(SH,SW)

    def sort_objects(self):
        obj = []
        for i in range(len(self.objects)):
            pos = self.objects[i].pos
            obj.append([Core3d.distance(pos,self.zero),self.objects[i]])
        obj.sort(key=lambda x: x[0],reverse=True)
        return obj
    
    def run(self,display):
        obj = self.sort_objects()
        for i in range(len(obj)):
            obj[i][1].drawModel(self.SW, self.SH, self.FOV,self.secne,self.light)

class Object3D:
    def __init__(self,model_path:str,pos,texture:str,display: pygame.Surface):
        self.model = loadFile.LoadObj(model_path)
        self.pos = pos
        self.texture_cords =self.model[1]
        self.tirangles = self.model[3]
        self.normals = self.model[2]
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

            disMap.append([avg_z, tri[0],tri[1],tri[2]])

        disMap.sort(key=lambda x: x[0], reverse=True)
        return [(a, b, c) for _, a, b, c in disMap]

    
    def move(self, newPos):
        self.pos = [self.pos[0]+newPos[0],self.pos[1]+newPos[1],self.pos[2]+newPos[2]]
        self.vert = Core3d.Core3d(self.vert).translate(newPos)

    def rotate_object(self, axis, angle):
        if axis=="x":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotX(angle)).translate(self.pos)
        if axis=="y":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotY(angle)).translate(self.pos)
        if axis=="z":self.vert=Core3d.Core3d(Core3d.Core3d(Core3d.Core3d(self.vert).translateFliped(self.pos)).RotZ(angle)).translate(self.pos)

    def rotate_camera(self, axis, angle):
        if axis=="x":self.vert=Core3d.Core3d(self.vert).RotX(angle); self.pos = Core3d.Core3d([self.pos]).RotX(angle)[0]
        if axis=="y":self.vert=Core3d.Core3d(self.vert).RotY(angle); self.pos = Core3d.Core3d([self.pos]).RotY(angle)[0]
        if axis=="z":self.vert=Core3d.Core3d(self.vert).RotZ(angle); self.pos = Core3d.Core3d([self.pos]).RotZ(angle)[0]
    
    def calculate_face_normal(self,v0, v1, v2):
        # Compute vectors for two edges of the triangle
        edge1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        edge2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])

        # Cross product edge1 x edge2
        nx = edge1[1]*edge2[2] - edge1[2]*edge2[1]
        ny = edge1[2]*edge2[0] - edge1[0]*edge2[2]
        nz = edge1[0]*edge2[1] - edge1[1]*edge2[0]

        # Normalize the normal vector
        length = (nx*nx + ny*ny + nz*nz) ** 0.5
        if length == 0:
            return (0, 0, 0)
        return (nx/length, ny/length, nz/length)

    
    def clipTirangles(self, scene):
        NewVert = []

        for y in range(len(self.tirangles)):
            v0 = self.vert[self.tirangles[y][0][0]]
            v1 = self.vert[self.tirangles[y][1][0]]
            v2 = self.vert[self.tirangles[y][2][0]]

            vt0 = self.texture_cords[self.tirangles[y][0][1]] #if self.tirangles[y][0][1] is not None else (0, 0)
            vt1 = self.texture_cords[self.tirangles[y][1][1]] #if self.tirangles[y][1][1] is not None else (0, 0)
            vt2 = self.texture_cords[self.tirangles[y][2][1]] #if self.tirangles[y][2][1] is not None else (0, 0)

            # Check if any normal index is None
            normal_indices = [self.tirangles[y][0][2], self.tirangles[y][1][2], self.tirangles[y][2][2]]
            if None in normal_indices:
                # Calculate face normal using cross product
                face_normal = self.calculate_face_normal(v0, v1, v2)
                vn0 = vn1 = vn2 = face_normal
            else:
                vn0 = self.normals[self.tirangles[y][0][2]]
                vn1 = self.normals[self.tirangles[y][1][2]]
                vn2 = self.normals[self.tirangles[y][2][2]]

            clipedPos = scene.clip_triangle(v0, v1, v2)

            NewVert.append((clipedPos, (vt0, vt1, vt2), (vn0, vn1, vn2)))

        return NewVert


    def drawModel(self,SW,SH,FOV,secne,light:Light3D):
        NewVert = self.clipTirangles(secne)
        NewVert = self.sortTriangles(NewVert)

        if self.vert is not None:
            transfromVert = Core3d.Core3d(NewVert).transform2d3(
                FOV, secne.NearPlane, SH, SW
            )
            for x in range(len(transfromVert)):
                face = transfromVert[x]
                Pos = face[0]
                Normals = face[2]

                lit_tint = (0,0,0)#light.lighting(Normals,face[3])

                self.texture.triangle_texture(
                    (secne.center_object((Pos[0][0], Pos[0][1])),
                    secne.center_object((Pos[1][0], Pos[1][1])),
                    secne.center_object((Pos[2][0], Pos[2][1]))),
                    texture_coords=face[1],
                    tint=lit_tint
                )