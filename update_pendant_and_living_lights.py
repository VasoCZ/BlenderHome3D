"""
update_pendant_and_living_lights.py
-----------------------------------
1. Move the pendant light assembly so it is centered directly over the dining table:
   - Dining_Table center: X = 6.5325, Y = 10.4249.
   - Previous pendant center: X = 7.3000, Y = 10.2000.
   - Offset: dx = -0.7675, dy = +0.2249.
2. Update light spots to emanate directly from the pendant fixture:
   - Light_Dining_Spot_1 at (6.2525, 10.4249, 1.6800), rot (0, 0, 0)
   - Light_Dining_Spot_2 at (6.8125, 10.4249, 1.6800), rot (0, 0, 0)
3. In 1.04 (living / dining space), remove all other light sources except the pendant lights and v2, v3:
   - Remove: Light_1.04_Obyvaci_pokoj_V1_Dining
   - Remove: Light_1.04_Obyvaci_pokoj_V4_Center
   - Remove: Light_1.04_Obyvaci_pokoj_V5_Angle
   - Retain: Light_1.04_Obyvaci_pokoj_V2_Patio1 (v2)
   - Retain: Light_1.04_Obyvaci_pokoj_V3_Patio2 (v3)
4. Ensure Isometric_Camera is active and save dum_pudorys.blend.
"""

import bpy
from mathutils import Vector, Euler

print(">>> Starting update of pendant light and room lights...")

# 1. Calculate Dining Table center
dt = bpy.data.objects.get('Dining_Table')
if not dt:
    raise RuntimeError("Dining_Table not found!")

dt_bb = [dt.matrix_world @ Vector(v) for v in dt.bound_box]
t_cx = (min(v.x for v in dt_bb) + max(v.x for v in dt_bb)) / 2.0
t_cy = (min(v.y for v in dt_bb) + max(v.y for v in dt_bb)) / 2.0
t_top_z = max(v.z for v in dt_bb)

print(f"  Dining Table center: X={t_cx:.4f}, Y={t_cy:.4f}, Top Z={t_top_z:.4f}")

# Target pendant center: exactly (t_cx, t_cy)
# Current pendant bar center is (7.3000, 10.2000)
p_bar = bpy.data.objects.get('Pendant_Horizontal_Bar')
if p_bar:
    bar_bb = [p_bar.matrix_world @ Vector(v) for v in p_bar.bound_box]
    old_cx = (min(v.x for v in bar_bb) + max(v.x for v in bar_bb)) / 2.0
    old_cy = (min(v.y for v in bar_bb) + max(v.y for v in bar_bb)) / 2.0
else:
    old_cx = 7.3000
    old_cy = 10.2000

dx = t_cx - old_cx
dy = t_cy - old_cy
print(f"  Pendant translation offset: dx={dx:.4f}, dy={dy:.4f}")

# Shift all pendant mesh objects by (dx, dy, 0)
pendant_objs = [o for o in bpy.data.objects if 'pendant' in o.name.lower()]
for obj in pendant_objs:
    if obj.type == 'MESH':
        for v in obj.data.vertices:
            v.co.x += dx
            v.co.y += dy
        obj.data.update()
        print(f"  Translated mesh of {obj.name}")

# Rename objects for clean hierarchy
name_renames = [
    ("Pendant_Tube_7.02", "Pendant_Tube_1"),
    ("Pendant_Tube_7.58", "Pendant_Tube_2"),
    ("Pendant_LED_7.02", "Pendant_LED_1"),
    ("Pendant_LED_7.58", "Pendant_LED_2"),
    ("Pendant_Wire_6.95", "Pendant_Wire_1"),
    ("Pendant_Wire_7.65", "Pendant_Wire_2"),
]
for old_n, new_n in name_renames:
    o = bpy.data.objects.get(old_n)
    if o:
        o.name = new_n

# 2. Position light spots directly at the bottom of the two tubes
spot1_x = t_cx - 0.28
spot2_x = t_cx + 0.28
spot_y = t_cy
spot_z = 1.6800 # exactly at the LED surface pointing down

col_k = bpy.data.collections.get("Kitchen_Furniture") or bpy.context.scene.collection

spot1 = bpy.data.objects.get('Light_Dining_Spot_1')
if not spot1:
    sdata1 = bpy.data.lights.new('Light_Dining_Spot_1', 'SPOT')
    spot1 = bpy.data.objects.new('Light_Dining_Spot_1', sdata1)
    col_k.objects.link(spot1)

spot1.location = Vector((spot1_x, spot_y, spot_z))
spot1.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
spot1.data.type = 'SPOT'
spot1.data.energy = 85.0
spot1.data.color = (1.0, 0.94, 0.85)
spot1.data.spot_size = 1.2217 # ~70 deg
spot1.data.spot_blend = 0.35
print(f"  Set Light_Dining_Spot_1 at {spot1.location}")

spot2 = bpy.data.objects.get('Light_Dining_Spot_2')
if not spot2:
    sdata2 = bpy.data.lights.new('Light_Dining_Spot_2', 'SPOT')
    spot2 = bpy.data.objects.new('Light_Dining_Spot_2', sdata2)
    col_k.objects.link(spot2)

spot2.location = Vector((spot2_x, spot_y, spot_z))
spot2.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
spot2.data.type = 'SPOT'
spot2.data.energy = 85.0
spot2.data.color = (1.0, 0.94, 0.85)
spot2.data.spot_size = 1.2217 # ~70 deg
spot2.data.spot_blend = 0.35
print(f"  Set Light_Dining_Spot_2 at {spot2.location}")

# Also remove any duplicate or old Light_Dining_Table_Spot if present
old_spot = bpy.data.objects.get('Light_Dining_Table_Spot')
if old_spot:
    bpy.data.objects.remove(old_spot, do_unlink=True)
    print("  Removed obsolete Light_Dining_Table_Spot.")

# 3. In room 1.04, remove extraneous lights, keeping only v2, v3 and the pendant spots
lights_to_remove = [
    'Light_1.04_Obyvaci_pokoj_V1_Dining',
    'Light_1.04_Obyvaci_pokoj_V4_Center',
    'Light_1.04_Obyvaci_pokoj_V5_Angle'
]

for lname in lights_to_remove:
    obj = bpy.data.objects.get(lname)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"  Removed {lname}.")

# Verify kept lights in 1.04
for kept in ['Light_1.04_Obyvaci_pokoj_V2_Patio1', 'Light_1.04_Obyvaci_pokoj_V3_Patio2']:
    obj = bpy.data.objects.get(kept)
    if obj:
        print(f"  Kept light: {kept} at {obj.location}")

# 4. Ensure camera is Isometric_Camera and shading is SOLID
iso_cam = bpy.data.objects.get('Isometric_Camera')
if iso_cam:
    bpy.context.scene.camera = iso_cam

for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

# Save file
blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Successfully updated and saved to: {blend_path}")
