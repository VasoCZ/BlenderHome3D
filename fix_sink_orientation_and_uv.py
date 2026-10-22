import bpy
import bmesh
from mathutils import Vector, Matrix
import math

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

print(">>> 1. Correcting Sink Rotation (180 deg around center)...")
sink_objs = [o for o in bpy.data.objects if o.name.startswith(('Sink_', 'Faucet_')) and o.type == 'MESH']
c = Vector((3.320, 11.378, 0.900))
R180 = Matrix.Rotation(math.pi, 4, 'Z')

for o in sink_objs:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        w = o.matrix_world @ v.co
        rel = w - c
        w_new = c + (R180 @ rel)
        v.co = o.matrix_world.inverted() @ w_new
    bm.to_mesh(o.data)
    o.data.update()
    bm.free()

faucet = bpy.data.objects.get("Faucet_Main_Pillar")
deck = bpy.data.objects.get("Sink_Deck_Rear")
front = bpy.data.objects.get("Sink_Rim_Front")
print(f"  Faucet X: {faucet.matrix_world.translation.x:.3f} Y: {faucet.matrix_world.translation.y:.3f}")
print(f"  Deck Rear X: {deck.bound_box[0][0]:.3f} to {deck.bound_box[6][0]:.3f}")
print(f"  Front Rim X: {front.bound_box[0][0]:.3f} to {front.bound_box[6][0]:.3f}")

print(">>> 2. Adding UV mapping to Countertop_West and Countertop_North_Solid...")
def add_planar_uv(obj, scale=1.5):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        for loop in face.loops:
            # Top/bottom faces (normal Z)
            if abs(face.normal.z) > 0.5:
                loop[uv_layer].uv = (loop.vert.co.x * scale, loop.vert.co.y * scale)
            # Side faces (normal X)
            elif abs(face.normal.x) > 0.5:
                loop[uv_layer].uv = (loop.vert.co.y * scale, loop.vert.co.z * scale)
            # Front/back faces (normal Y)
            else:
                loop[uv_layer].uv = (loop.vert.co.x * scale, loop.vert.co.z * scale)
    bm.to_mesh(obj.data)
    obj.data.update()
    bm.free()

cw = bpy.data.objects.get("Countertop_West")
if cw:
    add_planar_uv(cw, scale=1.5)
    print("  Added UVs to Countertop_West")

cn = bpy.data.objects.get("Countertop_North_Solid")
if cn:
    add_planar_uv(cn, scale=1.5)
    print("  Added UVs to Countertop_North_Solid")

bpy.ops.wm.save_mainfile()
print(">>> Saved dum_pudorys.blend!")
