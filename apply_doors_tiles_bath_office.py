"""
apply_doors_tiles_bath_office.py
--------------------------------
Comprehensive single-pass execution script for dum_pudorys.blend:
1. Door Decors & 7-Panel Oak Doors with dark reveal grooves & stainless steel handles.
2. Concrete-gray ceramic tiles for Bathroom, WC, Tech room, and Hallway.
3. Realistic Bathroom (1.10) detailing: oak vanity, sink, faucet, LED mirror, tall split oak cabinet,
   walk-in glass shower with horizontal oak planks & chrome rain column, chrome towel radiator.
4. Realistic Office (1.07) detailing: white desk, dual monitors (flat+curved), gaming PC with RGB & glass panel,
   Soundcore speaker, keyboard, mouse, dual white Kallax units, and tall white wardrobe with top cabinets.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import os

print(">>> Starting full update: Doors, Tiles, Bathroom & Office...")

# -------------------------------------------------------------------------
# 1. MATERIALS DEFINITION
# -------------------------------------------------------------------------

def get_or_create_mat(name):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    return mat

def clear_nodes(mat):
    mat.node_tree.nodes.clear()

def setup_concrete_gray_tile_mat():
    mat = get_or_create_mat("Mat_Tile_Concrete_Gray")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-1000, 0)
    
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-800, 0)
    mapping.inputs['Scale'].default_value = (1.667, 1.667, 1.667)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    brick = nodes.new('ShaderNodeTexBrick')
    brick.location = (-550, 200)
    brick.inputs['Mortar Size'].default_value = 0.005
    brick.inputs['Mortar Smooth'].default_value = 0.1
    brick.inputs['Row Height'].default_value = 1.0
    brick.inputs['Brick Width'].default_value = 1.0
    brick.offset = 0.0
    brick.squash = 1.0
    links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
    
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-550, -200)
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 4.0
    noise.inputs['Roughness'].default_value = 0.6
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (-300, -200)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.16, 0.18, 0.19, 1.0)
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.22, 0.24, 0.25, 1.0)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    
    mix_color = nodes.new('ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.location = (-50, 100)
    mortar_col = (0.38, 0.38, 0.37, 1.0)
    mix_color.inputs[6].default_value = mortar_col
    links.new(ramp.outputs['Color'], mix_color.inputs[7])
    links.new(brick.outputs['Color'], mix_color.inputs[0])
    
    bump = nodes.new('ShaderNodeBump')
    bump.location = (200, -100)
    bump.inputs['Strength'].default_value = 0.15
    bump.inputs['Distance'].default_value = 0.005
    links.new(brick.outputs['Fac'], bump.inputs['Height'])
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (450, 100)
    bsdf.inputs['Roughness'].default_value = 0.55
    links.new(mix_color.outputs[2], bsdf.inputs['Base Color'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (700, 100)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    
    return mat

def setup_door_oak_mat():
    mat = get_or_create_mat("Mat_Door_Oak")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (1.0, 1.0, 1.0)
    links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
    
    tex_path = r"C:\Users\Vaso\Antigravity\Project blender\assets\k003_gold_craft_oak\K003_original.jpg"
    img = None
    if os.path.exists(tex_path):
        img = bpy.data.images.get("K003_original.jpg") or bpy.data.images.load(tex_path)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 100)
    bsdf.inputs['Roughness'].default_value = 0.45
    
    if img:
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.location = (-350, 100)
        tex_node.image = img
        links.new(mapping.outputs['Vector'], tex_node.inputs['Vector'])
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        
        bump = nodes.new('ShaderNodeBump')
        bump.location = (-50, -100)
        bump.inputs['Strength'].default_value = 0.12
        bump.inputs['Distance'].default_value = 0.002
        links.new(tex_node.outputs['Color'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    else:
        bsdf.inputs['Base Color'].default_value = (0.58, 0.42, 0.26, 1.0)
        
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (500, 100)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_stainless_steel_mat():
    mat = get_or_create_mat("Mat_Brushed_Stainless_Steel")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.82, 0.82, 0.82, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.25
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_reveal_black_mat():
    mat = get_or_create_mat("Mat_Door_Reveal_Black")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.6
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_white_laminate_mat():
    mat = get_or_create_mat("Mat_Office_White_Laminate")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.92, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.35
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_white_ceramic_mat():
    mat = get_or_create_mat("Mat_White_Ceramic")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 1.50
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_glass_clear_mat():
    mat = get_or_create_mat("Mat_Glass_Clear")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.98, 0.98, 0.98, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.52
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_mirror_mat():
    mat = get_or_create_mat("Mat_Mirror_Reflective")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.95, 0.95, 0.95, 1.0)
    bsdf.inputs['Metallic'].default_value = 1.0
    bsdf.inputs['Roughness'].default_value = 0.0
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_mirror_led_edge_mat():
    mat = get_or_create_mat("Mat_Mirror_LED_Edge")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (1.0, 0.98, 0.94, 1.0)
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.96, 0.90, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 1.5
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def setup_rgb_cyan_mat():
    mat = get_or_create_mat("Mat_PC_RGB_Cyan")
    clear_nodes(mat)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.0, 0.75, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.0, 0.75, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 3.5
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# Initialize shaders
mat_tile = setup_concrete_gray_tile_mat()
mat_door_oak = setup_door_oak_mat()
mat_steel = setup_stainless_steel_mat()
mat_reveal = setup_reveal_black_mat()
mat_white = setup_white_laminate_mat()
mat_ceramic = setup_white_ceramic_mat()
mat_glass = setup_glass_clear_mat()
mat_mirror = setup_mirror_mat()
mat_mirror_led = setup_mirror_led_edge_mat()
mat_rgb = setup_rgb_cyan_mat()

# -------------------------------------------------------------------------
# 2. APPLY TILE MATERIAL TO ALL WET ROOM FLOORS & THRESHOLDS
# -------------------------------------------------------------------------
print("--- Applying Tile Material to Floors ---")
tile_floor_names = [
    'Floor_1.10_Koupelna',
    'Floor_1.08_WC',
    'Floor_1.09_Technicka_mistnost',
    'Floor_1.01_Zadveri',
    'Floor_1.11_Chodba',
    'Floor_Threshold_101_102',
    'Floor_Threshold_104_111',
    'Floor_Threshold_111_108',
    'Floor_Threshold_111_109',
    'Floor_Threshold_111_110',
    'Floor_Threshold_Front_Entrance'
]

for fname in tile_floor_names:
    obj = bpy.data.objects.get(fname)
    if obj and obj.data:
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name in ['koupelna', 'Concrete tiles', 'Light gray porcelain tile']:
                slot.material = mat_tile
        if not obj.material_slots:
            obj.data.materials.append(mat_tile)
        elif obj.material_slots[0].material != mat_tile and 'Floor_1.10' not in fname:
            obj.material_slots[0].material = mat_tile

# Update legacy materials
for legacy_name in ['koupelna', 'koupelna stena']:
    m = bpy.data.materials.get(legacy_name)
    if m and m.node_tree:
        for node in m.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                node.inputs['Base Color'].default_value = (0.18, 0.20, 0.21, 1.0)
                node.inputs['Roughness'].default_value = 0.55

# Assign oak material to Interior_Door_Frames
idf = bpy.data.objects.get('Interior_Door_Frames')
if idf and idf.data:
    if idf.material_slots:
        idf.material_slots[0].material = mat_door_oak
    else:
        idf.data.materials.append(mat_door_oak)

mat_drevo = bpy.data.materials.get('drevo')
if mat_drevo and mat_drevo.node_tree:
    for node in mat_drevo.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            node.image = bpy.data.images.get('K003_original.jpg')
        elif node.type == 'BSDF_PRINCIPLED':
            node.inputs['Roughness'].default_value = 0.45

# -------------------------------------------------------------------------
# 3. CREATE REALISTIC 7-PANEL INTERIOR DOORS (pracovna dvere.jpg)
# -------------------------------------------------------------------------
print("--- Creating 7-Panel Oak Interior Doors ---")

door_collection = bpy.data.collections.get("Doors_Interior")
if not door_collection:
    door_collection = bpy.data.collections.new("Doors_Interior")
    bpy.context.scene.collection.children.link(door_collection)

for obj in list(bpy.data.objects):
    if obj.name.startswith("DoorLeaf_"):
        bpy.data.objects.remove(obj, do_unlink=True)

def build_door_leaf_mesh(width, height=1.97, thickness=0.04):
    bm = bmesh.new()
    stile_w = 0.10
    top_rail_h = 0.10
    bot_rail_h = 0.15
    center_w = width - 2 * stile_w
    center_h = height - top_rail_h - bot_rail_h
    t = thickness

    uv_layer = bm.loops.layers.uv.new("UVMap")

    def add_box(min_x, max_x, min_y, max_y, min_z, max_z, mat_idx, uv_orientation="vertical"):
        v0 = bm.verts.new((min_x, min_y, min_z))
        v1 = bm.verts.new((max_x, min_y, min_z))
        v2 = bm.verts.new((max_x, max_y, min_z))
        v3 = bm.verts.new((min_x, max_y, min_z))
        v4 = bm.verts.new((min_x, min_y, max_z))
        v5 = bm.verts.new((max_x, min_y, max_z))
        v6 = bm.verts.new((max_x, max_y, max_z))
        v7 = bm.verts.new((min_x, max_y, max_z))

        faces = [
            bm.faces.new((v0, v1, v2, v3)), # bottom
            bm.faces.new((v4, v7, v6, v5)), # top
            bm.faces.new((v0, v4, v5, v1)), # front
            bm.faces.new((v2, v6, v7, v3)), # back
            bm.faces.new((v0, v3, v7, v4)), # left
            bm.faces.new((v1, v5, v6, v2)), # right
        ]
        for f in faces:
            f.material_index = mat_idx
            for loop in f.loops:
                v = loop.vert
                if uv_orientation == "horizontal":
                    loop[uv_layer].uv = Vector((v.co.z, v.co.x))
                else:
                    loop[uv_layer].uv = Vector((v.co.x, v.co.z))
        return faces

    # Left & right stiles (vertical grain)
    add_box(0.0, stile_w, 0.0, t, 0.0, height, 0, "vertical")
    add_box(width - stile_w, width, 0.0, t, 0.0, height, 0, "vertical")
    # Bottom & top rails (horizontal grain)
    add_box(stile_w, width - stile_w, 0.0, t, 0.0, bot_rail_h, 0, "horizontal")
    add_box(stile_w, width - stile_w, 0.0, t, height - top_rail_h, height, 0, "horizontal")
    
    # 7 panels + 6 reveals
    n_panels = 7
    reveal_h = 0.012
    total_reveal_h = (n_panels - 1) * reveal_h
    panel_h = (center_h - total_reveal_h) / n_panels
    
    cur_z = bot_rail_h
    for p in range(n_panels):
        add_box(stile_w, width - stile_w, 0.002, t - 0.002, cur_z, cur_z + panel_h, 0, "horizontal")
        cur_z += panel_h
        if p < n_panels - 1:
            add_box(stile_w, width - stile_w, 0.005, t - 0.005, cur_z, cur_z + reveal_h, 1, "horizontal")
            cur_z += reveal_h

    # Stainless steel handle & rosettes
    hx = width - 0.05
    hz = 0.98
    add_box(hx - 0.02, hx + 0.02, -0.008, 0.0, hz - 0.035, hz + 0.035, 2)
    add_box(hx - 0.11, hx + 0.01, -0.028, -0.012, hz - 0.01, hz + 0.01, 2)
    add_box(hx - 0.015, hx + 0.015, -0.006, 0.0, hz - 0.12, hz - 0.07, 2)
    add_box(hx - 0.02, hx + 0.02, t, t + 0.008, hz - 0.035, hz + 0.035, 2)
    add_box(hx - 0.11, hx + 0.01, t + 0.012, t + 0.028, hz - 0.01, hz + 0.01, 2)
    add_box(hx - 0.015, hx + 0.015, t, t + 0.006, hz - 0.12, hz - 0.07, 2)

    mesh = bpy.data.meshes.new("Mesh_DoorLeaf")
    bm.to_mesh(mesh)
    bm.free()
    
    mesh.materials.append(mat_door_oak)
    mesh.materials.append(mat_reveal)
    mesh.materials.append(mat_steel)
    return mesh

door_specs = [
    ("DoorLeaf_101_102", Vector((4.72, 2.41, 0.015)), 0.78, 75.0),
    ("DoorLeaf_102_105", Vector((6.16, 2.82, 0.015)), 0.78, -15.0),
    ("DoorLeaf_102_106", Vector((4.46, 2.72, 0.015)), 0.78, 165.0),
    ("DoorLeaf_102_107", Vector((4.46, 4.82, 0.015)), 0.78, -105.0),
    ("DoorLeaf_104_111", Vector((2.94, 7.22, 0.015)), 0.78, 165.0),
    ("DoorLeaf_111_108", Vector((1.81, 7.27, 0.015)), 0.68, -105.0),
    ("DoorLeaf_111_109", Vector((1.81, 8.57, 0.015)), 0.68, -105.0),
    ("DoorLeaf_111_110", Vector((2.07, 9.84, 0.015)), 0.68, 75.0),
]

for name, pos, w, rot_deg in door_specs:
    mesh = build_door_leaf_mesh(width=w, height=1.97, thickness=0.04)
    door_obj = bpy.data.objects.new(name, mesh)
    door_obj.location = pos
    door_obj.rotation_euler = Euler((0.0, 0.0, math.radians(rot_deg)), 'XYZ')
    door_collection.objects.link(door_obj)

print(">>> 8 interior doors created with authentic 7-panel oak finish & stainless handles.")

# -------------------------------------------------------------------------
# 4. DETAIL BATHROOM 1.10 (koupelna.jpg, skrine koupelna.jpg, detail sprcha.jpg)
# -------------------------------------------------------------------------
print("--- Detailing Bathroom (1.10) ---")

bath_collection = bpy.data.collections.get("Bathroom_Fixtures")
if not bath_collection:
    bath_collection = bpy.data.collections.new("Bathroom_Fixtures")
    bpy.context.scene.collection.children.link(bath_collection)

for obj in list(bpy.data.objects):
    if obj.name.startswith("Bath_"):
        bpy.data.objects.remove(obj, do_unlink=True)

# 4A. Walk-in Glass Shower Screen & Top Stabilizer Bar
glass_mesh = bpy.data.meshes.new("Mesh_Bath_Shower_Glass")
bm_glass = bmesh.new()
verts_g = [
    bm_glass.verts.new((1.346, 10.45, 0.02)),
    bm_glass.verts.new((1.354, 10.45, 0.02)),
    bm_glass.verts.new((1.354, 11.58, 0.02)),
    bm_glass.verts.new((1.346, 11.58, 0.02)),
    bm_glass.verts.new((1.346, 10.45, 2.05)),
    bm_glass.verts.new((1.354, 10.45, 2.05)),
    bm_glass.verts.new((1.354, 11.58, 2.05)),
    bm_glass.verts.new((1.346, 11.58, 2.05)),
]
for f_idx in [(0,1,2,3), (4,7,6,5), (0,4,5,1), (2,6,7,3), (0,3,7,4), (1,5,6,2)]:
    bm_glass.faces.new([verts_g[i] for i in f_idx])
bm_glass.to_mesh(glass_mesh)
bm_glass.free()
glass_obj = bpy.data.objects.new("Bath_Shower_Glass_Screen", glass_mesh)
glass_obj.data.materials.append(mat_glass)
bath_collection.objects.link(glass_obj)

bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.98, location=(0.86, 10.60, 2.02), rotation=(0, math.radians(90), 0))
bar_obj = bpy.context.active_object
bar_obj.name = "Bath_Shower_Stabilizer_Bar"
bar_obj.data.materials.append(mat_steel)
for col in bar_obj.users_collection:
    col.objects.unlink(bar_obj)
bath_collection.objects.link(bar_obj)

# 4B. Horizontal Oak Wood Plank Feature Wall inside Shower (skrine koupelna.jpg)
# On West wall X=0.37, Y from 10.45 to 11.58, Z from 0.02 to 2.45
sh_wall_mesh = bpy.data.meshes.new("Mesh_Bath_Shower_Wood_Wall")
bm_sw = bmesh.new()
bmesh.ops.create_cube(bm_sw, size=1.0, matrix=Matrix.Translation((0.375, 11.015, 1.235)) @ Matrix.Diagonal((0.015, 1.13, 2.43, 1.0)))
bm_sw.to_mesh(sh_wall_mesh)
bm_sw.free()
sh_wall_obj = bpy.data.objects.new("Bath_Shower_Wood_Wall", sh_wall_mesh)
sh_wall_obj.data.materials.append(mat_door_oak)
bath_collection.objects.link(sh_wall_obj)

def add_cylinder(bm, radius, depth, matrix):
    return bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, radius1=radius, radius2=radius, depth=depth, matrix=matrix)

shower_mesh = bpy.data.meshes.new("Mesh_Bath_Shower_Column")
bm_sh = bmesh.new()
add_cylinder(bm_sh, radius=0.015, depth=1.10, matrix=Matrix.Translation((0.395, 10.95, 1.60)))
bmesh.ops.create_cube(bm_sh, size=1.0, matrix=Matrix.Translation((0.55, 10.95, 2.15)) @ Matrix.Diagonal((0.22, 0.22, 0.02, 1.0)))
bmesh.ops.create_cube(bm_sh, size=1.0, matrix=Matrix.Translation((0.41, 10.95, 1.05)) @ Matrix.Diagonal((0.08, 0.28, 0.06, 1.0)))
bmesh.ops.create_cube(bm_sh, size=1.0, matrix=Matrix.Translation((0.44, 11.50, 1.25)) @ Matrix.Diagonal((0.14, 0.14, 0.05, 1.0)))
bmesh.ops.create_cube(bm_sh, size=1.0, matrix=Matrix.Translation((0.44, 11.50, 1.55)) @ Matrix.Diagonal((0.14, 0.14, 0.05, 1.0)))
bm_sh.to_mesh(shower_mesh)
bm_sh.free()
shower_col_obj = bpy.data.objects.new("Bath_Rain_Shower_Column", shower_mesh)
shower_col_obj.data.materials.append(mat_steel)
bath_collection.objects.link(shower_col_obj)

# 4D. Floating Oak Vanity with Dual Drawers (East Wall: X from 2.25 to 2.85, Y from 10.45 to 11.25)
vanity_mesh = bpy.data.meshes.new("Mesh_Bath_Vanity")
bm_v = bmesh.new()
bmesh.ops.create_cube(bm_v, size=1.0, matrix=Matrix.Translation((2.55, 10.85, 0.60)) @ Matrix.Diagonal((0.60, 0.80, 0.50, 1.0)))
bm_v.to_mesh(vanity_mesh)
bm_v.free()
vanity_obj = bpy.data.objects.new("Bath_Vanity_Cabinet", vanity_mesh)
vanity_obj.data.materials.append(mat_door_oak)
bath_collection.objects.link(vanity_obj)

sink_mesh = bpy.data.meshes.new("Mesh_Bath_Washbasin")
bm_s = bmesh.new()
bmesh.ops.create_cube(bm_s, size=1.0, matrix=Matrix.Translation((2.55, 10.85, 0.875)) @ Matrix.Diagonal((0.63, 0.84, 0.05, 1.0)))
bmesh.ops.create_cube(bm_s, size=1.0, matrix=Matrix.Translation((2.52, 10.85, 0.88)) @ Matrix.Diagonal((0.45, 0.65, 0.04, 1.0)))
bm_s.to_mesh(sink_mesh)
bm_s.free()
sink_obj = bpy.data.objects.new("Bath_Ceramic_Washbasin", sink_mesh)
sink_obj.data.materials.append(mat_ceramic)
bath_collection.objects.link(sink_obj)

bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.18, location=(2.75, 10.85, 0.99))
faucet_obj = bpy.context.active_object
faucet_obj.name = "Bath_Mixer_Faucet"
faucet_obj.data.materials.append(mat_steel)
for col in faucet_obj.users_collection:
    col.objects.unlink(faucet_obj)
bath_collection.objects.link(faucet_obj)

# 4E. LED Backlit Mirror above Vanity (East wall: X=2.865, Y from 10.50 to 11.20, Z from 1.15 to 1.95)
mirror_mesh = bpy.data.meshes.new("Mesh_Bath_Mirror")
bm_m = bmesh.new()
bmesh.ops.create_cube(bm_m, size=1.0, matrix=Matrix.Translation((2.855, 10.85, 1.55)) @ Matrix.Diagonal((0.015, 0.70, 0.80, 1.0)))
for f in bm_m.faces:
    f.material_index = 0
bmesh.ops.create_cube(bm_m, size=1.0, matrix=Matrix.Translation((2.850, 10.85, 1.55)) @ Matrix.Diagonal((0.018, 0.74, 0.84, 1.0)))
for f in bm_m.faces[6:]:
    f.material_index = 1
bm_m.to_mesh(mirror_mesh)
bm_m.free()
mirror_obj = bpy.data.objects.new("Bath_LED_Backlit_Mirror", mirror_mesh)
mirror_obj.data.materials.append(mat_mirror)
mirror_obj.data.materials.append(mat_mirror_led)
bath_collection.objects.link(mirror_obj)

# 4F. Tall Oak Storage Column next to shower (skrine koupelna.jpg)
tall_col_mesh = bpy.data.meshes.new("Mesh_Bath_Tall_Cabinet")
bm_tc = bmesh.new()
bmesh.ops.create_cube(bm_tc, size=1.0, matrix=Matrix.Translation((1.58, 10.15, 0.625)) @ Matrix.Diagonal((0.36, 0.40, 0.85, 1.0)))
bmesh.ops.create_cube(bm_tc, size=1.0, matrix=Matrix.Translation((1.58, 10.15, 1.75)) @ Matrix.Diagonal((0.36, 0.40, 0.80, 1.0)))
bm_tc.to_mesh(tall_col_mesh)
bm_tc.free()
tall_col_obj = bpy.data.objects.new("Bath_Tall_Storage_Cabinet", tall_col_mesh)
tall_col_obj.data.materials.append(mat_door_oak)
bath_collection.objects.link(tall_col_obj)

# 4G. Chrome Ladder Towel Radiator & Hamper
rad_mesh = bpy.data.meshes.new("Mesh_Bath_Ladder_Radiator")
bm_r = bmesh.new()
add_cylinder(bm_r, radius=0.015, depth=1.15, matrix=Matrix.Translation((2.84, 10.00, 1.225)))
add_cylinder(bm_r, radius=0.015, depth=1.15, matrix=Matrix.Translation((2.84, 10.30, 1.225)))
for r_idx in range(16):
    rz = 0.68 + r_idx * 0.07
    add_cylinder(bm_r, radius=0.010, depth=0.30, matrix=Matrix.Translation((2.84, 10.15, rz)) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
bm_r.to_mesh(rad_mesh)
bm_r.free()
rad_obj = bpy.data.objects.new("Bath_Ladder_Radiator", rad_mesh)
rad_obj.data.materials.append(mat_steel)
bath_collection.objects.link(rad_obj)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(2.65, 10.15, 0.285))
hamper_obj = bpy.context.active_object
hamper_obj.name = "Bath_Laundry_Hamper"
hamper_obj.dimensions = Vector((0.35, 0.45, 0.53))
hamper_obj.data.materials.append(mat_reveal)
for col in hamper_obj.users_collection:
    col.objects.unlink(hamper_obj)
bath_collection.objects.link(hamper_obj)

print(">>> Bathroom (1.10) fully detailed matching real photos.")

# -------------------------------------------------------------------------
# 5. DETAIL OFFICE 1.07 (pracovna dvere.jpg, pracovna, pc.jpg)
# -------------------------------------------------------------------------
print("--- Detailing Office (1.07) ---")

office_collection = bpy.data.collections.get("Office_107_Furniture")
if not office_collection:
    office_collection = bpy.data.collections.new("Office_107_Furniture")
    bpy.context.scene.collection.children.link(office_collection)

# Clean up stray desk duplicate and previous office additions
for obj in list(bpy.data.objects):
    if obj.name in ['table top.001', 'Legs.001', 'Ikea Table Linnmon - Adils.001', 'SM_tv screen led .002', 'Computer Build']:
        bpy.data.objects.remove(obj, do_unlink=True)
    elif obj.name.startswith("Office_") and obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# 5A. Tall White Wardrobe Unit with Top Cabinets (pracovna dvere.jpg)
wardrobe_mesh = bpy.data.meshes.new("Mesh_Office_Wardrobe")
bm_w = bmesh.new()
# Main lower body (Z from 0.02 to 1.95, width along Y=1.50m, depth along X=0.60m)
bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((4.05, 5.60, 0.985)) @ Matrix.Diagonal((0.60, 1.50, 1.93, 1.0)))
# Top extension cabinet reaching ceiling (Z from 1.95 to 2.45)
bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((4.05, 5.60, 2.20)) @ Matrix.Diagonal((0.60, 1.50, 0.50, 1.0)))
# Vertical chrome bow handles
for hy, hz in [(5.10, 1.00), (5.15, 1.00), (6.10, 1.00), (5.10, 2.05), (5.15, 2.05), (6.10, 2.05)]:
    bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Translation((3.73, hy, hz)) @ Matrix.Diagonal((0.02, 0.015, 0.14, 1.0)))
for f in bm_w.faces:
    f.material_index = 0
bm_w.to_mesh(wardrobe_mesh)
bm_w.free()
wardrobe_obj = bpy.data.objects.new("Office_Wardrobe_Tall", wardrobe_mesh)
wardrobe_obj.data.materials.append(mat_white)
wardrobe_obj.data.materials.append(mat_steel)
office_collection.objects.link(wardrobe_obj)

# 5B. Workstation Desk (Linnmon Adils) styling
desk_empty = bpy.data.objects.get('Ikea Table Linnmon - Adils')
if desk_empty:
    desk_empty.location = Vector((2.40, 6.62, 0.015))
tt = bpy.data.objects.get('table top')
if tt and tt.data:
    if tt.material_slots:
        tt.material_slots[0].material = mat_white
    else:
        tt.data.materials.append(mat_white)
legs = bpy.data.objects.get('Legs')
if legs and legs.data:
    for s in legs.material_slots:
        s.material = mat_white

# Desk accessories (mat & pad)
pad_mesh = bpy.data.meshes.new("Mesh_Office_Desk_Pad")
bm_pad = bmesh.new()
bmesh.ops.create_cube(bm_pad, size=1.0, matrix=Matrix.Translation((2.35, 6.55, 0.748)) @ Matrix.Diagonal((0.85, 0.40, 0.005, 1.0)))
bm_pad.to_mesh(pad_mesh)
bm_pad.free()
pad_obj = bpy.data.objects.new("Office_Desk_Pad", pad_mesh)
pad_obj.data.materials.append(mat_reveal)
office_collection.objects.link(pad_obj)

# 5C. Dual Monitors on Arms (pracovna, pc.jpg)
monitors_mesh = bpy.data.meshes.new("Mesh_Office_Dual_Monitors")
bm_mon = bmesh.new()
# Left Flat Monitor (27" 16:9, centered at X=2.15, Y=6.75, Z=1.02)
bmesh.ops.create_cube(bm_mon, size=1.0, matrix=Matrix.Translation((2.15, 6.75, 1.02)) @ Matrix.Diagonal((0.62, 0.04, 0.38, 1.0)))
# Right Curved Monitor (27" angled ~25° inwards, centered at X=2.70, Y=6.70, Z=1.02)
rot_mat = Matrix.Rotation(math.radians(-22), 4, 'Z')
trans_mat = Matrix.Translation((2.72, 6.68, 1.02))
bmesh.ops.create_cube(bm_mon, size=1.0, matrix=trans_mat @ rot_mat @ Matrix.Diagonal((0.62, 0.05, 0.38, 1.0)))
# Desktop monitor arm stand
add_cylinder(bm_mon, radius=0.02, depth=0.45, matrix=Matrix.Translation((2.40, 6.90, 0.95)))
bm_mon.to_mesh(monitors_mesh)
bm_mon.free()
monitors_obj = bpy.data.objects.new("Office_Dual_Monitors", monitors_mesh)
monitors_obj.data.materials.append(mat_reveal)
monitors_obj.data.materials.append(mat_steel)
office_collection.objects.link(monitors_obj)

# 5D. Gaming PC Desktop Tower with RGB & Tempered Glass (pracovna, pc.jpg)
# Located at X from 2.88 to 3.12, Y from 6.45 to 6.88, Z from 0.745 to 1.20
pc_mesh = bpy.data.meshes.new("Mesh_Office_PC_Tower")
bm_pc = bmesh.new()
bmesh.ops.create_cube(bm_pc, size=1.0, matrix=Matrix.Translation((2.98, 6.66, 0.975)) @ Matrix.Diagonal((0.22, 0.44, 0.45, 1.0)))
for f in bm_pc.faces:
    f.material_index = 0
# Internal glowing cyan RGB cooling fans & AIO liquid cooler block
bmesh.ops.create_cube(bm_pc, size=1.0, matrix=Matrix.Translation((2.90, 6.55, 1.08)) @ Matrix.Diagonal((0.04, 0.12, 0.12, 1.0)))
bmesh.ops.create_cube(bm_pc, size=1.0, matrix=Matrix.Translation((2.90, 6.72, 1.02)) @ Matrix.Diagonal((0.04, 0.08, 0.08, 1.0)))
for f in bm_pc.faces[6:]:
    f.material_index = 1
# Left side tempered glass panel (X=2.865)
bmesh.ops.create_cube(bm_pc, size=1.0, matrix=Matrix.Translation((2.868, 6.66, 0.975)) @ Matrix.Diagonal((0.006, 0.42, 0.43, 1.0)))
for f in bm_pc.faces[-6:]:
    f.material_index = 2

bm_pc.to_mesh(pc_mesh)
bm_pc.free()
pc_obj = bpy.data.objects.new("Office_PC_Tower_RGB", pc_mesh)
pc_obj.data.materials.append(mat_reveal)
pc_obj.data.materials.append(mat_rgb)
pc_obj.data.materials.append(mat_glass)
office_collection.objects.link(pc_obj)

# 5E. Soundcore Portable Boombox Speaker in front of PC (pracovna, pc.jpg)
bpy.ops.mesh.primitive_cylinder_add(radius=0.055, depth=0.18, location=(2.86, 6.40, 0.835), rotation=(0, 0, 0))
speaker_obj = bpy.context.active_object
speaker_obj.name = "Office_Soundcore_Speaker"
speaker_obj.data.materials.append(mat_reveal)
for col in speaker_obj.users_collection:
    col.objects.unlink(speaker_obj)
office_collection.objects.link(speaker_obj)

# 5F. Position Keyboard & Mouse on desk pad
kb = bpy.data.objects.get('Keyboard') or bpy.data.objects.get('G915 keyboard')
if kb:
    kb.location = Vector((2.28, 6.52, 0.755))
mouse_empty = bpy.data.objects.get('Logitech G102 LIGHTSYNC Gaming Mouse')
if mouse_empty:
    mouse_empty.location = Vector((2.65, 6.50, 0.755))

# 5G. IKEA Kallax Shelving Units (Flanking the desk)
for k_name in ['Ikea Kallax 147x147cm.001', 'Ikea Kallax 147x147cm.002']:
    old_k = bpy.data.objects.get(k_name)
    if old_k:
        bpy.data.objects.remove(old_k, do_unlink=True)

def build_kallax_mesh(name, total_w=0.77, total_h=1.47, depth=0.39):
    mesh = bpy.data.meshes.new(f"Mesh_{name}")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.0, 0.0, total_h/2.0)) @ Matrix.Diagonal((total_w, depth, total_h, 1.0)))
    for f in bm.faces:
        f.material_index = 0
    # Bottom DRÖNA box insert
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.0, 0.0, 0.20)) @ Matrix.Diagonal((total_w - 0.08, depth - 0.02, 0.33, 1.0)))
    for f in bm.faces[-6:]:
        f.material_index = 1
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_white)
    obj.data.materials.append(mat_reveal)
    return obj

kallax_left = build_kallax_mesh("Office_Kallax_Left", total_w=1.12, total_h=1.47, depth=0.39)
kallax_left.location = Vector((1.35, 6.75, 0.02))
office_collection.objects.link(kallax_left)

kallax_right = build_kallax_mesh("Office_Kallax_Right", total_w=0.77, total_h=1.47, depth=0.39)
kallax_right.location = Vector((3.45, 6.75, 0.02))
office_collection.objects.link(kallax_right)

# 5H. Office Chair positioned cleanly at desk
chair = bpy.data.objects.get('Office chair black.001')
if chair:
    chair.location = Vector((2.35, 6.05, 0.015))
    chair.rotation_euler = Euler((0.0, 0.0, math.radians(180)), 'XYZ')

old_chair = bpy.data.objects.get('Office chair black')
if old_chair:
    for ch in list(old_chair.children):
        bpy.data.objects.remove(ch, do_unlink=True)
    bpy.data.objects.remove(old_chair, do_unlink=True)

print(">>> Office (1.07) fully detailed matching real photos.")

# -------------------------------------------------------------------------
# 6. CAMERA & SAVE
# -------------------------------------------------------------------------
iso_cam = bpy.data.objects.get('Isometric_Camera')
if iso_cam:
    bpy.context.scene.camera = iso_cam

for area in bpy.context.screen.areas if bpy.context.screen else []:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Full update complete. dum_pudorys.blend successfully saved!")
