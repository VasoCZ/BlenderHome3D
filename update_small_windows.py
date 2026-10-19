import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector

def make_box_obj(name, x0, x1, y0, y1, z0, z1):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    dx = x1 - x0
    dy = y1 - y0
    dz = z1 - z0
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    cz = (z0 + z1) / 2
    bmesh.ops.scale(bm, vec=Vector((dx, dy, dz)), verts=bm.verts)
    bmesh.ops.translate(bm, vec=Vector((cx, cy, cz)), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    bpy.context.scene.collection.objects.link(obj)
    return obj

def update_exterior_walls(blend_path):
    print("\n--- 1. Updating Exterior_Walls with solid lintels and lowered window openings ---")
    ext_obj = bpy.data.objects.get("Exterior_Walls")
    if not ext_obj:
        raise RuntimeError("Exterior_Walls not found!")

    # 1. Fill old cutouts with solid wall
    fill_k = make_box_obj("Fill_K", 1.120, 2.120, 11.635, 12.000, 1.600, 1.800)
    fill_wc = make_box_obj("Fill_WC", 0.000, 0.365, 7.200, 8.000, 1.600, 1.800)
    fill_tech = make_box_obj("Fill_Tech", 0.000, 0.365, 8.375, 9.175, 1.750, 1.800)

    for fill_obj in [fill_k, fill_wc, fill_tech]:
        mod = ext_obj.modifiers.new(name="Union_Fill", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.solver = 'EXACT'
        mod.object = fill_obj
        bpy.context.view_layer.objects.active = ext_obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(fill_obj, do_unlink=True)

    # 2. Cut new window openings from Z = 1.350 to 1.600
    cut_k = make_box_obj("Cut_K", 1.120, 2.120, 11.500, 12.100, 1.350, 1.600)
    cut_wc = make_box_obj("Cut_WC", -0.100, 0.465, 7.200, 8.000, 1.350, 1.600)
    cut_tech = make_box_obj("Cut_Tech", -0.100, 0.465, 8.375, 9.175, 1.350, 1.600)

    for cut_obj in [cut_k, cut_wc, cut_tech]:
        mod = ext_obj.modifiers.new(name="Diff_Window", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.object = cut_obj
        bpy.context.view_layer.objects.active = ext_obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cut_obj, do_unlink=True)

    # Clean up degenerate geometry and doubles
    bm = bmesh.new()
    bm.from_mesh(ext_obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0005, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # Assign bathroom tile material to Koupelna lintel south face (Y = 11.635, Z in [1.600, 1.800])
    mat_bath_idx = 3 if len(ext_obj.data.materials) > 3 and ext_obj.data.materials[3] else 1
    uv_layer = bm.loops.layers.uv.verify()

    for f in bm.faces:
        c = f.calc_center_median()
        # Check south-facing face of Koupelna lintel: X in [1.12, 2.12], Y near 11.635, Z in [1.60, 1.80], normal -Y
        if 1.10 <= c.x <= 2.14 and 11.62 <= c.y <= 11.65 and 1.58 <= c.z <= 1.82 and f.normal.y < -0.8:
            f.material_index = mat_bath_idx
            for l in f.loops:
                vx, vz = l.vert.co.x, l.vert.co.z
                u = vx * 0.0601
                v = 0.4546 + (1.800 - vz) * (0.4666 - 0.4546) / 0.200
                l[uv_layer].uv = Vector((u, v))
            print(f"[OK] Assigned bathroom material {mat_bath_idx} and aligned UV to Koupelna lintel south face.")

    bm.to_mesh(ext_obj.data)
    bm.free()
    ext_obj.data.update()
    print("[OK] Exterior_Walls update complete.")

def add_box_bmesh(bm, x0, x1, y0, y1, z0, z1, mat_idx=0):
    v = [
        bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
    ]
    faces_def = [
        [v[0], v[1], v[2], v[3]],  # bottom
        [v[4], v[7], v[6], v[5]],  # top
        [v[0], v[4], v[5], v[1]],  # south
        [v[2], v[6], v[7], v[3]],  # north
        [v[0], v[3], v[7], v[4]],  # west
        [v[1], v[5], v[6], v[2]],  # east
    ]
    for fv in faces_def:
        f = bm.faces.new(fv)
        f.material_index = mat_idx

def build_windows_and_glass():
    print("\n--- 2. Building Window_Frames_and_Sills and Window_Glass ---")
    windows_specs = [
        # South facade (open cutaways up to 1.800)
        {'id': 'W1_South_106', 'wall': 'S', 'span': (1.300, 2.800), 'z_sill': 1.050, 'z_top': 1.800, 'has_lintel': False},
        {'id': 'W1_South_105', 'wall': 'S', 'span': (7.200, 8.700), 'z_sill': 1.050, 'z_top': 1.800, 'has_lintel': False},
        # East facade (open cutaways up to 1.800)
        {'id': 'W2_East_South_104', 'wall': 'E', 'span': (5.900, 7.640), 'z_sill': 1.200, 'z_top': 1.800, 'has_lintel': False},
        {'id': 'W2_East_North_104', 'wall': 'E', 'span': (8.780, 10.520), 'z_sill': 1.050, 'z_top': 1.800, 'has_lintel': False},
        # North facade
        {'id': 'W4_North_103', 'wall': 'N', 'span': (3.660, 5.400), 'z_sill': 1.050, 'z_top': 1.800, 'has_lintel': False},
        {'id': 'W5_North_110', 'wall': 'N', 'span': (1.120, 2.120), 'z_sill': 1.350, 'z_top': 1.600, 'has_lintel': True}, # KOUPELNA
        # West facade
        {'id': 'W6_West_Tech_109', 'wall': 'W', 'span': (8.375, 9.175), 'z_sill': 1.350, 'z_top': 1.600, 'has_lintel': True}, # TECH
        {'id': 'W6_West_WC_108', 'wall': 'W', 'span': (7.200, 8.000), 'z_sill': 1.350, 'z_top': 1.600, 'has_lintel': True}, # WC
        {'id': 'W05_West_107', 'wall': 'W', 'span': (4.725, 6.225), 'z_sill': 0.900, 'z_top': 1.800, 'has_lintel': False},
    ]

    mat_anthracite = bpy.data.materials.get("Mat_Roof_Soffit")
    if not mat_anthracite:
        mat_anthracite = bpy.data.materials.new("Mat_Roof_Soffit")
        mat_anthracite.use_nodes = True
        bsdf = mat_anthracite.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.50

    mat_glass = bpy.data.materials.get("Glass_Clear")
    if not mat_glass:
        mat_glass = bpy.data.materials.new("Glass_Clear")
        mat_glass.use_nodes = True
        nodes = mat_glass.node_tree.nodes
        nodes.clear()
        node_out = nodes.new('ShaderNodeOutputMaterial')
        node_glass = nodes.new('ShaderNodeBsdfGlass')
        node_glass.inputs['Roughness'].default_value = 0.05
        node_glass.inputs['IOR'].default_value = 1.52
        mat_glass.node_tree.links.new(node_glass.outputs['BSDF'], node_out.inputs['Surface'])

    # Build Window_Frames_and_Sills
    frame_obj_name = "Window_Frames_and_Sills"
    if frame_obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[frame_obj_name], do_unlink=True)
    if frame_obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[frame_obj_name])

    glass_obj_name = "Window_Glass"
    if glass_obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[glass_obj_name], do_unlink=True)
    if glass_obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[glass_obj_name])

    frame_mesh = bpy.data.meshes.new(frame_obj_name)
    glass_mesh = bpy.data.meshes.new(glass_obj_name)

    bm_frame = bmesh.new()
    bm_glass = bmesh.new()

    frame_d = 0.070    # 70 mm profile depth
    frame_w = 0.060    # 60 mm jamb width
    ear_w = 0.020      # 20 mm side ears

    # Exterior sill parameters
    ext_overhang = 0.035   # 35 mm projection past exterior wall
    ext_board_t = 0.020    # 20 mm plate thickness
    ext_nose_t = 0.015     # 15 mm nose thickness
    ext_nose_drop = 0.020  # 20 mm downward nose drop

    # Interior sill parameters
    int_overhang = 0.025   # 25 mm projection into room
    int_board_t = 0.020    # 20 mm board thickness
    int_nose_t = 0.015     # 15 mm nose thickness
    int_nose_drop = 0.020  # 20 mm downward nose drop

    glass_t = 0.008        # 8 mm architectural glass

    for spec in windows_specs:
        wall = spec['wall']
        p0, p1 = spec['span']
        z_sill = spec['z_sill']
        z_top = spec['z_top']
        has_lintel = spec['has_lintel']

        h_total = z_top - z_sill
        rail_h = 0.035 if has_lintel else min(0.045, h_total / 2.5)

        if wall == 'S':
            y_ext = 0.000
            y_int = 0.365
            y_f0 = 0.120
            y_f1 = y_f0 + frame_d
            y_mid = (y_f0 + y_f1) / 2

            # Frame jambs + bottom rail
            add_box_bmesh(bm_frame, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h)
            if has_lintel:
                add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_top - rail_h, z_top)
                # Glass pane
                add_box_bmesh(bm_glass, p0 + frame_w, p1 - frame_w, y_mid - glass_t/2, y_mid + glass_t/2, z_sill + rail_h, z_top - rail_h)

            # Exterior sill with downward drip nose
            y_ext_front = y_ext - ext_overhang
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_ext_front, y_f0 + 0.005, z_sill - 0.005, z_sill - 0.005 + ext_board_t)
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_ext_front, y_ext_front + ext_nose_t, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005)

            # Interior sill with downward nose
            y_int_front = y_int + int_overhang
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_int_front, z_sill, z_sill + int_board_t)
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_int_front - int_nose_t, y_int_front, z_sill - int_nose_drop, z_sill)

        elif wall == 'N':
            y_ext = 12.000
            y_int = 11.635
            y_f1 = y_ext - 0.120
            y_f0 = y_f1 - frame_d
            y_mid = (y_f0 + y_f1) / 2

            add_box_bmesh(bm_frame, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h)
            if has_lintel:
                add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_top - rail_h, z_top)
                # Glass pane
                add_box_bmesh(bm_glass, p0 + frame_w, p1 - frame_w, y_mid - glass_t/2, y_mid + glass_t/2, z_sill + rail_h, z_top - rail_h)

            y_ext_front = y_ext + ext_overhang
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_ext_front, z_sill - 0.005, z_sill - 0.005 + ext_board_t)
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_ext_front - ext_nose_t, y_ext_front, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005)

            y_int_front = y_int - int_overhang
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_int_front, y_f0 + 0.005, z_sill, z_sill + int_board_t)
            add_box_bmesh(bm_frame, p0 - ear_w, p1 + ear_w, y_int_front, y_int_front + int_nose_t, z_sill - int_nose_drop, z_sill)

        elif wall == 'E':
            x_ext = 10.000
            x_int = 9.635
            x_f1 = x_ext - 0.120
            x_f0 = x_f1 - frame_d
            x_mid = (x_f0 + x_f1) / 2

            add_box_bmesh(bm_frame, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top)
            add_box_bmesh(bm_frame, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top)
            add_box_bmesh(bm_frame, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h)
            if has_lintel:
                add_box_bmesh(bm_frame, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_top - rail_h, z_top)
                add_box_bmesh(bm_glass, x_mid - glass_t/2, x_mid + glass_t/2, p0 + frame_w, p1 - frame_w, z_sill + rail_h, z_top - rail_h)

            x_ext_front = x_ext + ext_overhang
            add_box_bmesh(bm_frame, x_f1 - 0.005, x_ext_front, p0 - ear_w, p1 + ear_w, z_sill - 0.005, z_sill - 0.005 + ext_board_t)
            add_box_bmesh(bm_frame, x_ext_front - ext_nose_t, x_ext_front, p0 - ear_w, p1 + ear_w, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005)

            x_int_front = x_int - int_overhang
            add_box_bmesh(bm_frame, x_int_front, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_board_t)
            add_box_bmesh(bm_frame, x_int_front, x_int_front + int_nose_t, p0 - ear_w, p1 + ear_w, z_sill - int_nose_drop, z_sill)

        elif wall == 'W':
            x_ext = 0.000
            x_int = 0.365
            x_f0 = 0.120
            x_f1 = x_f0 + frame_d
            x_mid = (x_f0 + x_f1) / 2

            add_box_bmesh(bm_frame, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top)
            add_box_bmesh(bm_frame, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top)
            add_box_bmesh(bm_frame, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h)
            if has_lintel:
                add_box_bmesh(bm_frame, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_top - rail_h, z_top)
                # Glass pane
                add_box_bmesh(bm_glass, x_mid - glass_t/2, x_mid + glass_t/2, p0 + frame_w, p1 - frame_w, z_sill + rail_h, z_top - rail_h)

            x_ext_front = x_ext - ext_overhang
            add_box_bmesh(bm_frame, x_ext_front, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill - 0.005, z_sill - 0.005 + ext_board_t)
            add_box_bmesh(bm_frame, x_ext_front, x_ext_front + ext_nose_t, p0 - ear_w, p1 + ear_w, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005)

            x_int_front = x_int + int_overhang
            add_box_bmesh(bm_frame, x_f1 - 0.005, x_int_front, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_board_t)
            add_box_bmesh(bm_frame, x_int_front - int_nose_t, x_int_front, p0 - ear_w, p1 + ear_w, z_sill - int_nose_drop, z_sill)

    # Finalize frames mesh
    bmesh.ops.remove_doubles(bm_frame, verts=bm_frame.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm_frame, faces=bm_frame.faces)
    bm_frame.to_mesh(frame_mesh)
    bm_frame.free()

    frame_obj = bpy.data.objects.new(frame_obj_name, frame_mesh)
    bpy.context.scene.collection.objects.link(frame_obj)
    frame_obj.data.materials.append(mat_anthracite)

    mod_b = frame_obj.modifiers.new(name="Bevel", type='BEVEL')
    mod_b.width = 0.002
    mod_b.segments = 2
    mod_b.limit_method = 'ANGLE'
    mod_b.angle_limit = math.radians(45)
    mod_b.harden_normals = True

    # Finalize glass mesh
    bmesh.ops.remove_doubles(bm_glass, verts=bm_glass.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm_glass, faces=bm_glass.faces)
    bm_glass.to_mesh(glass_mesh)
    bm_glass.free()

    glass_obj = bpy.data.objects.new(glass_obj_name, glass_mesh)
    bpy.context.scene.collection.objects.link(glass_obj)
    glass_obj.data.materials.append(mat_glass)

    print(f"[OK] {frame_obj_name} and {glass_obj_name} created successfully.")

