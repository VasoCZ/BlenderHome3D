import bpy
import os
import shutil
import numpy as np

def update_daylight_and_tvs():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> 1. Configuring realistic daylight environment and Cycles Fast GI...")
    # Setup daylight world background
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if not bg:
        bg = world.node_tree.nodes.new("ShaderNodeBackground")
        world.node_tree.links.new(bg.outputs["Background"], world.node_tree.nodes["World Output"].inputs["Surface"])
    
    # Daylight sky: soft natural sky blue with full ambient bounce
    bg.inputs["Color"].default_value = (0.85, 0.92, 1.0, 1.0)
    bg.inputs["Strength"].default_value = 1.30

    # Sun_Fill: direct sunlight for crisp contrast and sharp blinds stripes
    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.data.energy = 4.2
        sun.data.color = (1.0, 0.98, 0.95)
        sun.data.use_shadow = True

    # Fast GI: lifts enclosed interior spaces (corridors, bathrooms, tech room) naturally
    scene.cycles.use_fast_gi = True
    scene.cycles.fast_gi_method = 'ADD'
    scene.cycles.ao_bounces = 1

    print(">>> 2. Organizing TV hierarchy and setting default state to OFF...")
    app_col = bpy.data.collections.get("Appliances_TV_Lights")
    if not app_col:
        app_col = bpy.data.collections.new("Appliances_TV_Lights")
        scene.collection.children.link(app_col)

    # Helper function to configure a TV unit
    def setup_tv(room_id, glow_name, light_name, active_energy):
        glow = bpy.data.objects.get(glow_name)
        light = bpy.data.objects.get(light_name)
        
        # Sub-collection for each TV
        col_name = f"TV_{room_id}_Active"
        sub_col = bpy.data.collections.get(col_name)
        if not sub_col:
            sub_col = bpy.data.collections.new(col_name)
            app_col.children.link(sub_col)
        
        for o in [glow, light]:
            if o:
                # Store active energy in custom property
                if o.type == 'LIGHT':
                    o['active_energy'] = active_energy
                # Link to subcollection if not already linked
                if sub_col not in o.users_collection:
                    sub_col.objects.link(o)
                # Unlink from general scene collection if present to keep it tidy
                if scene.collection in o.users_collection:
                    scene.collection.objects.unlink(o)
                if app_col in o.users_collection and sub_col in o.users_collection:
                    app_col.objects.unlink(o)
                
                # Set DEFAULT STATE to OFF
                o.hide_render = True
                o.hide_viewport = True
                if o.type == 'LIGHT':
                    o.data.energy = 0.0

        print(f"  TV in room {room_id}: default set to OFF (active_energy={active_energy}W saved)")

    setup_tv("1.04", "TV_Screen_Glow_1.04", "Light_1.04_Obyvaci_pokoj_TV", 55.0)
    setup_tv("1.05", "TV_Screen_Glow_1.05", "Light_1.05_Loznice_TV", 45.0)

    # Save updated blend file
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend updated and saved!")

    # 3. Render pure daylight floorplan (All interior lights OFF, only Sun + Sky active)
    print(">>> 3. Rendering pure daylight floorplan (interior lights OFF, TVs OFF)...")
    # Temporarily turn off all interior lights for pure daylight render
    orig_energies = {}
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and obj.name != 'Sun_Fill':
            orig_energies[obj.name] = obj.data.energy
            obj.data.energy = 0.0

    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 48
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"
    pure_daylight_path = os.path.join(artifact_dir, "dum_pudorys_daylight_pure.png")
    scene.render.filepath = pure_daylight_path
    bpy.ops.render.render(write_still=True)
    print(">>> Pure daylight floorplan rendered!")

    # 4. Render master floorplan dum_pudorys_overview.png (with default settings, TVs OFF)
    # Restore interior lights
    for name, nrg in orig_energies.items():
        o = bpy.data.objects.get(name)
        if o and 'tv' not in o.name.lower():
            o.data.energy = nrg

    master_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_overview.png"
    scene.render.filepath = master_path
    bpy.ops.render.render(write_still=True)
    print(">>> Master overview floorplan rendered!")
    shutil.copy2(master_path, os.path.join(artifact_dir, "dum_pudorys_overview_fixed.png"))

    # 5. Create TV comparison crop (TV OFF vs TV ON)
    print(">>> 5. Rendering TV ON comparison crop...")
    # Turn ON living room TV
    tv_glow = bpy.data.objects.get("TV_Screen_Glow_1.04")
    tv_light = bpy.data.objects.get("Light_1.04_Obyvaci_pokoj_TV")
    if tv_glow:
        tv_glow.hide_render = False
    if tv_light:
        tv_light.hide_render = False
        tv_light.data.energy = 55.0

    tv_on_path = os.path.join(artifact_dir, "test_tv_on_render.png")
    scene.render.filepath = tv_on_path
    bpy.ops.render.render(write_still=True)

    # Load master (TV OFF) and TV ON to generate side-by-side TV crop
    im_off = bpy.data.images.load(master_path)
    im_on = bpy.data.images.load(tv_on_path)
    w, h = im_off.size[0], im_off.size[1]
    px_off = np.array(im_off.pixels[:]).reshape((h, w, 4))
    px_on = np.array(im_on.pixels[:]).reshape((h, w, 4))

    # Living room TV crop: y_blend: 350..600, x: 700..1050
    tv_crop_off = px_off[350:600, 700:1050]
    tv_crop_on = px_on[350:600, 700:1050]
    tv_comp = np.concatenate([tv_crop_off, tv_crop_on], axis=1)

    im_comp = bpy.data.images.new("TV_Comparison", width=tv_comp.shape[1], height=tv_comp.shape[0])
    im_comp.pixels = tv_comp.flatten().tolist()
    tv_comp_path = os.path.join(artifact_dir, "comparison_tv_off_vs_on.png")
    im_comp.filepath_raw = tv_comp_path
    im_comp.file_format = 'PNG'
    im_comp.save()
    print(">>> Saved comparison_tv_off_vs_on.png!")

    # Reset TV back to default OFF in blend file
    if tv_glow:
        tv_glow.hide_render = True
        tv_glow.hide_viewport = True
    if tv_light:
        tv_light.hide_render = True
        tv_light.hide_viewport = True
        tv_light.data.energy = 0.0

    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend cleanly finalized with TVs OFF!")

if __name__ == '__main__':
    update_daylight_and_tvs()
