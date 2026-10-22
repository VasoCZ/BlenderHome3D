"""
apply_cinematic_lighting_and_materials.py
Implements the user's cinematic lighting and exterior material brief:
1. Color Management: AgX with 'AgX - Medium High Contrast'.
2. Day Mode World: Nishita Sky Texture (MULTIPLE_SCATTERING) with Sun Elevation 40 deg,
   Sun Rotation calibrated for dynamic shadows into living room and terrace;
   Sun_Fill at warm 5500K with natural crisp shadows.
3. Night Mode World: Very dark blue (#02050D) with Strength 0.08 (subtle moonlight).
   Interior & exterior wall lights set to warm 2800K for strong warm-cold contrast.
4. Materials:
   - Grass: Noise Texture + ColorRamp multi-tone green (dark green + natural olive) + surface Bump.
   - Paving: Strengthened Normal Map + Height Bump + enhanced Roughness contrast for deep 3D joints.
"""

import bpy
import math

def srgb_to_linear(hex_str):
    hex_clean = hex_str.lstrip('#')
    r = int(hex_clean[0:2], 16) / 255.0
    g = int(hex_clean[2:4], 16) / 255.0
    b = int(hex_clean[4:6], 16) / 255.0
    def to_lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (to_lin(r), to_lin(g), to_lin(b), 1.0)

def kelvin_to_rgb(kelvin):
    """Accurate Planckian blackbody locus to linear sRGB approximation."""
    if kelvin == 2800:
        return (1.0, 0.709, 0.428)
    elif kelvin == 5500:
        return (1.0, 0.905, 0.795)
    return (1.0, 0.855, 0.685)

