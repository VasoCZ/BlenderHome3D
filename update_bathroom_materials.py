import bpy
import bmesh
from mathutils import Vector

def update_materials_and_edges(blend_path):
    print("Opening", blend_path)
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    mat_plank_ext = bpy.data.materials.get('Plank stena')
    mat_plank_int = bpy.data.materials.get('Plank stena.001')
    mat_koupelna = bpy.data.materials.get('koupelna stena')

    # -----------------------------------------------------------------
    # 1. EXTERIOR_WALLS
    # -----------------------------------------------------------------
    ext = bpy.data.objects['Exterior_Walls']
    bpy.context.view_layer.objects.active = ext
    bpy.ops.object.mode_set(mode='OBJECT')

    # Slot 0: Mat_Exterior_Wall
    # Slot 1: koupelna stena
    # Slot 2: Plank stena
    idx_koupelna_ext = 1
    idx_plank_ext = 2

    bm = bmesh.new()
    bm.from_mesh(ext.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    # Find Top face 73 (above wood: Y in [9.90, 10.89], Z=1.8, normal +Z)
    # Find Top face 75 (above grey: Y in [10.89, 11.635], Z=1.8, normal +Z)
    for f in bm.faces:
        if abs(f.normal.z - 1.0) < 0.1 and abs(f.calc_center_median().x - 0.1825) < 0.05:
            cy = f.calc_center_median().y
            if 9.85 < cy < 10.89:
                print(f"Setting Exterior top face (wood side) {f.index} to Plank stena")
                f.material_index = idx_plank_ext
            elif 10.89 < cy < 11.64:
                print(f"Setting Exterior top face (grey side) {f.index} to koupelna stena")
                f.material_index = idx_koupelna_ext

    # Set clean UVs on top faces
    uv_layer = bm.loops.layers.uv.verify()
    for f in bm.faces:
        if abs(f.normal.z - 1.0) < 0.1 and abs(f.calc_center_median().x - 0.1825) < 0.05:
            cy = f.calc_center_median().y
            if 9.85 < cy < 10.89: # Plank stena on top
                for loop in f.loops:
                    v = loop.vert
                    # Map UV smoothly with vertical face
                    loop[uv_layer].uv = Vector((0.2383, 0.5731 + (v.co.y - 9.900)/(10.890 - 9.900) * (0.6333 - 0.5731)))
            elif 10.89 < cy < 11.64: # koupelna stena on top
                for loop in f.loops:
                    v = loop.vert
                    loop[uv_layer].uv = Vector(((11.635 - v.co.y)/(11.635 - 10.890) * 0.4140, 0.0))

    bm.to_mesh(ext.data)
    bm.free()
    ext.data.update()
    print("Exterior_Walls updated!")

    # -----------------------------------------------------------------
    # 2. INTERIOR_WALLS
    # -----------------------------------------------------------------
    int_obj = bpy.data.objects['Interior_Walls']
    bpy.context.view_layer.objects.active = int_obj
    bpy.ops.object.mode_set(mode='OBJECT')

    # Ensure koupelna stena is in slot 1
    if len(int_obj.material_slots) < 2:
        int_obj.data.materials.append(mat_koupelna)
    else:
        int_obj.material_slots[1].material = mat_koupelna
    
    idx_koupelna_int = 1
    idx_plank_int = 2 # Plank stena.001

    bm = bmesh.new()
    bm.from_mesh(int_obj.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.verify()

    for f in bm.faces:
        c = f.calc_center_median()
        # South wall inner face facing into bathroom (Y=9.900, normal +Y)
        if abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.900) < 0.02:
            # Face between X = 1.368 and X = 2.050: transition to koupelna stena!
            if 1.36 < c.x < 2.06:
                print(f"Setting Interior south wall front face {f.index} to koupelna stena")
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 1.368) / (2.050 - 1.368) * 0.4
                    v_coord = 1.0 if abs(v.co.z) < 0.1 else 0.0
                    loop[uv_layer].uv = Vector((u, v_coord))
            # Door post at X in [2.75, 2.875] facing into bathroom
            elif 2.74 < c.x < 2.88:
                print(f"Setting Interior door post face {f.index} to koupelna stena")
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 2.750) / (2.875 - 2.750) * 0.1
                    v_coord = 1.0 if abs(v.co.z) < 0.1 else 0.0
                    loop[uv_layer].uv = Vector((u, v_coord))

        # Top faces at Z = 1.800
        elif abs(f.normal.z - 1.0) < 0.1 and abs(c.y - 9.8375) < 0.05:
            # Top above shower wood cladding (X in [0.365, 1.368])
            if 0.36 < c.x < 1.37:
                print(f"Setting Interior top face (wood shower) {f.index} to Plank stena.001")
                f.material_index = idx_plank_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 0.365) / (1.368 - 0.365) * 0.5568
                    loop[uv_layer].uv = Vector((u, 0.0))
            # Top above south wall grey tile (X in [1.368, 2.050])
            elif 1.36 < c.x < 2.06:
                print(f"Setting Interior top face (grey tile) {f.index} to koupelna stena")
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 1.368) / (2.050 - 1.368) * 0.4
                    loop[uv_layer].uv = Vector((u, 0.0))
            # Top above door post (X in [2.75, 2.875])
            elif 2.74 < c.x < 2.88:
                print(f"Setting Interior top face (door post) {f.index} to koupelna stena")
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 2.750) / (2.875 - 2.750) * 0.1
                    loop[uv_layer].uv = Vector((u, 0.0))

    bm.to_mesh(int_obj.data)
    bm.free()
    int_obj.data.update()
    print("Interior_Walls updated!")

    # Save blend file
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("File saved successfully!")

if __name__ == '__main__':
    update_materials_and_edges("dum_pudorys_dobra.blend")
