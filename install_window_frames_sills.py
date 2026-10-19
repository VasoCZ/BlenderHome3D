"""
install_window_frames_sills.py
==============================
Installs window frames and window sills for all 9 exterior window openings:
- NO glass panes (žádné sklo)
- NO dividing bars/mullions (žádné dělicí příčky)
- Obvodový rám v otvoru (antracitový materiál 'Mat_Roof_Soffit' ladící s atikou)
- Venkovní plechový parapet s okapovým nosem (antracitový 'Mat_Roof_Soffit')
- Vnitřní parapetní deska (bílý saténový lak 'Mat_Interior_Door_Frame')
- Bevel modifier pro realistické architektonické hrany
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

    # Parapet dimensions
    ext_overhang = 0.025   # 25 mm exterior drip ledge
    int_overhang = 0.015   # 15 mm interior sill overhang into room
    ear_w = 0.015          # 15 mm side ears
    ext_sill_t = 0.008     # 8 mm exterior sheet thickness
    int_sill_t = 0.020     # 20 mm interior board thickness

    if wall == 'S':
        # South wall: normal -Y, ext Y=0.000, int Y=0.365
        y_ext = 0.000
        y_int = 0.365
        y_f0 = 0.120
        y_f1 = y_f0 + frame_d

        # 1. Window Frame (Mat 0 = Anthracite)
        # Left jamb
        create_box(bm, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top, mat_idx=0)
        # Right jamb
        create_box(bm, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top, mat_idx=0)
        # Bottom rail
        create_box(bm, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h, mat_idx=0)

        # 2. Exterior Sill (Mat 0 = Anthracite)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_ext - ext_overhang, y_f0 + 0.005, z_sill - ext_sill_t, z_sill, mat_idx=0)

        # 3. Interior Sill Board (Mat 1 = White satin)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_int + int_overhang, z_sill, z_sill + int_sill_t, mat_idx=1)

    elif wall == 'N':
        # North wall: normal +Y, ext Y=12.000, int Y=11.635
        y_ext = 12.000
        y_int = 11.635
        y_f1 = y_ext - 0.120
        y_f0 = y_f1 - frame_d

        # 1. Window Frame
        create_box(bm, p0, p0 + frame_w, y_f0, y_f1, z_sill, z_top, mat_idx=0)
        create_box(bm, p1 - frame_w, p1, y_f0, y_f1, z_sill, z_top, mat_idx=0)
        create_box(bm, p0 + frame_w, p1 - frame_w, y_f0, y_f1, z_sill, z_sill + rail_h, mat_idx=0)

        # 2. Exterior Sill
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_ext + ext_overhang, z_sill - ext_sill_t, z_sill, mat_idx=0)

        # 3. Interior Sill Board
        create_box(bm, p0 - ear_w, p1 + ear_w, y_int - int_overhang, y_f0 + 0.005, z_sill, z_sill + int_sill_t, mat_idx=1)

    elif wall == 'E':
        # East wall: normal +X, ext X=10.000, int X=9.635
        x_ext = 10.000
        x_int = 9.635
        x_f1 = x_ext - 0.120
        x_f0 = x_f1 - frame_d

        # 1. Window Frame
        create_box(bm, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top, mat_idx=0)
        create_box(bm, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top, mat_idx=0)
        create_box(bm, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h, mat_idx=0)

        # 2. Exterior Sill
        create_box(bm, x_f1 - 0.005, x_ext + ext_overhang, p0 - ear_w, p1 + ear_w, z_sill - ext_sill_t, z_sill, mat_idx=0)

        # 3. Interior Sill Board
        create_box(bm, x_int - int_overhang, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_sill_t, mat_idx=1)

    elif wall == 'W':
        # West wall: normal -X, ext X=0.000, int X=0.365
        x_ext = 0.000
        x_int = 0.365
        x_f0 = 0.120
        x_f1 = x_f0 + frame_d

        # 1. Window Frame
        create_box(bm, x_f0, x_f1, p0, p0 + frame_w, z_sill, z_top, mat_idx=0)
        create_box(bm, x_f0, x_f1, p1 - frame_w, p1, z_sill, z_top, mat_idx=0)
        create_box(bm, x_f0, x_f1, p0 + frame_w, p1 - frame_w, z_sill, z_sill + rail_h, mat_idx=0)

        # 2. Exterior Sill
        create_box(bm, x_ext - ext_overhang, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill - ext_sill_t, z_sill, mat_idx=0)

        # 3. Interior Sill Board
        create_box(bm, x_f1 - 0.005, x_int + int_overhang, p0 - ear_w, p1 + ear_w, z_sill, z_sill + int_sill_t, mat_idx=1)

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

    # Materials
    mat_anthracite = bpy.data.materials.get("Mat_Roof_Soffit")
    if not mat_anthracite:
        mat_anthracite = bpy.data.materials.new("Mat_Roof_Soffit")
        mat_anthracite.use_nodes = True
        bsdf = mat_anthracite.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.50

    mat_int_sill = bpy.data.materials.get("Mat_Interior_Door_Frame")
    if not mat_int_sill:
        mat_int_sill = bpy.data.materials.new("Mat_Interior_Door_Frame")
        mat_int_sill.use_nodes = True
        bsdf = mat_int_sill.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.95, 0.94, 0.92, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.30

    obj_name = "Window_Frames_and_Sills"
    if obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)
    if obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[obj_name])

    print("[INFO] Building Window_Frames_and_Sills mesh (no glass, open cutaway openings)...")
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

    # Slot 0: Anthracite frame & exterior sill
    obj.data.materials.append(mat_anthracite)
    # Slot 1: White satin interior sill board
    obj.data.materials.append(mat_int_sill)

    # Bevel modifier for realistic joinery highlights
    mod_b = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod_b.width = 0.002
    mod_b.segments = 2
    mod_b.limit_method = 'ANGLE'
    mod_b.angle_limit = math.radians(45)
    mod_b.harden_normals = True

    print(f"[OK] {obj_name} created successfully.")

    # Preserve Isometric_Camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # Save blend file
    bpy.ops.wm.save_mainfile()
    print(f"[OK] Saved '{blend_path}'.")

    # Render verification views
    render_verification_views(iso_cam)

def render_verification_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # View 1: South facade perspective (Windows 106, 105 and Entrance Door)
    c1_data = bpy.data.cameras.new("Cam_Win_South")
    c1 = bpy.data.objects.new("Cam_Win_South", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((5.0, -5.5, 3.2))
    c1.rotation_euler = (Vector((5.0, 1.5, 1.2)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 35
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_south_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_south_view.png")

    # View 2: East facade perspective (Living Room windows 1.04)
    c2_data = bpy.data.cameras.new("Cam_Win_East")
    c2 = bpy.data.objects.new("Cam_Win_East", c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((14.5, 8.2, 3.2))
    c2.rotation_euler = (Vector((9.8, 8.2, 1.3)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 35
    scene.camera = c2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_east_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_east_view.png")

    # View 3: North facade perspective (Kitchen 1.03, Patio Slider 1.04, Bath 1.10)
    c3_data = bpy.data.cameras.new("Cam_Win_North")
    c3 = bpy.data.objects.new("Cam_Win_North", c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((5.5, 16.5, 3.6))
    c3.rotation_euler = (Vector((5.5, 11.5, 1.2)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 35
    scene.camera = c3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("window_north_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: window_north_view.png")

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
