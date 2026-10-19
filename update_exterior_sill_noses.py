"""
update_exterior_sill_noses.py
=============================
Updates 'Window_Frames_and_Sills' so that BOTH interior and exterior window sills
have architectural downward noses (převislé okapové nosy parapetů):

1. Exterior window sills with downward drip noses (venkovní parapety s nosem):
   - Horizontal plate: 20 mm thick (Z in [Z_sill - 0.005, Z_sill + 0.015])
   - Extends 35 mm past exterior facade face, with 20 mm side ears
   - Downward drip nose: 15 mm thick, hanging down 20 mm (Z in [Z_sill - 0.025, Z_sill - 0.005])
   - Total front fascia height: 40 mm, casting realistic architectural shadow on exterior plaster

2. Interior window sills with downward noses (vnitřní parapety s nosem):
   - Horizontal board: 20 mm thick (Z in [Z_sill, Z_sill + 0.020])
   - Extends 25 mm into room, with 20 mm side ears
   - Downward apron nose: 15 mm thick, hanging down 20 mm (Z in [Z_sill - 0.020, Z_sill])
   - Total front fascia height: 40 mm

3. Window frames:
   - Anthracite jambs and bottom rail lining the opening up to Z = 1.800 m
   - Open cutaway opening (0% glass, no dividing mullions)
   - All in 'Mat_Roof_Soffit' anthracite material matching the roof atika

4. Renders verification views:
   - Exterior close-up of window sill nose
   - Interior close-up of window sill nose
   - South facade perspective
   - Full floor plan overview
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

def create_box(bm, x0, x1, y0, y1, z0, z1, mat_idx=0):
    """Adds an axis-aligned box to bmesh."""
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

def build_window_frame_and_sills(bm, spec):
    wall = spec['wall']
    p0, p1 = spec['span']
    z_sill = spec['z_sill']
    z_top = spec['z_top']  # 1.800 m

    h_total = z_top - z_sill
    frame_d = 0.070    # 70 mm profile depth
    frame_w = 0.060    # 60 mm jamb width
    rail_h = min(0.045, h_total / 2.5)  # adaptive bottom rail height

    ear_w = 0.020          # 20 mm side ears

    # Exterior sill parameters (with downward drip nose)
    ext_overhang = 0.035   # 35 mm projection past exterior wall
    ext_board_t = 0.020    # 20 mm plate thickness
    ext_nose_t = 0.015     # 15 mm nose thickness
    ext_nose_drop = 0.020  # 20 mm downward nose drop

    # Interior sill parameters (with downward apron nose)
    int_overhang = 0.025   # 25 mm projection into room
    int_board_t = 0.020    # 20 mm board thickness
    int_nose_t = 0.015     # 15 mm nose thickness
    int_nose_drop = 0.020  # 20 mm downward nose drop

    mat_anthracite = 0

    if wall == 'S':
        # South wall: normal -Y, ext Y=0.000, int Y=0.365
        y_ext = 0.000
        y_int = 0.365
        y_f0 = 0.120
        y_f1 = y_f0 + frame_d

        # 1. Window Frame (Anthracite)
        create_box(bm, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h, mat_idx=mat_anthracite)

        # 2. Exterior Sill with Downward Drip Nose (Anthracite)
        # Front edge of exterior sill:
        y_ext_front = y_ext - ext_overhang  # -0.035 m
        # Horizontal plate:
        create_box(bm, p0 - ear_w, p1 + ear_w, y_ext_front, y_f0 + 0.005, z_sill - 0.005, z_sill - 0.005 + ext_board_t, mat_idx=mat_anthracite)
        # Downward drip nose at front:
        create_box(bm, p0 - ear_w, p1 + ear_w, y_ext_front, y_ext_front + ext_nose_t, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose (Anthracite)
        # Front edge of interior sill:
        y_int_front = y_int + int_overhang  # 0.390 m
        # Horizontal board:
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_int_front, z_sill, z_sill + int_board_t, mat_idx=mat_anthracite)
        # Downward front nose:
        create_box(bm, p0 - ear_w, p1 + ear_w, y_int_front - int_nose_t, y_int_front, z_sill - int_nose_drop, z_sill, mat_idx=mat_anthracite)

    elif wall == 'N':
        # North wall: normal +Y, ext Y=12.000, int Y=11.635
        y_ext = 12.000
        y_int = 11.635
        y_f1 = y_ext - 0.120
        y_f0 = y_f1 - frame_d

        # 1. Window Frame
        create_box(bm, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h, mat_idx=mat_anthracite)

        # 2. Exterior Sill with Downward Drip Nose
        y_ext_front = y_ext + ext_overhang  # 12.035 m
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_ext_front, z_sill - 0.005, z_sill - 0.005 + ext_board_t, mat_idx=mat_anthracite)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_ext_front - ext_nose_t, y_ext_front, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        y_int_front = y_int - int_overhang  # 11.610 m
        create_box(bm, p0 - ear_w, p1 + ear_w, y_int_front, y_f0 + 0.005, z_sill, z_sill + int_board_t, mat_idx=mat_anthracite)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_int_front, y_int_front + int_nose_t, z_sill - int_nose_drop, z_sill, mat_idx=mat_anthracite)

    elif wall == 'E':
        # East wall: normal +X, ext X=10.000, int X=9.635
        x_ext = 10.000
        x_int = 9.635
        x_f1 = x_ext - 0.120
        x_f0 = x_f1 - frame_d

        # 1. Window Frame
        create_box(bm, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h, mat_idx=mat_anthracite)

        # 2. Exterior Sill with Downward Drip Nose
        x_ext_front = x_ext + ext_overhang  # 10.035 m
        create_box(bm, x_f1 - 0.005, x_ext_front, p0 - ear_w, p1 + ear_w, z_sill - 0.005, z_sill - 0.005 + ext_board_t, mat_idx=mat_anthracite)
        create_box(bm, x_ext_front - ext_nose_t, x_ext_front, p0 - ear_w, p1 + ear_w, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        x_int_front = x_int - int_overhang  # 9.610 m
        create_box(bm, x_int_front, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_board_t, mat_idx=mat_anthracite)
        create_box(bm, x_int_front, x_int_front + int_nose_t, p0 - ear_w, p1 + ear_w, z_sill - int_nose_drop, z_sill, mat_idx=mat_anthracite)

    elif wall == 'W':
        # West wall: normal -X, ext X=0.000, int X=0.365
        x_ext = 0.000
        x_int = 0.365
        x_f0 = 0.120
        x_f1 = x_f0 + frame_d

        # 1. Window Frame
        create_box(bm, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top, mat_idx=mat_anthracite)
        create_box(bm, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h, mat_idx=mat_anthracite)

        # 2. Exterior Sill with Downward Drip Nose
        x_ext_front = x_ext - ext_overhang  # -0.035 m
        create_box(bm, x_ext_front, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill - 0.005, z_sill - 0.005 + ext_board_t, mat_idx=mat_anthracite)
        create_box(bm, x_ext_front, x_ext_front + ext_nose_t, p0 - ear_w, p1 + ear_w, z_sill - 0.005 - ext_nose_drop, z_sill - 0.005, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        x_int_front = x_int + int_overhang  # 0.390 m
        create_box(bm, x_f1 - 0.005, x_int_front, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_board_t, mat_idx=mat_anthracite)
        create_box(bm, x_int_front - int_nose_t, x_int_front, p0 - ear_w, p1 + ear_w, z_sill - int_nose_drop, z_sill, mat_idx=mat_anthracite)

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    windows_specs = [
        # South facade
        {'id': 'W1_South_106', 'wall': 'S', 'span': (1.300, 2.800), 'z_sill': 1.050, 'z_top': 1.800},
        {'id': 'W1_South_105', 'wall': 'S', 'span': (7.200, 8.700), 'z_sill': 1.050, 'z_top': 1.800},
        # East facade
        {'id': 'W2_East_South_104', 'wall': 'E', 'span': (5.900, 7.640), 'z_sill': 1.200, 'z_top': 1.800},
        {'id': 'W2_East_North_104', 'wall': 'E', 'span': (8.780, 10.520), 'z_sill': 1.050, 'z_top': 1.800},
        # North facade
        {'id': 'W4_North_103', 'wall': 'N', 'span': (3.660, 5.400), 'z_sill': 1.050, 'z_top': 1.800},
        {'id': 'W5_North_110', 'wall': 'N', 'span': (1.120, 2.120), 'z_sill': 1.600, 'z_top': 1.800},
        # West facade
        {'id': 'W6_West_Tech_109', 'wall': 'W', 'span': (8.375, 9.175), 'z_sill': 1.750, 'z_top': 1.800},
        {'id': 'W6_West_WC_108', 'wall': 'W', 'span': (7.200, 8.000), 'z_sill': 1.600, 'z_top': 1.800},
        {'id': 'W05_West_107', 'wall': 'W', 'span': (4.725, 6.225), 'z_sill': 0.900, 'z_top': 1.800},
    ]

    mat_anthracite = bpy.data.materials.get("Mat_Roof_Soffit")
    if not mat_anthracite:
        mat_anthracite = bpy.data.materials.new("Mat_Roof_Soffit")
        mat_anthracite.use_nodes = True
        bsdf = mat_anthracite.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.50

    obj_name = "Window_Frames_and_Sills"
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
    if obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[obj_name])

    print("[INFO] Constructing Window_Frames_and_Sills with BOTH interior and exterior downward noses...")
    mesh = bpy.data.meshes.new(obj_name)
    bm = bmesh.new()

    for spec in windows_specs:
        build_window_frame_and_sills(bm, spec)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(obj_name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Material: All anthracite (frames, exterior sills with drip noses, interior sills with apron noses)
    obj.data.materials.append(mat_anthracite)

    # Bevel modifier for crisp architectural highlights
    mod_b = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod_b.width = 0.002
    mod_b.segments = 2
    mod_b.limit_method = 'ANGLE'
    mod_b.angle_limit = math.radians(45)
    mod_b.harden_normals = True

    print(f"[OK] {obj_name} created with exterior and interior noses.")

    # Preserve Isometric_Camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # Save updated blend file
    bpy.ops.wm.save_mainfile()
    print(f"[OK] Saved '{blend_path}'.")

    # Render verification views
    render_verification_views(iso_cam)

def render_verification_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: Exterior close-up of South facade window sill with downward drip nose (Window 106)
    c1_data = bpy.data.cameras.new("Cam_Ext_Sill_Nose")
    c1 = bpy.data.objects.new("Cam_Ext_Sill_Nose", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((1.05, -1.25, 1.22))
    c1.rotation_euler = (Vector((1.55, 0.0, 1.03)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 42
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_exterior_sill_nose_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_exterior_sill_nose_view.png")

    # View 2: Interior close-up of windowsill with downward nose in room 1.05
    c2_data = bpy.data.cameras.new("Cam_Win_Sill_Nose")
    c2 = bpy.data.objects.new("Cam_Win_Sill_Nose", c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((7.0, 1.2, 1.35))
    c2.rotation_euler = (Vector((7.95, 0.365, 1.05)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 45
    scene.camera = c2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_interior_sill_nose_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_interior_sill_nose_view.png")

    # View 3: South facade perspective
    c3_data = bpy.data.cameras.new("Cam_Win_South")
    c3 = bpy.data.objects.new("Cam_Win_South", c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((5.0, -5.5, 3.2))
    c3.rotation_euler = (Vector((5.0, 1.5, 1.2)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 35
    scene.camera = c3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_south_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_south_view.png")

    # View 4: Full isometric overview
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

    bpy.ops.wm.save_mainfile()
    print("Cleaned up temporary cameras and resaved main blend file.")

if __name__ == "__main__":
    main()
