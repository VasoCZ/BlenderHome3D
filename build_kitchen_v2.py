import bpy
import bmesh
import mathutils
import math
import os

def create_or_get_material_black_matte():
    mat_name = "Mat_Kitchen_Black_Matte"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.028, 0.028, 0.028, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.38
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
        bsdf.inputs['IOR'].default_value = 1.5
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_oak():
    asset_path = r'C:\Users\Vaso\blenderkit_data\materials\halifax-oak-wood_edc1e4bf-e576-4d9a-bf78-529fc2b01490\halifax-oak-wood-natur_2K_95c171b0-28e6-4ef6-bd85-fddc1c535d93.blend'
    mat_name = "Halifax Oak Wood Natur"
    mat = bpy.data.materials.get(mat_name)
    if not mat and os.path.exists(asset_path):
        with bpy.data.libraries.load(asset_path) as (data_from, data_to):
            if mat_name in data_from.materials:
                data_to.materials = [mat_name]
        mat = bpy.data.materials.get(mat_name)
    
    if not mat:
        mat = bpy.data.materials.new(name="Mat_Kitchen_Wood_Oak")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.55, 0.38, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.45
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_black_glass():
    mat_name = "Mat_Kitchen_Black_Glass"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.01, 0.01, 0.01, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.03
        bsdf.inputs['Specular IOR Level'].default_value = 0.95
        bsdf.inputs['Metallic'].default_value = 0.1
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_stainless():
    mat_name = "Mat_Kitchen_Stainless_Steel"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.85, 0.85, 0.87, 1.0)
        bsdf.inputs['Metallic'].default_value = 1.0
        bsdf.inputs['Roughness'].default_value = 0.22
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_brass():
    mat_name = "Mat_Kitchen_Brass_Gold"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.88, 0.72, 0.38, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.9
        bsdf.inputs['Roughness'].default_value = 0.25
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_black_metal():
    mat_name = "Mat_Kitchen_Black_Metal"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.85
        bsdf.inputs['Roughness'].default_value = 0.32
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_plant():
    mat_name = "Mat_Kitchen_Plant_Green"
    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.12, 0.38, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.35
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_or_get_material_emission(name="Mat_Kitchen_LED_Warm", color=(1.0, 0.94, 0.82), strength=8.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (color[0], color[1], color[2], 1.0)
        emission.inputs['Strength'].default_value = strength
        out = nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(emission.outputs['Emission'], out.inputs['Surface'])
    return mat

def get_or_create_collection(col_name):
    if col_name in bpy.data.collections:
        return bpy.data.collections[col_name]
    col = bpy.data.collections.new(col_name)
    bpy.context.scene.collection.children.link(col)
    return col

def add_box(name, col, min_pt, max_pt, mat, uv_scale=1.0):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    x0, y0, z0 = min_pt
    x1, y1, z1 = max_pt
    v0 = bm.verts.new((x0, y0, z0))
    v1 = bm.verts.new((x1, y0, z0))
    v2 = bm.verts.new((x1, y1, z0))
    v3 = bm.verts.new((x0, y1, z0))
    v4 = bm.verts.new((x0, y0, z1))
    v5 = bm.verts.new((x1, y0, z1))
    v6 = bm.verts.new((x1, y1, z1))
    v7 = bm.verts.new((x0, y1, z1))
    
    bm.faces.new([v0, v1, v2, v3])
    bm.faces.new([v7, v6, v5, v4])
    bm.faces.new([v0, v4, v5, v1])
    bm.faces.new([v2, v6, v7, v3])
    bm.faces.new([v3, v7, v4, v0])
    bm.faces.new([v1, v5, v6, v2])
    
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for face in bm.faces:
        norm = face.normal
        for loop in face.loops:
            co = loop.vert.co
            if abs(norm.z) > 0.5:
                loop[uv_layer].uv = (co.x * uv_scale, co.y * uv_scale)
            elif abs(norm.x) > 0.5:
                loop[uv_layer].uv = (co.y * uv_scale, co.z * uv_scale)
            else:
                loop[uv_layer].uv = (co.x * uv_scale, co.z * uv_scale)
                
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

def add_cylinder(name, col, center, radius, height, mat, axis='Z', segments=24):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    
    rot = mathutils.Matrix.Identity(4)
    if axis == 'X':
        rot = mathutils.Matrix.Rotation(math.radians(90), 4, 'Y')
    elif axis == 'Y':
        rot = mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
        
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=height,
        matrix=rot
    )
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    if mat:
        obj.data.materials.append(mat)
    col.objects.link(obj)
    return obj