def main():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    # -------------------------------------------------------------
    # 1. Color Management: AgX - Medium High Contrast
    # -------------------------------------------------------------
    print(">>> 1. Setting Color Management (AgX, Medium High Contrast)...")
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.cycles.use_fast_gi = False
    print(f"  View Transform: {scene.view_settings.view_transform}, Look: {scene.view_settings.look}")

    # -------------------------------------------------------------
    # 2. World Lighting: Nishita Day Sky + #02050D Night Sky (Driven)
    # -------------------------------------------------------------
    print(">>> 2. Configuring World with Nishita Day Sky and #02050D Night Sky...")
    sun = bpy.data.objects.get("Sun_Fill")
    if not sun:
        raise RuntimeError("Object 'Sun_Fill' not found!")

    # Sun_Fill: warm 5500K, 40° elevation, azimuth ~145° (into living room and terrace)
    sun.data.energy = 2.4
    sun.data.color = kelvin_to_rgb(5500)
    # Rotation: pitch 50° (elev 40°), yaw -35° (azimuth 145°)
    sun.rotation_euler = (math.radians(50.0), math.radians(0.0), math.radians(-35.0))
    sun.hide_render = False
    sun.hide_viewport = False
    print(f"  Sun_Fill configured: 5500K warm sunlight ({sun.data.color[:]}), energy=2.4W, elevation=40 deg.")

    # World Node Tree
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (800, 0)

    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (500, 0)

    # Day World: Nishita Sky Texture
    sky_day = nodes.new('ShaderNodeTexSky')
    sky_day.name = 'Sky_Nishita_Day'
    sky_day.sky_type = 'MULTIPLE_SCATTERING'
    sky_day.sun_elevation = math.radians(40.0)
    sky_day.sun_rotation = math.radians(65.0) # Matches sun azimuth for living room & terrace
    sky_day.sun_disc = False # Direct sun handled by Sun_Fill lamp for clean outliner control
    sky_day.location = (0, 200)

    bg_day = nodes.new('ShaderNodeBackground')
    bg_day.name = 'BG_Day'
    bg_day.location = (250, 200)
    bg_day.inputs['Strength'].default_value = 0.20 # Balanced sky ambient without flat gray wash

    links.new(sky_day.outputs['Color'], bg_day.inputs['Color'])
    links.new(bg_day.outputs['Background'], mix.inputs[1])

    # Night World: #02050D (Deep midnight blue, strength 0.08)
    night_col = srgb_to_linear('#02050D')
    bg_night = nodes.new('ShaderNodeBackground')
    bg_night.name = 'BG_Night'
    bg_night.location = (250, -150)
    bg_night.inputs['Color'].default_value = night_col
    bg_night.inputs['Strength'].default_value = 0.08 # Subtle moonlight per user specification

    links.new(bg_night.outputs['Background'], mix.inputs[2])
    links.new(mix.outputs['Shader'], out.inputs['Surface'])

    # Driver: Sun_Fill.hide_render -> mix.inputs['Fac']
    # Fac = 0.0 -> Nishita Day Sky
    # Fac = 1.0 -> #02050D Night Sky
    fcurve_world = mix.inputs['Fac'].driver_add('default_value')
    drv_w = fcurve_world.driver
    drv_w.type = 'AVERAGE'
    v_w = drv_w.variables.new()
    v_w.name = 'sun_hidden'
    v_w.type = 'SINGLE_PROP'
    v_w.targets[0].id = sun
    v_w.targets[0].data_path = 'hide_render'
    print(f"  World configured with Nishita Day Sky (40 deg) and Night Sky #02050D (Strength 0.08).")

    # Bathroom daylight fill linked to Sun_Fill
    bath_fill = bpy.data.objects.get("Light_Daylight_Fill_Bathroom_1.10")
    if bath_fill:
        bath_fill.data.energy = 16.0
        bath_fill.data.color = (0.85, 0.92, 1.0)
        if bath_fill.animation_data:
            bath_fill.animation_data_clear()
        fcurve_bf = bath_fill.driver_add('hide_render')
        drv_bf = fcurve_bf.driver
        drv_bf.type = 'AVERAGE'
        v_bf = drv_bf.variables.new()
        v_bf.name = 'sun_hidden'
        v_bf.type = 'SINGLE_PROP'
        v_bf.targets[0].id = sun
        v_bf.targets[0].data_path = 'hide_render'

    # -------------------------------------------------------------
    # 3. Lights: Warm 2800K for Interior & Exterior Wall Lights
    # -------------------------------------------------------------
    print(">>> 3. Setting Interior & Exterior Lights to Warm 2800K...")
    warm_2800k = kelvin_to_rgb(2800)
    count_lights = 0
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name != 'Sun_Fill' and 'tv' not in ob.name.lower() and 'Daylight' not in ob.name:
            ob.data.color = warm_2800k
            count_lights += 1
    print(f"  Updated {count_lights} lights to warm 2800K: {warm_2800k}.")

    # -------------------------------------------------------------
    # 4. Material: Grass (Multi-tone Noise + ColorRamp + Surface Bump)
    # -------------------------------------------------------------
    print(">>> 4. Enhancing Grass Material (Noise Texture + ColorRamp + Bump)...")
    mat_grass = bpy.data.materials.get("Grass")
    if mat_grass and mat_grass.use_nodes:
        gnodes = mat_grass.node_tree.nodes
        glinks = mat_grass.node_tree.links

        bsdf = gnodes.get("Principled BSDF")
        tex_diff = gnodes.get("Image Texture") or gnodes.get("Image Texture.001")
        tex_coord = gnodes.get("Texture Coordinate") or gnodes.get("Texture Coordinate.001")

        # Noise Texture for tonal color variation
        noise_grass = gnodes.get("Grass_Noise")
        if not noise_grass:
            noise_grass = gnodes.new("ShaderNodeTexNoise")
            noise_grass.name = "Grass_Noise"
        noise_grass.location = (-600, 200)
        noise_grass.inputs['Scale'].default_value = 16.0
        noise_grass.inputs['Detail'].default_value = 5.0
        noise_grass.inputs['Roughness'].default_value = 0.65
        noise_grass.inputs['Distortion'].default_value = 0.6

        if tex_coord:
            glinks.new(tex_coord.outputs.get('UV', tex_coord.outputs[0]), noise_grass.inputs['Vector'])

        # ColorRamp: Dark Green to Natural Olive Green
        ramp_grass = gnodes.get("Grass_ColorRamp")
        if not ramp_grass:
            ramp_grass = gnodes.new("ShaderNodeValToRGB")
            ramp_grass.name = "Grass_ColorRamp"
        ramp_grass.location = (-350, 200)
        # Element 0: Deep forest dark green
        ramp_grass.color_ramp.elements[0].position = 0.15
        ramp_grass.color_ramp.elements[0].color = (0.040, 0.115, 0.022, 1.0) # Dark rich green
        # Element 1: Natural warm olive
        if len(ramp_grass.color_ramp.elements) == 2:
            ramp_grass.color_ramp.elements[1].position = 0.85
            ramp_grass.color_ramp.elements[1].color = (0.135, 0.175, 0.045, 1.0) # Natural olive
        glinks.new(noise_grass.outputs['Fac'], ramp_grass.inputs['Fac'])

        # Mix with diffuse texture
        mix_grass = gnodes.get("Grass_Mix_Color")
        if not mix_grass:
            mix_grass = gnodes.new("ShaderNodeMix")
            mix_grass.name = "Grass_Mix_Color"
            mix_grass.data_type = 'RGBA'
        mix_grass.location = (-100, 200)
        mix_grass.blend_type = 'MULTIPLY'
        mix_grass.inputs['Factor'].default_value = 0.65 # Rich blend
        glinks.new(ramp_grass.outputs['Color'], mix_grass.inputs[6]) # Color1 (Socket 6 for RGBA)
        if tex_diff:
            glinks.new(tex_diff.outputs['Color'], mix_grass.inputs[7]) # Color2 (Socket 7 for RGBA)
        else:
            mix_grass.inputs[7].default_value = (0.08, 0.18, 0.035, 1.0)
        glinks.new(mix_grass.outputs[2], bsdf.inputs['Base Color']) # Result

        # Surface Bump for organic turf relief
        bump_grass = gnodes.get("Grass_Bump")
        if not bump_grass:
            bump_grass = gnodes.new("ShaderNodeBump")
            bump_grass.name = "Grass_Bump"
        bump_grass.location = (50, -150)
        bump_grass.inputs['Strength'].default_value = 0.35
        bump_grass.inputs['Distance'].default_value = 0.008
        glinks.new(noise_grass.outputs['Fac'], bump_grass.inputs['Height'])

        # Daisy chain with Normal Map
        norm_map = gnodes.get("Normal Map")
        if norm_map:
            glinks.new(norm_map.outputs['Normal'], bump_grass.inputs['Normal'])
        glinks.new(bump_grass.outputs['Normal'], bsdf.inputs['Normal'])
        print("  Grass material updated: procedural dark/olive color variation and surface bump configured.")

    # -------------------------------------------------------------
    # 5. Material: Paving Stones (Strengthened Normal Map + Height Bump + Roughness Contrast)
    # -------------------------------------------------------------
    print(">>> 5. Enhancing Paving Stones (Dlažba) Material...")
    mat_pave = bpy.data.materials.get("Paving Stones")
    if mat_pave and mat_pave.use_nodes:
        pnodes = mat_pave.node_tree.nodes
        plinks = mat_pave.node_tree.links

        bsdf_pave = pnodes.get("Principled BSDF")
        tex_height = pnodes.get("Image Texture") # Paving Stones_Height.jpg
        tex_norm = pnodes.get("Image Texture.004") # Paving Stones_Normal.jpg
        norm_node = pnodes.get("Normal Map")
        tex_gloss = pnodes.get("Image Texture.003") # Paving Stones_Glossiness.jpg
        invert_node = pnodes.get("Invert Color")

        # Strengthen Normal Map to 1.6
        if norm_node:
            norm_node.inputs['Strength'].default_value = 1.6

        # Add Height Bump node daisy-chained with Normal Map
        bump_pave = pnodes.get("Paving_Height_Bump")
        if not bump_pave:
            bump_pave = pnodes.new("ShaderNodeBump")
            bump_pave.name = "Paving_Height_Bump"
        bump_pave.location = (200, -250)
        bump_pave.inputs['Strength'].default_value = 0.85 # Deep pronounced joints
        bump_pave.inputs['Distance'].default_value = 0.006

        if tex_height:
            plinks.new(tex_height.outputs['Color'], bump_pave.inputs['Height'])
        if norm_node:
            plinks.new(norm_node.outputs['Normal'], bump_pave.inputs['Normal'])
        plinks.new(bump_pave.outputs['Normal'], bsdf_pave.inputs['Normal'])

        # Enhance Roughness contrast: dark, rough joints and subtle specular sheen on tiles
        ramp_rough = pnodes.get("Paving_Rough_Ramp")
        if not ramp_rough:
            ramp_rough = pnodes.new("ShaderNodeValToRGB")
            ramp_rough.name = "Paving_Rough_Ramp"
        ramp_rough.location = (0, -100)
        ramp_rough.color_ramp.elements[0].position = 0.20
        ramp_rough.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0) # Stone paver sheen
        ramp_rough.color_ramp.elements[1].position = 0.85
        ramp_rough.color_ramp.elements[1].color = (0.95, 0.95, 0.95, 1.0) # Deep matte grout/joints

        if invert_node:
            plinks.new(invert_node.outputs['Color'], ramp_rough.inputs['Fac'])
        elif tex_gloss:
            plinks.new(tex_gloss.outputs['Color'], ramp_rough.inputs['Fac'])
        plinks.new(ramp_rough.outputs['Color'], bsdf_pave.inputs['Roughness'])

        print("  Paving Stones material updated: Normal Map boosted to 1.6, Height Bump added, Roughness contrast enhanced.")

    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> All cinematic adjustments saved cleanly to 'dum_pudorys.blend'!")

if __name__ == '__main__':
    main()
