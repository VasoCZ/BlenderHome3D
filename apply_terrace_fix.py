import bpy
import bmesh

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

slab = bpy.data.objects.get("Foundation_Slab")
mesh = slab.data
bm = bmesh.new()
bm.from_mesh(mesh)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()
uv_lay = bm.loops.layers.uv.verify()

# 1. Flatten all vertices to Z = 0.0
for v in bm.verts:
    if abs(v.co.z) > 1e-4:
        v.co.z = 0.0

# 2. Remove degenerate 0-area faces
deg = [f for f in bm.faces if f.calc_area() < 1e-5]
bmesh.ops.delete(bm, geom=deg, context='FACES')
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()

# 3. Remove the deformed diagonal terrace faces
mat_paving_idx = 0
for i, m in enumerate(slab.data.materials):
    if m and m.name == "Paving Stones":
        mat_paving_idx = i
        break

faces_to_remove = []
for f in bm.faces:
    verts_co = [v.co for v in f.verts]
    min_x = min(v.x for v in verts_co)
    max_x = max(v.x for v in verts_co)
    min_y = min(v.y for v in verts_co)
    max_y = max(v.y for v in verts_co)
    if min_x >= 4.99 and max_x <= 7.13 and min_y >= 11.99 and max_y <= 18.01:
        faces_to_remove.append(f)
    elif min_x >= 7.12 and max_x <= 8.20 and min_y >= 11.99 and max_y <= 13.21:
        faces_to_remove.append(f)

bmesh.ops.delete(bm, geom=faces_to_remove, context='FACES')
bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()

def get_or_create_vert(x, y, z=0.0):
    for v in bm.verts:
        if abs(v.co.x - x) < 0.001 and abs(v.co.y - y) < 0.001 and abs(v.co.z - z) < 0.001:
            return v
    return bm.verts.new((x, y, z))

new_quads_def = [
    [(5.000, 12.000), (7.125, 12.000), (7.125, 12.722), (5.000, 12.722)],
    [(5.000, 12.722), (7.125, 12.722), (7.125, 13.200), (5.000, 13.200)],
    [(5.000, 13.200), (7.125, 13.200), (7.125, 18.000), (5.000, 18.000)],
    [(7.125, 12.000), (8.190, 12.000), (8.190, 12.722), (7.125, 12.722)],
    [(7.125, 12.722), (8.190, 12.722), (8.190, 13.200), (7.125, 13.200)],
]

for coords in new_quads_def:
    v_list = [get_or_create_vert(x, y, 0.0) for x, y in coords]
    f = bm.faces.new(v_list)
    f.material_index = mat_paving_idx

bm.faces.ensure_lookup_table()
bm.verts.ensure_lookup_table()

# 4. Planar UVs across all terrace faces
for f in bm.faces:
    if f.material_index == mat_paving_idx:
        f_y = sum(v.co.y for v in f.verts) / len(f.verts)
        if f_y >= 11.8:
            for loop in f.loops:
                loop[uv_lay].uv = (loop.vert.co.x, loop.vert.co.y)

bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(mesh)
bm.free()
mesh.update()

# 5. Material displacement settings
mat = bpy.data.materials.get("Paving Stones")
if mat:
    if hasattr(mat, 'displacement_method'):
        mat.displacement_method = 'BUMP'
    if mat.node_tree:
        out_node = None
        for n in mat.node_tree.nodes:
            if n.type == 'OUTPUT_MATERIAL' and n.is_active_output:
                out_node = n
                break
        if out_node:
            disp_sock = out_node.inputs.get("Displacement")
            if disp_sock and disp_sock.is_linked:
                for link in list(disp_sock.links):
                    mat.node_tree.links.remove(link)

bpy.ops.wm.save_mainfile()
print("APPLIED_AND_SAVED_SUCCESSFULLY")
