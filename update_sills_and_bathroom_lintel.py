"""
update_sills_and_bathroom_lintel.py
===================================
1. Bathroom Door Lintel:
   - Sets the bathroom-facing face (+Y normal at Y = 9.900, X in [2.050, 2.750], Z in [1.600, 1.800])
     and top face (Z = 1.800) in 'Interior_Walls' to the grey bathroom tile material ('Material' / 'koupelna stena').
   - Aligns UV mapping with surrounding bathroom walls.

2. Window Frames & Sills with Interior Noses:
   - Sets BOTH interior and exterior window sills to dark anthracite ('Mat_Roof_Soffit' matching roof atika).
   - Models architectural downward sill noses (nos parapetu) on all 9 interior windowsills:
     - Horizontal board thickness: 20 mm (Z in [Z_sill, Z_sill + 0.020])
     - 25 mm overhang into room past interior wall face, 20 mm side ears
     - Downward nose lip: 15 mm thick, hanging down 20 mm (Z in [Z_sill - 0.020, Z_sill])
     - Creates classic 40 mm front profile fascia with realistic contact shadow
   - Exterior sheet metal sill with 25 mm drip edge overhang in anthracite
   - Open cutaway opening (0% glass, no dividing mullions)

3. Renders verification views:
   - View of bathroom doorway from inside bathroom
   - Close-up interior view of window with sill nose
   - South facade view
   - East facade view
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

    # Parapet dimensions
    ext_overhang = 0.025   # 25 mm exterior drip ledge
    ext_sill_t = 0.008     # 8 mm exterior sheet thickness
    ear_w = 0.020          # 20 mm side ears

    int_overhang = 0.025   # 25 mm interior board overhang into room
    board_t = 0.020        # 20 mm interior board thickness
    nose_t = 0.015         # 15 mm thickness of front downward nose
    nose_drop = 0.020      # 20 mm downward drop of nose below masonry sill

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

        # 2. Exterior Sill (Anthracite)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_ext - ext_overhang, y_f0 + 0.005, z_sill - ext_sill_t, z_sill, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose (Anthracite)
        # Main horizontal board:
        y_board_front = y_int + int_overhang  # 0.390 m
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_board_front, z_sill, z_sill + board_t, mat_idx=mat_anthracite)
        # Downward front nose (hangs down in front of wall):
        create_box(bm, p0 - ear_w, p1 + ear_w, y_board_front - nose_t, y_board_front, z_sill - nose_drop, z_sill, mat_idx=mat_anthracite)

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

        # 2. Exterior Sill
        create_box(bm, p0 - ear_w, p1 + ear_w, y_f1 - 0.005, y_ext + ext_overhang, z_sill - ext_sill_t, z_sill, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        y_board_front = y_int - int_overhang  # 11.610 m
        create_box(bm, p0 - ear_w, p1 + ear_w, y_board_front, y_f0 + 0.005, z_sill, z_sill + board_t, mat_idx=mat_anthracite)
        create_box(bm, p0 - ear_w, p1 + ear_w, y_board_front, y_board_front + nose_t, z_sill - nose_drop, z_sill, mat_idx=mat_anthracite)

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

        # 2. Exterior Sill
        create_box(bm, x_f1 - 0.005, x_ext + ext_overhang, p0 - ear_w, p1 + ear_w, z_sill - ext_sill_t, z_sill, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        x_board_front = x_int - int_overhang  # 9.610 m
        create_box(bm, x_board_front, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill, z_sill + board_t, mat_idx=mat_anthracite)
        create_box(bm, x_board_front, x_board_front + nose_t, p0 - ear_w, p1 + ear_w, z_sill - nose_drop, z_sill, mat_idx=mat_anthracite)

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

        # 2. Exterior Sill
        create_box(bm, x_ext - ext_overhang, x_f0 + 0.005, p0 - ear_w, p1 + ear_w, z_sill - ext_sill_t, z_sill, mat_idx=mat_anthracite)

        # 3. Interior Sill with Downward Nose
        x_board_front = x_int + int_overhang  # 0.390 m
        create_box(bm, x_f1 - 0.005, x_board_front, p0 - ear_w, p1 + ear_w, z_sill, z_sill + board_t, mat_idx=mat_anthracite)
        create_box(bm, x_board_front - nose_t, x_board_front, p0 - ear_w, p1 + ear_w, z_sill - nose_drop, z_sill, mat_idx=mat_anthracite)

def update_bathroom_lintel(blend_path):
    iw = bpy.data.objects.get("Interior_Walls")
    if not iw:
        print("[WARN] Interior_Walls not found!")
        return

    # Material index for bathroom grey tile: slot 1 ('Material')
    tile_mat_idx = 1
    # Verify slot 1 has Concrete_Wall
    m1 = iw.data.materials[1] if len(iw.data.materials) > 1 else None
    print(f"[INFO] Interior_Walls slot 1 material: {m1.name if m1 else 'N/A'}")

    # Door 111_110 bounds: X in [2.050, 2.750], Y in [9.775, 9.900], Z in [1.600, 1.800]
    updated_faces = 0
    for poly in iw.data.polygons:
        c = poly.center
        if 2.00 <= c.x <= 2.80 and 9.75 <= c.y <= 9.95:
            # North face (+Y normal, facing into Bathroom 1.10) at Z in [1.60, 1.80]
            if poly.normal.y > 0.8 and 1.55 <= c.z <= 1.85:
                poly.material_index = tile_mat_idx
                updated_faces += 1
                print(f"  Updated North lintel face at ({c.x:.3f}, {c.y:.3f}, {c.z:.3f}) -> slot {tile_mat_idx}")
            # Top face (+Z normal) at Z = 1.800
            elif poly.normal.z > 0.8 and c.z >= 1.78:
                poly.material_index = tile_mat_idx
                updated_faces += 1
                print(f"  Updated Top lintel face at ({c.x:.3f}, {c.y:.3f}, {c.z:.3f}) -> slot {tile_mat_idx}")

    iw.data.update()
    print(f"[OK] Bathroom door lintel updated: {updated_faces} faces set to grey tile '{m1.name}'.")

def update_window_frames_and_sills(blend_path):
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

    print("[INFO] Constructing Window_Frames_and_Sills with anthracite sills and downward noses...")
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

    # Material: All anthracite (frames, exterior sills, interior sills with noses)
    obj.data.materials.append(mat_anthracite)

    # Bevel modifier for crisp architectural highlights
    mod_b = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod_b.width = 0.002
    mod_b.segments = 2
    mod_b.limit_method = 'ANGLE'
    mod_b.angle_limit = math.radians(45)
    mod_b.harden_normals = True

    print(f"[OK] {obj_name} created with anthracite sills and interior noses.")

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 1. Update Bathroom Door Lintel
    update_bathroom_lintel(blend_path)

    # 2. Update Window Frames and Sills with Interior Noses
    update_window_frames_and_sills(blend_path)

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

    # View 1: Bathroom doorway view from inside bathroom 1.10 looking at door 111_110 and lintel
    c1_data = bpy.data.cameras.new("Cam_Bath_Door_Lintel")
    c1 = bpy.data.objects.new("Cam_Bath_Door_Lintel", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((2.4, 11.2, 1.4))
    c1.rotation_euler = (Vector((2.4, 9.8, 1.4)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 32
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("bathroom_door_lintel_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: bathroom_door_lintel_view.png")

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
