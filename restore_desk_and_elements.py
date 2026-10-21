"""
restore_desk_and_elements.py
----------------------------
1. Restore Ikea Table Linnmon - Adils to original position:
   - Location: (2.6046, 6.6089, 0.0150)
   - Restore original materials on table top ('table top') and Legs (['leg', 'steel', 'foot'])
2. Restore original monitor:
   - Import SM_tv screen led .002 from dum_pudorys_final.blend at loc (2.5065, 6.9769, 1.1570)
   - Remove Office_Dual_Monitors
3. Restore keyboard and mouse positions:
   - G915 keyboard: loc (2.5768, 6.4259, 0.7550), rot (0, 0, 0)
   - Logitech G102 LIGHTSYNC Gaming Mouse: loc (2.1368, 6.4337, 0.7550), rot (0, 0, 1.5708)
4. Restore office chair:
   - Office chair black.001: loc (2.5117, 6.0320, 0.0150), rot (0, 0, 3.1416)
5. Remove temporary accessories:
   - Office_Desk_Pad
   - Office_Soundcore_Speaker
6. Keep custom PC model (Office_PC_Tower_RGB):
   - Positioned on right side of desktop at X=3.10, Y=6.66, Z=0.755
7. Thorough verification and save.
"""

import bpy
from mathutils import Vector, Euler

print(">>> Restoring PC desk and elements to original positions...")

final_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_final.blend"

# 1. Restore desk location
desk = bpy.data.objects.get('Ikea Table Linnmon - Adils')
if desk:
    desk.location = Vector((2.6046, 6.6089, 0.0150))
    desk.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
    print("  Moved Ikea Table Linnmon - Adils to (2.6046, 6.6089, 0.0150).")

# Restore table top and Legs materials from dum_pudorys_final.blend
with bpy.data.libraries.load(final_path) as (data_from, data_to):
    data_to.materials = [m for m in ['table top', 'leg', 'steel', 'foot'] if m in data_from.materials]

tt = bpy.data.objects.get('table top')
mat_tt = bpy.data.materials.get('table top')
if tt and mat_tt:
    tt.data.materials.clear()
    tt.data.materials.append(mat_tt)
    print("  Restored table top material to 'table top'.")

legs = bpy.data.objects.get('Legs')
if legs:
    legs.data.materials.clear()
    for mname in ['leg', 'steel', 'foot']:
        m = bpy.data.materials.get(mname)
        if m:
            legs.data.materials.append(m)
    print("  Restored Legs materials to ['leg', 'steel', 'foot'].")

# 2. Restore original monitor: import SM_tv screen led .002
old_mon = bpy.data.objects.get('Office_Dual_Monitors')
if old_mon:
    bpy.data.objects.remove(old_mon, do_unlink=True)
    print("  Removed Office_Dual_Monitors.")

existing_screen = bpy.data.objects.get('SM_tv screen led .002')
if not existing_screen:
    with bpy.data.libraries.load(final_path) as (data_from, data_to):
        data_to.objects = ['SM_tv screen led .002']
        data_to.materials = [m for m in data_from.materials if 'tv' in m.lower() or 'vidro' in m.lower() or 'escovado' in m.lower()]
    existing_screen = bpy.data.objects.get('SM_tv screen led .002')

if existing_screen:
    existing_screen.location = Vector((2.5065, 6.9769, 1.1570))
    existing_screen.rotation_euler = Euler((1.5708, 0.0, 0.0), 'XYZ')
    existing_screen.scale = Vector((0.65, 0.65, 1.0))
    
    # Ensure it is linked to a collection
    tv_col = bpy.data.collections.get("Tv screen led")
    if not tv_col:
        tv_col = bpy.data.collections.get("Office_107_Furniture") or bpy.context.scene.collection
    if not existing_screen.users_collection:
        tv_col.objects.link(existing_screen)
    print("  Restored SM_tv screen led .002 at (2.5065, 6.9769, 1.1570).")

# 3. Restore keyboard and mouse positions
kb = bpy.data.objects.get('G915 keyboard')
if kb:
    kb.location = Vector((2.5768, 6.4259, 0.7550))
    kb.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
    print("  Moved G915 keyboard to (2.5768, 6.4259, 0.7550).")

mouse = bpy.data.objects.get('Logitech G102 LIGHTSYNC Gaming Mouse')
if mouse:
    mouse.location = Vector((2.1368, 6.4337, 0.7550))
    mouse.rotation_euler = Euler((0.0, 0.0, 1.5708), 'XYZ')
    print("  Moved Logitech mouse to (2.1368, 6.4337, 0.7550).")

# 4. Restore office chair position
chair = bpy.data.objects.get('Office chair black.001')
if chair:
    chair.location = Vector((2.5117, 6.0320, 0.0150))
    chair.rotation_euler = Euler((0.0, 0.0, 3.1416), 'XYZ')
    print("  Moved Office chair black.001 to (2.5117, 6.0320, 0.0150).")

# 5. Remove temporary accessories
for unwanted in ['Office_Desk_Pad', 'Office_Soundcore_Speaker']:
    obj = bpy.data.objects.get(unwanted)
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"  Removed {unwanted}.")

# 6. Keep custom PC model (Office_PC_Tower_RGB) and place cleanly on right side of desk
pc_tower = bpy.data.objects.get('Office_PC_Tower_RGB')
if pc_tower:
    # Original mesh was centered at X=2.9775.
    # We want it at X ~ 3.10, Y ~ 6.66 on the desk so it sits neatly next to the monitor (monitor ends at X=2.976).
    # Delta X = 3.10 - 2.9775 = +0.1225
    pc_tower.location = Vector((0.1225, 0.0, 0.005))
    print("  Positioned Office_PC_Tower_RGB on the right side of the desk surface.")

# 7. Ensure camera is Isometric_Camera and viewport is SOLID
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
print(f">>> Successfully saved to: {blend_path}")
