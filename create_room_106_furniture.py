import bpy
import bmesh
import math
import mathutils

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
    # 1. Oak material is strictly Mat_Kronospan_K003_Gold_Craft_Oak
    mat_oak = bpy.data.materials.get("Mat_Kronospan_K003_Gold_Craft_Oak")
    if not mat_oak:
        raise RuntimeError("Mat_Kronospan_K003_Gold_Craft_Oak not found!")

    # 2. White chair plastic
    mat_white_plastic = get_or_create_material("Mat_Plastic_White_Matte", base_color=(0.92, 0.92, 0.91, 1.0), roughness=0.32, metallic=0.0)

    # 3. Cabinet light grey doors (warm sage/light grey as in photo)
    mat_cabinet_grey = get_or_create_material("Mat_Cabinet_Light_Grey", base_color=(0.58, 0.59, 0.58, 1.0), roughness=0.38, metallic=0.0)

    # 4. Silver metal / chrome for legs and knobs
    mat_chrome = bpy.data.materials.get("Mat_Kitchen_Chrome") or get_or_create_material("Mat_Silver_Metal", base_color=(0.88, 0.88, 0.90, 1.0), roughness=0.18, metallic=0.95)

    # 5. Fabric materials for Drona boxes
    mat_fabric_anthracite = get_or_create_material("Mat_Fabric_Anthracite", base_color=(0.12, 0.12, 0.13, 1.0), roughness=0.90, metallic=0.0)
    mat_fabric_light_grey = get_or_create_material("Mat_Fabric_Light_Grey", base_color=(0.70, 0.70, 0.68, 1.0), roughness=0.88, metallic=0.0)
    mat_fabric_green = get_or_create_material("Mat_Fabric_Green", base_color=(0.28, 0.65, 0.18, 1.0), roughness=0.85, metallic=0.0)
    mat_fabric_pattern = get_or_create_material("Mat_Fabric_Bin_Pattern", base_color=(0.82, 0.80, 0.76, 1.0), roughness=0.92, metallic=0.0)

    return {
        "oak": mat_oak,
        "white_plastic": mat_white_plastic,
        "cabinet_grey": mat_cabinet_grey,
        "chrome": mat_chrome,
        "fabric_anthracite": mat_fabric_anthracite,
        "fabric_light_grey": mat_fabric_light_grey,
        "fabric_green": mat_fabric_green,
        "fabric_pattern": mat_fabric_pattern
    }

def get_or_create_collection(col_name):
    col = bpy.data.collections.get(col_name)
    if not col:
        col = bpy.data.collections.new(col_name)
        bpy.context.scene.collection.children.link(col)
    return col

def uv_unwrap_cube_projection(obj, scale=1.0):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=scale, correct_aspect=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)

print("Materials and helper functions defined successfully.")
