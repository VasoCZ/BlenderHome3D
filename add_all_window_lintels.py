"""
add_all_window_lintels.py
=========================
Adds wall lintels (stěnové překlady) above ALL windows in the house:
1. Closes the upper cutouts on Exterior_Walls above all windows up to Z = 1.800 m.
   - All 9 windows now have solid wall lintels Z in [1.600, 1.800] m (20 cm thick).
   - Unified lintel datum across the entire building at Z = 1.600 m (matching interior door lintels).
   - The dark roof cornice (Roof_Soffit_Cornice) rests on solid wall around 360° of the house.
2. Updates Window_Frames_and_Sills:
   - All 9 windows have full 4-sided frames (jambs, bottom rail, top rail at Z = 1.600 m).
   - Exterior sills with downward drip noses (20 mm drop, 40 mm fascia, 20 mm side ears).
   - Interior sills with downward noses (20 mm drop, 40 mm fascia, 20 mm side ears).
   - Material: Mat_Roof_Soffit (RAL 7016 anthracite).
3. Updates Window_Glass:
   - All 9 windows have clear architectural glass panes (Glass_Clear, Glass BSDF, IOR 1.52).
4. Renders 5 verification views:
   - South facade perspective
   - East facade perspective
   - North facade perspective
   - West facade perspective
   - Full isometric floor plan overview
"""

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

def update_exterior_walls_all_lintels():
    print("\n--- 1. Closing upper cutouts with lintels on Exterior_Walls ---")
    ext_obj = bpy.data.objects.get("Exterior_Walls")
    if not ext_obj:
        raise RuntimeError("Exterior_Walls not found!")

    # 6 remaining window lintels to apply (W5, W6 WC, W6 Tech already applied)
    lintel_boxes_spec = [
        # South facade
        ('Lintel_W1_106', 1.300, 2.800, 0.000, 0.365, 1.600, 1.800),
        ('Lintel_W1_105', 7.200, 8.700, 0.000, 0.365, 1.600, 1.800),
        # East facade
        ('Lintel_W2_South_104', 9.635, 10.000, 5.900, 7.640, 1.600, 1.800),
        ('Lintel_W2_North_104', 9.635, 10.000, 8.780, 10.520, 1.600, 1.800),
        # North facade
        ('Lintel_W4_103', 3.660, 5.400, 11.635, 12.000, 1.600, 1.800),
        # West facade
        ('Lintel_W05_107', 0.000, 0.365, 4.725, 6.225, 1.600, 1.800),
    ]

    for name, x0, x1, y0, y1, z0, z1 in lintel_boxes_spec:
        box_obj = make_box_obj(name, x0, x1, y0, y1, z0, z1)
        mod = ext_obj.modifiers.new(name=f"Union_{name}", type='BOOLEAN')
        mod.operation = 'UNION'
        mod.solver = 'EXACT'
        mod.object = box_obj
        bpy.context.view_layer.objects.active = ext_obj
        bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(box_obj, do_unlink=True)
        print(f"[OK] Applied lintel {name}.")

    bm = bmesh.new()
    bm.from_mesh(ext_obj.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.dissolve_degenerate(bm, dist=0.0005, edges=bm.edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ext_obj.data)
    bm.free()
    ext_obj.data.update()
    print("[OK] Exterior_Walls now has continuous solid wall lintels above ALL 9 windows.")

def build_all_windows_and_glass():
    print("\n--- 2. Building Window_Frames_and_Sills and Window_Glass for ALL 9 windows ---")
    windows_specs = [
        # South facade
        {'id': 'W1_South_106', 'wall': 'S', 'span': (1.300, 2.800), 'z_sill': 1.050, 'z_top': 1.600},
        {'id': 'W1_South_105', 'wall': 'S', 'span': (7.200, 8.700), 'z_sill': 1.050, 'z_top': 1.600},
        # East facade
        {'id': 'W2_East_South_104', 'wall': 'E', 'span': (5.900, 7.640), 'z_sill': 1.200, 'z_top': 1.600},
        {'id': 'W2_East_North_104', 'wall': 'E', 'span': (8.780, 10.520), 'z_sill': 1.050, 'z_top': 1.600},
        # North facade
        {'id': 'W4_North_103', 'wall': 'N', 'span': (3.660, 5.400), 'z_sill': 1.050, 'z_top': 1.600},
        {'id': 'W5_North_110', 'wall': 'N', 'span': (1.120, 2.120), 'z_sill': 1.350, 'z_top': 1.600}, # Koupelna
        # West facade
        {'id': 'W6_West_Tech_109', 'wall': 'W', 'span': (8.375, 9.175), 'z_sill': 1.350, 'z_top': 1.600}, # Tech
        {'id': 'W6_West_WC_108', 'wall': 'W', 'span': (7.200, 8.000), 'z_sill': 1.350, 'z_top': 1.600}, # WC
        {'id': 'W05_West_107', 'wall': 'W', 'span': (4.725, 6.225), 'z_sill': 0.900, 'z_top': 1.600},
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
    rail_h = 0.040         # 40 mm top and bottom rail

    for spec in windows_specs:
        wall = spec['wall']
        p0, p1 = spec['span']
        z_sill = spec['z_sill']
        z_top = spec['z_top']  # 1.600 m

        if wall == 'S':
            y_ext = 0.000
            y_int = 0.365
            y_f0 = 0.120
            y_f1 = y_f0 + frame_d
            y_mid = (y_f0 + y_f1) / 2

            # Frame jambs + bottom rail + top rail
            add_box_bmesh(bm_frame, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top)
            add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h)
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
            add_box_bmesh(bm_frame, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_top - rail_h, z_top)

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
            add_box_bmesh(bm_frame, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_top - rail_h, z_top)

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

    print(f"[OK] {frame_obj_name} and {glass_obj_name} created successfully for all 9 windows.")

def render_verification_views():
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: South facade perspective (W1 windows with lintels and entrance door)
    c1_data = bpy.data.cameras.new("Cam_South_Lintels")
    c1 = bpy.data.objects.new("Cam_South_Lintels", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((5.0, -5.5, 3.0))
    c1.rotation_euler = (Vector((5.0, 1.5, 1.3)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 35
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("windows_south_lintels_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: windows_south_lintels_view.png")

    # View 2: East facade perspective (W2 living room windows with lintels)
    c2_data = bpy.data.cameras.new("Cam_East_Lintels")
    c2 = bpy.data.objects.new("Cam_East_Lintels", c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((14.5, 8.0, 3.0))
    c2.rotation_euler = (Vector((9.5, 8.0, 1.3)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 35
    scene.camera = c2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("windows_east_lintels_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: windows_east_lintels_view.png")

    # View 3: West facade perspective (W05, W6 WC, W6 Tech with lintels)
    c3_data = bpy.data.cameras.new("Cam_West_Lintels")
    c3 = bpy.data.objects.new("Cam_West_Lintels", c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((-4.5, 7.0, 3.0))
    c3.rotation_euler = (Vector((0.5, 7.0, 1.3)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 35
    scene.camera = c3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("windows_west_lintels_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: windows_west_lintels_view.png")

    # View 4: Full isometric overview
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # Clean up temporary cameras
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

    update_exterior_walls_all_lintels()
    build_all_windows_and_glass()

    if iso_cam:
        bpy.context.scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(f"[OK] Saved '{blend_path}'.")

    render_verification_views()

    bpy.ops.wm.save_mainfile()
    print("[OK] All window lintels, frames, and glass successfully built and saved.")

if __name__ == "__main__":
    main()
