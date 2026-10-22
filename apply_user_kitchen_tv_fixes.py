"""
apply_user_kitchen_tv_fixes.py
Implements the 3 user requested fixes:
1. Move sink & faucet into corpus under Upper_Oak_Door_4 (West run):
   - Rotate sink & faucet -90 deg around Z so it faces East into kitchen aisle
   - Center at X=3.32, Y=11.378 (directly under Upper_Oak_Door_4)
   - Update Countertop_West to include sink cutout
   - Restore Countertop_North to a solid continuous slab
   - Add matching lower cabinet door & Gola under Upper_Oak_Door_4
2. TV_1.05_Active light orientation:
   - Set rotation to (90 deg, 0, -90 deg) with size=1.40 (Y) and size_y=0.84 (Z)
   - Landscape orientation matching screen, shining +X towards the bed
3. Oven handle material:
   - Create Mat_Kitchen_Oven_Handle matching Oven_Control_Panel's dark brushed steel
   - Eliminates intense specular sky reflection / white glare
"""

import bpy
import bmesh
from mathutils import Vector, Matrix, Euler
import math
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

print(">>> 1. Fixing Bedroom TV 1.05 Area Light Orientation...")
light_105 = bpy.data.objects.get("Light_1.05_Loznice_TV")
if light_105:
    # Target: local X along world -Y (horizontal), local Y along world +Z (vertical), local -Z along world +X (emission)
    light_105.location = Vector((6.300, 1.950, 1.723))
    light_105.rotation_euler = Euler((math.radians(90.0), 0.0, -math.radians(90.0)), 'XYZ')
    light_105.data.type = 'AREA'
    light_105.data.shape = 'RECTANGLE'
    light_105.data.size = 1.40    # Horizontal width along Y
    light_105.data.size_y = 0.84  # Vertical height along Z
    light_105.data.energy = 45.0
    light_105.data.color = (0.75, 0.88, 1.0)
    print("  Bedroom TV Area Light oriented horizontally (landscape) to match screen shape!")

print(">>> 2. Fixing Oven Handle Material...")
mat_handle = bpy.data.materials.get("Mat_Kitchen_Oven_Handle")
if not mat_handle:
    mat_handle = bpy.data.materials.new("Mat_Kitchen_Oven_Handle")
    mat_handle.use_nodes = True

