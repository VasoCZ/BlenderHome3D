import bpy
import mathutils

print("=== CHECKING TERRACE AND PAVING OBJECTS ===")
for obj in bpy.data.objects:
    name_lower = obj.name.lower()
    if any(k in name_lower for k in ['terrace', 'terasa', 'dlazb', 'paving', 'slab']):
        mods = [f"{m.name} ({m.type})" for m in obj.modifiers]
        mats = [m.name for m in obj.data.materials if m] if hasattr(obj.data, "materials") else []
        print(f"OBJ: {obj.name} | Type: {obj.type} | Loc: {obj.location} | Mods: {mods} | Mats: {mats}")

# Check materials: Paving Stones and Kombi_Paving
for mat_name in ['Paving Stones', 'Kombi_Paving', 'Mat_Terrace_Paving']:
    mat = bpy.data.materials.get(mat_name)
    if mat:
        print(f"\n=== MATERIAL: {mat_name} ===")
        if mat.use_nodes and mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type in ['DISPLACEMENT', 'BUMP', 'TEX_IMAGE', 'NORMAL_MAP']:
                    print(f"  Node: {node.name} ({node.type})")
                    if node.type == 'DISPLACEMENT':
                        print(f"    Inputs: {[i.name + ': ' + str(i.default_value) for i in node.inputs if hasattr(i, 'default_value')]}")
                    if node.type == 'BUMP':
                        print(f"    Bump strength: {node.inputs['Strength'].default_value}, distance: {node.inputs['Distance'].default_value}")
            # check displacement setting
            print(f"  displacement_method: {mat.cycles.displacement_method}")
