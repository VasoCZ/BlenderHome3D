import bpy
import bmesh
from mathutils import Vector

def fix_bathroom_walls(filepath):
    print(f"Loading {filepath}...")
    bpy.ops.wm.open_mainfile(filepath=filepath)
    
    # Ensure object mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # ==========================================
    # 1. FIX EXTERIOR_WALLS
    # ==========================================
    ext_obj = bpy.data.objects.get('Exterior_Walls')
    if not ext_obj:
        raise RuntimeError("Exterior_Walls object not found!")

    bpy.context.view_layer.objects.active = ext_obj
    ext_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(ext_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Find relevant vertices
    # Inner corner at room 1.09 window/opening: (0.365, 9.175, 1.8), (0.365, 9.175, 1.75)
    # Inner corner at bathroom South: (0.365, 9.900, 0.0) and (0.365, 9.900, 1.8)
    # Shower / wall split: (0.365, 10.890, 0.0) and (0.365, 10.890, 1.8)
    # Inner corner at North wall: (0.365, 11.635, 0.0) [idx 65] and (0.365, 11.635, 1.8) [idx 67]
    # Outer vertices at X=0.0: (0.0, 9.175, 1.8) [idx 87], (0.0, 9.900, 1.8), (0.0, 11.635, 1.8) [idx 36], (0.0, 11.635, 0.0) [idx 32]

    # Let's clean up faces in Exterior_Walls:
    # Identify faces: 45, 72, 74, 71, 73
    # Face 45 is the big inner face
    # Face 72 is the shower face (Plank stena)
    # Face 74 is the tile face (koupelna stena)
    # Face 71 is the top face [9.175 -> 9.900]
    # Face 73 is the top face [9.900 -> 11.635]

    # Let's inspect faces around Y in [9.0, 11.7] on inner wall X=0.365
    print("\n--- Processing Exterior_Walls ---")
    
    # Snap existing vertices to exact mathematical coordinates
    # Vert 112 was (0.365, 9.9008, 1.8) -> snap to (0.365, 9.9000, 1.8)
    # Vert 113 was (0.0, 9.9008, 1.8) -> snap to (0.0, 9.9000, 1.8)
    # Vert 114 was (0.365, 10.8898, 0.0) -> snap to (0.365, 10.8900, 0.0)
    # Vert 116 was (0.365, 10.9035, 1.8) -> snap to (0.365, 10.8900, 1.8)
    # Vert 115 was (0.365, 9.897, 0.0265) -> snap to (0.365, 9.9000, 0.0)
    v_ext_map = {}
    for v in bm.verts:
        if abs(v.co.x - 0.365) < 0.01:
            if abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.365, 9.900, 1.8))
                v_ext_map['inner_990_top'] = v
            elif abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 0.0) < 0.05:
                v.co = Vector((0.365, 9.900, 0.0))
                v_ext_map['inner_990_bot'] = v
            elif abs(v.co.y - 10.890) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.365, 10.890, 1.8))
                v_ext_map['inner_1089_top'] = v
            elif abs(v.co.y - 10.890) < 0.05 and abs(v.co.z - 0.0) < 0.05:
                v.co = Vector((0.365, 10.890, 0.0))
                v_ext_map['inner_1089_bot'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v.co = Vector((0.365, 11.635, 1.8))
                v_ext_map['inner_1163_top'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v.co = Vector((0.365, 11.635, 0.0))
                v_ext_map['inner_1163_bot'] = v
            elif abs(v.co.y - 9.175) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext_map['inner_917_top'] = v
            elif abs(v.co.y - 0.365) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_ext_map['inner_036_bot'] = v
        elif abs(v.co.x - 0.0) < 0.01:
            if abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.0, 9.900, 1.8))
                v_ext_map['outer_990_top'] = v
            elif abs(v.co.y - 9.175) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext_map['outer_917_top'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext_map['outer_1163_top'] = v

    print("Exterior mapped verts:", {k: (v.index, tuple(round(c, 3) for c in v.co)) for k, v in v_ext_map.items()})

    # Now let's fix Face 45:
    # Face 45 previously had: (0.365, 0.365, 0.0) -> (0.365, 10.8898, 0.0) -> (0.365, 9.897, 0.0265) -> (0.365, 9.9008, 1.8) -> (0.365, 9.175, 1.8)
    # It must NOT visit (0.365, 10.8898, 0.0)!
    # It should visit: ... -> (0.365, 0.365, 0.0) -> (0.365, 9.900, 0.0) -> (0.365, 9.900, 1.8) -> (0.365, 9.175, 1.8) -> ...
    f45 = None
    for f in bm.faces:
        if v_ext_map.get('inner_036_bot') in f.verts and v_ext_map.get('inner_917_top') in f.verts:
            f45 = f
            break

    if f45:
        print(f"Found Face 45: index {f45.index}")
        # Recreate Face 45 cleanly
        verts_45 = [v for v in f45.verts]
        # Remove inner_1089_bot from verts_45 if present
        clean_verts_45 = []
        for v in verts_45:
            # Skip any vert that is inside bathroom (y > 9.901)
            if v.co.y > 9.901:
                continue
            clean_verts_45.append(v)
        
        # Ensure inner_990_bot and inner_990_top are in the sequence in correct order
        # Let's inspect the order of clean_verts_45:
        # We want: ... inner_036_bot -> inner_990_bot -> inner_990_top -> inner_917_top ...
        bm.faces.remove(f45)
        # Build ordered list
        ordered_45 = []
        for v in clean_verts_45:
            if v == v_ext_map.get('inner_990_bot') or v == v_ext_map.get('inner_990_top'):
                continue
            ordered_45.append(v)
            if v == v_ext_map.get('inner_036_bot'):
                ordered_45.append(v_ext_map['inner_990_bot'])
                ordered_45.append(v_ext_map['inner_990_top'])

        new_f45 = bm.faces.new(ordered_45)
        new_f45.material_index = 0
        new_f45.normal_update()
        print("Recreated Face 45 cleanly with", len(new_f45.verts), "verts")

    # Now fix Face 72 (shower wall, Plank stena)
    # Must be quad: inner_990_bot -> inner_1089_bot -> inner_1089_top -> inner_990_top
    # Remove old Face 72 and Face 74
    old_faces_to_remove = []
    for f in bm.faces:
        if f.material_index in [1, 2]: # Plank stena or koupelna stena
            old_faces_to_remove.append(f)
    for f in old_faces_to_remove:
        bm.faces.remove(f)

    # Create clean Face 72 (Plank stena, mat_index = 2)
    f72_verts = [
        v_ext_map['inner_990_bot'],
        v_ext_map['inner_1089_bot'],
        v_ext_map['inner_1089_top'],
        v_ext_map['inner_990_top']
    ]
    new_f72 = bm.faces.new(f72_verts)
    new_f72.material_index = 2 # Plank stena
    new_f72.normal_update()

    # Create clean Face 74 (koupelna stena, mat_index = 1)
    # inner_1089_bot -> inner_1163_bot -> inner_1163_top -> inner_1089_top
    f74_verts = [
        v_ext_map['inner_1089_bot'],
        v_ext_map['inner_1163_bot'],
        v_ext_map['inner_1163_top'],
        v_ext_map['inner_1089_top']
    ]
    new_f74 = bm.faces.new(f74_verts)
    new_f74.material_index = 1 # koupelna stena
    new_f74.normal_update()

    # Fix top face Face 73:
    # Previously: (0.365, 10.9035, 1.8), (0.365, 11.635, 1.8), (0.0, 11.635, 1.8), (0.0, 9.9008, 1.8), (0.365, 9.9008, 1.8)
    # Find and recreate top face over bathroom
    for f in list(bm.faces):
        if abs(f.normal.z - 1.0) < 0.1 and any(abs(v.co.y - 10.5) < 0.5 for v in f.verts) and any(v.co.x < 0.2 for v in f.verts):
            bm.faces.remove(f)

    # Add outer top vertex at (0.0, 10.890, 1.8) for clean quad top faces
    v_outer_1089_top = bm.verts.new((0.0, 10.890, 1.8))
    v_ext_map['outer_1089_top'] = v_outer_1089_top

    # Top Quad 1 (above shower: 9.900 to 10.890)
    # inner_990_top -> inner_1089_top -> outer_1089_top -> outer_990_top
    f_top1 = bm.faces.new([
        v_ext_map['inner_990_top'],
        v_ext_map['inner_1089_top'],
        v_ext_map['outer_1089_top'],
        v_ext_map['outer_990_top']
    ])
    f_top1.material_index = 0
    f_top1.normal_update()

    # Top Quad 2 (above rest: 10.890 to 11.635)
    # inner_1089_top -> inner_1163_top -> outer_1163_top -> outer_1089_top
    f_top2 = bm.faces.new([
        v_ext_map['inner_1089_top'],
        v_ext_map['inner_1163_top'],
        v_ext_map['outer_1163_top'],
        v_ext_map['outer_1089_top']
    ])
    f_top2.material_index = 0
    f_top2.normal_update()

    # Outer wall face (Face 47, normal -X):
    # Check if outer_990_top and outer_1163_top are in Face 47, insert outer_1089_top between them
    for f in bm.faces:
        if v_ext_map['outer_990_top'] in f.verts and v_ext_map['outer_1163_top'] in f.verts and f.normal.x < -0.8:
            verts_47 = [v for v in f.verts]
            idx_990 = verts_47.index(v_ext_map['outer_990_top'])
            idx_1163 = verts_47.index(v_ext_map['outer_1163_top'])
            bm.faces.remove(f)
            # Insert outer_1089_top in proper position
            new_verts_47 = []
            for i, v in enumerate(verts_47):
                new_verts_47.append(v)
                if (i == idx_990 and (i + 1) % len(verts_47) == idx_1163):
                    new_verts_47.append(v_outer_1089_top)
                elif (i == idx_1163 and (i + 1) % len(verts_47) == idx_990):
                    new_verts_47.append(v_outer_1089_top)
            new_f47 = bm.faces.new(new_verts_47)
            new_f47.material_index = 0
            new_f47.normal_update()
            break

    # Bottom face (Face 40, normal -Z):
    # Ensure inner edge has inner_036_bot -> inner_990_bot -> inner_1089_bot -> inner_1163_bot
    for f in list(bm.faces):
        if f.normal.z < -0.8 and v_ext_map['inner_036_bot'] in f.verts and v_ext_map['inner_1163_bot'] in f.verts:
            verts_40 = [v for v in f.verts]
            bm.faces.remove(f)
            new_verts_40 = []
            for v in verts_40:
                if v == v_ext_map['inner_036_bot']:
                    new_verts_40.extend([v, v_ext_map['inner_990_bot'], v_ext_map['inner_1089_bot']])
                elif v not in [v_ext_map['inner_990_bot'], v_ext_map['inner_1089_bot']]:
                    new_verts_40.append(v)
            new_f40 = bm.faces.new(new_verts_40)
            new_f40.material_index = 0
            new_f40.normal_update()
            break

    # Fix UVs on Exterior_Walls
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

    # Set clean UVs on new_f72 (Plank stena)
    for loop in new_f72.loops:
        v = loop.vert
        if abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.3465, 0.5731))
        elif abs(v.co.y - 10.890) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.3465, 0.6333))
        elif abs(v.co.y - 10.890) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.2383, 0.6333))
        elif abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.2383, 0.5731))

    # Set clean UVs on new_f74 (koupelna stena)
    for loop in new_f74.loops:
        v = loop.vert
        if abs(v.co.y - 10.890) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.4140, 1.0000))
        elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.0000, 1.0000))
        elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.0000, 0.0000))
        elif abs(v.co.y - 10.890) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.4140, 0.0000))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ext_obj.data)
    bm.free()
    ext_obj.data.update()
    print("Exterior_Walls successfully fixed!")


    # ==========================================
    # 2. FIX INTERIOR_WALLS
    # ==========================================
    int_obj = bpy.data.objects.get('Interior_Walls')
    if not int_obj:
        raise RuntimeError("Interior_Walls object not found!")

    bpy.context.view_layer.objects.active = int_obj
    int_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(int_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    print("\n--- Processing Interior_Walls ---")
    
    # Vertices to find:
    # Wall corners:
    # (0.365, 9.900, 0.0) [idx 95]
    # (0.365, 9.900, 1.8) [idx 99]
    # (0.365, 9.775, 0.0) [idx 92]
    # (0.365, 9.775, 1.8) [idx 96]
    # (2.050, 9.900, 0.0) [idx 106]
    # (2.050, 9.900, 1.8) [idx 103]
    # (2.050, 9.775, 0.0) [idx 104]
    # (2.050, 9.775, 1.8) [idx 100]

    v_int_map = {}
    for v in bm.verts:
        if abs(v.co.x - 0.365) < 0.01:
            if abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int_map['w_990_bot'] = v
            elif abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int_map['w_990_top'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int_map['w_977_bot'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int_map['w_977_top'] = v
        elif abs(v.co.x - 2.050) < 0.01:
            if abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int_map['e_990_bot'] = v
            elif abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int_map['e_990_top'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int_map['e_977_bot'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int_map['e_977_top'] = v

    print("Interior mapped corners:", {k: (v.index, tuple(round(c, 3) for c in v.co)) for k, v in v_int_map.items()})

    # Remove all faces in this wall segment between X in [0.365, 2.050] and Y in [9.775, 9.900]
    # Faces to remove: Face 118, 116, 80, 117, 115, 75, 77
    faces_to_remove = []
    for f in bm.faces:
        c = f.calc_center_median()
        if 0.35 <= c.x <= 2.06 and 9.76 <= c.y <= 9.91:
            # But DO NOT remove Face 82 (the side end-cap at X=0.365) or Face 84 (side end-cap at X=2.050)
            if abs(f.normal.x) > 0.9:
                continue
            faces_to_remove.append(f)

    print(f"Removing {len(faces_to_remove)} old wall faces: {[f.index for f in faces_to_remove]}")
    for f in faces_to_remove:
        bm.faces.remove(f)

    # Remove any orphan/unused vertices in that range
    for v in list(bm.verts):
        if len(v.link_faces) == 0:
            bm.verts.remove(v)

    # Create new clean vertices at X = 1.368 (shower partition boundary)
    # Matching exactly the shower floor boundary at X = 1.368
    X_SPLIT = 1.368
    v_s_990_bot = bm.verts.new((X_SPLIT, 9.900, 0.0))
    v_s_990_top = bm.verts.new((X_SPLIT, 9.900, 1.8))
    v_s_977_bot = bm.verts.new((X_SPLIT, 9.775, 0.0))
    v_s_977_top = bm.verts.new((X_SPLIT, 9.775, 1.8))

    # Reconstruct the 6 faces cleanly:
    # 1. Shower face facing North (Y = 9.900, normal +Y)
    # Verts: w_990_bot -> s_990_bot -> s_990_top -> w_990_top
    f_shower = bm.faces.new([
        v_int_map['w_990_bot'],
        v_s_990_bot,
        v_s_990_top,
        v_int_map['w_990_top']
    ])
    f_shower.material_index = 2 # Plank stena.001
    f_shower.normal_update()

    # 2. White wall face facing North (Y = 9.900, normal +Y)
    # Verts: s_990_bot -> e_990_bot -> e_990_top -> s_990_top
    f_white_front = bm.faces.new([
        v_s_990_bot,
        v_int_map['e_990_bot'],
        v_int_map['e_990_top'],
        v_s_990_top
    ])
    f_white_front.material_index = 0 # Mat_Interior_Wall
    f_white_front.normal_update()

    # 3. Top face over shower (Z = 1.800, normal +Z)
    # w_977_top -> s_977_top -> s_990_top -> w_990_top
    f_top_shower = bm.faces.new([
        v_int_map['w_977_top'],
        v_s_977_top,
        v_s_990_top,
        v_int_map['w_990_top']
    ])
    f_top_shower.material_index = 0 # Mat_Interior_Wall
    f_top_shower.normal_update()

    # 4. Top face over white wall (Z = 1.800, normal +Z)
    # s_977_top -> e_977_top -> e_990_top -> s_990_top
    f_top_white = bm.faces.new([
        v_s_977_top,
        v_int_map['e_977_top'],
        v_int_map['e_990_top'],
        v_s_990_top
    ])
    f_top_white.material_index = 0 # Mat_Interior_Wall
    f_top_white.normal_update()

    # 5. Bottom face over shower (Z = 0.000, normal -Z)
    # w_977_bot -> w_990_bot -> s_990_bot -> s_977_bot
    f_bot_shower = bm.faces.new([
        v_int_map['w_977_bot'],
        v_int_map['w_990_bot'],
        v_s_990_bot,
        v_s_977_bot
    ])
    f_bot_shower.material_index = 0
    f_bot_shower.normal_update()

    # 6. Bottom face over white wall (Z = 0.000, normal -Z)
    # s_977_bot -> s_990_bot -> e_990_bot -> e_977_bot
    f_bot_white = bm.faces.new([
        v_s_977_bot,
        v_s_990_bot,
        v_int_map['e_990_bot'],
        v_int_map['e_977_bot']
    ])
    f_bot_white.material_index = 0
    f_bot_white.normal_update()

    # 7. Back faces facing South into room 1.09 (Y = 9.775, normal -Y)
    # w_977_top -> w_977_bot -> s_977_bot -> s_977_top
    f_back_shower = bm.faces.new([
        v_int_map['w_977_top'],
        v_int_map['w_977_bot'],
        v_s_977_bot,
        v_s_977_top
    ])
    f_back_shower.material_index = 0
    f_back_shower.normal_update()

    # s_977_top -> s_977_bot -> e_977_bot -> e_977_top
    f_back_white = bm.faces.new([
        v_s_977_top,
        v_s_977_bot,
        v_int_map['e_977_bot'],
        v_int_map['e_977_top']
    ])
    f_back_white.material_index = 0
    f_back_white.normal_update()

    # Clean UV mapping for Interior_Walls
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

    # UV for f_shower (Plank stena.001)
    for loop in f_shower.loops:
        v = loop.vert
        if abs(v.co.x - 0.365) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.0000, 1.0000))
        elif abs(v.co.x - X_SPLIT) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.5568, 1.0000))
        elif abs(v.co.x - X_SPLIT) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.5568, 0.0000))
        elif abs(v.co.x - 0.365) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.0000, 0.0000))

    # UV for f_white_front (Mat_Interior_Wall)
    for loop in f_white_front.loops:
        v = loop.vert
        if abs(v.co.x - X_SPLIT) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((0.0, 1.0))
        elif abs(v.co.x - 2.050) < 0.01 and abs(v.co.z - 0.0) < 0.01:
            loop[uv_layer].uv = Vector((1.0, 1.0))
        elif abs(v.co.x - 2.050) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((1.0, 0.0))
        elif abs(v.co.x - X_SPLIT) < 0.01 and abs(v.co.z - 1.8) < 0.01:
            loop[uv_layer].uv = Vector((0.0, 0.0))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(int_obj.data)
    bm.free()
    int_obj.data.update()
    print("Interior_Walls successfully fixed!")

    # Check non-manifold edges on both objects to verify 100% clean geometry
    for obj_name in ['Exterior_Walls', 'Interior_Walls']:
        o = bpy.data.objects[obj_name]
        b = bmesh.new()
        b.from_mesh(o.data)
        non_manifold = [e for e in b.edges if not e.is_manifold]
        print(f"{obj_name}: {len(non_manifold)} non-manifold edges (boundary edges are normal for open shells)")
        b.free()

    # Save file
    print(f"\nSaving modified blend to {filepath}...")
    bpy.ops.wm.save_mainfile(filepath=filepath)
    print("Done!")

if __name__ == '__main__':
    fix_bathroom_walls("dum_pudorys_dobra.blend")
