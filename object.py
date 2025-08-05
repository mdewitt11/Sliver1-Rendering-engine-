from render import Core3d,textures,loadFile
import pygame

class Group:
    def __init__(self, objects=[],SW=900,SH=1000,FOV=0.5):
        self.objects = objects
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
        self.normals = self.model[2]
        self.texture = textures.Texture(display,pygame.image.load(texture).convert_alpha())
        self.vert = Core3d.Core3d(self.model[0]).translate(pos)

        self.dispaly = display
    
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

            vt0 = self.texture_cords[self.tirangles[y][0][1]]
            vt1 = self.texture_cords[self.tirangles[y][1][1]]
            vt2 = self.texture_cords[self.tirangles[y][2][1]]

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

            if clipedPos != None:
                NewVert.append((clipedPos, (vt0, vt1, vt2), (vn0, vn1, vn2)))

        return NewVert


    def drawModel(self,SW,SH,FOV,secne):
        NewVert = self.clipTirangles(secne)

        if self.vert is not None:
            transfromVert = Core3d.Core3d(NewVert).transform2d3(
                FOV, secne.NearPlane, SH, SW
            )
            for x in range(len(transfromVert)):
                face = transfromVert[x]
                old_vert = NewVert[x]
                Pos = face[0]
                Normals = face[2]

                lit_tint = (0,0,0)

                self.texture.triangle_texture(
                    (secne.center_object((Pos[0][0], Pos[0][1])),
                    secne.center_object((Pos[1][0], Pos[1][1])),
                    secne.center_object((Pos[2][0], Pos[2][1]))),
                    texture_coords=face[1],
                    tint=lit_tint,
                    z=(old_vert[0][0][2],old_vert[0][1][2],old_vert[0][2][2])
                )
            
        self.texture.clear_z()