def render_verification_views():
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: West facade close-up (WC and Tech windows with lintels and lowered sills)
    c1_data = bpy.data.cameras.new("Cam_West_Small_Windows")
    c1 = bpy.data.objects.new("Cam_West_Small_Windows", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((-3.2, 8.2, 2.3))
    c1.rotation_euler = (Vector((0.0, 8.2, 1.45)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 42
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("small_windows_west_facade.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: small_windows_west_facade.png")

    # View 2: North facade close-up (Koupelna window with lintel and lowered sill)
    c2_data = bpy.data.cameras.new("Cam_North_Bath_Window")
    c2 = bpy.data.objects.new("Cam_North_Bath_Window", c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((1.62, 14.5, 2.2))
    c2.rotation_euler = (Vector((1.62, 12.0, 1.45)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 45
    scene.camera = c2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("small_window_bathroom_facade.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: small_window_bathroom_facade.png")

    # View 3: Bathroom interior close-up (showing lintel with matching tiles and window)
    c3_data = bpy.data.cameras.new("Cam_Bath_Interior_Lintel")
    c3 = bpy.data.objects.new("Cam_Bath_Interior_Lintel", c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((1.62, 10.3, 1.35))
    c3.rotation_euler = (Vector((1.62, 11.635, 1.50)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 38
    scene.camera = c3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("small_window_bathroom_interior.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: small_window_bathroom_interior.png")

    # View 4: Full isometric overview
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # Cleanup temporary cameras
    for c in [c1, c2, c3]:
        bpy.data.objects.remove(c, do_unlink=True)
    for cd in [c1_data, c2_data, c3_data]:
        bpy.data.cameras.remove(cd)

    if iso_cam:
        scene.camera = iso_cam

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    iso_cam = bpy.data.objects.get("Isometric_Camera")

    update_exterior_walls(blend_path)
    build_windows_and_glass()

    if iso_cam:
        bpy.context.scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(f"[OK] Saved '{blend_path}'.")

    render_verification_views()

    # Re-save to keep camera clean
    bpy.ops.wm.save_mainfile()
    print("[OK] Complete process finished and saved.")

if __name__ == "__main__":
    main()
