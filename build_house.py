"""
build_house.py
Generates a complete 3D architectural cutaway model in Blender 5.2
based on 'Půdorys-aktualní 27.10.2020.png'.

Specifications:
- Outer house dimensions: 10.0 m x 12.0 m
- Exterior wall thickness: 0.365 m, height: 1.8 m
- Interior partition wall thickness: 0.125 m, height: 1.8 m
- 11 rooms according to the room schedule (1.01 to 1.11)
- Window & door cutouts per blueprint dimensions and parapet heights
- Individual room floor meshes with designated materials (Tiles / Laminate)
- Foundation slab base
- Dedicated point lights in each room named after the room
- Orthographic isometric camera
"""

import sys
import os
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

def clear_scene():
    """Wipes all objects, meshes, materials, lights, and cameras from the scene."""
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for collection in [bpy.data.objects, bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights]:
        for item in list(collection):
            collection.remove(item)

def create_material(name, diffuse_color, roughness=0.5, specular=0.5):
    """Creates a clean Principled BSDF material."""
    mat = bpy.data.materials.new(name=name)
    if mat.node_tree is None and hasattr(mat, "use_nodes"):
        mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = diffuse_color
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = specular
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = specular
    return mat

def create_box_mesh(name, x_min, x_max, y_min, y_max, z_min, z_max, material=None):
    """Creates an axis-aligned box object with given bounds."""
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

    # 6 quad faces
    bm.faces.new([v[0], v[1], v[2], v[3]]) # bottom
    bm.faces.new([v[4], v[7], v[6], v[5]]) # top
    bm.faces.new([v[0], v[4], v[5], v[1]]) # front (south)
    bm.faces.new([v[1], v[5], v[6], v[2]]) # right (east)
    bm.faces.new([v[2], v[6], v[7], v[3]]) # back (north)
    bm.faces.new([v[3], v[7], v[4], v[0]]) # left (west)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    if material:
        obj.data.materials.append(material)

    return obj