bsdf_h = mat_handle.node_tree.nodes.get("Principled BSDF")
if bsdf_h:
    bsdf_h.inputs['Base Color'].default_value = (0.28, 0.29, 0.31, 1.0)
    bsdf_h.inputs['Metallic'].default_value = 0.95
    bsdf_h.inputs['Roughness'].default_value = 0.42
    bsdf_h.inputs['Specular IOR Level'].default_value = 0.5
    bsdf_h.inputs['Emission Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    bsdf_h.inputs['Emission Strength'].default_value = 0.0

for o_name in ['Oven_Handle', 'Oven_Handle_Post_L', 'Oven_Handle_Post_R']:
    obj = bpy.data.objects.get(o_name)
    if obj:
        obj.data.materials.clear()
        obj.data.materials.append(mat_handle)
        print(f"  Assigned Mat_Kitchen_Oven_Handle to {obj.name}")

print(">>> 3. Moving Sink and Faucet under Upper_Oak_Door_4...")
sink_objs = [o for o in bpy.data.objects if o.name.startswith(('Sink_', 'Faucet_')) and o.type == 'MESH']

# Current center at countertop level
c_old = Vector((3.930, 11.320, 0.900))

# Target center under Upper_Oak_Door_4
# West countertop X in [3.00, 3.62] -> center X = 3.32
# Upper_Oak_Door_4 Y in [11.12, 11.635] -> center Y = 11.378
c_new = Vector((3.320, 11.378, 0.900))
R = Matrix.Rotation(-math.pi / 2.0, 4, 'Z')

for o in sink_objs:
    bm = bmesh.new()
    bm.from_mesh(o.data)
    for v in bm.verts:
        w = o.matrix_world @ v.co
        rel = w - c_old
        w_new = c_new + (R @ rel)
        v.co = o.matrix_world.inverted() @ w_new
    bm.to_mesh(o.data)
    o.data.update()
    bm.free()

print(f"  Transformed {len(sink_objs)} sink & faucet parts to West run under Upper_Oak_Door_4!")

print(">>> 4. Updating Countertops...")
mat_oak = bpy.data.materials.get("Mat_Kronospan_K003_Gold_Craft_Oak")

# 4A. Solid North Countertop (reunify North run X: 3.62 to 5.85, Y: 11.015 to 11.635)
for name in ['Countertop_North_Front', 'Countertop_North_Back', 'Countertop_North_Left']:
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

cn_main = bpy.data.objects.get("Countertop_North_Right")
if cn_main:
    cn_main.name = "Countertop_North_Solid"
    bm = bmesh.new()
    res = bmesh.ops.create_cube(bm, size=1.0)
    dx = 5.850 - 3.620
    dy = 11.635 - 11.015
    dz = 0.900 - 0.862
    for v in res['verts']:
        v.co.x = 3.620 + (v.co.x + 0.5) * dx
        v.co.y = 11.015 + (v.co.y + 0.5) * dy
        v.co.z = 0.862 + (v.co.z + 0.5) * dz
    bm.to_mesh(cn_main.data)
    cn_main.data.update()
    bm.free()
    if mat_oak and mat_oak.name not in [m.name for m in cn_main.data.materials if m]:
        cn_main.data.materials.append(mat_oak)
    print("  Created solid Countertop_North_Solid!")

# 4B. Countertop_West with cutout for sink:
# Sink bounds in X: [3.070, 3.570], Y: [11.098, 11.658]
cw = bpy.data.objects.get("Countertop_West")
if cw:
    bm = bmesh.new()
    boxes = [
        ((3.000, 9.560, 0.862), (3.620, 11.098, 0.900)),
        ((3.000, 11.098, 0.862), (3.070, 11.635, 0.900)),
        ((3.570, 11.098, 0.862), (3.620, 11.635, 0.900)),
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

    bm.to_mesh(cw.data)
    cw.data.update()
    bm.free()
    if mat_oak and mat_oak.name not in [m.name for m in cw.data.materials if m]:
        cw.data.materials.append(mat_oak)
    print("  Updated Countertop_West with clean sink cutout!")

# 4C. Add matching lower cabinet door & Gola under Upper_Oak_Door_4
mat_black = bpy.data.materials.get("Mat_Kitchen_Black_Matte")
kitch_col = bpy.data.collections.get("Kitchen_Furniture")
if not kitch_col:
    kitch_col = scene.collection

door_west_sink = bpy.data.objects.get("Door_West_Sink_Module")
if not door_west_sink:
    m_door = bpy.data.meshes.new("Door_West_Sink_Module")
    door_west_sink = bpy.data.objects.new("Door_West_Sink_Module", m_door)
    kitch_col.objects.link(door_west_sink)

bm_d = bmesh.new()
res_d = bmesh.ops.create_cube(bm_d, size=1.0)
min_x, max_x = 3.585, 3.605
min_y, max_y = 11.020, 11.620
min_z, max_z = 0.100, 0.842
for v in res_d['verts']:
    v.co.x = min_x + (v.co.x + 0.5) * (max_x - min_x)
    v.co.y = min_y + (v.co.y + 0.5) * (max_y - min_y)
    v.co.z = min_z + (v.co.z + 0.5) * (max_z - min_z)
bm_d.to_mesh(door_west_sink.data)
door_west_sink.data.update()
bm_d.free()
door_west_sink.data.materials.clear()
if mat_black:
    door_west_sink.data.materials.append(mat_black)

gola_west_sink = bpy.data.objects.get("Gola_West_Sink_Module")
if not gola_west_sink:
    m_gola = bpy.data.meshes.new("Gola_West_Sink_Module")
    gola_west_sink = bpy.data.objects.new("Gola_West_Sink_Module", m_gola)
    kitch_col.objects.link(gola_west_sink)

bm_g = bmesh.new()
res_g = bmesh.ops.create_cube(bm_g, size=1.0)
min_x, max_x = 3.550, 3.585
min_y, max_y = 11.020, 11.620
min_z, max_z = 0.842, 0.862
for v in res_g['verts']:
    v.co.x = min_x + (v.co.x + 0.5) * (max_x - min_x)
    v.co.y = min_y + (v.co.y + 0.5) * (max_y - min_y)
    v.co.z = min_z + (v.co.z + 0.5) * (max_z - min_z)
bm_g.to_mesh(gola_west_sink.data)
gola_west_sink.data.update()
bm_g.free()
gola_west_sink.data.materials.clear()
if mat_black:
    gola_west_sink.data.materials.append(mat_black)

print("  Added Door_West_Sink_Module and Gola_West_Sink_Module under Upper_Oak_Door_4!")

bpy.ops.wm.save_mainfile()
print(">>> Successfully saved dum_pudorys.blend with all fixes!")
