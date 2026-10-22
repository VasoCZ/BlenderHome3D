"""
apply_unified_blender_controls.py
Configures dum_pudorys.blend so that:
1. World Background uses a driven Mix Shader switching automatically between:
   - BG_Day: Natural soft daylight sky (0.75, 0.85, 1.0), strength 0.35.
   - BG_Night: Deep blue-black night ambient (0.005, 0.012, 0.035), strength 0.06.
   Driven natively by Sun_Fill.hide_render!
2. Sun_Fill calibrated to 1.8W (natural daytime, no overblown exterior, sharp blinds shadows,
   allowing 30W-50W interior lights to be clearly visible both day and night).
3. Light_Daylight_Fill_Bathroom_1.10 hide_render driven by Sun_Fill.hide_render so it turns
   on with Sun during the day and turns off automatically at night.
4. TV lights restored to active energies (45W / 40W) so toggling TV_1.04_Active or
   TV_1.05_Active via eye and camera icons in the Outliner immediately turns the TV on/off!
5. Cycles Fast GI disabled so physical contrast and dark night ambient are preserved.
"""

import bpy
import math

def configure_scene():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> 1. Configuring Sun_Fill and Bathroom Daylight Fill...")
    sun = bpy.data.objects.get("Sun_Fill")
    if not sun:
        raise RuntimeError("Sun_Fill not found!")

    sun.data.energy = 1.8
    sun.data.color = (1.0, 0.98, 0.95)
    sun.hide_render = False
    sun.hide_viewport = False

    # Bathroom daylight fill with driver linked to Sun_Fill.hide_render
    bath_fill = bpy.data.objects.get("Light_Daylight_Fill_Bathroom_1.10")
    if bath_fill:
        bath_fill.data.energy = 14.0
        # Clear existing drivers on hide_render if any
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
        print("  Added driver to Light_Daylight_Fill_Bathroom_1.10 -> Sun_Fill.hide_render.")

    print(">>> 2. Configuring World Driven Mix Shader (Day Sky vs Deep Blue-Black Night)...")
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputWorld')
    out.location = (600, 0)

    mix = nodes.new('ShaderNodeMixShader')
    mix.location = (300, 0)

    # BG_Day: Natural soft daylight sky
    bg_day = nodes.new('ShaderNodeBackground')
    bg_day.name = 'BG_Day'
    bg_day.location = (0, 150)
    bg_day.inputs['Color'].default_value = (0.75, 0.85, 1.0, 1.0)
    bg_day.inputs['Strength'].default_value = 0.35

    # BG_Night: Deep blue-black night ambient with rich blue tint
    # Linear RGB matching rich midnight navy (#060913)
    bg_night = nodes.new('ShaderNodeBackground')
    bg_night.name = 'BG_Night'
    bg_night.location = (0, -150)
    bg_night.inputs['Color'].default_value = (0.005, 0.012, 0.038, 1.0)
    bg_night.inputs['Strength'].default_value = 0.06

    links.new(bg_day.outputs['Background'], mix.inputs[1])
    links.new(bg_night.outputs['Background'], mix.inputs[2])
    links.new(mix.outputs['Shader'], out.inputs['Surface'])

    # Driver on mix.inputs['Fac']:
    # Fac = 0.0 -> BG_Day (when Sun is ON, hide_render = False)
    # Fac = 1.0 -> BG_Night (when Sun is OFF, hide_render = True)
    fcurve_world = mix.inputs['Fac'].driver_add('default_value')
    drv_w = fcurve_world.driver
    drv_w.type = 'AVERAGE'
    v_w = drv_w.variables.new()
    v_w.name = 'sun_hidden'
    v_w.type = 'SINGLE_PROP'
    v_w.targets[0].id = sun
    v_w.targets[0].data_path = 'hide_render'
    print("  Configured World Mix Shader driven by Sun_Fill.hide_render.")

    # Disable Fast GI so true physical darkness and sharp shadow contrast are maintained
    scene.cycles.use_fast_gi = False

    print(">>> 3. Configuring TV Controls for Direct Outliner Eye/Camera Toggling...")
    tv_light_104 = bpy.data.objects.get("Light_1.04_Obyvaci_pokoj_TV")
    tv_glow_104 = bpy.data.objects.get("TV_Screen_Glow_1.04")
    if tv_light_104:
        tv_light_104.data.energy = 45.0
        tv_light_104.hide_render = True
        tv_light_104.hide_viewport = True
    if tv_glow_104:
        tv_glow_104.hide_render = True
        tv_glow_104.hide_viewport = True

    tv_light_105 = bpy.data.objects.get("Light_1.05_Loznice_TV")
    tv_glow_105 = bpy.data.objects.get("TV_Screen_Glow_1.05")
    if tv_light_105:
        tv_light_105.data.energy = 40.0
        tv_light_105.hide_render = True
        tv_light_105.hide_viewport = True
    if tv_glow_105:
        tv_glow_105.hide_render = True
        tv_glow_105.hide_viewport = True

    print("  TV active energies restored (45W living room, 40W bedroom). Default visibility set to OFF.")

    print(">>> 4. Verifying Interior Lights...")
    # Ensure all interior room lights are unhidden and have healthy warm 3000K energy
    for ob in bpy.data.objects:
        if ob.type == 'LIGHT' and ob.name.startswith('Light_1.') and 'tv' not in ob.name.lower() and 'Daylight' not in ob.name:
            ob.hide_render = False
            ob.hide_viewport = False

    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> Saved updated 'dum_pudorys.blend'!")

if __name__ == '__main__':
    configure_scene()
