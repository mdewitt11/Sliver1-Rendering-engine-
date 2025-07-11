
def LoadObj(fileName):
    with open(fileName, "r") as file:
        vertices = []
        texcoords = []
        normals = []
        faces = []

        for line in file:
            if line.startswith("v "):
                _, x, y, z = line.strip().split()
                vertices.append((float(x), float(y), float(z)))

            elif line.startswith("vt "):
                _, u, v = line.strip().split()
                texcoords.append((float(u), float(v)))

            elif line.startswith("vn "):
                _, nx, ny, nz = line.strip().split()
                normals.append((float(nx), float(ny), float(nz)))

            elif line.startswith("f "):
                parts = line.strip().split()[1:]
                face = []
                for part in parts:
                    vals = part.split("/")
                    vi = int(vals[0]) - 1
                    vti = int(vals[1]) - 1 if len(vals) > 1 and vals[1] != '' else None
                    vni = int(vals[2]) - 1 if len(vals) > 2 and vals[2] != '' else None
                    face.append((vi, vti, vni))
                if len(face) == 3:
                    faces.append(face)
                elif len(face) > 3:
                    # Fan triangulate quads/ngons
                    for i in range(1, len(face) - 1):
                        faces.append([face[0], face[i], face[i + 1]])

        return vertices, texcoords, normals, faces