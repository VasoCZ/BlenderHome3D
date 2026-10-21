import bpy
import math
import mathutils

def execute_pokyny():
    print("==================================================")
    print("EXECUTING POKYNY.TXT OPTIMIZATIONS")
    print("==================================================")
    
    # ----------------------------------------------------
    # 1. GEOMETRIE ZDÍ (BEVEL)
    # Width: 0.012 m, Segments: 3, Harden Normals: True
    # ----------------------------------------------------
    print("\n--- 1. Applying Bevel to Walls ---")
    wall_names = ["Exterior_Walls", "Interior_Walls"]
    for name in wall_names:
        obj = bpy.data.objects.get(name)
        if not obj:
            print(f"WARNING: Wall object {name} not found!")
            continue
        
        # Enable smooth shading on all wall polygons for harden normals
        for p in obj.data.polygons:
            p.use_smooth = True
            
        bev = obj.modifiers.get("Bevel")
        if not bev:
            bev = obj.modifiers.new("Bevel", 'BEVEL')
            
        bev.width = 0.012
        bev.segments = 3
        bev.harden_normals = True
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35.0)
        bev.miter_outer = 'MITER_ARC'
        print(f"Applied Bevel to {name}: width={bev.width}m, segments={bev.segments}, harden_normals={bev.harden_normals}")

    # ----------------------------------------------------
    # 2. MATERIÁL STĚN (OMÍTKA / PLASTER)
    # Subtle paint/plaster bump, roughness 0.7 - 0.8
    # ----------------------------------------------------
    print("\n--- 2. Setting up Plaster Material (Omítka) ---")
    
    def create_plaster_shader(mat_name, base_val=0.88, bump_str=0.18, scale=100.0):
        mat = bpy.data.materials.get(mat_name)
        if not mat:
            mat = bpy.data.materials.new(mat_name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        # Material Output
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_out.location = (600, 0)
        
        # Principled BSDF
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.location = (200, 0)
        node_bsdf.inputs['Roughness'].default_value = 0.75 # 0.7 - 0.8 per pokyny.txt
        if 'Specular IOR Level' in node_bsdf.inputs:
            node_bsdf.inputs['Specular IOR Level'].default_value = 0.5
        if 'IOR' in node_bsdf.inputs:
            node_bsdf.inputs['IOR'].default_value = 1.5
            
        # Texture Coordinates (Object mapping ensures seamless 3D distribution)
        node_tex_coord = nodes.new(type='ShaderNodeTexCoord')
        node_tex_coord.location = (-800, 0)
        
        node_mapping = nodes.new(type='ShaderNodeMapping')
        node_mapping.location = (-600, 0)
        links.new(node_tex_coord.outputs['Object'], node_mapping.inputs['Vector'])
        
        # Noise Texture for micro-plaster stipple / grain
        node_noise = nodes.new(type='ShaderNodeTexNoise')
        node_noise.location = (-400, -100)
        node_noise.inputs['Scale'].default_value = scale
        node_noise.inputs['Detail'].default_value = 6.0
        node_noise.inputs['Roughness'].default_value = 0.55
        links.new(node_mapping.outputs['Vector'], node_noise.inputs['Vector'])
        
        # Subtle off-white color variation
        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_ramp.location = (-150, 150)
        node_ramp.color_ramp.elements[0].position = 0.3
        node_ramp.color_ramp.elements[0].color = (base_val - 0.02, base_val - 0.02, base_val - 0.025, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.7
        node_ramp.color_ramp.elements[1].color = (base_val + 0.02, base_val + 0.02, base_val + 0.015, 1.0)
        links.new(node_noise.outputs['Fac'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
        
        # Bump node for soft micro-shadows
        node_bump = nodes.new(type='ShaderNodeBump')
        node_bump.location = (0, -150)
        node_bump.inputs['Strength'].default_value = bump_str
        node_bump.inputs['Distance'].default_value = 0.0015 # 1.5 mm
        links.new(node_noise.outputs['Fac'], node_bump.inputs['Height'])
        links.new(node_bump.outputs['Normal'], node_bsdf.inputs['Normal'])
        
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        print(f"Configured plaster shader for {mat_name} (base_val={base_val}, roughness=0.75, bump={bump_str})")

    # Exterior Plaster: slightly richer texture for outdoor facade
    create_plaster_shader("Mat_Exterior_Wall", base_val=0.88, bump_str=0.22, scale=90.0)
    # Interior Plaster: smooth delicate indoor paint finish
    create_plaster_shader("Mat_Interior_Wall", base_val=0.89, bump_str=0.16, scale=110.0)

    # ----------------------------------------------------
    # 3. ZMĚKČENÍ OSVĚTLENÍ (SOFT SHADOWS) & 3000 K
    # Radius / Size: 0.25 m to 0.4 m
    # Color temperature: warm white ~3000 K
    # ----------------------------------------------------
    print("\n--- 3. Softening Interior Lights & 3000 K Warm White ---")
    warm_white = (1.0, 0.855, 0.685)
    
    interior_prefixes = [
        "Light_1.01", "Light_1.02", "Light_1.03", "Light_1.04", "Light_1.05",
        "Light_1.06", "Light_1.07", "Light_1.08", "Light_1.09", "Light_1.10",
        "Light_1.11", "Light_Dining_Spot"
    ]
    
    updated_lights = []
    for obj in bpy.data.objects:
        if obj.type != 'LIGHT':
            continue
        if "TV" in obj.name or obj.data.type == 'SUN':
            continue
            
        if any(pref in obj.name for pref in interior_prefixes):
            l = obj.data
            l.color = warm_white
            if l.node_tree and "Emission" in l.node_tree.nodes:
                em = l.node_tree.nodes["Emission"]
                em.inputs['Color'].default_value = (warm_white[0], warm_white[1], warm_white[2], 1.0)
            
            # Radius / Size 0.25 - 0.4 m
            if l.type in ['POINT', 'SPOT']:
                if "1.10" in obj.name or "1.04" in obj.name:
                    new_r = 0.35
                elif "Spot" in obj.name or "Dining" in obj.name:
                    new_r = 0.28
                else:
                    new_r = 0.30
                l.shadow_soft_size = new_r
                updated_lights.append((obj.name, l.type, f"radius={new_r}m"))
            elif l.type == 'AREA':
                new_s = 0.35
                l.size = new_s
                l.size_y = new_s
                updated_lights.append((obj.name, l.type, f"size={new_s}m"))

    for name, ltype, rsize in updated_lights:
        print(f"  - {name} ({ltype}): {rsize}, color=3000K")

    # ----------------------------------------------------
    # 4. AMBIENTNÍ NOČNÍ SVĚTLO (WORLD BACKGROUND)
    # Color: #060913, Strength: 0.15
    # ----------------------------------------------------
    print("\n--- 4. Setting World Ambient Night Background ---")
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    
    bg = None
    for n in nodes:
        if n.type == 'BACKGROUND':
            bg = n
            break
    if not bg:
        bg = nodes.new(type='ShaderNodeBackground')
        
    out = None
    for n in nodes:
        if n.type == 'OUTPUT_WORLD':
            out = n
            break
    if not out:
        out = nodes.new(type='ShaderNodeOutputWorld')
        
    links.new(bg.outputs['Background'], out.inputs['Surface'])
    
    # Linear RGB for sRGB #060913
    r_lin = 0.001821
    g_lin = 0.002732
    b_lin = 0.006512
    bg.inputs['Color'].default_value = (r_lin, g_lin, b_lin, 1.0)
    bg.inputs['Strength'].default_value = 0.15
    world.color = (0x06 / 255.0, 0x09 / 255.0, 0x13 / 255.0)
    print(f"World Background set: hex=#060913, Strength=0.15")

    # ----------------------------------------------------
    # 5. SPRÁVA BAREV (COLOR MANAGEMENT)
    # View Transform: AgX, Look: Medium High Contrast
    # ----------------------------------------------------
    print("\n--- 5. Setting Color Management ---")
    scene = bpy.context.scene
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    print(f"Color Management set: View Transform={scene.view_settings.view_transform}, Look={scene.view_settings.look}")

    # Ensure active camera remains Isometric_Camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam
        print(f"Active scene camera verified: {scene.camera.name}")

    # Save to dum_pudorys.blend
    bpy.ops.wm.save_mainfile()
    print("\n>>> All optimizations applied and saved to dum_pudorys.blend successfully!")

if __name__ == '__main__':
    execute_pokyny()