def build_kitchen(save_file=False):
    print("Building high-detail kitchen matching kuchyne.jpg...")
    col = get_or_create_collection("Kitchen_Furniture")
    
    # Remove existing objects in Kitchen_Furniture
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)

    mat_black = create_or_get_material_black_matte()
    mat_oak = create_or_get_material_oak()
    mat_glass = create_or_get_material_black_glass()
    mat_steel = create_or_get_material_stainless()
    mat_brass = create_or_get_material_brass()
    mat_metal = create_or_get_material_black_metal()
    mat_led = create_or_get_material_emission("Mat_Kitchen_LED_Warm", (1.0, 0.94, 0.82), 8.0)
    mat_disp_led = create_or_get_material_emission("Mat_Kitchen_LED_Cyan", (0.5, 0.85, 1.0), 4.0)
    mat_plant = create_or_get_material_plant()

    z_floor = 0.015
    z_counter = 0.900
    thick_counter = 0.038
    z_plinth = 0.100
    z_tall_top = 2.150  # Ergonomic tall cabinet height (allows camera to see over cleanly)

    # ==========================================
    # 1. COUNTERTOPS & SPLASHBACK
    # ==========================================
    # West Countertop: X in [3.00, 3.62], Y in [9.56, 11.635]
    add_box("Countertop_West", col, (3.000, 9.560, z_counter - thick_counter), (3.620, 11.635, z_counter), mat_oak, uv_scale=1.5)
    
    # North Countertop: X in [3.62, 5.85], Y in [11.015, 11.635]
    add_box("Countertop_North", col, (3.620, 11.015, z_counter - thick_counter), (5.850, 11.635, z_counter), mat_oak, uv_scale=1.5)
    
    # Peninsula Countertop: X in [5.10, 5.85], Y in [9.15, 11.015] (length 1.865m, width 75cm)
    add_box("Countertop_Peninsula", col, (5.100, 9.150, z_counter - thick_counter), (5.850, 11.015, z_counter), mat_oak, uv_scale=1.5)
    
    # Peninsula Waterfall end panel (South edge)
    add_box("Peninsula_Waterfall_End", col, (5.100, 9.112, z_floor), (5.850, 9.150, z_counter), mat_oak, uv_scale=1.5)
    
    # Peninsula Living Room Side panel (East face)
    add_box("Peninsula_Back_Panel", col, (5.835, 9.150, z_floor), (5.850, 11.015, z_counter - thick_counter), mat_oak, uv_scale=1.5)

    # Backsplash North Wall (under window): X in [3.00, 5.50], Y in [11.620, 11.635], Z in [0.90, 1.02]
    add_box("Backsplash_North", col, (3.000, 11.620, z_counter), (5.500, 11.635, 1.020), mat_oak, uv_scale=1.5)
    
    # Backsplash West Wall: X in [3.00, 3.015], Y in [9.56, 11.015], Z in [0.90, 1.45]
    add_box("Backsplash_West", col, (3.000, 9.560, z_counter), (3.015, 11.015, 1.450), mat_oak, uv_scale=1.5)

    # ==========================================
    # 2. PLINTH (SOKL)
    # ==========================================
    add_box("Plinth_West", col, (3.050, 9.560, z_floor), (3.570, 9.610, z_plinth), mat_black)
    add_box("Plinth_North", col, (3.620, 11.065, z_floor), (5.050, 11.115, z_plinth), mat_black)
    add_box("Plinth_Peninsula", col, (5.150, 9.200, z_floor), (5.200, 11.015, z_plinth), mat_black)

    # ==========================================
    # 3. BASE CABINETS & DRAWERS (MATTE BLACK)
    # ==========================================
    # West base units: 2 drawer stacks (cooktop stack and prep stack)
    for y_start, y_end in [(9.58, 10.28), (10.30, 11.00)]:
        z_ranges = [(z_plinth, 0.36), (0.38, 0.63), (0.65, z_counter - thick_counter - 0.02)]
        for z0, z1 in z_ranges:
            add_box(f"Drawer_West_{y_start:.2f}_{z0:.2f}", col, (3.585, y_start, z0), (3.605, y_end, z1), mat_black)
            add_box(f"Gola_West_{y_start:.2f}_{z1:.2f}", col, (3.550, y_start, z1), (3.585, y_end, z1 + 0.02), mat_black)

    # North base units: Sink cabinet (X in [3.70, 4.40]) and Dishwasher (X in [4.45, 5.05])
    add_box("Cabinet_Sink_Door1", col, (3.70, 11.015, z_plinth), (4.04, 11.035, z_counter - thick_counter - 0.02), mat_black)
    add_box("Cabinet_Sink_Door2", col, (4.06, 11.015, z_plinth), (4.40, 11.035, z_counter - thick_counter - 0.02), mat_black)
    
    # Dishwasher front with top control trim
    add_box("Dishwasher_Door", col, (4.45, 11.015, z_plinth), (5.05, 11.035, z_counter - thick_counter - 0.02), mat_black)
    add_box("Dishwasher_Handle_Trim", col, (4.45, 11.012, z_counter - thick_counter - 0.04), (5.05, 11.037, z_counter - thick_counter - 0.02), mat_metal)

    # Peninsula kitchen-side drawers (facing West, X = 5.10):
    for y_start, y_end in [(9.20, 10.08), (10.12, 11.00)]:
        z_ranges = [(z_plinth, 0.36), (0.38, 0.63), (0.65, z_counter - thick_counter - 0.02)]
        for z0, z1 in z_ranges:
            add_box(f"Drawer_Peninsula_{y_start:.2f}_{z0:.2f}", col, (5.095, y_start, z0), (5.115, y_end, z1), mat_black)
            add_box(f"Gola_Peninsula_{y_start:.2f}_{z1:.2f}", col, (5.115, y_start, z1), (5.150, y_end, z1 + 0.02), mat_black)

    # ==========================================
    # 4. TALL APPLIANCE TOWER (OVEN & MICROWAVE)
    # ==========================================
    # Position: X in [3.00, 3.60], Y in [8.96, 9.56], Z in [z_floor, z_tall_top]
    add_box("Tower_Carcass_Left", col, (3.00, 8.96, z_floor), (3.60, 8.98, z_tall_top), mat_black)
    add_box("Tower_Carcass_Right", col, (3.00, 9.54, z_floor), (3.60, 9.56, z_tall_top), mat_black)
    add_box("Tower_Top", col, (3.00, 8.96, z_tall_top - 0.02), (3.60, 9.56, z_tall_top), mat_black)
    
    # Lower drawer under oven: Z in [z_plinth, 0.74]
    add_box("Tower_Lower_Door", col, (3.585, 8.98, z_plinth), (3.605, 9.54, 0.74), mat_black)
    
    # Built-in Oven: Z in [0.75, 1.34]
    add_box("Oven_Glass_Front", col, (3.590, 8.98, 0.75), (3.610, 9.54, 1.34), mat_glass)
    add_box("Oven_Inner_Window", col, (3.605, 9.06, 0.83), (3.612, 9.46, 1.25), mat_black)
    add_box("Oven_Handle", col, (3.640, 9.04, 1.28), (3.655, 9.48, 1.30), mat_steel)
    add_box("Oven_Handle_Post_L", col, (3.610, 9.05, 1.28), (3.640, 9.07, 1.30), mat_steel)
    add_box("Oven_Handle_Post_R", col, (3.610, 9.45, 1.28), (3.640, 9.47, 1.30), mat_steel)
    add_box("Oven_Control_Panel", col, (3.600, 8.98, 1.27), (3.612, 9.54, 1.34), mat_steel)

    # Built-in Microwave: Z in [1.36, 1.76]
    add_box("Microwave_Glass_Front", col, (3.590, 8.98, 1.36), (3.610, 9.54, 1.76), mat_glass)
    add_box("Microwave_Trim_Top", col, (3.600, 8.98, 1.72), (3.612, 9.54, 1.76), mat_steel)
    add_box("Microwave_Trim_Bottom", col, (3.600, 8.98, 1.36), (3.612, 9.54, 1.39), mat_steel)

    # Upper cabinet above microwave: Z in [1.77, z_tall_top]
    add_box("Tower_Upper_Door", col, (3.585, 8.98, 1.77), (3.605, 9.54, z_tall_top - 0.02), mat_black)

    # ==========================================
    # 5. AMERICAN SIDE-BY-SIDE REFRIGERATOR
    # ==========================================
    # Position: X in [3.00, 3.68], Y in [8.05, 8.96], Z in [z_floor, 1.78]
    add_box("Fridge_Body", col, (3.00, 8.05, z_floor), (3.65, 8.96, 1.78), mat_black)
    
    # Left Door (Freezer with dispenser): Y in [8.05, 8.42]
    add_box("Fridge_Door_L", col, (3.65, 8.05, z_floor + 0.02), (3.68, 8.42, 1.77), mat_black)
    
    # Right Door (Fridge): Y in [8.44, 8.96]
    add_box("Fridge_Door_R", col, (3.65, 8.44, z_floor + 0.02), (3.68, 8.96, 1.77), mat_black)
    
    # Water/Ice Dispenser in left door: recessed niche
    add_box("Fridge_Dispenser_Cavity", col, (3.64, 8.13, 1.08), (3.681, 8.35, 1.36), mat_black)
    add_box("Fridge_Dispenser_Back", col, (3.642, 8.14, 1.09), (3.655, 8.34, 1.35), mat_glass)
    add_box("Fridge_Dispenser_Paddle", col, (3.655, 8.21, 1.15), (3.665, 8.27, 1.25), mat_steel)
    add_box("Fridge_Display_Strip", col, (3.679, 8.14, 1.32), (3.682, 8.34, 1.35), mat_disp_led)

    # Top Storage Box above Fridge: Z in [1.78, z_tall_top]
    add_box("Fridge_Top_Box", col, (3.00, 8.05, 1.78), (3.65, 8.96, z_tall_top), mat_black)

    # ==========================================
    # 6. UPPER WALL CABINETS (WEST WALL)
    # ==========================================
    # Depth 34cm: X in [3.00, 3.34], Y in [9.56, 11.015], Z in [1.45, z_tall_top]
    # Carcass
    add_box("Upper_Carcass", col, (3.00, 9.56, 1.45), (3.32, 11.015, z_tall_top), mat_black)
    
    # Lower Tier: Warm Oak Doors, Z in [1.45, 1.95] (height 50cm)
    door_ys = [(9.56, 10.04), (10.05, 10.53), (10.54, 11.015)]
    for y0, y1 in door_ys:
        add_box(f"Upper_Oak_Door_{y0:.2f}", col, (3.32, y0, 1.45), (3.34, y1, 1.95), mat_oak, uv_scale=1.5)

    # Upper Tier: Matte Black Soffit Box, Z in [1.95, z_tall_top] (height 20cm)
    for y0, y1 in door_ys:
        add_box(f"Upper_Black_Box_{y0:.2f}", col, (3.32, y0, 1.95), (3.34, y1, z_tall_top), mat_black)

    # Extractor / Hood undermount above cooktop
    add_box("Range_Hood_Mesh", col, (3.05, 10.05, 1.44), (3.32, 10.53, 1.45), mat_steel)

    # LED under-cabinet strip light: warm ambient kitchen glow
    add_box("Kitchen_Under_Cabinet_LED", col, (3.30, 9.56, 1.44), (3.32, 11.015, 1.445), mat_led)

    # ==========================================
    # 7. INDUCTION COOKTOP
    # ==========================================
    # West counter: X in [3.10, 3.58], Y in [10.00, 10.60], Z = z_counter
    add_box("Induction_Glass", col, (3.10, 10.00, z_counter), (3.58, 10.60, z_counter + 0.004), mat_glass)
    # 4 cooking zones
    for cx, cy in [(3.22, 10.15), (3.46, 10.15), (3.22, 10.45), (3.46, 10.45)]:
        add_cylinder(f"Induction_Zone_{cx:.2f}_{cy:.2f}", col, mathutils.Vector((cx, cy, z_counter + 0.0045)), 0.09, 0.001, mat_black, axis='Z', segments=20)
    add_box("Induction_Controls", col, (3.53, 10.15, z_counter + 0.0045), (3.56, 10.45, z_counter + 0.005), mat_steel)

    # ==========================================
    # 8. SINK & GOOSENECK FAUCET
    # ==========================================
    # North counter: X in [4.15, 4.85], Y in [11.10, 11.55]
    add_box("Sink_Rim", col, (4.15, 11.10, z_counter - 0.002), (4.85, 11.55, z_counter + 0.003), mat_black)
    add_box("Sink_Basin", col, (4.18, 11.13, z_counter - 0.20), (4.65, 11.52, z_counter), mat_black)
    add_cylinder("Sink_Drain", col, mathutils.Vector((4.415, 11.325, z_counter - 0.198)), 0.045, 0.002, mat_steel, axis='Z')

    # Modern high-arc black gooseneck faucet
    faucet_pos = mathutils.Vector((4.415, 11.52, z_counter))
    add_cylinder("Faucet_Base", col, faucet_pos + mathutils.Vector((0, 0, 0.04)), 0.022, 0.08, mat_metal, axis='Z', segments=16)
    add_box("Faucet_Handle", col, (4.44, 11.51, z_counter + 0.04), (4.49, 11.53, z_counter + 0.09), mat_metal)
    add_cylinder("Faucet_Spout_Vert", col, faucet_pos + mathutils.Vector((0, 0, 0.20)), 0.012, 0.24, mat_metal, axis='Z', segments=16)
    add_box("Faucet_Spout_Arc", col, (4.38, 11.45, z_counter + 0.31), (4.45, 11.53, z_counter + 0.33), mat_metal)
    add_cylinder("Faucet_Nozzle", col, mathutils.Vector((4.415, 11.45, z_counter + 0.27)), 0.014, 0.06, mat_metal, axis='Z', segments=16)

    # ==========================================
    # 9. WINDOW BLINDS & SILL DECORATIONS
    # ==========================================
    # Window blinds: black horizontal slats across Window_1.03
    win_x0, win_x1 = 3.70, 5.36
    win_y = 11.835
    for z_slat in [0.90 + i*0.06 for i in range(21)]:
        add_box(f"Blind_Slat_{z_slat:.2f}", col, (win_x0, win_y, z_slat), (win_x1, win_y + 0.015, z_slat + 0.003), mat_metal)

    # Potted herbs / plants on sill
    for px in [3.80, 4.95, 5.20]:
        add_cylinder(f"Plant_Pot_{px:.2f}", col, mathutils.Vector((px, 11.75, z_counter + 0.04)), 0.045, 0.08, mat_black, axis='Z', segments=16)
        add_cylinder(f"Plant_Foliage_{px:.2f}", col, mathutils.Vector((px, 11.75, z_counter + 0.12)), 0.06, 0.10, mat_plant, axis='Z', segments=12)

    # ==========================================
    # 10. DINING TABLE (OAK TOP & BLACK METAL SPIDER LEGS)
    # ==========================================
    t_cx, t_cy = 7.30, 10.20
    t_half_x, t_half_y = 0.80, 0.45
    t_z_top = 0.76
    t_thick = 0.04

    # Table Top
    add_box("Dining_Table_Top", col, (t_cx - t_half_x, t_cy - t_half_y, t_z_top - t_thick), (t_cx + t_half_x, t_cy + t_half_y, t_z_top), mat_oak, uv_scale=1.5)

    # Black Metal Spider Base
    add_box("Dining_Table_Base_Plate", col, (t_cx - 0.20, t_cy - 0.15, t_z_top - t_thick - 0.02), (t_cx + 0.20, t_cy + 0.15, t_z_top - t_thick), mat_metal)
    
    corners = [
        (t_cx - 0.65, t_cy - 0.35),
        (t_cx + 0.65, t_cy - 0.35),
        (t_cx - 0.65, t_cy + 0.35),
        (t_cx + 0.65, t_cy + 0.35),
    ]
    for i, (lx, ly) in enumerate(corners):
        leg_mesh = bpy.data.meshes.new(f"Dining_Table_Leg_{i}")
        bm_leg = bmesh.new()
        p_top = mathutils.Vector((t_cx + (lx - t_cx)*0.15, t_cy + (ly - t_cy)*0.15, t_z_top - t_thick - 0.02))
        p_bot = mathutils.Vector((lx, ly, z_floor))
        
        dir_v = (p_bot - p_top).normalized()
        up_v = mathutils.Vector((0, 0, 1))
        side_v = dir_v.cross(up_v).normalized() * 0.03
        norm_v = dir_v.cross(side_v).normalized() * 0.03
        
        v0 = bm_leg.verts.new(p_top - side_v - norm_v)
        v1 = bm_leg.verts.new(p_top + side_v - norm_v)
        v2 = bm_leg.verts.new(p_top + side_v + norm_v)
        v3 = bm_leg.verts.new(p_top - side_v + norm_v)
        v4 = bm_leg.verts.new(p_bot - side_v - norm_v)
        v5 = bm_leg.verts.new(p_bot + side_v - norm_v)
        v6 = bm_leg.verts.new(p_bot + side_v + norm_v)
        v7 = bm_leg.verts.new(p_bot - side_v + norm_v)
        
        bm_leg.faces.new([v0, v1, v2, v3])
        bm_leg.faces.new([v7, v6, v5, v4])
        bm_leg.faces.new([v0, v4, v5, v1])
        bm_leg.faces.new([v1, v5, v6, v2])
        bm_leg.faces.new([v2, v6, v7, v3])
        bm_leg.faces.new([v3, v7, v4, v0])
        bmesh.ops.recalc_face_normals(bm_leg, faces=bm_leg.faces)
        bm_leg.to_mesh(leg_mesh)
        bm_leg.free()
        
        leg_obj = bpy.data.objects.new(f"Dining_Table_Leg_{i}", leg_mesh)
        leg_obj.data.materials.append(mat_metal)
        col.objects.link(leg_obj)

    # ==========================================
    # 11. MODERN DINING CHAIRS (4 CHAIRS)
    # ==========================================
    chair_positions = [
        (t_cx - 0.40, t_cy + 0.65, math.radians(180)),
        (t_cx + 0.40, t_cy + 0.65, math.radians(180)),
        (t_cx - 0.40, t_cy - 0.65, 0.0),
        (t_cx + 0.40, t_cy - 0.65, 0.0),
    ]

    for ci, (ch_x, ch_y, ch_rot) in enumerate(chair_positions):
        ch_mesh = bpy.data.meshes.new(f"Dining_Chair_{ci}")
        bm_ch = bmesh.new()

        # Seat shell: curved ergonomic cushion
        seat_w, seat_d = 0.46, 0.44
        seat_z = 0.46
        res_seat = bmesh.ops.create_cube(bm_ch, size=1.0)
        for v in res_seat['verts']:
            v.co.x *= seat_w
            v.co.y *= seat_d
            v.co.z *= 0.04
            v.co.z += seat_z
            
        # Backrest: upright curved shell
        res_back = bmesh.ops.create_cube(bm_ch, size=1.0)
        for v in res_back['verts']:
            v.co.x *= (seat_w * 0.95)
            v.co.y *= 0.035
            v.co.z *= 0.38
            v.co.y -= (seat_d * 0.45)
            v.co.z += (seat_z + 0.21)

        # 4 angled dowel legs
        leg_r = 0.015
        leg_offsets = [
            (-seat_w*0.38, -seat_d*0.38),
            ( seat_w*0.38, -seat_d*0.38),
            (-seat_w*0.38,  seat_d*0.38),
            ( seat_w*0.38,  seat_d*0.38),
        ]
        for lox, loy in leg_offsets:
            p_top = mathutils.Vector((lox*0.8, loy*0.8, seat_z - 0.02))
            p_bot = mathutils.Vector((lox*1.15, loy*1.15, z_floor))
            dir_l = (p_bot - p_top)
            rot_l = dir_l.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            bmesh.ops.create_cone(
                bm_ch,
                cap_ends=True,
                segments=12,
                radius1=leg_r,
                radius2=leg_r*0.7,
                depth=dir_l.length,
                matrix=mathutils.Matrix.Translation((p_top + p_bot)*0.5) @ rot_l
            )

        mat_rot = mathutils.Matrix.Rotation(ch_rot, 4, 'Z')
        mat_trans = mathutils.Matrix.Translation((ch_x, ch_y, 0))
        bmesh.ops.transform(bm_ch, matrix=mat_trans @ mat_rot, verts=bm_ch.verts)
        bmesh.ops.recalc_face_normals(bm_ch, faces=bm_ch.faces)
        
        bm_ch.to_mesh(ch_mesh)
        bm_ch.free()
        
        ch_obj = bpy.data.objects.new(f"Dining_Chair_{ci}", ch_mesh)
        ch_obj.data.materials.append(mat_black)
        col.objects.link(ch_obj)

    # ==========================================
    # 12. DESIGNER PENDANT LIGHT
    # ==========================================
    # Over dining table: X = 7.30, Y = 10.20
    # Horizontal black bar: Length 1.10m, thickness 2.5cm, Z = 1.95m
    add_cylinder("Pendant_Horizontal_Bar", col, mathutils.Vector((t_cx, t_cy, 1.95)), 0.013, 1.10, mat_metal, axis='X', segments=20)
    
    # 2 vertical suspension wires to ceiling (Z = 2.50)
    for wx in [t_cx - 0.35, t_cx + 0.35]:
        add_cylinder(f"Pendant_Wire_{wx:.2f}", col, mathutils.Vector((wx, t_cy, (1.95 + 2.50)/2.0)), 0.003, 2.50 - 1.95, mat_metal, axis='Z', segments=8)

    # 2 vertical brass/black cylindrical light tubes (length 35cm, diameter 4cm)
    for lx in [t_cx - 0.28, t_cx + 0.28]:
        add_cylinder(f"Pendant_Tube_{lx:.2f}", col, mathutils.Vector((lx, t_cy, 1.85)), 0.020, 0.30, mat_brass, axis='Z', segments=20)
        add_cylinder(f"Pendant_LED_{lx:.2f}", col, mathutils.Vector((lx, t_cy, 1.69)), 0.018, 0.02, mat_led, axis='Z', segments=16)

    # 2 interlocking decorative rings matching photo:
    # Ring 1: diameter 40cm (radius 0.20m), vertical in YZ plane
    # Ring 2: diameter 32cm (radius 0.16m), slightly angled
    for rx, r_rad, tube_r in [(t_cx - 0.10, 0.20, 0.008), (t_cx + 0.10, 0.16, 0.008)]:
        ring_mesh = bpy.data.meshes.new(f"Pendant_Ring_{rx:.2f}")
        bm_ring = bmesh.new()
        segs = 36
        pts = []
        for s in range(segs):
            ang = 2.0 * math.pi * s / segs
            pts.append(mathutils.Vector((rx, t_cy + r_rad * math.cos(ang), 1.95 + r_rad * math.sin(ang))))
        for s in range(segs):
            p1 = pts[s]
            p2 = pts[(s + 1) % segs]
            dir_seg = (p2 - p1)
            rot_s = dir_seg.to_track_quat('Z', 'Y').to_matrix().to_4x4()
            bmesh.ops.create_cone(
                bm_ring,
                cap_ends=True,
                segments=10,
                radius1=tube_r,
                radius2=tube_r,
                depth=dir_seg.length,
                matrix=mathutils.Matrix.Translation((p1 + p2)*0.5) @ rot_s
            )
        bm_ring.to_mesh(ring_mesh)
        bm_ring.free()
        ring_obj = bpy.data.objects.new(f"Pendant_Ring_{rx:.2f}", ring_mesh)
        ring_obj.data.materials.append(mat_metal)
        col.objects.link(ring_obj)

    # Dedicated Spot light illuminating the table warmly
    lamp_data = bpy.data.lights.new(name="Light_Dining_Table_Spot", type='SPOT')
    lamp_data.energy = 30.0
    lamp_data.spot_size = math.radians(75)
    lamp_data.spot_blend = 0.35
    lamp_data.color = (1.0, 0.94, 0.82)
    lamp_obj = bpy.data.objects.new("Light_Dining_Table_Spot", lamp_data)
    lamp_obj.location = (t_cx, t_cy, 1.68)
    col.objects.link(lamp_obj)

    # ==========================================
    # 13. FIREPLACE STOVE (KRBOVÁ KAMNA)
    # ==========================================
    stove_blend = r'C:\Users\Vaso\blenderkit_data\models\fire-stove-with-_58411a9a-b876-4488-9b59-50f1556694ba\fire-stove-with-chimney_2K_c7cf79b3-4d1f-4c70-94d1-6ae5efc8d137.blend'
    if os.path.exists(stove_blend):
        with bpy.data.libraries.load(stove_blend) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        stove_root = None
        for obj in data_to.objects:
            if obj.name == 'Fire stove with chimney':
                stove_root = obj
                break
        
        if stove_root:
            col.objects.link(stove_root)
            for child in stove_root.children:
                col.objects.link(child)
            
            # Position at X = 3.35, Y = 7.45
            stove_root.location = (3.35, 7.45, z_floor + 0.467)
            stove_root.rotation_euler = (0, 0, math.radians(135))
            print("Positioned Fire stove with chimney at (3.35, 7.45)")
    else:
        add_cylinder("Stove_Body", col, mathutils.Vector((3.35, 7.45, z_floor + 0.50)), 0.24, 1.00, mat_black, axis='Z', segments=24)
        add_cylinder("Stove_Flue_Pipe", col, mathutils.Vector((3.35, 7.45, z_floor + 1.75)), 0.08, 1.50, mat_black, axis='Z', segments=20)
        add_box("Stove_Glass_Door", col, (3.36, 7.30, z_floor + 0.35), (3.59, 7.60, z_floor + 0.75), mat_glass)

    print("Kitchen build v2 complete!")
    if save_file:
        bpy.ops.wm.save_mainfile()
        print("Mainfile 'dum_pudorys.blend' saved with kitchen furniture.")

if __name__ == '__main__':
    build_kitchen(save_file=True)
