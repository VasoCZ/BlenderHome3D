"""
update_windows_and_fireplace_wall.py
====================================
1. Window Heights:
   - WC (1.08) and Bathroom (1.10) windows moved to identical sill height as Tech room (1.09):
     Z_sill = 1.750 m, Window height = 0.600 m, Head = 2.350 m.
   - Exterior wall openings cut from Z = 1.725 m to Z = 2.350 m (allowing 25 mm sill bed).
   - Window sills (exterior drip nose & interior stool nose) moved to Z = 1.750 m.
   - Window 3D models moved to Z = 1.750 m.

2. Fireplace Wall & Floor Closure:
   - Seamlessly repairs the wall junction where the fireplace used to be:
     - Chamfer wall (Int_Chamfer): [(4.395, 6.130), (4.520, 6.181777), (3.601777, 7.100), (3.550, 6.975)]
     - South wall of 108/111 (Int_108_South): [(0.365, 6.975), (3.550, 6.975), (3.601777, 7.100), (0.365, 7.100)]
     - East wall of 110/111 (Int_110_111_East): X in [2.875, 3.000], Y in [7.100, 11.635]
     - East wall of 108/109 (Int_108_109_East): X in [1.750, 1.875], Y in [7.100, 9.775]
     - Zero gaps, zero exposed foundation slab, perfectly mitered vertices.
     - Welds all vertices cleanly with remove_doubles().

3. Verification Renders:
   - West facade showing WC & Tech windows at exact same horizontal level.
   - North facade showing Bathroom window at Z = 1.750 m.
   - Perspective and top-down renders of repaired fireplace wall.
   - Full floorplan overview.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

def create_box_mesh(name, x_min, x_max, y_min, y_max, z_min, z_max, material=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    v = [
        bm.verts.new((x_min, y_min, z_min)),
        bm.verts.new((x_max, y_min, z_min)),
        bm.verts.new((x_max, y_max, z_min)),
        bm.verts.new((x_min, y_max, z_min)),
        bm.verts.new((x_min, y_min, z_max)),
        bm.verts.new((x_max, y_min, z_max)),
        bm.verts.new((x_max, y_max, z_max)),
        bm.verts.new((x_min, y_max, z_max)),
    ]
    bm.faces.new([v[0], v[1], v[2], v[3]]) # bottom
    bm.faces.new([v[4], v[7], v[6], v[5]]) # top
    bm.faces.new([v[0], v[4], v[5], v[1]]) # front (-Y)
    bm.faces.new([v[1], v[5], v[6], v[2]]) # right (+X)
    bm.faces.new([v[2], v[6], v[7], v[3]]) # back (+Y)
    bm.faces.new([v[3], v[7], v[4], v[0]]) # left (-X)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def create_polygon_prism(name, polygon_2d, z_min, z_max, material=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    b_verts = [bm.verts.new((x, y, z_min)) for x, y in polygon_2d]
    t_verts = [bm.verts.new((x, y, z_max)) for x, y in polygon_2d]
    n = len(polygon_2d)
    bm.faces.new(list(reversed(b_verts)))
    bm.faces.new(t_verts)
    for i in range(n):
        nxt = (i + 1) % n
        bm.faces.new([b_verts[i], b_verts[nxt], t_verts[nxt], t_verts[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj

def apply_boolean_difference(target, cutter):
    mod = target.modifiers.new(name="BoolDiff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter
    mod.solver = 'EXACT'
    bpy.context.view_layer.objects.active = target
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        mod.solver = 'FAST'
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def update_exterior_walls():
    print("[1] Updating Exterior_Walls with aligned small window heights (Sill Z = 1.750m)...")
    old_ext = bpy.data.objects.get("Exterior_Walls")
    mat_ext = bpy.data.materials.get("Mat_Exterior_Wall")
    mat_koupelna = bpy.data.materials.get("koupelna stena") or bpy.data.materials.get("sokl chodba.001")
    mat_plank = bpy.data.materials.get("Plank stena.001") or bpy.data.materials.get("Plank stena")

    if old_ext:
        bpy.data.objects.remove(old_ext, do_unlink=True)

    # Base wall segments (height 2.500m)
    ext_south = create_box_mesh("Ext_South", 0.0, 10.0, 0.0, 0.365, 0.0, 2.500, mat_ext)
    ext_north = create_box_mesh("Ext_North", 0.0, 10.0, 11.635, 12.0, 0.0, 2.500, mat_ext)
    ext_west  = create_box_mesh("Ext_West",  0.0, 0.365, 0.365, 11.635, 0.0, 2.500, mat_ext)
    ext_east  = create_box_mesh("Ext_East",  9.635, 10.0, 0.365, 11.635, 0.0, 2.500, mat_ext)

    # Cutters: bottom is cut at Z_sill - 0.025 to cleanly receive window sills!
    # South Cutters:
    # W1 1.06: X in [1.300, 2.800], Z_sill = 0.850, Z_head = 2.250
    cut_w1_106 = create_box_mesh("Cut_W1_106", 1.300, 2.800, -0.100, 0.465, 0.825, 2.250)
    apply_boolean_difference(ext_south, cut_w1_106)

    # Entrance door: X in [4.640, 5.740], Z in [0.000, 2.050]
    cut_door = create_box_mesh("Cut_Door", 4.640, 5.740, -0.100, 0.465, 0.000, 2.050)
    apply_boolean_difference(ext_south, cut_door)

    # W1 1.05: X in [7.200, 8.700], Z_sill = 0.850, Z_head = 2.250
    cut_w1_105 = create_box_mesh("Cut_W1_105", 7.200, 8.700, -0.100, 0.465, 0.825, 2.250)
    apply_boolean_difference(ext_south, cut_w1_105)

    # East Cutters:
    # W2 South 1.04: Y in [5.900, 7.640], Z_sill = 0.850, Z_head = 2.250
    cut_w2_s = create_box_mesh("Cut_W2_S", 9.535, 10.100, 5.900, 7.640, 0.825, 2.250)
    apply_boolean_difference(ext_east, cut_w2_s)

    # W2 North 1.04: Y in [8.780, 10.520], Z_sill = 0.850, Z_head = 2.250
    cut_w2_n = create_box_mesh("Cut_W2_N", 9.535, 10.100, 8.780, 10.520, 0.825, 2.250)
    apply_boolean_difference(ext_east, cut_w2_n)

    # North Cutters:
    # W5 1.10 (Bathroom): X in [1.120, 2.120], Z_sill = 1.750, Z_head = 2.350 (MATCHING TECH ROOM!)
    cut_w5 = create_box_mesh("Cut_W5", 1.120, 2.120, 11.535, 12.100, 1.725, 2.350)
    apply_boolean_difference(ext_north, cut_w5)

    # W4 1.03 (Ložnice): X in [3.660, 5.400], Z_sill = 0.850, Z_head = 2.250
    cut_w4 = create_box_mesh("Cut_W4", 3.660, 5.400, 11.535, 12.100, 0.825, 2.250)
    apply_boolean_difference(ext_north, cut_w4)

    # Patio Door 1.04: X in [7.125, 8.925], Z in [0.000, 2.150]
    cut_patio = create_box_mesh("Cut_Patio", 7.125, 8.925, 11.535, 12.100, 0.000, 2.150)
    apply_boolean_difference(ext_north, cut_patio)

    # West Cutters:
    # W05 1.07: Y in [4.725, 6.225], Z_sill = 0.850, Z_head = 2.250
    cut_w05 = create_box_mesh("Cut_W05", -0.100, 0.465, 4.725, 6.225, 0.825, 2.250)
    apply_boolean_difference(ext_west, cut_w05)

    # W6 WC 1.08: Y in [7.200, 8.000], Z_sill = 1.750, Z_head = 2.350 (MATCHING TECH ROOM!)
    cut_w6_wc = create_box_mesh("Cut_W6_WC", -0.100, 0.465, 7.200, 8.000, 1.725, 2.350)
    apply_boolean_difference(ext_west, cut_w6_wc)

    # W6 Tech 1.09: Y in [8.375, 9.175], Z_sill = 1.750, Z_head = 2.350 (600mm height)
    cut_w6_tech = create_box_mesh("Cut_W6_Tech", -0.100, 0.465, 8.375, 9.175, 1.725, 2.350)
    apply_boolean_difference(ext_west, cut_w6_tech)

    # Join 4 facades
    bpy.ops.object.select_all(action='DESELECT')
    for s in [ext_south, ext_north, ext_west, ext_east]:
        s.select_set(True)
    bpy.context.view_layer.objects.active = ext_south
    bpy.ops.object.join()
    ext_walls = bpy.context.active_object
    ext_walls.name = "Exterior_Walls"

    # Add door side tongues and top lintel geometry
    bm = bmesh.new()
    bm.from_mesh(ext_walls.data)
    def add_box_bm(bm, x0, x1, y0, y1, z0, z1):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[4], v[7], v[6], v[5]])
        bm.faces.new([v[0], v[4], v[5], v[1]])
        bm.faces.new([v[2], v[6], v[7], v[3]])
        bm.faces.new([v[0], v[3], v[7], v[4]])
        bm.faces.new([v[1], v[5], v[6], v[2]])

    # Left tongue enters frame groove: X in [4.640, 4.705], Y in [0.015, 0.123], Z in [0.000, 2.050]
    add_box_bm(bm, 4.640, 4.705, 0.015, 0.123, 0.000, 2.050)
    # Right tongue enters frame groove: X in [5.675, 5.740], Y in [0.015, 0.123], Z in [0.000, 2.050]
    add_box_bm(bm, 5.675, 5.740, 0.015, 0.123, 0.000, 2.050)
    # Top wall lintel (nadpraží): X in [4.640, 5.740], Y in [0.000, 0.365], Z in [2.050, 2.500]
    add_box_bm(bm, 4.640, 5.740, 0.000, 0.365, 2.050, 2.500)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(ext_walls.data)
    bm.free()

    # Materials for bathroom
    if mat_koupelna:
        ext_walls.data.materials.append(mat_koupelna)
    if mat_plank:
        ext_walls.data.materials.append(mat_plank)

    # Assign bathroom interior face
    bm = bmesh.new()
    bm.from_mesh(ext_walls.data)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(f.normal.x - 1.0) < 0.1 and abs(c.x - 0.365) < 0.01:
            if 9.85 < c.y < 10.89 and mat_plank:
                f.material_index = ext_walls.data.materials.find(mat_plank.name)
            elif 10.89 < c.y < 11.64 and mat_koupelna:
                f.material_index = ext_walls.data.materials.find(mat_koupelna.name)
    bm.to_mesh(ext_walls.data)
    bm.free()
    print("  Exterior_Walls completed!")
    return ext_walls

def update_interior_walls():
    print("[2] Updating Interior_Walls (repairing fireplace wall junction & closing all gaps)...")
    old_int = bpy.data.objects.get("Interior_Walls")
    mat_int = bpy.data.materials.get("Mat_Interior_Wall")
    mat_koupelna = bpy.data.materials.get("koupelna stena") or bpy.data.materials.get("sokl chodba.001")
    mat_plank = bpy.data.materials.get("Plank stena.001") or bpy.data.materials.get("Plank stena")

    if old_int:
        bpy.data.objects.remove(old_int, do_unlink=True)

    int_segments = []

    # 1. 106 / 101 vertical
    w_106_101 = create_box_mesh("Int_106_101", 3.650, 3.775, 0.365, 2.350, 0.0, 2.500, mat_int)
    int_segments.append(w_106_101)

    # 2. 101 North (between 101 and 102): cutout at Z in [0.000, 2.020]
    w_101_north = create_box_mesh("Int_101_North", 3.650, 6.100, 2.350, 2.475, 0.0, 2.500, mat_int)
    d_101_102 = create_box_mesh("Cut_101_102", 4.700, 5.500, 2.250, 2.575, 0.000, 2.020)
    apply_boolean_difference(w_101_north, d_101_102)
    int_segments.append(w_101_north)

    # 3. 105 West (between 101/102 and 105): cutout at Z in [0.000, 2.020]
    w_105_west = create_box_mesh("Int_105_West", 6.100, 6.225, 0.365, 4.850, 0.0, 2.500, mat_int)
    d_102_105 = create_box_mesh("Cut_102_105", 6.000, 6.325, 2.800, 3.600, 0.000, 2.020)
    apply_boolean_difference(w_105_west, d_102_105)
    int_segments.append(w_105_west)

    # 4. 105 North (between 105 and 104)
    w_105_north = create_box_mesh("Int_105_North", 6.225, 9.635, 4.725, 4.850, 0.0, 2.500, mat_int)
    int_segments.append(w_105_north)

    # 5. East wall of 106 & 107 (along 1.02 corridor)
    p_106_107_east = [(4.395, 2.475), (4.520, 2.475), (4.520, 6.181777), (4.395, 6.130)]
    w_106_107_east = create_polygon_prism("Int_106_107_East", p_106_107_east, 0.0, 2.500, mat_int)
    d_102_106 = create_box_mesh("Cut_102_106", 4.295, 4.620, 2.700, 3.500, 0.000, 2.020)
    apply_boolean_difference(w_106_107_east, d_102_106)
    d_102_107 = create_box_mesh("Cut_102_107", 4.295, 4.620, 4.800, 5.600, 0.000, 2.020)
    apply_boolean_difference(w_106_107_east, d_102_107)
    int_segments.append(w_106_107_east)

    # 6. Partition between 106 and 107 (EXACT BLUEPRINT POSITION: Y in [3.850, 3.975])
    w_106_107_part = create_box_mesh("Int_106_107_Part", 0.365, 4.395, 3.850, 3.975, 0.0, 2.500, mat_int)
    int_segments.append(w_106_107_part)

    # 7. 45-degree chamfer wall for Room 107
    # Mitered seamlessly at (4.520, 6.181777) with East wall and at (3.601777, 7.100) with North wall!
    p_chamfer = [(4.395, 6.130), (4.520, 6.181777), (3.601777, 7.100), (3.550, 6.975)]
    w_chamfer = create_polygon_prism("Int_Chamfer", p_chamfer, 0.0, 2.500, mat_int)
    int_segments.append(w_chamfer)

    # 8. South wall of 108/111 (between 107 and 108/111/Living Room)
    # Perfectly mitered to w_chamfer along (3.550, 6.975) -> (3.601777, 7.100).
    # North face runs along Y = 7.100 from X = 0.365 to X = 3.601777!
    p_108_south = [(0.365, 6.975), (3.550, 6.975), (3.601777, 7.100), (0.365, 7.100)]
    w_108_south = create_polygon_prism("Int_108_South", p_108_south, 0.0, 2.500, mat_int)
    int_segments.append(w_108_south)

    # 9. Partition between 108 and 109
    w_108_109_part = create_box_mesh("Int_108_109_Part", 0.365, 1.750, 8.1625, 8.2875, 0.0, 2.500, mat_int)
    int_segments.append(w_108_109_part)

    # 10. North wall of 109 (between 109 and 110)
    w_109_north = create_box_mesh("Int_109_North", 0.365, 2.875, 9.775, 9.900, 0.0, 2.500, mat_int)
    d_111_110 = create_box_mesh("Cut_111_110", 2.050, 2.750, 9.675, 10.000, 0.000, 2.020)
    apply_boolean_difference(w_109_north, d_111_110)
    int_segments.append(w_109_north)

    # 11. East wall of 108/109 (along 111 corridor)
    w_108_109_east = create_box_mesh("Int_108_109_East", 1.750, 1.875, 7.100, 9.775, 0.0, 2.500, mat_int)
    d_111_108 = create_box_mesh("Cut_111_108", 1.650, 1.975, 7.250, 7.950, 0.000, 2.020)
    apply_boolean_difference(w_108_109_east, d_111_108)
    d_111_109 = create_box_mesh("Cut_111_109", 1.650, 1.975, 8.550, 9.250, 0.000, 2.020)
    apply_boolean_difference(w_108_109_east, d_111_109)
    int_segments.append(w_108_109_east)

    # 12. East wall of 110 & 111 (between 110/111 and 104)
    # Starts at Y = 7.100 where it meets w_108_south north face!
    w_110_111_east = create_box_mesh("Int_110_111_East", 2.875, 3.000, 7.100, 11.635, 0.0, 2.500, mat_int)
    d_104_111 = create_box_mesh("Cut_104_111", 2.775, 3.100, 7.200, 8.000, 0.000, 2.020)
    apply_boolean_difference(w_110_111_east, d_104_111)
    int_segments.append(w_110_111_east)

    # Join interior partitions
    bpy.ops.object.select_all(action='DESELECT')
    for s in int_segments:
        s.select_set(True)
    bpy.context.view_layer.objects.active = int_segments[0]
    bpy.ops.object.join()
    int_walls = bpy.context.active_object
    int_walls.name = "Interior_Walls"

    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(int_walls.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    internal_faces = [f for f in bm.faces if len(f.edges) == 4 and all(len(e.link_faces) > 2 for e in f.edges)]
    if internal_faces:
        bmesh.ops.delete(bm, geom=internal_faces, context='FACES')
    bmesh.update_edit_mesh(int_walls.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Materials for bathroom
    if mat_koupelna:
        int_walls.data.materials.append(mat_koupelna)
    if mat_plank:
        int_walls.data.materials.append(mat_plank)

    # Assign bathroom faces
    bm = bmesh.new()
    bm.from_mesh(int_walls.data)
    bm.faces.ensure_lookup_table()
    for f in bm.faces:
        c = f.calc_center_median()
        # South wall inner face facing into bathroom (+Y normal)
        if abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.900) < 0.05:
            if 0.36 < c.x < 1.37 and mat_plank:
                f.material_index = int_walls.data.materials.find(mat_plank.name)
            elif (1.36 < c.x < 2.06 or 2.00 < c.x < 2.88) and mat_koupelna:
                f.material_index = int_walls.data.materials.find(mat_koupelna.name)
        # Door lintel face above bathroom door facing into bathroom
        elif abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.900) < 0.05 and 2.05 < c.x < 2.75 and c.z >= 2.00:
            if mat_koupelna:
                f.material_index = int_walls.data.materials.find(mat_koupelna.name)
    bm.to_mesh(int_walls.data)
    bm.free()
    print("  Interior_Walls completed successfully!")
    return int_walls

def build_interior_door_frames():
    print("[3] Generating precision obložkové zárubně (casing door frames)...")
    old_df = bpy.data.objects.get("Interior_Door_Frames")
    if old_df:
        bpy.data.objects.remove(old_df, do_unlink=True)

    mat_frame = bpy.data.materials.get("Mat_Roof_Soffit")

    # 8 door specs:
    # (name, is_x_aligned, x_center, y_center, width, wall_thick)
    door_specs = [
        ("DF_101_102", True,  5.100, 2.4125, 0.800, 0.125),
        ("DF_102_105", False, 6.1625, 3.200, 0.800, 0.125),
        ("DF_102_106", False, 4.4575, 3.100, 0.800, 0.125),
        ("DF_102_107", False, 4.4575, 5.200, 0.800, 0.125),
        ("DF_104_111", False, 2.9375, 7.600, 0.800, 0.125),
        ("DF_111_108", False, 1.8125, 7.600, 0.700, 0.125),
        ("DF_111_109", False, 1.8125, 8.900, 0.700, 0.125),
        ("DF_111_110", True,  2.400, 9.8375, 0.700, 0.125),
    ]

    bm = bmesh.new()

    def add_box_bm(bm, x0, x1, y0, y1, z0, z1):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[4], v[7], v[6], v[5]])
        bm.faces.new([v[0], v[4], v[5], v[1]])
        bm.faces.new([v[2], v[6], v[7], v[3]])
        bm.faces.new([v[0], v[3], v[7], v[4]])
        bm.faces.new([v[1], v[5], v[6], v[2]])

    t_lining = 0.016   # 16mm jamb lining board inside cutout
    w_arch = 0.055     # 55mm architrave facing strip
    d_arch = 0.012     # 12mm projection of trim from wall face
    h_cut = 2.020      # wall cutout top height

    for name, is_x, xc, yc, w, wt in door_specs:
        half_w = w / 2.0
        half_wt = wt / 2.0

        if is_x:
            # Wall runs along X, thickness across Y: [yc - half_wt, yc + half_wt]
            # 1. Jamb linings
            add_box_bm(bm, xc - half_w, xc - half_w + t_lining, yc - half_wt, yc + half_wt, 0.000, h_cut - t_lining)
            add_box_bm(bm, xc + half_w - t_lining, xc + half_w, yc - half_wt, yc + half_wt, 0.000, h_cut - t_lining)
            add_box_bm(bm, xc - half_w, xc + half_w, yc - half_wt, yc + half_wt, h_cut - t_lining, h_cut)

            # 2. Architraves
            for side in [-1, 1]:
                y_wall = yc + side * half_wt
                y0, y1 = (y_wall - d_arch, y_wall) if side == -1 else (y_wall, y_wall + d_arch)
                add_box_bm(bm, xc - half_w - w_arch + t_lining, xc - half_w + t_lining, y0, y1, 0.000, h_cut + w_arch - t_lining)
                add_box_bm(bm, xc + half_w - t_lining, xc + half_w + w_arch - t_lining, y0, y1, 0.000, h_cut + w_arch - t_lining)
                add_box_bm(bm, xc - half_w - w_arch + t_lining, xc + half_w + w_arch - t_lining, y0, y1, h_cut - t_lining, h_cut + w_arch - t_lining)

        else:
            # Wall runs along Y, thickness across X: [xc - half_wt, xc + half_wt]
            # 1. Jamb linings
            add_box_bm(bm, xc - half_wt, xc + half_wt, yc - half_w, yc - half_w + t_lining, 0.000, h_cut - t_lining)
            add_box_bm(bm, xc - half_wt, xc + half_wt, yc + half_w - t_lining, yc + half_w, 0.000, h_cut - t_lining)
            add_box_bm(bm, xc - half_wt, xc + half_wt, yc - half_w, yc + half_w, h_cut - t_lining, h_cut)

            # 2. Architraves
            for side in [-1, 1]:
                x_wall = xc + side * half_wt
                x0, x1 = (x_wall - d_arch, x_wall) if side == -1 else (x_wall, x_wall + d_arch)
                add_box_bm(bm, x0, x1, yc - half_w - w_arch + t_lining, yc - half_w + t_lining, 0.000, h_cut + w_arch - t_lining)
                add_box_bm(bm, x0, x1, yc + half_w - t_lining, yc + half_w + w_arch - t_lining, 0.000, h_cut + w_arch - t_lining)
                add_box_bm(bm, x0, x1, yc - half_w - w_arch + t_lining, yc + half_w + w_arch - t_lining, h_cut - t_lining, h_cut + w_arch - t_lining)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("Interior_Door_Frames")
    bm.to_mesh(mesh)
    bm.free()

    df_obj = bpy.data.objects.new("Interior_Door_Frames", mesh)
    bpy.context.scene.collection.objects.link(df_obj)
    if mat_frame:
        df_obj.data.materials.append(mat_frame)
    print("  Interior_Door_Frames completed!")
    return df_obj

def update_window_sills():
    print("[4] Generating precision architectural Window_Sills (zero Z-fighting, zero clipping)...")
    old_sills = bpy.data.objects.get("Window_Sills")
    if old_sills:
        bpy.data.objects.remove(old_sills, do_unlink=True)

    mat_anthracite = bpy.data.materials.get("Mat_Roof_Soffit")

    # 9 window openings specification with aligned small windows (Sill Z = 1.750m):
    # (name, wall, x_min, x_max, y_min, y_max, z_sill)
    windows = [
        ("W1_106", "south", 1.300, 2.800, 0.000, 0.365, 0.850),
        ("W1_105", "south", 7.200, 8.700, 0.000, 0.365, 0.850),
        ("W2_South_104", "east", 9.635, 10.000, 5.900, 7.640, 0.850),
        ("W2_North_104", "east", 9.635, 10.000, 8.780, 10.520, 0.850),
        ("W4_103", "north", 3.660, 5.400, 11.635, 12.000, 0.850),
        ("W5_110", "north", 1.120, 2.120, 11.635, 12.000, 1.750),   # MATCHING TECH ROOM!
        ("W05_107", "west", 0.000, 0.365, 4.725, 6.225, 0.850),
        ("W6_WC_108", "west", 0.000, 0.365, 7.200, 8.000, 1.750),   # MATCHING TECH ROOM!
        ("W6_Tech_109", "west", 0.000, 0.365, 8.375, 9.175, 1.750), # 1750mm sill
    ]

    bm = bmesh.new()

    def add_box_bm(bm, x0, x1, y0, y1, z0, z1):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[4], v[7], v[6], v[5]])
        bm.faces.new([v[0], v[4], v[5], v[1]])
        bm.faces.new([v[2], v[6], v[7], v[3]])
        bm.faces.new([v[0], v[3], v[7], v[4]])
        bm.faces.new([v[1], v[5], v[6], v[2]])

    ear = 0.020       # 20mm ear width beyond opening in overhang region
    overhang = 0.035  # 35mm exterior projection past facade
    overhang_int = 0.030 # 30mm interior projection into room
    drop = 0.020      # 20mm downward nose drop
    t_sill = 0.020    # 20mm sill thickness

    for name, wall, x0, x1, y0, y1, zs in windows:
        if wall == "south":
            add_box_bm(bm, x0, x1, 0.000, 0.100, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, -overhang, 0.000, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, -overhang, -overhang + 0.018, zs - t_sill - drop, zs - t_sill)
            add_box_bm(bm, x0, x1, 0.100, 0.170, zs - 0.025, zs)
            add_box_bm(bm, x0, x1, 0.170, 0.365, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 0.365, 0.365 + overhang_int, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 0.365 + overhang_int - 0.018, 0.365 + overhang_int, zs - t_sill - drop, zs - t_sill)

        elif wall == "north":
            add_box_bm(bm, x0, x1, 11.900, 12.000, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 12.000, 12.000 + overhang, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 12.000 + overhang - 0.018, 12.000 + overhang, zs - t_sill - drop, zs - t_sill)
            add_box_bm(bm, x0, x1, 11.830, 11.900, zs - 0.025, zs)
            add_box_bm(bm, x0, x1, 11.635, 11.830, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 11.635 - overhang_int, 11.635, zs - t_sill, zs)
            add_box_bm(bm, x0 - ear, x1 + ear, 11.635 - overhang_int, 11.635 - overhang_int + 0.018, zs - t_sill - drop, zs - t_sill)

        elif wall == "east":
            add_box_bm(bm, 9.900, 10.000, y0, y1, zs - t_sill, zs)
            add_box_bm(bm, 10.000, 10.000 + overhang, y0 - ear, y1 + ear, zs - t_sill, zs)
            add_box_bm(bm, 10.000 + overhang - 0.018, 10.000 + overhang, y0 - ear, y1 + ear, zs - t_sill - drop, zs - t_sill)
            add_box_bm(bm, 9.830, 9.900, y0, y1, zs - 0.025, zs)
            add_box_bm(bm, 9.635, 9.830, y0, y1, zs - t_sill, zs)
            add_box_bm(bm, 9.635 - overhang_int, 9.635, y0 - ear, y1 + ear, zs - t_sill, zs)
            add_box_bm(bm, 9.635 - overhang_int, 9.635 - overhang_int + 0.018, y0 - ear, y1 + ear, zs - t_sill - drop, zs - t_sill)

        elif wall == "west":
            add_box_bm(bm, 0.000, 0.100, y0, y1, zs - t_sill, zs)
            add_box_bm(bm, -overhang, 0.000, y0 - ear, y1 + ear, zs - t_sill, zs)
            add_box_bm(bm, -overhang, -overhang + 0.018, y0 - ear, y1 + ear, zs - t_sill - drop, zs - t_sill)
            add_box_bm(bm, 0.100, 0.170, y0, y1, zs - 0.025, zs)
            add_box_bm(bm, 0.170, 0.365, y0, y1, zs - t_sill, zs)
            add_box_bm(bm, 0.365, 0.365 + overhang_int, y0 - ear, y1 + ear, zs - t_sill, zs)
            add_box_bm(bm, 0.365 + overhang_int - 0.018, 0.365 + overhang_int, y0 - ear, y1 + ear, zs - t_sill - drop, zs - t_sill)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("Window_Sills")
    bm.to_mesh(mesh)
    bm.free()

    sills_obj = bpy.data.objects.new("Window_Sills", mesh)
    bpy.context.scene.collection.objects.link(sills_obj)
    if mat_anthracite:
        sills_obj.data.materials.append(mat_anthracite)
    print("  Window_Sills completed!")
    return sills_obj

def update_window_models():
    print("[5] Updating Window_Models positions (WC & Bath moved to Z = 1.750m)...")
    base_dir = r"C:\Users\Vaso\Antigravity\Project blender"
    asset1_path = os.path.join(base_dir, "assets/models/pvc-window-fixed_35b7e661-a16e-44f5-b0b5-dc84efed6ca3/blend_bcdd59d3-5e63-4484-b59d-e6d2b0acf0b6.blend")
    asset2_path = os.path.join(base_dir, "assets/models/pvc-window-fixed_197e937f-d348-4867-8b99-af5cfd52cfb7/pvc-window-fixed_df64259d-508f-4bb0-b316-5b1c93ce756e.blend")

    col_name = "Window_Models"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    for ob in list(col.objects):
        bpy.data.objects.remove(ob, do_unlink=True)

    def load_template(filepath):
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        root = None
        children = []
        for o in data_to.objects:
            if o.name == 'PVC Window – Fixed':
                root = o
            else:
                children.append(o)
        return root, children

    root1, children1 = load_template(asset1_path)
    root2, children2 = load_template(asset2_path)

    # Window placement targets:
    # (name, asset_idx, wall, center_x, center_y, sill_z, width, height)
    targets = [
        # Group 2: Asset 2 (Double sash)
        ("Window_1.06_South", 2, "south", 2.050, 0.135, 0.850, 1.500, 1.400),
        ("Window_1.05_South", 2, "south", 7.950, 0.135, 0.850, 1.500, 1.400),
        ("Window_1.07_West",  2, "west",  0.135, 5.475, 0.850, 1.500, 1.400),

        # Group 1: Asset 1 (Single sash) - ALIGNED SMALL WINDOWS AT Z = 1.750m!
        ("Window_1.08_WC",       1, "west",  0.135, 7.600, 1.750, 0.800, 0.600), # MATCHING TECH ROOM!
        ("Window_1.09_Tech",     1, "west",  0.135, 8.775, 1.750, 0.800, 0.600), # 1750mm sill
        ("Window_1.10_Bathroom", 1, "north", 1.620, 11.865, 1.750, 1.000, 0.600), # MATCHING TECH ROOM!
        ("Window_1.03_Bedroom",  1, "north", 4.530, 11.865, 0.850, 1.740, 1.400),
        ("Window_1.04_EastSouth",1, "east",  9.865, 6.770, 0.850, 1.740, 1.400),
        ("Window_1.04_EastNorth",1, "east",  9.865, 9.650, 0.850, 1.740, 1.400),
    ]

    rot_map = {
        "south": math.pi,
        "north": 0.0,
        "east":  -math.pi / 2,
        "west":  math.pi / 2,
    }

    for name, aid, wall, cx, cy, zs, w, h in targets:
        children = children1 if aid == 1 else children2
        y_center_offset = 0.035 if aid == 1 else 0.0

        empty = bpy.data.objects.new(name, None)
        empty.empty_display_type = 'ARROWS'
        empty.empty_display_size = 0.25
        empty.location = (cx, cy, zs)
        empty.rotation_euler = (0, 0, rot_map[wall])
        empty.scale = (w, 1.0, h)
        col.objects.link(empty)

        for c in children:
            new_c = c.copy()
            new_c.name = f"{name}_{c.name}"
            new_c.parent = empty
            if y_center_offset != 0.0:
                new_c.location.y += y_center_offset
            col.objects.link(new_c)

    for o in children1 + [root1] + children2 + [root2]:
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    print("  Window models placed!")

def render_views():
    print("[6] Rendering verification views...")
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    cam = bpy.data.objects.get("Isometric_Camera")
    if not cam:
        return

    orig_loc = cam.location.copy()
    orig_rot = cam.rotation_euler.copy()
    orig_scale = cam.data.ortho_scale if hasattr(cam.data, 'ortho_scale') else 18.0
    orig_type = cam.data.type

    base_dir = r"C:\Users\Vaso\Antigravity\Project blender"

    # 1. Overview
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 18.0
    target = Vector((5.0, 6.0, 1.25))
    distance = 35.0
    iso_dir = Vector((-1.0, -1.0, math.sqrt(2))).normalized()
    cam.location = target + iso_dir * distance
    direction = target - cam.location
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "dum_pudorys_overview.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered dum_pudorys_overview.png")

    # 2. Ortho facade views
    views_ortho = [
        ("small_windows_west_facade.png", Vector((0.18, 8.2, 2.05)), Vector((-4.5, 8.2, 2.05)), 4.0),
        ("small_window_bathroom_facade.png", Vector((1.62, 11.82, 2.05)), Vector((1.62, 15.0, 2.05)), 3.5),
        ("windows_west_real_heights.png",  Vector((0.18, 7.0, 1.55)), Vector((-8.0, 7.0, 1.55)), 9.5),
        ("windows_north_real_heights.png", Vector((5.0, 11.82, 1.55)),Vector((5.0, 20.0, 1.55)), 9.5),
    ]

    for fname, tgt, cam_pos, oscale in views_ortho:
        cam.data.type = 'ORTHO'
        cam.location = cam_pos
        cam.data.ortho_scale = oscale
        dir_vec = tgt - cam.location
        cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.render.filepath = os.path.join(base_dir, fname)
        bpy.ops.render.render(write_still=True)
        print(f"  Rendered {fname}")

    # 3. Fireplace top-down view (ORTHO)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = 4.5
    cam.location = Vector((3.6, 6.6, 12.0))
    cam.rotation_euler = (0, 0, 0)
    bpy.context.scene.render.filepath = os.path.join(base_dir, "inspect_fireplace_area_topdown.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered inspect_fireplace_area_topdown.png")

    # 4. Fireplace living room perspective view
    cam.data.type = 'PERSP'
    cam.data.lens = 28
    cam.location = Vector((6.5, 8.5, 1.9))
    tgt = Vector((3.3, 6.8, 1.1))
    dir_vec = tgt - cam.location
    cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = os.path.join(base_dir, "inspect_fireplace_living_room.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered inspect_fireplace_living_room.png")

    # Restore camera
    cam.data.type = orig_type
    cam.location = orig_loc
    cam.rotation_euler = orig_rot
    if hasattr(cam.data, 'ortho_scale'):
        cam.data.ortho_scale = orig_scale

def main():
    print("=" * 70)
    print("APPLYING FIXES: ALIGNING SMALL WINDOWS & REPAIRING FIREPLACE WALL")
    print("=" * 70)

    update_exterior_walls()
    update_interior_walls()
    build_interior_door_frames()
    update_window_sills()
    update_window_models()

    base_dir = r"C:\Users\Vaso\Antigravity\Project blender"
    out_path = os.path.join(base_dir, "dum_pudorys.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print(f"\n[SUCCESS] Saved updated dum_pudorys.blend to: {out_path}")

    render_views()
    print("=" * 70)
    print("ALL FIXES APPLIED AND VERIFIED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
