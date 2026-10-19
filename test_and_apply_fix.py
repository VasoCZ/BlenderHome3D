import bpy
import bmesh
import os
from mathutils import Vector

def fix_all(blend_path):
    print("="*60)
    print("STARTING BATHROOM WALL REPAIR")
    print("="*60)
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # -------------------------------------------------------------
    # 1. FIX EXTERIOR_WALLS
    # -------------------------------------------------------------
    ext_obj = bpy.data.objects['Exterior_Walls']
    bpy.context.view_layer.objects.active = ext_obj
    ext_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(ext_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    v_ext = {}
    for v in bm.verts:
        if abs(v.co.x - 0.365) < 0.01:
            if abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.365, 9.900, 1.8))
                v_ext['inner_990_top'] = v
            elif abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 0.0) < 0.05:
                v.co = Vector((0.365, 9.900, 0.0))
                v_ext['inner_990_bot'] = v
            elif abs(v.co.y - 10.890) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.365, 10.890, 1.8))
                v_ext['inner_1089_top'] = v
            elif abs(v.co.y - 10.890) < 0.05 and abs(v.co.z - 0.0) < 0.05:
                v.co = Vector((0.365, 10.890, 0.0))
                v_ext['inner_1089_bot'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v.co = Vector((0.365, 11.635, 1.8))
                v_ext['inner_1163_top'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v.co = Vector((0.365, 11.635, 0.0))
                v_ext['inner_1163_bot'] = v
            elif abs(v.co.y - 9.175) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext['inner_917_top'] = v
            elif abs(v.co.y - 0.365) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_ext['inner_036_bot'] = v
        elif abs(v.co.x - 0.0) < 0.01:
            if abs(v.co.y - 9.900) < 0.05 and abs(v.co.z - 1.8) < 0.05:
                v.co = Vector((0.0, 9.900, 1.8))
                v_ext['outer_990_top'] = v
            elif abs(v.co.y - 9.175) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext['outer_917_top'] = v
            elif abs(v.co.y - 11.635) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_ext['outer_1163_top'] = v

    print("Found Exterior mapped vertices:", {k: v.index for k, v in v_ext.items()})

    # Fix Face 45
    f45 = None
    for f in bm.faces:
        if v_ext['inner_036_bot'] in f.verts and v_ext['inner_917_top'] in f.verts:
            f45 = f
            break

    if f45:
        orig_verts = list(f45.verts)
        bm.faces.remove(f45)
        new_verts = []
        for v in orig_verts:
            # skip any vertex that was inside bathroom (y > 9.901)
            if v.co.y > 9.901:
                continue
            if v == v_ext['inner_990_bot'] or v == v_ext['inner_990_top']:
                continue
            new_verts.append(v)
            if v == v_ext['inner_036_bot']:
                new_verts.append(v_ext['inner_990_bot'])
                new_verts.append(v_ext['inner_990_top'])

        new_f45 = bm.faces.new(new_verts)
        new_f45.material_index = 0
        new_f45.normal_update()
        print("Rebuilt Face 45, vert count:", len(new_f45.verts))

    # Remove old bathroom wall faces (material index 1 and 2)
    for f in list(bm.faces):
        if f.material_index in [1, 2]:
            bm.faces.remove(f)

    # Clean Face 72: Shower Wall (Plank stena, mat_index = 2)
    new_f72 = bm.faces.new([
        v_ext['inner_990_bot'],
        v_ext['inner_1089_bot'],
        v_ext['inner_1089_top'],
        v_ext['inner_990_top']
    ])
    new_f72.material_index = 2
    new_f72.normal_update()

    # Clean Face 74: Bathroom Tile Wall (koupelna stena, mat_index = 1)
    new_f74 = bm.faces.new([
        v_ext['inner_1089_bot'],
        v_ext['inner_1163_bot'],
        v_ext['inner_1163_top'],
        v_ext['inner_1089_top']
    ])
    new_f74.material_index = 1
    new_f74.normal_update()

    # Clean top faces over bathroom west wall
    for f in list(bm.faces):
        if abs(f.normal.z - 1.0) < 0.1 and any(abs(v.co.y - 10.5) < 0.5 for v in f.verts) and any(v.co.x < 0.2 for v in f.verts):
            bm.faces.remove(f)

    v_outer_1089_top = bm.verts.new((0.0, 10.890, 1.8))
    v_ext['outer_1089_top'] = v_outer_1089_top

    f_top1 = bm.faces.new([
        v_ext['inner_990_top'],
        v_ext['inner_1089_top'],
        v_ext['outer_1089_top'],
        v_ext['outer_990_top']
    ])
    f_top1.material_index = 0
    f_top1.normal_update()

    f_top2 = bm.faces.new([
        v_ext['inner_1089_top'],
        v_ext['inner_1163_top'],
        v_ext['outer_1163_top'],
        v_ext['outer_1089_top']
    ])
    f_top2.material_index = 0
    f_top2.normal_update()

    # Insert v_outer_1089_top into Face 47 (outer wall)
    for f in list(bm.faces):
        if v_ext['outer_990_top'] in f.verts and v_ext['outer_1163_top'] in f.verts and f.normal.x < -0.8:
            verts_47 = list(f.verts)
            idx_990 = verts_47.index(v_ext['outer_990_top'])
            idx_1163 = verts_47.index(v_ext['outer_1163_top'])
            bm.faces.remove(f)
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

    # Update bottom face 40
    for f in list(bm.faces):
        if f.normal.z < -0.8 and v_ext['inner_036_bot'] in f.verts and v_ext['inner_1163_bot'] in f.verts:
            verts_40 = list(f.verts)
            bm.faces.remove(f)
            new_verts_40 = []
            for v in verts_40:
                if v == v_ext['inner_036_bot']:
                    new_verts_40.extend([v, v_ext['inner_990_bot'], v_ext['inner_1089_bot']])
                elif v not in [v_ext['inner_990_bot'], v_ext['inner_1089_bot']]:
                    new_verts_40.append(v)
            new_f40 = bm.faces.new(new_verts_40)
            new_f40.material_index = 0
            new_f40.normal_update()
            break

    # UV assignment for Exterior_Walls
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

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
    print("Exterior_Walls complete!")

    # -------------------------------------------------------------
    # 2. FIX INTERIOR_WALLS
    # -------------------------------------------------------------
    int_obj = bpy.data.objects['Interior_Walls']
    bpy.context.view_layer.objects.active = int_obj
    int_obj.select_set(True)
    bpy.ops.object.mode_set(mode='OBJECT')

    bm = bmesh.new()
    bm.from_mesh(int_obj.data)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    v_int = {}
    for v in bm.verts:
        if abs(v.co.x - 0.365) < 0.01:
            if abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int['w_990_bot'] = v
            elif abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int['w_990_top'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int['w_977_bot'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int['w_977_top'] = v
        elif abs(v.co.x - 2.050) < 0.01:
            if abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int['e_990_bot'] = v
            elif abs(v.co.y - 9.900) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int['e_990_top'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 0.0) < 0.01:
                v_int['e_977_bot'] = v
            elif abs(v.co.y - 9.775) < 0.01 and abs(v.co.z - 1.8) < 0.01:
                v_int['e_977_top'] = v

    print("Found Interior mapped vertices:", {k: v.index for k, v in v_int.items()})

    # Remove all old faces in partition wall
    faces_to_remove = []
    for f in bm.faces:
        c = f.calc_center_median()
        if 0.35 <= c.x <= 2.06 and 9.76 <= c.y <= 9.91:
            if abs(f.normal.x) > 0.9: # Preserve side end-caps
                continue
            faces_to_remove.append(f)

    for f in faces_to_remove:
        bm.faces.remove(f)

    # Remove any isolated vertices
    for v in list(bm.verts):
        if len(v.link_faces) == 0:
            bm.verts.remove(v)

    # Create new clean vertices at X = 1.368
    X_SPLIT = 1.368
    v_s_990_bot = bm.verts.new((X_SPLIT, 9.900, 0.0))
    v_s_990_top = bm.verts.new((X_SPLIT, 9.900, 1.8))
    v_s_977_bot = bm.verts.new((X_SPLIT, 9.775, 0.0))
    v_s_977_top = bm.verts.new((X_SPLIT, 9.775, 1.8))

    # 1. Shower face facing North (normal +Y)
    f_shower = bm.faces.new([
        v_s_990_top,
        v_s_990_bot,
        v_int['w_990_bot'],
        v_int['w_990_top']
    ])
    f_shower.material_index = 2 # Plank stena.001
    f_shower.normal_update()

    # 2. White wall face facing North (normal +Y)
    f_white_front = bm.faces.new([
        v_int['e_990_top'],
        v_int['e_990_bot'],
        v_s_990_bot,
        v_s_990_top
    ])
    f_white_front.material_index = 0 # Mat_Interior_Wall
    f_white_front.normal_update()

    # 3. Top shower (normal +Z)
    f_top_shower = bm.faces.new([
        v_int['w_977_top'],
        v_s_977_top,
        v_s_990_top,
        v_int['w_990_top']
    ])
    f_top_shower.material_index = 0
    f_top_shower.normal_update()

    # 4. Top white wall (normal +Z)
    f_top_white = bm.faces.new([
        v_s_977_top,
        v_int['e_977_top'],
        v_int['e_990_top'],
        v_s_990_top
    ])
    f_top_white.material_index = 0
    f_top_white.normal_update()

    # 5. Bottom shower (normal -Z)
    f_bot_shower = bm.faces.new([
        v_int['w_977_bot'],
        v_int['w_990_bot'],
        v_s_990_bot,
        v_s_977_bot
    ])
    f_bot_shower.material_index = 0
    f_bot_shower.normal_update()

    # 6. Bottom white wall (normal -Z)
    f_bot_white = bm.faces.new([
        v_s_977_bot,
        v_s_990_bot,
        v_int['e_990_bot'],
        v_int['e_977_bot']
    ])
    f_bot_white.material_index = 0
    f_bot_white.normal_update()

    # 7. Back faces facing South (normal -Y)
    f_back_shower = bm.faces.new([
        v_int['w_977_bot'],
        v_s_977_bot,
        v_s_977_top,
        v_int['w_977_top']
    ])
    f_back_shower.material_index = 0
    f_back_shower.normal_update()

    f_back_white = bm.faces.new([
        v_s_977_bot,
        v_int['e_977_bot'],
        v_int['e_977_top'],
        v_s_977_top
    ])
    f_back_white.material_index = 0
    f_back_white.normal_update()

    # UV assignment for Interior_Walls
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

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
    print("Interior_Walls complete!")

    # Ensure all objects remain in OBJECT mode
    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.select_set(False)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Save changes to blend file
    print(f"Saving changes to {blend_path}...")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("File saved successfully!")

    # -------------------------------------------------------------
    # 3. RENDERING VERIFICATION IMAGES
    # -------------------------------------------------------------
    scene = bpy.context.scene
    orig_cam = scene.camera

    # Render 1: bathroom_closeup.png (West Wall focus)
    print("Rendering bathroom_closeup.png...")
    cam_data1 = bpy.data.cameras.new('Temp_Cam1')
    cam_obj1 = bpy.data.objects.new('Temp_Cam1', cam_data1)
    scene.collection.objects.link(cam_obj1)
    cam_obj1.location = Vector((4.5, 8.5, 4.0))
    target1 = Vector((1.6, 10.7, 0.9))
    direction1 = target1 - cam_obj1.location
    cam_obj1.rotation_euler = direction1.to_track_quat('-Z', 'Y').to_euler()
    cam_data1.type = 'PERSP'
    cam_data1.lens = 40
    scene.camera = cam_obj1
    scene.render.filepath = os.path.abspath('bathroom_closeup.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj1, do_unlink=True)
    bpy.data.cameras.remove(cam_data1, do_unlink=True)

    # Render 2: bathroom_south_wall.png (South Wall focus)
    print("Rendering bathroom_south_wall.png...")
    cam_data2 = bpy.data.cameras.new('Temp_Cam2')
    cam_obj2 = bpy.data.objects.new('Temp_Cam2', cam_data2)
    scene.collection.objects.link(cam_obj2)
    cam_obj2.location = Vector((0.5, 12.5, 3.5))
    target2 = Vector((1.8, 10.0, 0.9))
    direction2 = target2 - cam_obj2.location
    cam_obj2.rotation_euler = direction2.to_track_quat('-Z', 'Y').to_euler()
    cam_data2.type = 'PERSP'
    cam_data2.lens = 35
    scene.camera = cam_obj2
    scene.render.filepath = os.path.abspath('bathroom_south_wall.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj2, do_unlink=True)
    bpy.data.cameras.remove(cam_data2, do_unlink=True)

    # Render 3: dum_pudorys_dobra_preview.png (Full House overview using original camera)
    print("Rendering dum_pudorys_dobra_preview.png...")
    if orig_cam:
        scene.camera = orig_cam
        scene.render.filepath = os.path.abspath('dum_pudorys_dobra_preview.png')
        scene.render.resolution_x = 1280
        scene.render.resolution_y = 720
        bpy.ops.render.render(write_still=True)

    print("ALL RENDERS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    fix_all("dum_pudorys_dobra.blend")
