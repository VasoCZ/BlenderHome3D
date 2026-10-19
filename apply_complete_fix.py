import bpy
import bmesh
import os
from mathutils import Vector

def apply_complete_fix(blend_path):
    print("=" * 60)
    print("APPLYING COMPLETE BATHROOM WALL & EDGE REPAIR")
    print("=" * 60)
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    mat_plank_ext = bpy.data.materials.get('Plank stena')
    mat_plank_int = bpy.data.materials.get('Plank stena.001')
    mat_plank_floor = bpy.data.materials.get('Plank 1')
    mat_koupelna = bpy.data.materials.get('koupelna stena')
    mat_koupelna_floor = bpy.data.materials.get('koupelna')

    # 1. REMOVE DISPLACEMENT OUTPUT LINKS THAT CAUSE EDGE TEARING
    print("Removing displacement links to eliminate mesh boundary tears...")
    for mat in [mat_plank_ext, mat_plank_int, mat_plank_floor, mat_koupelna, mat_koupelna_floor]:
        if mat and mat.node_tree:
            for link in list(mat.node_tree.links):
                if link.to_socket.name == 'Displacement':
                    print(f"  Removed displacement link in {mat.name}")
                    mat.node_tree.links.remove(link)

    # 2. FIX EXTERIOR_WALLS
    print("\nUpdating Exterior_Walls...")
    ext = bpy.data.objects['Exterior_Walls']
    bpy.context.view_layer.objects.active = ext
    bpy.ops.object.mode_set(mode='OBJECT')

    idx_koupelna_ext = 1
    idx_plank_ext = 2

    bm = bmesh.new()
    bm.from_mesh(ext.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

    for f in bm.faces:
        c = f.calc_center_median()
        # Top faces at Z = 1.800
        if abs(f.normal.z - 1.0) < 0.1 and abs(c.x - 0.1825) < 0.05:
            if 9.85 < c.y < 10.89:
                f.material_index = idx_plank_ext
                for loop in f.loops:
                    v = loop.vert
                    loop[uv_layer].uv = Vector((0.2383, 0.5731 + (v.co.y - 9.900)/(10.890 - 9.900) * (0.6333 - 0.5731)))
            elif 10.89 < c.y < 11.64:
                f.material_index = idx_koupelna_ext
                for loop in f.loops:
                    v = loop.vert
                    loop[uv_layer].uv = Vector(((11.635 - v.co.y)/(11.635 - 10.890) * 0.4140, 0.0))

        # Vertical face for shower (Y in [9.90, 10.89])
        elif abs(f.normal.x - 1.0) < 0.1 and abs(c.x - 0.365) < 0.01 and 9.85 < c.y < 10.89:
            f.material_index = idx_plank_ext
            for loop in f.loops:
                v = loop.vert
                u = 0.3465 if abs(v.co.z) < 0.1 else 0.2383
                v_coord = 0.5731 if abs(v.co.y - 9.900) < 0.01 else 0.6333
                loop[uv_layer].uv = Vector((u, v_coord))

        # Vertical face for koupelna stena (Y in [10.89, 11.635])
        elif abs(f.normal.x - 1.0) < 0.1 and abs(c.x - 0.365) < 0.01 and 10.89 < c.y < 11.64:
            f.material_index = idx_koupelna_ext
            for loop in f.loops:
                v = loop.vert
                u = 0.0 if abs(v.co.y - 11.635) < 0.01 else 0.4140
                v_coord = 1.0 if abs(v.co.z) < 0.1 else 0.0
                loop[uv_layer].uv = Vector((u, v_coord))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ext.data)
    bm.free()
    ext.data.update()

    # 3. FIX INTERIOR_WALLS
    print("\nUpdating Interior_Walls...")
    int_obj = bpy.data.objects['Interior_Walls']
    bpy.context.view_layer.objects.active = int_obj
    bpy.ops.object.mode_set(mode='OBJECT')

    if len(int_obj.material_slots) < 2:
        int_obj.data.materials.append(mat_koupelna)
    else:
        int_obj.material_slots[1].material = mat_koupelna

    idx_koupelna_int = 1
    idx_plank_int = 2

    bm = bmesh.new()
    bm.from_mesh(int_obj.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.verify()

    for f in bm.faces:
        c = f.calc_center_median()
        # South wall inner faces facing into bathroom (Y = 9.900, normal +Y)
        if abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.900) < 0.02:
            # Shower face (X in [0.365, 1.368])
            if 0.36 < c.x < 1.37:
                f.material_index = idx_plank_int
                for loop in f.loops:
                    v = loop.vert
                    u = 0.0000 if abs(v.co.x - 0.365) < 0.01 else 0.5568
                    v_coord = 1.0000 if abs(v.co.z) < 0.1 else 0.0000
                    loop[uv_layer].uv = Vector((u, v_coord))
            # Wall next to shower (X in [1.368, 2.050]) -> koupelna stena
            elif 1.36 < c.x < 2.06:
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 1.368) / (2.050 - 1.368) * 0.4
                    v_coord = 1.0 if abs(v.co.z) < 0.1 else 0.0
                    loop[uv_layer].uv = Vector((u, v_coord))
            # Door post face (X in [2.750, 2.875]) -> koupelna stena
            elif 2.74 < c.x < 2.88:
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 2.750) / (2.875 - 2.750) * 0.1
                    v_coord = 1.0 if abs(v.co.z) < 0.1 else 0.0
                    loop[uv_layer].uv = Vector((u, v_coord))

        # Top faces at Z = 1.800
        elif abs(f.normal.z - 1.0) < 0.1 and abs(c.y - 9.8375) < 0.05:
            # Above shower wood cladding
            if 0.36 < c.x < 1.37:
                f.material_index = idx_plank_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 0.365) / (1.368 - 0.365) * 0.5568
                    loop[uv_layer].uv = Vector((u, 0.0))
            # Above bathroom south wall grey tile
            elif 1.36 < c.x < 2.06:
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 1.368) / (2.050 - 1.368) * 0.4
                    loop[uv_layer].uv = Vector((u, 0.0))
            # Above door post
            elif 2.74 < c.x < 2.88:
                f.material_index = idx_koupelna_int
                for loop in f.loops:
                    v = loop.vert
                    u = (v.co.x - 2.750) / (2.875 - 2.750) * 0.1
                    loop[uv_layer].uv = Vector((u, 0.0))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(int_obj.data)
    bm.free()
    int_obj.data.update()

    # Save changes to blend file
    print(f"\nSaving updated scene to {blend_path}...")
    bpy.ops.wm.save_mainfile(filepath=blend_path)
    print("Saved successfully!")

    # 4. RENDER VERIFICATION VIEWS
    print("\nRendering verification images...")
    scene = bpy.context.scene

    # View 1: Zoom top transition (West wall transition + top edge)
    c1_data = bpy.data.cameras.new('C1')
    c1 = bpy.data.objects.new('C1', c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((1.8, 10.890, 2.5))
    c1.rotation_euler = (Vector((0.365, 10.890, 1.8)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 50
    scene.camera = c1
    scene.render.filepath = os.path.abspath('zoom_top_transition.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c1, do_unlink=True)
    bpy.data.cameras.remove(c1_data, do_unlink=True)

    # View 2: South wall overhead view (South wall transition + top edge)
    l1_data = bpy.data.lights.new('L1', 'POINT')
    l1_data.energy = 50.0
    l1 = bpy.data.objects.new('L1', l1_data)
    scene.collection.objects.link(l1)
    l1.location = Vector((1.5, 10.5, 2.5))

    c2_data = bpy.data.cameras.new('C2')
    c2 = bpy.data.objects.new('C2', c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((1.5, 11.2, 2.4))
    c2.rotation_euler = (Vector((1.4, 9.9, 1.5)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 45
    scene.camera = c2
    scene.render.filepath = os.path.abspath('inspect_south_overhead.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c2, do_unlink=True)
    bpy.data.cameras.remove(c2_data, do_unlink=True)
    bpy.data.objects.remove(l1, do_unlink=True)
    bpy.data.lights.remove(l1_data, do_unlink=True)

    # View 3: Viewport simulation (LookDev with ambient top sun)
    l2_data = bpy.data.lights.new('LookDev_Sun', 'SUN')
    l2_data.energy = 3.0
    l2 = bpy.data.objects.new('LookDev_Sun', l2_data)
    scene.collection.objects.link(l2)
    l2.rotation_euler = (0.5, 0.2, 0.8)

    c3_data = bpy.data.cameras.new('LookDev_Cam')
    c3 = bpy.data.objects.new('LookDev_Cam', c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((3.5, 9.0, 3.8))
    c3.rotation_euler = (Vector((1.3, 10.7, 1.0)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 35
    scene.camera = c3
    scene.render.filepath = os.path.abspath('viewport_sim_render.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c3, do_unlink=True)
    bpy.data.cameras.remove(c3_data, do_unlink=True)
    bpy.data.objects.remove(l2, do_unlink=True)
    bpy.data.lights.remove(l2_data, do_unlink=True)

    # View 4: Bathroom closeup
    c4_data = bpy.data.cameras.new('C4')
    c4 = bpy.data.objects.new('C4', c4_data)
    scene.collection.objects.link(c4)
    c4.location = Vector((4.5, 8.5, 4.0))
    c4.rotation_euler = (Vector((1.6, 10.7, 0.9)) - c4.location).to_track_quat('-Z', 'Y').to_euler()
    c4_data.type = 'PERSP'
    c4_data.lens = 40
    scene.camera = c4
    scene.render.filepath = os.path.abspath('bathroom_closeup.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c4, do_unlink=True)
    bpy.data.cameras.remove(c4_data, do_unlink=True)

    # View 5: Bathroom south wall
    c5_data = bpy.data.cameras.new('C5')
    c5 = bpy.data.objects.new('C5', c5_data)
    scene.collection.objects.link(c5)
    c5.location = Vector((0.5, 12.5, 3.5))
    c5.rotation_euler = (Vector((1.8, 10.0, 0.9)) - c5.location).to_track_quat('-Z', 'Y').to_euler()
    c5_data.type = 'PERSP'
    c5_data.lens = 35
    scene.camera = c5
    scene.render.filepath = os.path.abspath('bathroom_south_wall.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c5, do_unlink=True)
    bpy.data.cameras.remove(c5_data, do_unlink=True)

    # View 6: dum_pudorys_dobra_preview.png (Full overview with scene camera)
    orig_cam = bpy.data.objects.get('Isometric_Camera')
    if orig_cam:
        scene.camera = orig_cam
        scene.render.filepath = os.path.abspath('dum_pudorys_dobra_preview.png')
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        bpy.ops.render.render(write_still=True)

    print("\nALL PREVIEWS RENDERED SUCCESSFULLY!")

if __name__ == '__main__':
    apply_complete_fix("dum_pudorys_dobra.blend")
