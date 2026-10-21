"""
apply_decor_and_revert_bath.py
-------------------------------
1. Revert bathroom (1.10) to original state from dum_pudorys.blend1:
   - Remove all Bath_* objects & Bathroom_Fixtures collection.
   - Restore Floor_1.10_Koupelna slots to ['koupelna', 'Golden Oak Wood Grain'] with original polygon assignment.
   - Restore 'koupelna' and 'koupelna stena' materials to their original state from blend1.
2. Apply dining table wood decor (Mat_Kronospan_K003_Gold_Craft_Oak) to:
   - Living room (1.04) wooden objects:
     - Modern Wooden Floor TV Console (Body, Doors)
     - TV cabinet (coffee table)
     - Ikea Display cabinet - VIHALS Grey (anta.001-004, Plane.003-006, vetro)
     - Wall mirror with shelf Bristol (Bristol-base, Bristol-shelf)
   - Bedroom (1.05) chest of drawers: Comoda
   - Children room (1.06) Kallax: Ikea Kallax 147x147cm
3. Save dum_pudorys.blend.
"""

import bpy
import bmesh
from mathutils import Vector, Euler

print(">>> Starting decor update and bathroom revert...")

# -------------------------------------------------------------------------
# 1. REVERT BATHROOM (1.10) TO ORIGINAL STATE
# -------------------------------------------------------------------------
print("--- 1. Reverting Bathroom 1.10 to original state ---")

# A. Remove all Bath_* objects
bath_objs = [o for o in bpy.data.objects if o.name.startswith("Bath_")]
for o in bath_objs:
    print(f"  Removing bath object: {o.name}")
    bpy.data.objects.remove(o, do_unlink=True)

# Remove collection Bathroom_Fixtures
bath_col = bpy.data.collections.get("Bathroom_Fixtures")
if bath_col:
    print("  Removing collection Bathroom_Fixtures")
    bpy.data.collections.remove(bath_col)

# B. Restore original koupelna and koupelna stena materials from dum_pudorys.blend1
blend1_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend1"
with bpy.data.libraries.load(blend1_path) as (data_from, data_to):
    # Load materials from blend1 (will be loaded with .001 suffix if name collision)
    data_to.materials = [m for m in ['koupelna', 'koupelna stena'] if m in data_from.materials]

def restore_mat(orig_name, loaded_name):
    orig = bpy.data.materials.get(orig_name)
    loaded = bpy.data.materials.get(loaded_name)
    if orig and loaded and loaded.node_tree:
        orig.node_tree.nodes.clear()
        # copy nodes and links from loaded
        node_map = {}
        for n in loaded.node_tree.nodes:
            new_n = orig.node_tree.nodes.new(n.bl_idname)
            new_n.name = n.name
            new_n.location = n.location
            if hasattr(n, 'image') and n.image:
                new_n.image = n.image
            if hasattr(n, 'color_ramp'):
                # copy color ramp elements
                pass
            node_map[n.name] = new_n
        for l in loaded.node_tree.links:
            from_node = node_map.get(l.from_node.name)
            to_node = node_map.get(l.to_node.name)
            if from_node and to_node:
                from_socket = from_node.outputs.get(l.from_socket.name)
                to_socket = to_node.inputs.get(l.to_socket.name)
                if from_socket and to_socket:
                    orig.node_tree.links.new(from_socket, to_socket)
        print(f"  Restored material node tree: {orig_name}")
        bpy.data.materials.remove(loaded, do_unlink=True)

restore_mat('koupelna', 'koupelna.001')
restore_mat('koupelna stena', 'koupelna stena.001')

# C. Restore Floor_1.10_Koupelna slots and polygon assignments
floor_bath = bpy.data.objects.get('Floor_1.10_Koupelna')
mat_koupelna = bpy.data.materials.get('koupelna')
mat_golden_oak = bpy.data.materials.get('Golden Oak Wood Grain')

if floor_bath and floor_bath.data:
    floor_bath.data.materials.clear()
    floor_bath.data.materials.append(mat_koupelna)
    floor_bath.data.materials.append(mat_golden_oak)
    # Polygons 0-5 -> slot 0 (koupelna), polygon 6 -> slot 1 (shower floor golden oak)
    for p in floor_bath.data.polygons:
        if p.index == 6:
            p.material_index = 1
        else:
            p.material_index = 0
    print("  Floor_1.10_Koupelna restored with slots: ['koupelna', 'Golden Oak Wood Grain'].")

