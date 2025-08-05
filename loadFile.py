
def LoadObj(fileName):
    with open(fileName, "r") as file:
        vertices = []
        texcoords = []
        normals = []
        faces = []

        for line in file:
            line = line.strip()
            #if not line or line.startswith('#'):
            #    continue

            if line.startswith("v "):  # Vertex
                parts = line.split()
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                vertices.append((x, y, z))

            elif line.startswith("vt "):  # Texture coord
                parts = line.split()
                u, v = float(parts[1]), float(parts[2])
                texcoords.append((u, v))

            elif line.startswith("vn "):  # Normal
                parts = line.split()
                nx, ny, nz = float(parts[1]), float(parts[2]), float(parts[3])
                normals.append((nx, ny, nz))

            elif line.startswith("f "):  # Face
                parts = line[2:].split()
                raw_face = []
                for part in parts:
                    vals = part.split('/')
                    vi = int(vals[0]) - 1
                    vti = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else None
                    vni = int(vals[2]) - 1 if len(vals) > 2 and vals[2] else None
                    raw_face.append((vi, vti, vni))

                # Fan triangulate faces with more than 3 vertices
                if len(raw_face) == 3:
                    faces.append(raw_face)
                elif len(raw_face) > 3:   
                    for i in range(1, len(raw_face)-1):
                        tri = [raw_face[0], raw_face[i], raw_face[i+1]]
                        faces.append(tri)

    return vertices, texcoords, normals, faces
