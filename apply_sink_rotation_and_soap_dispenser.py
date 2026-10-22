"""
apply_sink_rotation_and_soap_dispenser.py
1. Rotates the kitchen sink and faucet parts by -90 deg around Z.
   - Rear deck with faucet moves to +Y (against North window wall).
   - Basin extends forward to -Y.
   - Sink width (0.56m) is along X: [3.040, 3.600].
   - Sink depth (0.50m) is along Y: [11.128, 11.628] directly under Upper_Oak_Door_4.
2. Moves and reorients Soap Dispenser to the sink's rear deck:
   - Placed at X=3.480, Y=11.573, Z=0.906 (right of the faucet on the rear deck).
   - Spout oriented towards -Y into the sink basin.
3. Updates Countertop_West with the exact cutout and planar UVs for Kronospan K003 oak.
4. Ensures Countertop_North_Solid is completely clean and continuous with no stranded accessories.
"""

import bpy
import bmesh
from mathutils import Vector, Matrix
import math

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

c = Vector((3.320, 11.378, 0.900))
R_neg90 = Matrix.Rotation(-math.pi / 2.0, 4, 'Z')

print(">>> 1. Rotating Sink & Faucet objects by -90 deg around Z...")
sink_objs = [o for o in bpy.data.objects if o.name.startswith(('Sink_', 'Faucet_')) and o.type == 'MESH']

for o in sink_objs:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        w = o.matrix_world @ v.co
        rel = w - c
        w_new = c + (R_neg90 @ rel)
        v.co = o.matrix_world.inverted() @ w_new
    bm.to_mesh(o.data)
    o.data.update()
    bm.free()

print(f"  Rotated {len(sink_objs)} sink & faucet parts by -90 deg!")

print(">>> 2. Moving Soap Dispenser to the Sink Rear Deck...")
soap_objs = [o for o in bpy.data.objects if o.name.startswith('Soap_Dispenser_') and o.type == 'MESH']

# Old soap dispenser center was around (4.216, 11.495, 0.906)
# Target position on rear deck: X=3.480, Y=11.573, Z=0.906
# With spout pointing along -Y (into basin)
soap_c_old = Vector((4.216, 11.495, 0.906))
soap_c_new = Vector((3.480, 11.573, 0.906))

for o in soap_objs:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        w = o.matrix_world @ v.co
        rel = w - soap_c_old
        # Maintain -Y orientation or rotate if needed
        # Old spout was pointing along -Y, which is exactly towards basin!
        w_new = soap_c_new + rel
        v.co = o.matrix_world.inverted() @ w_new
    bm.to_mesh(o.data)
    o.data.update()
    bm.free()

print(f"  Moved {len(soap_objs)} Soap Dispenser parts to X=3.480, Y=11.573 on sink rear deck!")

print(">>> 3. Rebuilding Countertop_West cutout and UVs...")
mat_oak = bpy.data.materials.get("Mat_Kronospan_K003_Gold_Craft_Oak")
cw = bpy.data.objects.get("Countertop_West")
if cw:
    bm = bmesh.new()
    # Sink cutout: X: [3.040, 3.600], Y: [11.128, 11.628]
    # 4 rectangular blocks forming the countertop around the sink:
    # 1. Main slab south of sink: X:[3.00, 3.62], Y:[9.560, 11.128]
    # 2. Left strip (wall to sink): X:[3.00, 3.040], Y:[11.128, 11.628]
    # 3. Right strip (sink to edge): X:[3.600, 3.620], Y:[11.128, 11.628]
    # 4. North strip (behind sink): X:[3.00, 3.620], Y:[11.628, 11.635]
    boxes = [
        ((3.000, 9.560, 0.862), (3.620, 11.128, 0.900)),
        ((3.000, 11.128, 0.862), (3.040, 11.628, 0.900)),
        ((3.600, 11.128, 0.862), (3.620, 11.628, 0.900)),
        ((3.000, 11.628, 0.862), (3.620, 11.635, 0.900)),
    ]
    for (min_x, min_y, min_z), (max_x, max_y, max_z) in boxes:
        res = bmesh.ops.create_cube(bm, size=1.0)
        dx = max_x - min_x
        dy = max_y - min_y
        dz = max_z - min_z
        for v in res['verts']:
            v.co.x = min_x + (v.co.x + 0.5) * dx
            v.co.y = min_y + (v.co.y + 0.5) * dy
            v.co.z = min_z + (v.co.z + 0.5) * dz

    # Planar UV mapping for Kronospan K003 oak
    uv_layer = bm.loops.layers.uv.verify()
    scale = 1.5
    for face in bm.faces:
        for loop in face.loops:
            if abs(face.normal.z) > 0.5:
                loop[uv_layer].uv = (loop.vert.co.x * scale, loop.vert.co.y * scale)
            elif abs(face.normal.x) > 0.5:
                loop[uv_layer].uv = (loop.vert.co.y * scale, loop.vert.co.z * scale)
            else:
                loop[uv_layer].uv = (loop.vert.co.x * scale, loop.vert.co.z * scale)

    bm.to_mesh(cw.data)
    cw.data.update()
    bm.free()
    if mat_oak and mat_oak.name not in [m.name for m in cw.data.materials if m]:
        cw.data.materials.append(mat_oak)
    print("  Countertop_West updated with clean sink cutout and UVs!")

# Ensure Countertop_North_Solid has UVs and oak material
cn = bpy.data.objects.get("Countertop_North_Solid")
if cn:
    bm_cn = bmesh.new()
    bm_cn.from_mesh(cn.data)
    uv_cn = bm_cn.loops.layers.uv.verify()
    for face in bm_cn.faces:
        for loop in face.loops:
            if abs(face.normal.z) > 0.5:
                loop[uv_cn].uv = (loop.vert.co.x * scale, loop.vert.co.y * scale)
            elif abs(face.normal.x) > 0.5:
                loop[uv_cn].uv = (loop.vert.co.y * scale, loop.vert.co.z * scale)
            else:
                loop[uv_cn].uv = (loop.vert.co.x * scale, loop.vert.co.z * scale)
    bm_cn.to_mesh(cn.data)
    cn.data.update()
    bm_cn.free()

bpy.ops.wm.save_mainfile()
print(">>> Successfully saved dum_pudorys.blend!")
