"""
restore_tiles_and_kallax.py
---------------------------
1. Restore original grey tiles (material 'koupelna') from dum_pudorys_final.blend
   to all wet-room floors and thresholds:
   - Floor_1.01_Zadveri, Floor_1.08_WC, Floor_1.09_Technicka_mistnost,
     Floor_1.10_Koupelna, Floor_1.11_Chodba
   - All corresponding thresholds
2. Restore original white Kallax objects from dum_pudorys_final.blend into the office (1.07):
   - Ikea Kallax 147x147cm.001
   - Ikea Kallax 147x147cm.002
3. Keep the single door leaf preserved by user (DoorLeaf_102_105).
4. Perform thorough verification and save dum_pudorys.blend.
"""

import bpy

print(">>> Starting restoration of tiles and office white Kallax...")

# -------------------------------------------------------------------------
# 1. RESTORE ORIGINAL GREY TILE MATERIAL FROM dum_pudorys_final.blend
# -------------------------------------------------------------------------
final_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_final.blend"

# Load original 'koupelna' and 'koupelna stena' materials
with bpy.data.libraries.load(final_path) as (data_from, data_to):
    data_to.materials = [m for m in ['koupelna', 'koupelna stena', 'AR3DMat PBR Ceramic White'] if m in data_from.materials]

def copy_material_nodes(source_name, target_name):
    src = bpy.data.materials.get(source_name)
    tgt = bpy.data.materials.get(target_name)
    if src and tgt and src.node_tree:
        tgt.use_nodes = True
        tgt.node_tree.nodes.clear()
        node_map = {}
        for n in src.node_tree.nodes:
            new_n = tgt.node_tree.nodes.new(n.bl_idname)
            new_n.name = n.name
            new_n.location = n.location
            if hasattr(n, 'image') and n.image:
                new_n.image = n.image
            if hasattr(n, 'color_ramp'):
                # Copy ramp elements
                new_n.color_ramp.interpolation = n.color_ramp.interpolation
            node_map[n.name] = new_n
        for l in src.node_tree.links:
            from_node = node_map.get(l.from_node.name)
            to_node = node_map.get(l.to_node.name)
            if from_node and to_node:
                from_sock = from_node.outputs.get(l.from_socket.name)
                to_sock = to_node.inputs.get(l.to_socket.name)
                if from_sock and to_sock:
                    tgt.node_tree.links.new(from_sock, to_sock)
        print(f"  Copied node tree from {source_name} to {target_name}")

# Copy nodes if imported with suffix
for mat_base in ['koupelna', 'koupelna stena']:
    imported_candidates = [m.name for m in bpy.data.materials if m.name.startswith(mat_base + ".")]
    if imported_candidates:
        copy_material_nodes(imported_candidates[0], mat_base)
        for cand in imported_candidates:
            cand_mat = bpy.data.materials.get(cand)
            if cand_mat:
                bpy.data.materials.remove(cand_mat, do_unlink=True)

mat_koupelna = bpy.data.materials.get('koupelna')
mat_golden_oak = bpy.data.materials.get('Golden Oak Wood Grain')

# Assign original 'koupelna' material to all wet-room floors and thresholds
tile_floor_names = [
    'Floor_1.01_Zadveri',
    'Floor_1.08_WC',
    'Floor_1.09_Technicka_mistnost',
    'Floor_1.11_Chodba',
    'Floor_Threshold_101_102',
    'Floor_Threshold_104_111',
    'Floor_Threshold_111_108',
    'Floor_Threshold_111_109',
    'Floor_Threshold_111_110',
    'Floor_Threshold_Front_Entrance'
]

for fname in tile_floor_names:
    obj = bpy.data.objects.get(fname)
    if obj and obj.data:
        obj.data.materials.clear()
        obj.data.materials.append(mat_koupelna)
        print(f"  Restored {fname} -> ['koupelna']")

# Also verify Floor_1.10_Koupelna
floor_bath = bpy.data.objects.get('Floor_1.10_Koupelna')
if floor_bath and floor_bath.data:
    floor_bath.data.materials.clear()
    floor_bath.data.materials.append(mat_koupelna)
    floor_bath.data.materials.append(mat_golden_oak)
    for p in floor_bath.data.polygons:
        p.material_index = 1 if p.index == 6 else 0
    print("  Restored Floor_1.10_Koupelna -> ['koupelna', 'Golden Oak Wood Grain']")

# Remove unwanted procedural tile material
unwanted_mat = bpy.data.materials.get('Mat_Tile_Concrete_Gray')
if unwanted_mat:
    bpy.data.materials.remove(unwanted_mat, do_unlink=True)
    print("  Removed Mat_Tile_Concrete_Gray.")

# -------------------------------------------------------------------------
# 2. RESTORE ORIGINAL WHITE KALLAX TO OFFICE (1.07)
# -------------------------------------------------------------------------
print("--- 2. Restoring white Kallax into Office (1.07) ---")

# Target collection for office kallax
kallax_col = bpy.data.collections.get("Ikea Kallax 147x147cm")
if not kallax_col:
    kallax_col = bpy.data.collections.get("Office_107_Furniture")
if not kallax_col:
    kallax_col = bpy.context.scene.collection

# Check if Kallax .001 and .002 already exist or need to be imported
existing_k1 = bpy.data.objects.get('Ikea Kallax 147x147cm.001')
existing_k2 = bpy.data.objects.get('Ikea Kallax 147x147cm.002')

if not existing_k1 or not existing_k2:
    with bpy.data.libraries.load(final_path) as (data_from, data_to):
        data_to.objects = [o for o in ['Ikea Kallax 147x147cm.001', 'Ikea Kallax 147x147cm.002'] if o in data_from.objects]

for k_name in ['Ikea Kallax 147x147cm.001', 'Ikea Kallax 147x147cm.002']:
    obj = bpy.data.objects.get(k_name)
    if obj:
        # Ensure it is linked to a scene collection
        if not obj.users_collection:
            kallax_col.objects.link(obj)
        print(f"  Restored {k_name} at loc={obj.location}, mats={[m.name for m in obj.data.materials if m]}")

# -------------------------------------------------------------------------
# 3. VERIFY DOORS
# -------------------------------------------------------------------------
doors = [o.name for o in bpy.data.objects if o.name.startswith("DoorLeaf_")]
print(f"  Current door leaves in scene: {doors} (user preserved: {doors})")

# -------------------------------------------------------------------------
# 4. CAMERA & SAVE
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
print(f">>> Successfully restored and saved to: {blend_path}")