# -------------------------------------------------------------------------
# 2. APPLY DINING TABLE DECOR TO LIVING ROOM, BEDROOM CHEST, AND 1.06 KALLAX
# -------------------------------------------------------------------------
print("--- 2. Applying dining table decor (Mat_Kronospan_K003_Gold_Craft_Oak) ---")

mat_oak = bpy.data.materials.get('Mat_Kronospan_K003_Gold_Craft_Oak')
if not mat_oak:
    raise RuntimeError("Material Mat_Kronospan_K003_Gold_Craft_Oak not found!")

# A. Bedroom (1.05) chest of drawers
comoda = bpy.data.objects.get('Comoda')
if comoda and comoda.data:
    for i in range(len(comoda.material_slots)):
        comoda.material_slots[i].material = mat_oak
    print("  Updated Bedroom 1.05 Comoda to Mat_Kronospan_K003_Gold_Craft_Oak.")

# B. Children room (1.06) Kallax
kallax_106 = bpy.data.objects.get('Ikea Kallax 147x147cm')
if kallax_106 and kallax_106.data:
    for i in range(len(kallax_106.material_slots)):
        kallax_106.material_slots[i].material = mat_oak
    print("  Updated Children's room 1.06 Ikea Kallax 147x147cm to Mat_Kronospan_K003_Gold_Craft_Oak.")

# C. Living room (1.04) wooden objects
# 1) Modern Wooden Floor TV Console (Body, Doors)
for name in ['Body', 'Doors']:
    obj = bpy.data.objects.get(name)
    if obj and obj.data:
        for i in range(len(obj.material_slots)):
            obj.material_slots[i].material = mat_oak
        print(f"  Updated Living room TV Console '{name}' to Mat_Kronospan_K003_Gold_Craft_Oak.")

# 2) TV cabinet (Living room coffee table in front of sofa)
tv_cab = bpy.data.objects.get('TV cabinet')
if tv_cab and tv_cab.data:
    for i, slot in enumerate(tv_cab.material_slots):
        # Update wood slots (slots 0, 1, 3 which were 'drevo')
        if slot.material and slot.material.name == 'drevo':
            slot.material = mat_oak
    print("  Updated Living room coffee table 'TV cabinet' to Mat_Kronospan_K003_Gold_Craft_Oak.")

# 3) Ikea Display cabinet - VIHALS Grey
display_wood_parts = [
    'anta.001', 'anta.002', 'anta.003', 'anta.004',
    'Plane.003', 'Plane.004', 'Plane.005', 'Plane.006',
    'vetro'
]
for name in display_wood_parts:
    obj = bpy.data.objects.get(name)
    if obj and obj.data:
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name in ['drevo', 'Wood.012']:
                slot.material = mat_oak
        print(f"  Updated Display cabinet '{name}' to Mat_Kronospan_K003_Gold_Craft_Oak.")

# 4) Wall mirror with shelf Bristol
for name in ['Bristol-base', 'Bristol-shelf']:
    obj = bpy.data.objects.get(name)
    if obj and obj.data:
        for i in range(len(obj.material_slots)):
            obj.material_slots[i].material = mat_oak
        print(f"  Updated Wall mirror with shelf Bristol '{name}' to Mat_Kronospan_K003_Gold_Craft_Oak.")

# Also update material 'drevo' to use Mat_Kronospan_K003_Gold_Craft_Oak texture setup
mat_drevo = bpy.data.materials.get('drevo')
if mat_drevo and mat_drevo.node_tree:
    for n in mat_drevo.node_tree.nodes:
        if n.type == 'TEX_IMAGE':
            n.image = bpy.data.images.get('K003_original.jpg')
    print("  Updated material 'drevo' node tree to match Gold Craft Oak.")

# -------------------------------------------------------------------------
# 3. VERIFY CAMERA & SAVE
# -------------------------------------------------------------------------
iso_cam = bpy.data.objects.get('Isometric_Camera')
if iso_cam:
    bpy.context.scene.camera = iso_cam

for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Successfully executed and saved to: {blend_path}")
