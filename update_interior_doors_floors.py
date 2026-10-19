"""
update_interior_doors_floors.py
===============================
Fixes floors in door openings and adds interior door frames and lintels:

1. Fixes floors in door openings (Zárubňové prahy a podlahy):
   - Fills all 8 interior doorways + front entrance threshold + patio threshold at Z in [0.000, 0.015] m.
   - Assigns matching interior floor materials (Laminate or Tile) with proper UV coordinates (UVMap & automap)
     so the textures continue seamlessly through the doorway and outdoor paving NEVER shows inside.
   - For tile/laminate transitions (101->102 and 104->111), creates realistic transition threshold with satin aluminum strip.

2. Adds Wall Lintels (Překlady nad vnitřními dveřmi):
   - Adds solid wall lintels to 'Interior_Walls' spanning Z in [1.600, 1.800] m for all 8 interior doors.
   - Completely unifies the wall top at Z = 1.800 m across the entire house (idempotent).

3. Adds Interior Door Frames (Obložkové zárubně):
   - Creates 'Interior_Door_Frames' object with clean, non-overlapping wrap-around casing profiles.
   - Side jambs + top head casing extending 5 cm onto the wall face and 1.2 cm thick.
   - Modern satin white lacquer material 'Mat_Interior_Door_Frame' (#F2F0EC, roughness 0.30, specular 0.40).
   - Crisp 1.5 mm edge beveling with hardened normals.

4. Renders verification views (hallway corridor, transition close-up, bathroom doors, full overview).
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

def hex_to_linear(hex_str):
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    to_lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (to_lin(r), to_lin(g), to_lin(b), 1.0)

def create_box_mesh(bm, x0, x1, y0, y1, z0, z1, mat_idx=0, uv_layers=('UVMap', 'automap')):
    v = [
        bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
    ]
    faces_def = [
        ([v[0], v[1], v[2], v[3]], 'Z'),  # bottom (-Z)
        ([v[4], v[7], v[6], v[5]], 'Z'),  # top (+Z)
        ([v[0], v[4], v[5], v[1]], 'Y'),  # south (-Y)
        ([v[2], v[6], v[7], v[3]], 'Y'),  # north (+Y)
        ([v[0], v[3], v[7], v[4]], 'X'),  # west (-X)
        ([v[1], v[5], v[6], v[2]], 'X'),  # east (+X)
    ]
    new_faces = []
    for fverts, f_axis in faces_def:
        f = bm.faces.new(fverts)
        f.material_index = mat_idx
        new_faces.append((f, f_axis))
    
    if uv_layers:
        b_uvs = []
        for uv_name in uv_layers:
            u_lay = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)
            b_uvs.append(u_lay)
        for f, f_axis in new_faces:
            for loop in f.loops:
                co = loop.vert.co
                if f_axis == 'Z':
                    uv_val = (co.x, co.y)
                elif f_axis == 'Y':
                    uv_val = (co.x, co.z)
                else:
                    uv_val = (co.y, co.z)
                for u_lay in b_uvs:
                    loop[u_lay].uv = uv_val

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    # ----------------------------------------------------
    # Door specifications: (door_id, axis, x_range, y_range, type_from, type_to)
    # axis: 'H' (horizontal wall, normal Y) or 'V' (vertical wall, normal X)
    # ----------------------------------------------------
    doors_spec = [
        ("101_102", 'H', (4.700, 5.500), (2.350, 2.475), 'tile_koupelna', 'laminate'),
        ("102_105", 'V', (6.100, 6.225), (2.800, 3.600), 'laminate', 'laminate'),
        ("102_106", 'V', (4.395, 4.520), (2.700, 3.500), 'laminate', 'laminate'),
        ("102_107", 'V', (4.395, 4.520), (4.800, 5.600), 'laminate', 'laminate'),
        ("104_111", 'V', (2.875, 3.000), (7.200, 8.000), 'laminate', 'tile_koupelna'),
        ("111_108", 'V', (1.750, 1.875), (7.250, 7.950), 'tile_koupelna', 'tile_wc'),
        ("111_109", 'V', (1.750, 1.875), (8.550, 9.250), 'tile_koupelna', 'tile_tech'),
        ("111_110", 'H', (2.050, 2.750), (9.775, 9.900), 'tile_koupelna', 'tile_koupelna'),
    ]

    # Materials lookup
    mat_laminate = bpy.data.materials.get("laminate_floor_02.001") or bpy.data.materials.get("Mat_Wood_Laminate")
    mat_tile_koupelna = bpy.data.materials.get("koupelna") or bpy.data.materials.get("Mat_Ceramic_Tiles")
    mat_tile_chodba = bpy.data.materials.get("chodba.002") or mat_tile_koupelna

    # Transition strip material (satin anodized aluminum)
    mat_strip_name = "Mat_Transition_Strip"
    mat_strip = bpy.data.materials.get(mat_strip_name)
    if not mat_strip:
        mat_strip = bpy.data.materials.new(name=mat_strip_name)
        if mat_strip.node_tree is None and hasattr(mat_strip, "use_nodes"):
            mat_strip.use_nodes = True
        bsdf = mat_strip.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.85, 0.86, 0.88, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.20
            if "Metallic" in bsdf.inputs:
                bsdf.inputs["Metallic"].default_value = 0.90

    # Door frame material (modern satin white lacquer)
    mat_frame_name = "Mat_Interior_Door_Frame"
    mat_frame = bpy.data.materials.get(mat_frame_name)
    if not mat_frame:
        mat_frame = bpy.data.materials.new(name=mat_frame_name)
        if mat_frame.node_tree is None and hasattr(mat_frame, "use_nodes"):
            mat_frame.use_nodes = True
        bsdf = mat_frame.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = hex_to_linear("F2F0EC")
            bsdf.inputs["Roughness"].default_value = 0.30
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.40
            elif "Specular" in bsdf.inputs:
                bsdf.inputs["Specular"].default_value = 0.40

    # ----------------------------------------------------
    # 1. Update Interior_Walls: Add Wall Lintels (Překlady nad dveřmi)
    # ----------------------------------------------------
    iw = bpy.data.objects.get("Interior_Walls")
    if not iw:
        raise RuntimeError("Object 'Interior_Walls' not found!")

    bm_iw = bmesh.new()
    bm_iw.from_mesh(iw.data)

    z_lintel_bot = 1.600
    z_lintel_top = 1.800

    print("[INFO] Checking/adding solid wall lintels (překlady) to Interior_Walls...")
    lintels_added = 0
    for door_id, axis, (x0, x1), (y0, y1), _, _ in doors_spec:
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        # Check if bottom face of lintel already exists
        has_lintel = any(
            abs(f.calc_center_median().x - cx) < 0.05 and 
            abs(f.calc_center_median().y - cy) < 0.05 and 
            abs(f.calc_center_median().z - z_lintel_bot) < 0.05 
            for f in bm_iw.faces
        )
        if not has_lintel:
            create_box_mesh(bm_iw, x0, x1, y0, y1, z_lintel_bot, z_lintel_top, mat_idx=0, uv_layers=())
            lintels_added += 1

    if lintels_added > 0:
        bmesh.ops.remove_doubles(bm_iw, verts=bm_iw.verts, dist=0.002)
        bmesh.ops.recalc_face_normals(bm_iw, faces=bm_iw.faces)
        bm_iw.to_mesh(iw.data)
        iw.data.update()
        print(f"[OK] {lintels_added} wall lintels added at Z in [1.600, 1.800] m.")
    else:
        print("[OK] Wall lintels already present for all 8 interior doors.")
    bm_iw.free()

    # ----------------------------------------------------
    # 2. Fix Floors in Door Openings (Zárubňové podlahy a prahy)
    # ----------------------------------------------------
    print("[INFO] Generating threshold floor meshes with UV mapping...")
    # Clean previous threshold objects if present
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Floor_Threshold"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for m in list(bpy.data.meshes):
        if m.name.startswith("Floor_Threshold"):
            bpy.data.meshes.remove(m)

    z_fl_min = 0.000
    z_fl_max = 0.015

    for door_id, axis, (x0, x1), (y0, y1), t_from, t_to in doors_spec:
        t_obj_name = f"Floor_Threshold_{door_id}"

        if t_from == 'laminate' and t_to == 'laminate':
            mesh = bpy.data.meshes.new(t_obj_name)
            bm = bmesh.new()
            create_box_mesh(bm, x0, x1, y0, y1, z_fl_min, z_fl_max, mat_idx=0)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new(t_obj_name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            obj.data.materials.append(mat_laminate)

        elif 'tile' in t_from and 'tile' in t_to:
            mesh = bpy.data.meshes.new(t_obj_name)
            bm = bmesh.new()
            mat = mat_tile_chodba if ('wc' in t_to or 'tech' in t_to) else mat_tile_koupelna
            create_box_mesh(bm, x0, x1, y0, y1, z_fl_min, z_fl_max, mat_idx=0)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new(t_obj_name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            obj.data.materials.append(mat)

        else:
            # Transition between Tile and Laminate: split in half + aluminum transition strip
            mesh = bpy.data.meshes.new(t_obj_name)
            bm = bmesh.new()
            strip_w = 0.020  # 20 mm transition strip

            if axis == 'H':
                y_mid = (y0 + y1) / 2.0
                # South half (Tile - Zádveří)
                create_box_mesh(bm, x0, x1, y0, y_mid, z_fl_min, z_fl_max, mat_idx=0)
                # North half (Laminate - Chodba)
                create_box_mesh(bm, x0, x1, y_mid, y1, z_fl_min, z_fl_max, mat_idx=1)
                # Aluminum strip slightly raised (+1.5 mm above finished floor)
                create_box_mesh(bm, x0, x1, y_mid - strip_w/2, y_mid + strip_w/2, z_fl_max, z_fl_max + 0.0015, mat_idx=2)
            else:
                x_mid = (x0 + x1) / 2.0
                m_w = 1 if t_from == 'laminate' else 0
                create_box_mesh(bm, x0, x_mid, y0, y1, z_fl_min, z_fl_max, mat_idx=m_w)
                m_e = 0 if t_from == 'laminate' else 1
                create_box_mesh(bm, x_mid, x1, y0, y1, z_fl_min, z_fl_max, mat_idx=m_e)
                create_box_mesh(bm, x_mid - strip_w/2, x_mid + strip_w/2, y0, y1, z_fl_max, z_fl_max + 0.0015, mat_idx=2)

            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(mesh)
            bm.free()
            obj = bpy.data.objects.new(t_obj_name, mesh)
            bpy.context.scene.collection.objects.link(obj)
            obj.data.materials.append(mat_tile_koupelna)
            obj.data.materials.append(mat_laminate)
            obj.data.materials.append(mat_strip)

    # Front Entrance Door threshold (inside wall thickness between door frame and room 1.01)
    t_front_name = "Floor_Threshold_Front_Entrance"
    mesh_front = bpy.data.meshes.new(t_front_name)
    bm_front = bmesh.new()
    create_box_mesh(bm_front, 4.640, 5.740, 0.138, 0.365, z_fl_min, z_fl_max, mat_idx=0)
    bmesh.ops.recalc_face_normals(bm_front, faces=bm_front.faces)
    bm_front.to_mesh(mesh_front)
    bm_front.free()
    obj_front = bpy.data.objects.new(t_front_name, mesh_front)
    bpy.context.scene.collection.objects.link(obj_front)
    obj_front.data.materials.append(mat_tile_koupelna)

    # Patio Sliding Door threshold (between room 1.04 and sliding door track)
    t_patio_name = "Floor_Threshold_Patio"
    mesh_patio = bpy.data.meshes.new(t_patio_name)
    bm_patio = bmesh.new()
    create_box_mesh(bm_patio, 7.125, 8.925, 11.635, 11.710, z_fl_min, z_fl_max, mat_idx=0)
    bmesh.ops.recalc_face_normals(bm_patio, faces=bm_patio.faces)
    bm_patio.to_mesh(mesh_patio)
    bm_patio.free()
    obj_patio = bpy.data.objects.new(t_patio_name, mesh_patio)
    bpy.context.scene.collection.objects.link(obj_patio)
    obj_patio.data.materials.append(mat_laminate)

    print("[OK] All door thresholds covered with UV-mapped finished floor materials.")

    # ----------------------------------------------------
    # 3. Add Interior Door Frames (Obložkové zárubně)
    # ----------------------------------------------------
    frames_obj_name = "Interior_Door_Frames"
    if frames_obj_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[frames_obj_name], do_unlink=True)
    if frames_obj_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[frames_obj_name])

    mesh_frames = bpy.data.meshes.new(frames_obj_name)
    bm_frames = bmesh.new()

    c_w = 0.050   # 50 mm casing width onto wall face
    t_c = 0.012   # 12 mm casing protrusion off wall
    t_l = 0.020   # 20 mm inner jamb lining thickness
    z_frame_top = 1.600
    z_head_clear = 1.580
    z_arch_top = z_frame_top + c_w  # 1.650 m

    print("[INFO] Modeling wrap-around door frames (obložkové zárubně)...")
    for door_id, axis, (x0, x1), (y0, y1), _, _ in doors_spec:
        if axis == 'H':
            # Wall along X: opening X in [x0, x1], wall Y in [y0, y1]
            # Left post (continuous up to top architrave Z = 1.650 m)
            create_box_mesh(bm_frames, x0, x0 + t_l, y0, y1, 0.000, z_frame_top, mat_idx=0) # lining
            create_box_mesh(bm_frames, x0 - c_w, x0 + t_l, y0 - t_c, y0, 0.000, z_arch_top, mat_idx=0) # south casing
            create_box_mesh(bm_frames, x0 - c_w, x0 + t_l, y1, y1 + t_c, 0.000, z_arch_top, mat_idx=0) # north casing

            # Right post (continuous up to top architrave Z = 1.650 m)
            create_box_mesh(bm_frames, x1 - t_l, x1, y0, y1, 0.000, z_frame_top, mat_idx=0) # lining
            create_box_mesh(bm_frames, x1 - t_l, x1 + c_w, y0 - t_c, y0, 0.000, z_arch_top, mat_idx=0) # south casing
            create_box_mesh(bm_frames, x1 - t_l, x1 + c_w, y1, y1 + t_c, 0.000, z_arch_top, mat_idx=0) # north casing

            # Head frame (neatly seated between vertical posts, zero overlap)
            create_box_mesh(bm_frames, x0 + t_l, x1 - t_l, y0, y1, z_head_clear, z_frame_top, mat_idx=0) # head soffit lining
            create_box_mesh(bm_frames, x0 + t_l, x1 - t_l, y0 - t_c, y0, z_head_clear, z_arch_top, mat_idx=0) # south head casing
            create_box_mesh(bm_frames, x0 + t_l, x1 - t_l, y1, y1 + t_c, z_head_clear, z_arch_top, mat_idx=0) # north head casing

        else:
            # Wall along Y: opening Y in [y0, y1], wall X in [x0, x1]
            # South post
            create_box_mesh(bm_frames, x0, x1, y0, y0 + t_l, 0.000, z_frame_top, mat_idx=0) # lining
            create_box_mesh(bm_frames, x0 - t_c, x0, y0 - c_w, y0 + t_l, 0.000, z_arch_top, mat_idx=0) # west casing
            create_box_mesh(bm_frames, x1, x1 + t_c, y0 - c_w, y0 + t_l, 0.000, z_arch_top, mat_idx=0) # east casing

            # North post
            create_box_mesh(bm_frames, x0, x1, y1 - t_l, y1, 0.000, z_frame_top, mat_idx=0) # lining
            create_box_mesh(bm_frames, x0 - t_c, x0, y1 - t_l, y1 + c_w, 0.000, z_arch_top, mat_idx=0) # west casing
            create_box_mesh(bm_frames, x1, x1 + t_c, y1 - t_l, y1 + c_w, 0.000, z_arch_top, mat_idx=0) # east casing

            # Head frame (seated between vertical posts, zero overlap)
            create_box_mesh(bm_frames, x0, x1, y0 + t_l, y1 - t_l, z_head_clear, z_frame_top, mat_idx=0) # head soffit lining
            create_box_mesh(bm_frames, x0 - t_c, x0, y0 + t_l, y1 - t_l, z_head_clear, z_arch_top, mat_idx=0) # west head casing
            create_box_mesh(bm_frames, x1, x1 + t_c, y0 + t_l, y1 - t_l, z_head_clear, z_arch_top, mat_idx=0) # east head casing

    bmesh.ops.remove_doubles(bm_frames, verts=bm_frames.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm_frames, faces=bm_frames.faces)
    bm_frames.to_mesh(mesh_frames)
    bm_frames.free()

    obj_frames = bpy.data.objects.new(frames_obj_name, mesh_frames)
    bpy.context.scene.collection.objects.link(obj_frames)
    obj_frames.data.materials.append(mat_frame)

    # Crisp Bevel modifier for realistic joinery edges
    mod_b = obj_frames.modifiers.new(name="Bevel", type='BEVEL')
    mod_b.width = 0.0015
    mod_b.segments = 2
    mod_b.limit_method = 'ANGLE'
    mod_b.angle_limit = math.radians(45)
    mod_b.harden_normals = True

    print("[OK] Interior_Door_Frames created with 8 cleanly fitted wrap-around casings.")

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

    # View 1: Close-up of doorway 101 -> 102 and 102 -> 105 showing threshold floor, casing & lintel
    c1_data = bpy.data.cameras.new("Cam_Door_Transition")
    c1 = bpy.data.objects.new("Cam_Door_Transition", c1_data)
    scene.collection.objects.link(c1)
    c1.location = Vector((6.5, 1.2, 2.6))
    c1.rotation_euler = (Vector((5.3, 2.8, 1.0)) - c1.location).to_track_quat('-Z', 'Y').to_euler()
    c1_data.type = 'PERSP'
    c1_data.lens = 45
    scene.camera = c1
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("doorway_transition_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: doorway_transition_view.png")

    # View 2: Perspective view along hallway 1.02 showing multiple framed doorways and lintels
    c2_data = bpy.data.cameras.new("Cam_Door_Hallway")
    c2 = bpy.data.objects.new("Cam_Door_Hallway", c2_data)
    scene.collection.objects.link(c2)
    c2.location = Vector((5.3, 1.8, 2.2))
    c2.rotation_euler = (Vector((5.1, 4.5, 1.2)) - c2.location).to_track_quat('-Z', 'Y').to_euler()
    c2_data.type = 'PERSP'
    c2_data.lens = 38
    scene.camera = c2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("doorway_hallway_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: doorway_hallway_view.png")

    # View 3: Close-up of hallway 1.11 showing doors to Bathroom, WC and Tech room
    c3_data = bpy.data.cameras.new("Cam_Door_Bath")
    c3 = bpy.data.objects.new("Cam_Door_Bath", c3_data)
    scene.collection.objects.link(c3)
    c3.location = Vector((3.6, 7.8, 2.4))
    c3.rotation_euler = (Vector((2.2, 8.5, 1.1)) - c3.location).to_track_quat('-Z', 'Y').to_euler()
    c3_data.type = 'PERSP'
    c3_data.lens = 42
    scene.camera = c3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("doorway_bath_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: doorway_bath_view.png")

    # View 4: Full floor plan overview using user's Isometric_Camera
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
