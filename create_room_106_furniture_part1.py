import bpy
import bmesh
import math
import mathutils

# -------------------------------------------------------------
# 1. HELPERS & MATERIALS
# -------------------------------------------------------------
def get_or_create_material(name, base_color=(0.8, 0.8, 0.8, 1.0), roughness=0.4, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

def setup_materials():
    mat_oak = bpy.data.materials.get("Mat_Kronospan_K003_Gold_Craft_Oak")
    if not mat_oak:
        raise RuntimeError("Mat_Kronospan_K003_Gold_Craft_Oak not found!")

    mat_white_plastic = get_or_create_material("Mat_Plastic_White_Matte", base_color=(0.92, 0.92, 0.91, 1.0), roughness=0.35, metallic=0.0)
    mat_cabinet_grey = get_or_create_material("Mat_Cabinet_Light_Grey", base_color=(0.58, 0.59, 0.58, 1.0), roughness=0.38, metallic=0.0)
    mat_chrome = bpy.data.materials.get("Mat_Kitchen_Chrome") or get_or_create_material("Mat_Silver_Metal", base_color=(0.85, 0.85, 0.87, 1.0), roughness=0.18, metallic=0.95)
    mat_dark_plastic = get_or_create_material("Mat_Plastic_Dark_Grey", base_color=(0.15, 0.15, 0.16, 1.0), roughness=0.5, metallic=0.0)

    # Fabric box materials
    mat_fabric_anthracite = get_or_create_material("Mat_Fabric_Anthracite", base_color=(0.14, 0.14, 0.15, 1.0), roughness=0.92, metallic=0.0)
    mat_fabric_light_grey = get_or_create_material("Mat_Fabric_Light_Grey", base_color=(0.68, 0.68, 0.66, 1.0), roughness=0.90, metallic=0.0)
    mat_fabric_green = get_or_create_material("Mat_Fabric_Green", base_color=(0.28, 0.65, 0.18, 1.0), roughness=0.88, metallic=0.0)
    mat_fabric_pattern = get_or_create_material("Mat_Fabric_Bin_Pattern", base_color=(0.82, 0.80, 0.76, 1.0), roughness=0.92, metallic=0.0)

    # Toy colors
    mat_toy_red = get_or_create_material("Mat_Toy_Red", base_color=(0.85, 0.12, 0.12, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_blue = get_or_create_material("Mat_Toy_Blue", base_color=(0.12, 0.35, 0.85, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_yellow = get_or_create_material("Mat_Toy_Yellow", base_color=(0.92, 0.80, 0.10, 1.0), roughness=0.3, metallic=0.0)
    mat_toy_purple = get_or_create_material("Mat_Toy_Purple", base_color=(0.55, 0.25, 0.70, 1.0), roughness=0.3, metallic=0.0)

    return {
        "oak": mat_oak,
        "white_plastic": mat_white_plastic,
        "cabinet_grey": mat_cabinet_grey,
        "chrome": mat_chrome,
        "dark_plastic": mat_dark_plastic,
        "fabric_anthracite": mat_fabric_anthracite,
        "fabric_light_grey": mat_fabric_light_grey,
        "fabric_green": mat_fabric_green,
        "fabric_pattern": mat_fabric_pattern,
        "toy_red": mat_toy_red,
        "toy_blue": mat_toy_blue,
        "toy_yellow": mat_toy_yellow,
        "toy_purple": mat_toy_purple,
    }

def get_or_create_collection(col_name):
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    return col

def add_box_geometry(bm, min_pt, max_pt):
    # Adds an axis-aligned box to bmesh
    x0, y0, z0 = min_pt
    x1, y1, z1 = max_pt
    verts = [
        bm.verts.new((x0, y0, z0)),
        bm.verts.new((x1, y0, z0)),
        bm.verts.new((x1, y1, z0)),
        bm.verts.new((x0, y1, z0)),
        bm.verts.new((x0, y0, z1)),
        bm.verts.new((x1, y0, z1)),
        bm.verts.new((x1, y1, z1)),
        bm.verts.new((x0, y1, z1)),
    ]
    faces = [
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]]), # bottom (-Z)
        bm.faces.new([verts[4], verts[7], verts[6], verts[5]]), # top (+Z)
        bm.faces.new([verts[0], verts[4], verts[5], verts[1]]), # south (-Y)
        bm.faces.new([verts[2], verts[6], verts[7], verts[3]]), # north (+Y)
        bm.faces.new([verts[0], verts[3], verts[7], verts[4]]), # west (-X)
        bm.faces.new([verts[1], verts[5], verts[6], verts[2]]), # east (+X)
    ]
    return faces

def apply_bevel_and_uv(obj, bevel_width=0.002, uv_scale=1.0):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    
    # UV cube projection for clean wood grain
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=uv_scale, correct_aspect=True)
    bpy.ops.object.mode_set(mode='OBJECT')

    # Bevel modifier
    bev = obj.modifiers.new(name="Bevel", type='BEVEL')
    bev.width = bevel_width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(40)
    bev.use_clamp_overlap = True
    obj.select_set(False)

print("Base helpers ready.")