def create_polygon_prism(name, polygon_2d, z_min, z_max, material=None):
    """Creates an extruded vertical prism from a 2D polygon (list of (x, y) tuples in CCW order)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    bottom_verts = [bm.verts.new((x, y, z_min)) for x, y in polygon_2d]
    top_verts = [bm.verts.new((x, y, z_max)) for x, y in polygon_2d]

    # Bottom face
    bm.faces.new(list(reversed(bottom_verts)))
    # Top face
    bm.faces.new(top_verts)

    # Side walls
    n = len(polygon_2d)
    for i in range(n):
        i_next = (i + 1) % n
        bm.faces.new([bottom_verts[i], bottom_verts[i_next], top_verts[i_next], top_verts[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    if material:
        obj.data.materials.append(material)

    return obj

def apply_boolean_difference(target_obj, cutter_obj):
    """Applies a boolean difference modifier cutting cutter_obj out of target_obj."""
    mod = target_obj.modifiers.new(name="BoolDiff", type='BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = cutter_obj
    mod.solver = 'EXACT'

    bpy.context.view_layer.objects.active = target_obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter_obj, do_unlink=True)

def build_house():
    clear_scene()

    # Materials definition
    mat_ext_wall = create_material("Mat_Exterior_Wall", (0.92, 0.91, 0.88, 1.0), roughness=0.8)
    mat_int_wall = create_material("Mat_Interior_Wall", (0.96, 0.96, 0.95, 1.0), roughness=0.7)
    mat_wood = create_material("Mat_Wood_Laminate", (0.75, 0.54, 0.35, 1.0), roughness=0.35)
    mat_tiles = create_material("Mat_Ceramic_Tiles", (0.82, 0.84, 0.85, 1.0), roughness=0.25)
    mat_foundation = create_material("Mat_Foundation", (0.35, 0.36, 0.38, 1.0), roughness=0.9)
    mat_fireplace = create_material("Mat_Fireplace", (0.25, 0.25, 0.26, 1.0), roughness=0.6)

    # ----------------------------------------------------
    # 1. Foundation Slab Base
    # ----------------------------------------------------
    create_box_mesh("Foundation_Slab", -0.3, 10.3, -0.3, 12.3, -0.2, 0.0, mat_foundation)

    # ----------------------------------------------------
    # 2. Exterior Walls (10.0 x 12.0 m, thickness 0.365 m, height 1.8 m)
    #    We create 4 non-overlapping segments, cut their respective
    #    windows & doors, and then join them into Exterior_Walls.
    # ----------------------------------------------------
    ext_south = create_box_mesh("Ext_South", 0.0, 10.0, 0.0, 0.365, 0.0, 1.8, mat_ext_wall)
    ext_north = create_box_mesh("Ext_North", 0.0, 10.0, 11.635, 12.0, 0.0, 1.8, mat_ext_wall)
    ext_west  = create_box_mesh("Ext_West",  0.0, 0.365, 0.365, 11.635, 0.0, 1.8, mat_ext_wall)
    ext_east  = create_box_mesh("Ext_East",  9.635, 10.0, 0.365, 11.635, 0.0, 1.8, mat_ext_wall)

    # Cutters on ext_south:
    # - Window 1 (Room 1.06): X: [1.300, 2.800], sill=1.050, height=1.300
    w_ext_1_106 = create_box_mesh("Cut_Ext_W1_106", 1.300, 2.800, -0.100, 0.465, 1.050, 2.000)
    apply_boolean_difference(ext_south, w_ext_1_106)

    # - Door P1 (Room 1.01): X: [4.640, 5.740], sill=0.0
    d_ext_p1 = create_box_mesh("Cut_Ext_Door_P1", 4.640, 5.740, -0.100, 0.465, 0.000, 2.000)
    apply_boolean_difference(ext_south, d_ext_p1)

    # - Window 1 (Room 1.05): X: [7.200, 8.700], sill=1.050, height=1.300
    w_ext_1_105 = create_box_mesh("Cut_Ext_W1_105", 7.200, 8.700, -0.100, 0.465, 1.050, 2.000)
    apply_boolean_difference(ext_south, w_ext_1_105)

    # Cutters on ext_east:
    # - Window 2 South (Room 1.04): Y: [5.900, 7.640], sill=1.200, height=1.140
    w_ext_2_south = create_box_mesh("Cut_Ext_W2_South", 9.535, 10.100, 5.900, 7.640, 1.200, 2.000)
    apply_boolean_difference(ext_east, w_ext_2_south)

    # - Window 2 North Fix (Room 1.04): Y: [8.780, 10.520], sill=1.050, height=1.140
    w_ext_2_north = create_box_mesh("Cut_Ext_W2_North", 9.535, 10.100, 8.780, 10.520, 1.050, 2.000)
    apply_boolean_difference(ext_east, w_ext_2_north)

    # Cutters on ext_north:
    # - Window 5 (Room 1.10): X: [1.120, 2.120], sill=1.600, height=0.600
    w_ext_5 = create_box_mesh("Cut_Ext_W5", 1.120, 2.120, 11.535, 12.100, 1.600, 2.000)
    apply_boolean_difference(ext_north, w_ext_5)

    # - Window 4 (Room 1.03): X: [3.660, 5.400], sill=1.050, height=1.140
    w_ext_4 = create_box_mesh("Cut_Ext_W4", 3.660, 5.400, 11.535, 12.100, 1.050, 2.000)
    apply_boolean_difference(ext_north, w_ext_4)

    # - Patio Double Door 3 (Room 1.04): X: [7.125, 8.925], sill=0.0
    d_ext_patio = create_box_mesh("Cut_Ext_Patio_Door", 7.125, 8.925, 11.535, 12.100, 0.000, 2.000)
    apply_boolean_difference(ext_north, d_ext_patio)

    # Cutters on ext_west:
    # - Window 05 (Room 1.07): Y: [4.725, 6.225], sill=0.900, height=1.300
    w_ext_05 = create_box_mesh("Cut_Ext_W05", -0.100, 0.465, 4.725, 6.225, 0.900, 2.000)
    apply_boolean_difference(ext_west, w_ext_05)

    # - Window 6 South (Room 1.08 WC): Y: [7.200, 8.000], sill=1.600, height=0.600
    w_ext_6_wc = create_box_mesh("Cut_Ext_W6_WC", -0.100, 0.465, 7.200, 8.000, 1.600, 2.000)
    apply_boolean_difference(ext_west, w_ext_6_wc)

    # - Window 6 North (Room 1.09 Tech): Y: [8.375, 9.175], sill=1.750, height=0.600
    w_ext_6_tech = create_box_mesh("Cut_Ext_W6_Tech", -0.100, 0.465, 8.375, 9.175, 1.750, 2.000)
    apply_boolean_difference(ext_west, w_ext_6_tech)

    # Join 4 exterior walls into a single Exterior_Walls object
    ext_walls_list = [ext_south, ext_north, ext_west, ext_east]
    bpy.ops.object.select_all(action='DESELECT')
    for w in ext_walls_list:
        w.select_set(True)
    bpy.context.view_layer.objects.active = ext_south
    bpy.ops.object.join()
    ext_walls = bpy.context.active_object
    ext_walls.name = "Exterior_Walls"

    # Weld vertices at corner seams
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(ext_walls.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    bmesh.update_edit_mesh(ext_walls.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # ----------------------------------------------------
    # 3. Interior Partition Walls (thickness 0.125 m, height 1.8 m)
    #    Each partition wall is created and its individual doors are cut.
    # ----------------------------------------------------
    int_segments = []

    # 1. Wall between 1.06 and 1.01 (South vertical)
    w_106_101 = create_box_mesh("Int_106_101", 3.650, 3.775, 0.365, 2.350, 0.0, 1.8, mat_int_wall)
    int_segments.append(w_106_101)

    # 2. Wall North of 1.01 (horizontal, between 1.01 and 1.02)
    w_101_north = create_box_mesh("Int_101_North", 3.650, 6.100, 2.350, 2.475, 0.0, 1.8, mat_int_wall)
    d_int_101_102 = create_box_mesh("Cut_Int_101_102", 4.700, 5.500, 2.250, 2.575, 0.000, 2.000)
    apply_boolean_difference(w_101_north, d_int_101_102)
    int_segments.append(w_101_north)

    # 3. West wall of 1.05 (vertical, between 1.01/1.02 and 1.05)
    w_105_west = create_box_mesh("Int_105_West", 6.100, 6.225, 0.365, 4.850, 0.0, 1.8, mat_int_wall)
    d_int_102_105 = create_box_mesh("Cut_Int_102_105", 6.000, 6.325, 2.800, 3.600, 0.000, 2.000)
    apply_boolean_difference(w_105_west, d_int_102_105)
    int_segments.append(w_105_west)

    # 4. North wall of 1.05 (horizontal, between 1.05 and 1.04)
    w_105_north = create_box_mesh("Int_105_North", 6.225, 9.635, 4.725, 4.850, 0.0, 1.8, mat_int_wall)
    int_segments.append(w_105_north)

    # 5. East wall of 1.06 and 1.07 (vertical, along 1.02 corridor, mitered at top to 45 deg)
    p_106_107_east = [(4.395, 2.475), (4.520, 2.475), (4.520, 6.181777), (4.395, 6.130)]
    w_106_107_east = create_polygon_prism("Int_106_107_East", p_106_107_east, 0.0, 1.8, mat_int_wall)
    d_int_102_106 = create_box_mesh("Cut_Int_102_106", 4.295, 4.620, 2.700, 3.500, 0.000, 2.000)
    apply_boolean_difference(w_106_107_east, d_int_102_106)
    d_int_102_107 = create_box_mesh("Cut_Int_102_107", 4.295, 4.620, 4.800, 5.600, 0.000, 2.000)
    apply_boolean_difference(w_106_107_east, d_int_102_107)
    int_segments.append(w_106_107_east)

    # 6. Between 1.06 and 1.07 (horizontal partition)
    w_106_107_part = create_box_mesh("Int_106_107_Partition", 0.365, 4.395, 3.850, 3.975, 0.0, 1.8, mat_int_wall)
    int_segments.append(w_106_107_part)

    # 7. Angled chamfer wall of 1.07 at 45 degrees (seamlessly mitered to east & north walls)
    # Inner face: (4.395, 6.130) -> (3.550, 6.975) (exact blueprint dimension: 1.195 m)
    # Outer face: (4.520, 6.181777) -> (3.601777, 7.100) (thickness: 0.125 m)
    p_107_angled = [(4.395, 6.130), (4.520, 6.181777), (3.601777, 7.100), (3.550, 6.975)]
    angled_wall = create_polygon_prism("Int_107_Angled", p_107_angled, 0.0, 1.8, mat_int_wall)
    int_segments.append(angled_wall)

    # 8. North wall of 1.07 / South wall of 1.08 & 1.11 (mitered at east end to 45 deg)
    p_107_north = [(0.365, 6.975), (3.550, 6.975), (3.601777, 7.100), (0.365, 7.100)]
    w_107_north = create_polygon_prism("Int_107_North", p_107_north, 0.0, 1.8, mat_int_wall)
    int_segments.append(w_107_north)

    # 9. Between 1.08 (WC) and 1.09 (Tech)
    w_108_109 = create_box_mesh("Int_108_109", 0.365, 1.750, 8.100, 8.225, 0.0, 1.8, mat_int_wall)
    int_segments.append(w_108_109)

    # 10. Between 1.09 (Tech) and 1.10 (Koupelna), continuing across 1.11
    w_109_110 = create_box_mesh("Int_109_110", 0.365, 2.875, 9.775, 9.900, 0.0, 1.8, mat_int_wall)
    d_int_111_110 = create_box_mesh("Cut_Int_111_110", 2.050, 2.750, 9.675, 10.000, 0.000, 2.000)
    apply_boolean_difference(w_109_110, d_int_111_110)
    int_segments.append(w_109_110)

    # 11. East wall of 1.08 and 1.09 (separating them from Chodba 1.11)
    w_108_109_east = create_box_mesh("Int_108_109_East", 1.750, 1.875, 7.100, 9.775, 0.0, 1.8, mat_int_wall)
    d_int_111_108 = create_box_mesh("Cut_Int_111_108", 1.650, 1.975, 7.250, 7.950, 0.000, 2.000)
    apply_boolean_difference(w_108_109_east, d_int_111_108)
    d_int_111_109 = create_box_mesh("Cut_Int_111_109", 1.650, 1.975, 8.550, 9.250, 0.000, 2.000)
    apply_boolean_difference(w_108_109_east, d_int_111_109)
    int_segments.append(w_108_109_east)

    # 12. East wall of 1.10 and 1.11 (separating them from Kitchen 1.03 & Living 1.04)
    w_110_111_east = create_box_mesh("Int_110_111_East", 2.875, 3.000, 7.100, 11.635, 0.0, 1.8, mat_int_wall)
    d_int_104_111 = create_box_mesh("Cut_Int_104_111", 2.775, 3.100, 7.200, 8.000, 0.000, 2.000)
    apply_boolean_difference(w_110_111_east, d_int_104_111)
    int_segments.append(w_110_111_east)

    # Join interior partitions into Interior_Walls
    bpy.ops.object.select_all(action='DESELECT')
    for s in int_segments:
        s.select_set(True)
    bpy.context.view_layer.objects.active = int_segments[0]
    bpy.ops.object.join()
    int_walls = bpy.context.active_object
    int_walls.name = "Interior_Walls"

    # Weld vertices at seams and delete internal shared faces
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(int_walls.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
    internal_faces = [f for f in bm.faces if len(f.edges) == 4 and all(len(e.link_faces) > 2 for e in f.edges)]
    if internal_faces:
        bmesh.ops.delete(bm, geom=internal_faces, context='FACES')
    bmesh.update_edit_mesh(int_walls.data)
    bpy.ops.object.mode_set(mode='OBJECT')

    # ----------------------------------------------------
    # 5. Floors per Room (11 rooms according to legend)
    # ----------------------------------------------------
    z_fl_min = 0.000
    z_fl_max = 0.015  # 15mm finished floor layer

    # 1.01 ZÁDVEŘÍ (Tiles)
    create_box_mesh("Floor_1.01_Zadveri", 3.775, 6.100, 0.365, 2.350, z_fl_min, z_fl_max, mat_tiles)

    # 1.02 CHODBA (Laminate)
    fl_102_p = [
        (4.520, 2.475),
        (6.100, 2.475),
        (6.100, 4.850),
        (4.520, 6.181777)
    ]
    create_polygon_prism("Floor_1.02_Chodba", fl_102_p, z_fl_min, z_fl_max, mat_wood)

    # 1.03 KUCHYNĚ (Laminate)
    create_box_mesh("Floor_1.03_Kuchyne", 3.000, 5.525, 7.100, 11.635, z_fl_min, z_fl_max, mat_wood)

    # 1.04 OBÝVACÍ POKOJ (Laminate)
    fl_104_p1 = (5.525, 7.100)
    fl_104_p2 = (9.635, 7.100)
    fl_104_p3 = (9.635, 11.635)
    fl_104_p4 = (5.525, 11.635)
    create_polygon_prism("Floor_1.04_Obyvaci_pokoj_North", [fl_104_p1, fl_104_p2, fl_104_p3, fl_104_p4], z_fl_min, z_fl_max, mat_wood)

    fl_104_south_p = [
        (4.520, 6.181777),
        (6.100, 4.850),
        (9.635, 4.850),
        (9.635, 7.100),
        (3.000, 7.100),
        (3.601777, 7.100)
    ]
    create_polygon_prism("Floor_1.04_Obyvaci_pokoj_South", fl_104_south_p, z_fl_min, z_fl_max, mat_wood)

    # 1.05 POKOJ (Laminate)
    create_box_mesh("Floor_1.05_Pokoj", 6.225, 9.635, 0.365, 4.725, z_fl_min, z_fl_max, mat_wood)

    # 1.06 POKOJ (Laminate - L shape)
    fl_106_p = [
        (0.365, 0.365),
        (3.650, 0.365),
        (3.650, 2.475),
        (4.395, 2.475),
        (4.395, 3.850),
        (0.365, 3.850)
    ]
    create_polygon_prism("Floor_1.06_Pokoj", fl_106_p, z_fl_min, z_fl_max, mat_wood)

    # 1.07 POKOJ (Laminate - chamfered NE corner)
    fl_107_p = [
        (0.365, 3.975),
        (4.395, 3.975),
        (4.395, 6.130),
        (3.550, 6.975),
        (0.365, 6.975)
    ]
    create_polygon_prism("Floor_1.07_Pokoj", fl_107_p, z_fl_min, z_fl_max, mat_wood)

    # 1.08 WC (Tiles)
    create_box_mesh("Floor_1.08_WC", 0.365, 1.750, 7.100, 8.100, z_fl_min, z_fl_max, mat_tiles)

    # 1.09 TECHNICKÁ MÍSTNOST (Tiles)
    create_box_mesh("Floor_1.09_Technicka_mistnost", 0.365, 1.750, 8.225, 9.775, z_fl_min, z_fl_max, mat_tiles)

    # 1.10 KOUPELNA (Tiles)
    create_box_mesh("Floor_1.10_Koupelna", 0.365, 2.875, 9.900, 11.635, z_fl_min, z_fl_max, mat_tiles)

    # 1.11 CHODBA (Tiles)
    create_box_mesh("Floor_1.11_Chodba", 1.875, 2.875, 7.100, 9.775, z_fl_min, z_fl_max, mat_tiles)

    # ----------------------------------------------------
    # 6. Point Lights per 'svetla 2022.jpg'
    #    All interior lights are point lights.
    #    Exterior front (5 lights) in soffits are point lights.
    #    Exterior rear patio lights are on the wall at height 1.8 m.
    #    Exterior side lights on west and east walls.
    # ----------------------------------------------------
    z_int = 1.65        # Interior ceiling light height
    z_ext_soffit = 1.80 # Exterior soffit light height
    z_ext_wall = 1.80   # Exterior wall light height (1.8m per user specification)

    lights_spec = [
        # --- 1.01 ZÁDVEŘÍ ---
        # #26: V (17.5x17.5cm), 90cm from south wall, 90cm from east wall
        ("Light_1.01_Zadveri_V", (5.20, 1.265, z_int), 35.0, (1.0, 0.95, 0.88), 0.175),

        # --- 1.02 CHODBA ---
        # #17: V (17.5x17.5cm), centered in corridor
        ("Light_1.02_Chodba_V", (5.31, 3.70, z_int), 35.0, (1.0, 0.95, 0.88), 0.175),

        # --- 1.03 KUCHYNĚ ---
        # #6: V, 130cm from north wall
        ("Light_1.03_Kuchyne_V1", (4.30, 10.335, z_int), 40.0, (1.0, 0.96, 0.90), 0.175),
        # #10: V, 130cm south of #6
        ("Light_1.03_Kuchyne_V2", (4.30, 9.035, z_int), 40.0, (1.0, 0.96, 0.90), 0.175),

        # --- 1.04 OBÝVACÍ POKOJ ---
        # #4: V, dining zone, 100cm from north wall
        ("Light_1.04_Obyvaci_pokoj_V1_Dining", (6.50, 10.635, z_int), 45.0, (1.0, 0.95, 0.88), 0.175),
        # #5: V, in front of patio doors, 120cm from north wall
        ("Light_1.04_Obyvaci_pokoj_V2_Patio1", (8.025, 10.435, z_int), 45.0, (1.0, 0.95, 0.88), 0.175),
        # #8: V, 120cm south of #5
        ("Light_1.04_Obyvaci_pokoj_V3_Patio2", (8.025, 9.235, z_int), 45.0, (1.0, 0.95, 0.88), 0.175),
        # #13: V, central living area
        ("Light_1.04_Obyvaci_pokoj_V4_Center", (8.025, 7.20, z_int), 55.0, (1.0, 0.95, 0.88), 0.175),
        # #14: V, angled area / passage
        ("Light_1.04_Obyvaci_pokoj_V5_Angle", (5.00, 6.50, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),

        # --- 1.05 POKOJ ---
        # #25: V, 120cm from south wall, 120cm from east wall
        ("Light_1.05_Pokoj_V1_South", (8.435, 1.565, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),
        # #22: V, 120cm north of #25
        ("Light_1.05_Pokoj_V2_Center", (8.435, 2.765, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),
        # #21: přisazené/stavitelné spot near door, 85cm from west wall
        ("Light_1.05_Pokoj_Spot_West", (7.075, 4.10, z_int), 30.0, (1.0, 0.95, 0.88), 0.12),
        # #20: přisazené/stavitelné spot near east wall, 85cm from east wall
        ("Light_1.05_Pokoj_Spot_East", (8.785, 4.10, z_int), 30.0, (1.0, 0.95, 0.88), 0.12),

        # --- 1.06 POKOJ ---
        # #24: V, aligned with window 1, 120cm from south wall
        ("Light_1.06_Pokoj_V1_South", (2.05, 1.565, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),
        # #23: V, 100cm from north partition wall
        ("Light_1.06_Pokoj_V2_North", (2.05, 2.850, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),

        # --- 1.07 POKOJ ---
        # #15: V, 120cm from west wall (window 05)
        ("Light_1.07_Pokoj_V1_West", (1.565, 5.475, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),
        # #16: V, 120cm from east wall
        ("Light_1.07_Pokoj_V2_East", (3.195, 5.475, z_int), 40.0, (1.0, 0.95, 0.88), 0.175),

        # --- 1.08 WC ---
        # #12: M (12x12cm), centered
        ("Light_1.08_WC_M", (1.06, 7.60, z_int), 20.0, (1.0, 0.95, 0.88), 0.12),

        # --- 1.09 TECHNICKÁ MÍSTNOST ---
        # #9: M (12x12cm), centered
        ("Light_1.09_Technicka_mistnost_M", (1.06, 8.95, z_int), 25.0, (1.0, 0.95, 0.88), 0.12),

        # --- 1.10 KOUPELNA ---
        # #3: V+ (Velké koupelnové 22.5x22.5cm)
        ("Light_1.10_Koupelna_Vplus", (1.62, 10.60, z_int), 50.0, (1.0, 0.97, 0.92), 0.225),

        # --- 1.11 CHODBA ---
        # #7: M, near bathroom door
        ("Light_1.11_Chodba_M1_Bath", (2.375, 9.20, z_int), 25.0, (1.0, 0.95, 0.88), 0.12),
        # #11: M, near WC door
        ("Light_1.11_Chodba_M2_WC", (2.375, 7.65, z_int), 25.0, (1.0, 0.95, 0.88), 0.12),

        # --- EXTERIOR LIGHTS (Adjusted layout & heights) ---
        # Southwest corner & front facade
        ("Light_Ext_Front_Soffit_2_Window106", (-0.30, -0.30, 1.65), 25.0, (1.0, 0.94, 0.82), 0.12),
        ("Light_Ext_Front_Soffit_3_Entrance", (5.19, -0.30, 1.65), 30.0, (1.0, 0.94, 0.82), 0.12),
        ("Light_Ext_Front_Soffit_5_CornerR", (10.00, -0.30, 1.65), 25.0, (1.0, 0.94, 0.82), 0.12),

        # Symmetrical side lights (West and East facades)
        ("Light_Ext_Front_Soffit_1_CornerL", (-0.30, 3.50, 1.65), 25.0, (1.0, 0.94, 0.82), 0.12),
        ("Light_Ext_Side_East_A2", (10.30, 3.50, 1.65), 30.0, (1.0, 0.94, 0.82), 0.15),

        # Rear patio wall lights (at height 1.8 m)
        ("Light_Ext_Rear_Patio_Left", (6.26, 12.05, z_ext_wall), 35.0, (1.0, 0.94, 0.82), 0.15),
        ("Light_Ext_Rear_Patio_Right", (9.46, 12.05, z_ext_wall), 35.0, (1.0, 0.94, 0.82), 0.15),
    ]

    for light_name, loc, energy, color, size in lights_spec:
        l_data = bpy.data.lights.new(name=light_name, type='POINT')
        l_data.energy = energy
        l_data.color = color
        l_data.shadow_soft_size = size
        l_data.use_shadow = False
        l_obj = bpy.data.objects.new(name=light_name, object_data=l_data)
        l_obj.location = loc
        bpy.context.scene.collection.objects.link(l_obj)

    # Soft sun / fill light for clear architectural preview
    sun_data = bpy.data.lights.new(name="Sun_Fill", type='SUN')
    sun_data.energy = 2.0
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new(name="Sun_Fill", object_data=sun_data)
    sun_obj.location = (15.0, -10.0, 25.0)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-35))
    bpy.context.scene.collection.objects.link(sun_obj)

    # ----------------------------------------------------
    # 7. Orthographic Camera for Isometric View
    # ----------------------------------------------------
    cam_data = bpy.data.cameras.new("Isometric_Camera")
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = 16.5  # Fits 10.0 x 12.0 m house with margins
    cam_data.clip_start = 0.1
    cam_data.clip_end = 200.0

    cam_obj = bpy.data.objects.new("Isometric_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Target point: center of the house
    target = Vector((5.0, 6.0, 0.9))
    distance = 35.0
    iso_dir = Vector((-1.0, -1.0, math.sqrt(2))).normalized()
    cam_obj.location = target + iso_dir * distance

    # Aim camera at target
    direction = target - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

    print("House modeling completed successfully!")

def main():
    # Parse CLI argument for output filename
    output_filepath = "dum_pudorys.blend"
    if "--" in sys.argv:
        idx = sys.argv.index("--")
        if idx + 1 < len(sys.argv):
            output_filepath = sys.argv[idx + 1]

    build_house()

    abs_path = os.path.abspath(output_filepath)
    bpy.ops.wm.save_as_mainfile(filepath=abs_path)
    print(f"Project saved to: {abs_path}")

    # Render a high quality preview image
    try:
        preview_path = os.path.splitext(abs_path)[0] + "_preview.png"
        bpy.context.scene.render.filepath = preview_path
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        bpy.ops.render.render(write_still=True)
        print(f"Preview image rendered to: {preview_path}")
    except Exception as e:
        print(f"Note: Could not render preview image: {e}")

if __name__ == "__main__":
    main()
