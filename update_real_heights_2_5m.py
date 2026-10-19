"""
Script: update_real_heights_2_5m.py
Updates dum_pudorys.blend to realistic 2.50m wall heights:
1. Reconstructs Exterior_Walls with height 2.500m, unified lintels at Z = 2.250-2.500m.
2. Reconstructs Interior_Walls with height 2.500m, door openings at 2.000m, lintels at 2.000-2.500m.
3. Shifts Roof_Soffit_Cornice to Z in [2.420, 2.500m].
4. Reconstructs Interior_Door_Frames for 2.000m clear height (2.050m frame).
5. Scales Entrance Door assembly to 2.050m height.
6. Scales Patio Sliding Door assembly to 2.150m height.
7. Generates realistic Window_Sills (exterior drip noses, interior stool noses).
8. Instantiates exact BlenderKit models:
   - Asset 1 (08d106b3-58d9-42d0-ae99-bce92d0b2667): Rooms 1.03, 1.04 South, 1.04 North, 1.08, 1.09, 1.10
   - Asset 2 (dfc43034-0e61-4ed3-9ebd-4d703fc152a2): Rooms 1.05, 1.06, 1.07
9. Updates lighting heights and isometric camera.
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
    print("[1] Updating Exterior_Walls to 2.500m...")
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

    # South Cutters:
    # W1 1.06: X in [1.300, 2.800], Z in [0.850, 2.250]
    cut_w1_106 = create_box_mesh("Cut_W1_106", 1.300, 2.800, -0.100, 0.465, 0.850, 2.250)
    apply_boolean_difference(ext_south, cut_w1_106)

    # Entrance door: X in [4.640, 5.740], Z in [0.000, 2.050]
    cut_door = create_box_mesh("Cut_Door", 4.640, 5.740, -0.100, 0.465, 0.000, 2.050)
    apply_boolean_difference(ext_south, cut_door)

    # W1 1.05: X in [7.200, 8.700], Z in [0.850, 2.250]
    cut_w1_105 = create_box_mesh("Cut_W1_105", 7.200, 8.700, -0.100, 0.465, 0.850, 2.250)
    apply_boolean_difference(ext_south, cut_w1_105)

    # East Cutters:
    # W2 South 1.04: Y in [5.900, 7.640], Z in [0.850, 2.250]
    cut_w2_s = create_box_mesh("Cut_W2_S", 9.535, 10.100, 5.900, 7.640, 0.850, 2.250)
    apply_boolean_difference(ext_east, cut_w2_s)

    # W2 North 1.04: Y in [8.780, 10.520], Z in [0.850, 2.250]
    cut_w2_n = create_box_mesh("Cut_W2_N", 9.535, 10.100, 8.780, 10.520, 0.850, 2.250)
    apply_boolean_difference(ext_east, cut_w2_n)

    # North Cutters:
    # W5 1.10 (Bathroom): X in [1.120, 2.120], Z in [1.250, 2.250]
    cut_w5 = create_box_mesh("Cut_W5", 1.120, 2.120, 11.535, 12.100, 1.250, 2.250)
    apply_boolean_difference(ext_north, cut_w5)

    # W4 1.03 (Ložnice): X in [3.660, 5.400], Z in [0.850, 2.250]
    cut_w4 = create_box_mesh("Cut_W4", 3.660, 5.400, 11.535, 12.100, 0.850, 2.250)
    apply_boolean_difference(ext_north, cut_w4)

    # Patio Door 1.04: X in [7.125, 8.925], Z in [0.000, 2.150]
    cut_patio = create_box_mesh("Cut_Patio", 7.125, 8.925, 11.535, 12.100, 0.000, 2.150)
    apply_boolean_difference(ext_north, cut_patio)

    # West Cutters:
    # W05 1.07: Y in [4.725, 6.225], Z in [0.850, 2.250]
    cut_w05 = create_box_mesh("Cut_W05", -0.100, 0.465, 4.725, 6.225, 0.850, 2.250)
    apply_boolean_difference(ext_west, cut_w05)

    # W6 WC 1.08: Y in [7.200, 8.000], Z in [1.250, 2.250]
    cut_w6_wc = create_box_mesh("Cut_W6_WC", -0.100, 0.465, 7.200, 8.000, 1.250, 2.250)
    apply_boolean_difference(ext_west, cut_w6_wc)

    # W6 Tech 1.09: Y in [8.375, 9.175], Z in [1.250, 2.250]
    cut_w6_tech = create_box_mesh("Cut_W6_Tech", -0.100, 0.465, 8.375, 9.175, 1.250, 2.250)
    apply_boolean_difference(ext_west, cut_w6_tech)

    # Join 4 facades
    bpy.ops.object.select_all(action='DESELECT')
    for s in [ext_south, ext_north, ext_west, ext_east]:
        s.select_set(True)
    bpy.context.view_layer.objects.active = ext_south
    bpy.ops.object.join()
    ext_walls = bpy.context.active_object
    ext_walls.name = "Exterior_Walls"

    # Add door side tongues and lintel geometry
    bm = bmesh.new()
    bm.from_mesh(ext_walls.data)
    def add_box_bm(bm, x0, x1, y0, y1, z0, z1):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y1, z1)),
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
    print("[2] Updating Interior_Walls to 2.500m...")
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

    # 2. 101 North (between 101 and 102)
    w_101_north = create_box_mesh("Int_101_North", 3.650, 6.100, 2.350, 2.475, 0.0, 2.500, mat_int)
    d_101_102 = create_box_mesh("Cut_101_102", 4.700, 5.500, 2.250, 2.575, 0.000, 2.000)
    apply_boolean_difference(w_101_north, d_101_102)
    int_segments.append(w_101_north)

    # 3. 105 West (between 101/102 and 105)
    w_105_west = create_box_mesh("Int_105_West", 6.100, 6.225, 0.365, 4.850, 0.0, 2.500, mat_int)
    d_102_105 = create_box_mesh("Cut_102_105", 6.000, 6.325, 2.800, 3.600, 0.000, 2.000)
    apply_boolean_difference(w_105_west, d_102_105)
    int_segments.append(w_105_west)

    # 4. 105 North (between 105 and 104)
    w_105_north = create_box_mesh("Int_105_North", 6.225, 9.635, 4.725, 4.850, 0.0, 2.500, mat_int)
    int_segments.append(w_105_north)

    # 5. East wall of 106 & 107
    p_106_107_east = [(4.395, 2.475), (4.520, 2.475), (4.520, 6.181777), (4.395, 6.130)]
    w_106_107_east = create_polygon_prism("Int_106_107_East", p_106_107_east, 0.0, 2.500, mat_int)
    d_102_106 = create_box_mesh("Cut_102_106", 4.295, 4.620, 2.700, 3.500, 0.000, 2.000)
    apply_boolean_difference(w_106_107_east, d_102_106)
    d_102_107 = create_box_mesh("Cut_102_107", 4.295, 4.620, 4.800, 5.600, 0.000, 2.000)
    apply_boolean_difference(w_106_107_east, d_102_107)
    int_segments.append(w_106_107_east)

    # 6. Partition between 106 and 107
    w_106_107_part = create_box_mesh("Int_106_107_Part", 0.365, 4.395, 4.200, 4.325, 0.0, 2.500, mat_int)
    int_segments.append(w_106_107_part)

    # 7. 45-degree chamfer wall for Room 107
    p_chamfer = [(4.395, 6.130), (4.520, 6.181777), (3.630, 7.071777), (3.541612, 6.983388)]
    w_chamfer = create_polygon_prism("Int_Chamfer", p_chamfer, 0.0, 2.500, mat_int)
    int_segments.append(w_chamfer)

    # 8. South wall of 108/109 (between 107 and 108)
    w_108_south = create_box_mesh("Int_108_South", 0.365, 3.541612, 6.983388, 7.108388, 0.0, 2.500, mat_int)
    int_segments.append(w_108_south)

    # 9. Partition between 108 and 109
    w_108_109_part = create_box_mesh("Int_108_109_Part", 0.365, 1.750, 8.1625, 8.2875, 0.0, 2.500, mat_int)
    int_segments.append(w_108_109_part)

    # 10. North wall of 109 (between 109 and 110)
    w_109_north = create_box_mesh("Int_109_North", 0.365, 2.875, 9.8375, 9.9625, 0.0, 2.500, mat_int)
    d_111_110 = create_box_mesh("Cut_111_110", 2.050, 2.750, 9.7375, 10.0625, 0.000, 2.000)
    apply_boolean_difference(w_109_north, d_111_110)
    int_segments.append(w_109_north)

    # 11. East wall of 108/109 (along 111 corridor)
    w_108_109_east = create_box_mesh("Int_108_109_East", 1.750, 1.875, 7.108388, 9.8375, 0.0, 2.500, mat_int)
    d_111_108 = create_box_mesh("Cut_111_108", 1.650, 1.975, 7.250, 7.950, 0.000, 2.000)
    apply_boolean_difference(w_108_109_east, d_111_108)
    d_111_109 = create_box_mesh("Cut_111_109", 1.650, 1.975, 8.550, 9.250, 0.000, 2.000)
    apply_boolean_difference(w_108_109_east, d_111_109)
    int_segments.append(w_108_109_east)

    # 12. East wall of 110 & 111 (between 110/111 and 104)
    w_110_111_east = create_box_mesh("Int_110_111_East", 2.875, 3.000, 7.108388, 11.635, 0.0, 2.500, mat_int)
    d_104_111 = create_box_mesh("Cut_104_111", 2.775, 3.100, 7.200, 8.000, 0.000, 2.000)
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
        if abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.9625) < 0.05:
            if 0.36 < c.x < 1.37 and mat_plank:
                f.material_index = int_walls.data.materials.find(mat_plank.name)
            elif (1.36 < c.x < 2.06 or 2.00 < c.x < 2.88) and mat_koupelna:
                f.material_index = int_walls.data.materials.find(mat_koupelna.name)
        # Door lintel face above bathroom door facing into bathroom
        elif abs(f.normal.y - 1.0) < 0.1 and abs(c.y - 9.9625) < 0.05 and 2.05 < c.x < 2.75 and c.z >= 2.00:
            if mat_koupelna:
                f.material_index = int_walls.data.materials.find(mat_koupelna.name)
    bm.to_mesh(int_walls.data)
    bm.free()
    print("  Interior_Walls completed!")
    return int_walls

def update_roof_soffit_cornice():
    print("[3] Updating Roof_Soffit_Cornice to 2.420-2.500m...")
    soffit = bpy.data.objects.get("Roof_Soffit_Cornice")
    if soffit:
        # Shift all vertices so top is at Z = 2.500m
        bm = bmesh.new()
        bm.from_mesh(soffit.data)
        z_max = max(v.co.z for v in bm.verts)
        shift_z = 2.500 - z_max
        for v in bm.verts:
            v.co.z += shift_z
        bm.to_mesh(soffit.data)
        bm.free()
        print(f"  Roof_Soffit_Cornice shifted by +{shift_z:.3f}m to Z=[2.420, 2.500m]")

def update_doors():
    print("[4] Updating doors and frames...")
    # 1. Entrance door
    dvere = bpy.data.objects.get("dvere")
    dvere_sub = bpy.data.objects.get("dvere.001")
    ram = bpy.data.objects.get("ram")

    # ram unscaled height is ~2.0809m. We want ram to reach exactly 2.050m.
    if ram:
        # Measure unscaled height
        pts = [ram.matrix_world @ v.co for v in ram.data.vertices]
        unscaled_h = (max(p.z for p in pts) - min(p.z for p in pts)) / ram.scale.z
        ram.scale.z = 2.050 / unscaled_h
        print(f"  Scaled entrance door ram to exactly 2.050m height (scale.z = {ram.scale.z:.4f})")
    if dvere:
        dvere.scale.z = 1.0
    if dvere_sub:
        dvere_sub.scale.z = 1.0

    # 2. Patio sliding door in 1.04
    patio_obs = ["Frame_Aluminum", "Bottom Track", "Sash_L", "Sash_R", "Screen", "Latch Handle_1", "Latch Handle_2"]
    scale_factor_patio = 2.150 / 1.797
    for name in patio_obs:
        ob = bpy.data.objects.get(name)
        if ob:
            ob.scale.z = scale_factor_patio
            print(f"  Scaled patio door component {name} along Z by {scale_factor_patio:.4f}")

    # 3. Interior Door Frames
    old_frames = bpy.data.objects.get("Interior_Door_Frames")
    if old_frames:
        bpy.data.objects.remove(old_frames, do_unlink=True)

    mat_frame = bpy.data.materials.get("Mat_Roof_Soffit") or bpy.data.materials.get("Mat_Exterior_Wall")

    # Reconstruct 8 door frames for clear opening height 2.000m (frame top 2.050m)
    door_specs = [
        # (name, is_x_aligned, x_center, y_center, width, wall_thick)
        ("DF_101_102", True,  5.100, 2.4125, 0.800, 0.125),
        ("DF_102_105", False, 6.1625, 3.200, 0.800, 0.125),
        ("DF_102_106", False, 4.4575, 3.100, 0.800, 0.125),
        ("DF_102_107", False, 4.4575, 5.200, 0.800, 0.125),
        ("DF_104_111", False, 2.9375, 7.600, 0.800, 0.125),
        ("DF_111_108", False, 1.8125, 7.600, 0.700, 0.125),
        ("DF_111_109", False, 1.8125, 8.900, 0.700, 0.125),
        ("DF_111_110", True,  2.400, 9.900, 0.700, 0.125),
    ]

    frame_objs = []
    arch_width = 0.050  # 50mm frame facing
    arch_depth = 0.015  # 15mm projection
    jamb_thick = wall_thick = 0.125
    total_depth = jamb_thick + 2 * arch_depth

    for name, is_x, xc, yc, w, wt in door_specs:
        half_w = w / 2.0
        # side 1, side 2, top jamb
        if is_x:
            # Door extends along X, wall normal along Y
            s1 = create_box_mesh(f"{name}_S1", xc - half_w - arch_width, xc - half_w, yc - total_depth/2, yc + total_depth/2, 0.0, 2.050, mat_frame)
            s2 = create_box_mesh(f"{name}_S2", xc + half_w, xc + half_w + arch_width, yc - total_depth/2, yc + total_depth/2, 0.0, 2.050, mat_frame)
            top = create_box_mesh(f"{name}_Top", xc - half_w - arch_width, xc + half_w + arch_width, yc - total_depth/2, yc + total_depth/2, 2.000, 2.050, mat_frame)
        else:
            # Door extends along Y, wall normal along X
            s1 = create_box_mesh(f"{name}_S1", xc - total_depth/2, xc + total_depth/2, yc - half_w - arch_width, yc - half_w, 0.0, 2.050, mat_frame)
            s2 = create_box_mesh(f"{name}_S2", xc - total_depth/2, xc + total_depth/2, yc + half_w, yc + half_w + arch_width, 0.0, 2.050, mat_frame)
            top = create_box_mesh(f"{name}_Top", xc - total_depth/2, xc + total_depth/2, yc - half_w - arch_width, yc + half_w + arch_width, 2.000, 2.050, mat_frame)
        frame_objs.extend([s1, s2, top])

    bpy.ops.object.select_all(action='DESELECT')
    for fo in frame_objs:
        fo.select_set(True)
    bpy.context.view_layer.objects.active = frame_objs[0]
    bpy.ops.object.join()
    df_all = bpy.context.active_object
    df_all.name = "Interior_Door_Frames"
    print("  Interior_Door_Frames completed!")

def update_window_sills():
    print("[5] Generating Window_Sills with drip and stool noses...")
    # Clean up old window frames/glass/sills
    for old_name in ["Window_Frames_and_Sills", "Window_Glass", "Window_Sills"]:
        old_ob = bpy.data.objects.get(old_name)
        if old_ob:
            bpy.data.objects.remove(old_ob, do_unlink=True)

    mat_anthracite = bpy.data.materials.get("Mat_Roof_Soffit")

    # 9 window openings specification:
    # (name, wall, x_min, x_max, y_min, y_max, z_sill)
    windows = [
        ("W1_106", "south", 1.300, 2.800, 0.000, 0.365, 0.850),
        ("W1_105", "south", 7.200, 8.700, 0.000, 0.365, 0.850),
        ("W2_South_104", "east", 9.635, 10.000, 5.900, 7.640, 0.850),
        ("W2_North_104", "east", 9.635, 10.000, 8.780, 10.520, 0.850),
        ("W4_103", "north", 3.660, 5.400, 11.635, 12.000, 0.850),
        ("W5_110", "north", 1.120, 2.120, 11.635, 12.000, 1.250),
        ("W05_107", "west", 0.000, 0.365, 4.725, 6.225, 0.850),
        ("W6_WC_108", "west", 0.000, 0.365, 7.200, 8.000, 1.250),
        ("W6_Tech_109", "west", 0.000, 0.365, 8.375, 9.175, 1.250),
    ]

    bm = bmesh.new()

    def add_box_bm(bm, x0, x1, y0, y1, z0, z1):
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y1, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new([v[0], v[1], v[2], v[3]])
        bm.faces.new([v[4], v[7], v[6], v[5]])
        bm.faces.new([v[0], v[4], v[5], v[1]])
        bm.faces.new([v[2], v[6], v[7], v[3]])
        bm.faces.new([v[0], v[3], v[7], v[4]])
        bm.faces.new([v[1], v[5], v[6], v[2]])

    for name, wall, x0, x1, y0, y1, zs in windows:
        # Window frame is centered at reveal depth (100mm from exterior)
        # Sill plate thickness = 20mm
        # Extends 20mm past reveal on both sides (ears)
        ear = 0.020
        overhang = 0.035
        drop = 0.020

        if wall == "south":
            # Exterior is -Y (Y = 0.000), frame at Y in [0.100, 0.170]
            # Exterior sill: from Y=0.120 to Y=-overhang (-0.035)
            add_box_bm(bm, x0 - ear, x1 + ear, -overhang, 0.120, zs - 0.020, zs)
            # Drip nose: at Y=-overhang, drops 20mm down
            add_box_bm(bm, x0 - ear, x1 + ear, -overhang, -overhang + 0.020, zs - 0.020 - drop, zs - 0.020)
            # Interior sill: from Y=0.150 to Y=0.365 + overhang
            add_box_bm(bm, x0 - ear, x1 + ear, 0.150, 0.365 + overhang, zs - 0.025, zs)
            # Interior stool nose:
            add_box_bm(bm, x0 - ear, x1 + ear, 0.365 + overhang - 0.020, 0.365 + overhang, zs - 0.025 - drop, zs - 0.025)

        elif wall == "north":
            # Exterior is +Y (Y = 12.000), frame at Y in [11.830, 11.900]
            # Exterior sill: from Y=11.880 to Y=12.000 + overhang
            add_box_bm(bm, x0 - ear, x1 + ear, 11.880, 12.000 + overhang, zs - 0.020, zs)
            # Drip nose
            add_box_bm(bm, x0 - ear, x1 + ear, 12.000 + overhang - 0.020, 12.000 + overhang, zs - 0.020 - drop, zs - 0.020)
            # Interior sill: from Y=11.635 - overhang to Y=11.850
            add_box_bm(bm, x0 - ear, x1 + ear, 11.635 - overhang, 11.850, zs - 0.025, zs)
            # Interior stool nose
            add_box_bm(bm, x0 - ear, x1 + ear, 11.635 - overhang, 11.635 - overhang + 0.020, zs - 0.025 - drop, zs - 0.025)

        elif wall == "east":
            # Exterior is +X (X = 10.000), frame at X in [9.830, 9.900]
            # Exterior sill: from X=9.880 to X=10.000 + overhang
            add_box_bm(bm, 9.880, 10.000 + overhang, y0 - ear, y1 + ear, zs - 0.020, zs)
            # Drip nose
            add_box_bm(bm, 10.000 + overhang - 0.020, 10.000 + overhang, y0 - ear, y1 + ear, zs - 0.020 - drop, zs - 0.020)
            # Interior sill: from X=9.635 - overhang to X=9.850
            add_box_bm(bm, 9.635 - overhang, 9.850, y0 - ear, y1 + ear, zs - 0.025, zs)
            # Interior stool nose
            add_box_bm(bm, 9.635 - overhang, 9.635 - overhang + 0.020, y0 - ear, y1 + ear, zs - 0.025 - drop, zs - 0.025)

        elif wall == "west":
            # Exterior is -X (X = 0.000), frame at X in [0.100, 0.170]
            # Exterior sill: from X=-overhang to X=0.120
            add_box_bm(bm, -overhang, 0.120, y0 - ear, y1 + ear, zs - 0.020, zs)
            # Drip nose
            add_box_bm(bm, -overhang, -overhang + 0.020, y0 - ear, y1 + ear, zs - 0.020 - drop, zs - 0.020)
            # Interior sill: from X=0.150 to X=0.365 + overhang
            add_box_bm(bm, 0.150, 0.365 + overhang, y0 - ear, y1 + ear, zs - 0.025, zs)
            # Interior stool nose
            add_box_bm(bm, 0.365 + overhang - 0.020, 0.365 + overhang, y0 - ear, y1 + ear, zs - 0.025 - drop, zs - 0.025)

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new("Window_Sills")
    bm.to_mesh(mesh)
    bm.free()

    sills_obj = bpy.data.objects.new("Window_Sills", mesh)
    bpy.context.scene.collection.objects.link(sills_obj)
    if mat_anthracite:
        sills_obj.data.materials.append(mat_anthracite)
    print("  Window_Sills generated!")
    return sills_obj

def instantiate_window_assets():
    print("[6] Instantiating BlenderKit window models into openings...")
    asset1_path = os.path.abspath("assets/models/pvc-window-fixed_35b7e661-a16e-44f5-b0b5-dc84efed6ca3/blend_bcdd59d3-5e63-4484-b59d-e6d2b0acf0b6.blend")
    asset2_path = os.path.abspath("assets/models/pvc-window-fixed_197e937f-d348-4867-8b99-af5cfd52cfb7/pvc-window-fixed_df64259d-508f-4bb0-b316-5b1c93ce756e.blend")

    # Create collection for windows
    col_name = "Window_Models"
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)

    # Clean existing window instances if any
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

        # Group 1: Asset 1 (Single sash)
        ("Window_1.08_WC",       1, "west",  0.135, 7.600, 1.250, 0.800, 1.000),
        ("Window_1.09_Tech",     1, "west",  0.135, 8.775, 1.250, 0.800, 1.000),
        ("Window_1.10_Bathroom", 1, "north", 1.620, 11.865, 1.250, 1.000, 1.000),
        ("Window_1.03_Bedroom",  1, "north", 4.530, 11.865, 0.850, 1.740, 1.400),
        ("Window_1.04_EastSouth",1, "east",  9.865, 6.770, 0.850, 1.740, 1.400),
        ("Window_1.04_EastNorth",1, "east",  9.865, 9.650, 0.850, 1.740, 1.400),
    ]

    rot_map = {
        "south": math.pi,       # Local +Y faces -Y (South)
        "north": 0.0,           # Local +Y faces +Y (North)
        "east":  -math.pi / 2,  # Local +Y faces +X (East)
        "west":  math.pi / 2,   # Local +Y faces -X (West)
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

        print(f"  Placed {name} (Asset {aid}) at ({cx:.3f}, {cy:.3f}, {zs:.3f}), size: {w:.2f}x{h:.2f}m")

    # Remove template objects
    for o in children1 + [root1] + children2 + [root2]:
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    print("  Window models successfully placed!")

def update_lights_and_camera():
    print("[7] Updating lighting and camera parameters...")
    # Update Soffit spots to Z = 2.450m
    soffit_lights = [
        "Light_Ext_Front_Soffit_1_CornerL",
        "Light_Ext_Front_Soffit_2_Window106",
        "Light_Ext_Front_Soffit_3_Entrance",
        "Light_Ext_Front_Soffit_5_CornerR",
        "Light_Ext_Side_East_A2",
    ]
    for ln in soffit_lights:
        l_obj = bpy.data.objects.get(ln)
        if l_obj:
            l_obj.location.z = 2.450

    patio_lights = ["Light_Ext_Rear_Patio_Left", "Light_Ext_Rear_Patio_Right"]
    for ln in patio_lights:
        l_obj = bpy.data.objects.get(ln)
        if l_obj:
            l_obj.location.z = 2.400

    # Interior ceiling lights to Z = 2.400m
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith("Light_1."):
            ob.location.z = 2.400

    # Camera
    cam = bpy.data.objects.get("Isometric_Camera")
    if cam:
        cam.data.ortho_scale = 18.0
        target = Vector((5.0, 6.0, 1.25))
        distance = 35.0
        iso_dir = Vector((-1.0, -1.0, math.sqrt(2))).normalized()
        cam.location = target + iso_dir * distance
        direction = target - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()
        print("  Camera target updated to Z = 1.25m, ortho_scale = 18.0")

def render_views():
    print("[8] Rendering verification views...")
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # 1. Isometric Overview
    bpy.context.scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered dum_pudorys_overview.png")

    # Helper camera positioner
    cam = bpy.data.objects.get("Isometric_Camera")
    if not cam:
        return

    orig_loc = cam.location.copy()
    orig_rot = cam.rotation_euler.copy()
    orig_scale = cam.data.ortho_scale

    views = [
        ("windows_south_real_heights.png", Vector((5.0, 0.18, 1.55)), Vector((5.0, -8.0, 3.5)), 9.5),
        ("windows_east_real_heights.png",  Vector((9.82, 8.0, 1.55)), Vector((18.0, 8.0, 3.5)), 9.5),
        ("windows_west_real_heights.png",  Vector((0.18, 7.0, 1.55)), Vector((-8.0, 7.0, 3.5)), 9.5),
        ("windows_north_real_heights.png", Vector((5.0, 11.82, 1.55)),Vector((5.0, 20.0, 3.5)), 9.5),
        ("doors_interior_real_heights.png", Vector((3.5, 4.5, 1.10)), Vector((6.5, 8.5, 2.5)), 8.0),
    ]

    for fname, target, cam_pos, oscale in views:
        cam.location = cam_pos
        cam.data.ortho_scale = oscale
        dir_vec = target - cam.location
        cam.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.render.filepath = os.path.abspath(fname)
        bpy.ops.render.render(write_still=True)
        print(f"  Rendered {fname}")

    # Restore camera
    cam.location = orig_loc
    cam.rotation_euler = orig_rot
    cam.data.ortho_scale = orig_scale

def main():
    print("=" * 70)
    print("UPDATING DUM_PUDORYS.BLEND TO REAL HEIGHTS (2.50M WALLS, REAL WINDOWS & DOORS)")
    print("=" * 70)

    update_exterior_walls()
    update_interior_walls()
    update_roof_soffit_cornice()
    update_doors()
    update_window_sills()
    instantiate_window_assets()
    update_lights_and_camera()

    out_path = os.path.abspath("dum_pudorys.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print(f"\n[SUCCESS] dum_pudorys.blend updated and saved to: {out_path}")

    render_views()
    print("=" * 70)
    print("REAL HEIGHTS UPDATE COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    main()
