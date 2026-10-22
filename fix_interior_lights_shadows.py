import bpy
import shutil
import os

def fix_lights_and_render():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> 1. Fixing interior lights shadows and soft radius...")
    fixed_count = 0
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            l = obj.data
            # Ensure ALL lights in scene have shadow enabled
            if not l.use_shadow:
                l.use_shadow = True
                print(f"  Enabled shadows on: {obj.name}")
                fixed_count += 1
            
            # For ceiling point lights, optimize soft size and height so they stay strictly within room boundaries
            if '1.' in obj.name and l.type == 'POINT':
                l.shadow_soft_size = 0.12
                if obj.location.z >= 2.38:
                    obj.location.z = 2.36
                print(f"  Adjusted ceiling point light {obj.name}: Z={obj.location.z:.2f}, soft_size={l.shadow_soft_size:.2f}")

    print(f">>> Updated shadows on {fixed_count} lights.")

    # Ensure Isometric_Camera is active
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    # Save the updated blend file
    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend saved successfully!")

    # Render daytime overview
    print(">>> 2. Rendering master daytime floorplan dum_pudorys_overview.png...")
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 48
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    daytime_out = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_overview.png"
    scene.render.filepath = daytime_out
    bpy.ops.render.render(write_still=True)
    print(">>> Master daytime floorplan rendered!")

    # Copy to artifacts directory
    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"
    shutil.copy2(daytime_out, os.path.join(artifact_dir, "dum_pudorys_overview_fixed.png"))

    # Render night floorplan with interior lights and exterior soffits active
    print(">>> 3. Rendering night floorplan verification dum_pudorys_night_overview.png...")
    sun = bpy.data.objects.get("Sun_Fill")
    sun_orig_energy = sun.data.energy if sun else 2.0
    if sun:
        sun.data.energy = 0.0

    world = scene.world
    bg_orig_strength = 0.35
    bg_node = None
    if world and world.node_tree:
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_orig_strength = bg_node.inputs["Strength"].default_value
            # Set to slight moonlight ambient
            bg_node.inputs["Strength"].default_value = 0.04

    night_out = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_night_overview.png"
    scene.render.filepath = night_out
    bpy.ops.render.render(write_still=True)
    print(">>> Night floorplan rendered!")

    shutil.copy2(night_out, os.path.join(artifact_dir, "dum_pudorys_night_overview.png"))

    # Restore sun and world background for daytime consistency
    if sun:
        sun.data.energy = sun_orig_energy
    if bg_node:
        bg_node.inputs["Strength"].default_value = bg_orig_strength

    # Save clean state
    bpy.ops.wm.save_mainfile()
    print(">>> All renders and updates completed successfully!")

if __name__ == '__main__':
    fix_lights_and_render()
