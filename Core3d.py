import math

class Core3d:
    def __init__(self, vert):
        self.vert = vert

    def translate(self, Tcord):
        vert = []
        for x in range(len(self.vert)):
            cord = self.vert[x]
            if cord == None:
                continue
            if len(cord) != 3:
                continue

            vert.append([cord[0] + Tcord[0], cord[1] + Tcord[1], cord[2] + Tcord[2]])
        return vert
    
    def translateFliped(self, Tcord):
        vert = []
        for x in range(len(self.vert)):
            cord = self.vert[x]
            if cord == None:
                continue
            if len(cord) != 3:
                continue

            vert.append([cord[0] + -Tcord[0], cord[1] + -Tcord[1], cord[2] + -Tcord[2]])
        return vert


    def scale(self, Tcord):
        vert = []
        for x in range(len(self.vert)):
            cord = self.vert[x]
            vert.append([cord[0] * Tcord[0], cord[1] * Tcord[1], cord[2] * Tcord[2]])
        return vert

    def RotX(self, a):
        vert = []
        for cord in self.vert:
            x = cord[0]
            y = cord[1] * math.cos(a) - cord[2] * math.sin(a)
            z = cord[1] * math.sin(a) + cord[2] * math.cos(a)
            vert.append([x, y, z])
        return vert

    def RotY(self, a):
        vert = []
        for i in range(len(self.vert)):
            cord = self.vert[i]
            x = cord[2] * math.sin(a) + cord[0] * math.cos(a)
            y = cord[1]
            z = cord[2] * math.cos(a) - cord[0] * math.sin(a)
            vert.append([x, y, z])
        return vert

    def RotZ(self, a):
        vert = []
        for i in range(len(self.vert)):
            cord = self.vert[i]
            x = cord[0] * math.cos(a) - cord[1] * math.sin(a)
            y = cord[0] * math.sin(a) + cord[1] * math.cos(a)
            z = cord[2]
            vert.append([x, y, z])
        return vert
    
    def transform2d3(self, focal, Nearplane, SH1, SW1):
        AR = SW1 / SH1
        new_vert = []
        for i in range(len(self.vert)):
            face = self.vert[i]
            cord = face[0]

            if cord is None or cord[0] is None or cord[1] is None:
                continue

            x1 = -cord[0][0] + 0.0001
            y1 = -cord[0][1] + 0.0001
            z1 = -cord[0][2] + 0.0001

            x2 = -cord[1][0] + 0.0001
            y2 = -cord[1][1] + 0.0001
            z2 = -cord[1][2] + 0.0001

            x3 = -cord[2][0] + 0.0001
            y3 = -cord[2][1] + 0.0001
            z3 = -cord[2][2] + 0.0001

            if z1 > Nearplane:
                z1 = Nearplane
            if z2 > Nearplane:
                z2 = Nearplane
            if z3 > Nearplane:
                z3 = Nearplane

            new_vert.append(
                [
                    [
                        [focal * x1 / z1 * AR, focal * y1 / z1],
                        [focal * x2 / z2 * AR, focal * y2 / z2],
                        [focal * x3 / z3 * AR, focal * y3 / z3]
                    ],
                    face[1],
                    face[2]
                ]
            )
        return new_vert

class Secne:
    def __init__(self, ScreenWidth, ScreenHeight, fov):
        self.SH = ScreenHeight
        self.SW = ScreenWidth
        self.NearPlane = 0.1
        self.Farplane = 0
        self.fov_degrees = fov

    def center_object(self, cord):
        return (self.SW / 2 + cord[0], self.SH / 2 + cord[1])
    
    def update_screen(self,SH,SW):
        self.SH,self.SW = SH,SW

    def Flip(self, cord):
        vert = []
        for i in range(len(cord)):
            c = cord[i]
            vert.append([-c[0], -c[1], -c[2]])
        return vert

    def Zclip(self, cord1, cord2):
        NC1 = cord1[2]
        NC2 = cord2[2]

        #if NC1 < self.NearPlane and NC2 < self.NearPlane:
        #    return None

        p1 = cord1[:]
        p2 = cord2[:]

        if NC1 < self.NearPlane:
            t = (self.NearPlane - NC1) / (NC2 - NC1)
            p1 = [
                cord1[0] + t * (cord2[0] - cord1[0]),
                cord1[1] + t * (cord2[1] - cord1[1]),
                self.NearPlane
            ]

        if NC2 < self.NearPlane:
            t = (self.NearPlane - NC2) / (NC1 - NC2)
            p2 = [
                cord2[0] + t * (cord1[0] - cord2[0]),
                cord2[1] + t * (cord1[1] - cord2[1]),
                self.NearPlane
            ]

        return [p1, p2]

    
    
    def clip_triangle(self, cord1, cord2, cord3):
        def is_inside(v): return v[2] >= self.NearPlane

        inside = [v for v in [cord1, cord2, cord3] if is_inside(v)]
        outside = [v for v in [cord1, cord2, cord3] if not is_inside(v)]

        if len(inside) == 0:
            return None

        if len(inside) == 3:
            return [cord1, cord2, cord3]
        
        if len(inside) == 1:
            a = inside[0]
            b, c = outside
            clipped1 = self.Zclip(a, b)
            clipped2 = self.Zclip(a, c)
            if clipped1 is not None and clipped2 is not None:
                return [a, clipped1[1], clipped2[1]]

        if len(inside) == 2:
            a, b = inside
            c = outside[0]
            clipped1 = self.Zclip(a, c)
            clipped2 = self.Zclip(b, c)
            if clipped1 is not None and clipped2 is not None:
                return [a, b, clipped1[1]] 

        return None
    
def distance(a, b):
    return sum((a[i] - b[i])**2 for i in range(3)) ** 0.5