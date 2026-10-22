import bpy
import bmesh
from mathutils import Vector
import os
import shutil

def apply_kitchen_and_lighting_adjustments():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> 1. Moving induction hob into the first base corpus (Y: 9.58 - 10.28)...")
    # Shift along Y by -0.370m to center hob at Y = 9.930m
    shift_hob_y = -0.370
    hob_objs = [o for o in bpy.data.objects if o.name.startswith("Induction_") or o.name == "Range_Hood_Mesh"]
    for o in hob_objs:
        if o.type == 'MESH':
            # Shift mesh vertices or object location
            # If location is (0,0,0), shift vertices
            if o.location.length < 0.001:
                bm = bmesh.new()
                bm.from_mesh(o.data)
                for v in bm.verts:
                    v.co.y += shift_hob_y
                bm.to_mesh(o.data)
                o.data.update()
                bm.free()
            else:
                o.location.y += shift_hob_y
            print(f"  Shifted {o.name} by dy={shift_hob_y:.3f}")

    print(">>> 2. Moving kitchen sink and faucet into the corner of the corpus (X: 3.65 - 4.21)...")
    shift_sink_x = -0.090
    sink_objs = [o for o in bpy.data.objects if o.name.startswith(("Sink_", "Faucet_"))]
    for o in sink_objs:
        if o.type == 'MESH':
            if o.location.length < 0.001:
                bm = bmesh.new()
                bm.from_mesh(o.data)
                for v in bm.verts:
                    v.co.x += shift_sink_x
                bm.to_mesh(o.data)
                o.data.update()
                bm.free()
            else:
                o.location.x += shift_sink_x
    print(f"  Shifted {len(sink_objs)} sink and faucet objects by dx={shift_sink_x:.3f}")

    print(">>> 3. Adjusting countertop meshes to match new sink corner position...")
    # Countertop_North_Left: X: [3.620, 3.650]
    cn_left = bpy.data.objects.get("Countertop_North_Left")
    if cn_left:
        bm = bmesh.new()
        bm.from_mesh(cn_left.data)
        for v in bm.verts:
            if v.co.x > 3.65:
                v.co.x = 3.65
        bm.to_mesh(cn_left.data)
        cn_left.data.update()
        bm.free()
        print("  Adjusted Countertop_North_Left")

    # Countertop_North_Back: shift X by shift_sink_x
    cn_back = bpy.data.objects.get("Countertop_North_Back")
    if cn_back:
        bm = bmesh.new()
        bm.from_mesh(cn_back.data)
        for v in bm.verts:
            v.co.x += shift_sink_x
        bm.to_mesh(cn_back.data)
        cn_back.data.update()
        bm.free()
        print("  Adjusted Countertop_North_Back")

    # Countertop_North_Front: shift X by shift_sink_x
    cn_front = bpy.data.objects.get("Countertop_North_Front")
    if cn_front:
        bm = bmesh.new()
        bm.from_mesh(cn_front.data)
        for v in bm.verts:
            v.co.x += shift_sink_x
        bm.to_mesh(cn_front.data)
        cn_front.data.update()
        bm.free()
        print("  Adjusted Countertop_North_Front")

    # Countertop_North_Right: extend left edge from 4.300 to 4.210
    cn_right = bpy.data.objects.get("Countertop_North_Right")
    if cn_right:
        bm = bmesh.new()
        bm.from_mesh(cn_right.data)
        for v in bm.verts:
            if v.co.x < 4.25:
                v.co.x = 4.210
        bm.to_mesh(cn_right.data)
        cn_right.data.update()
        bm.free()
        print("  Adjusted Countertop_North_Right")

    print(">>> 4. Fine-tuning Sun and World for high contrast blind shadows on bed...")
    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.data.energy = 5.8
        sun.data.color = (1.0, 0.98, 0.95)
        sun.data.use_shadow = True

    world = scene.world
    if world and world.node_tree:
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs["Color"].default_value = (0.82, 0.90, 1.0, 1.0)
            bg.inputs["Strength"].default_value = 0.85

    scene.cycles.use_fast_gi = True
    scene.cycles.fast_gi_method = 'REPLACE'
    scene.cycles.ao_bounces = 2

    # Ensure camera is Isometric_Camera and save file
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend successfully updated and saved!")

    # Render closeups
    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 48
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    # 1. Close-up of kitchen sink and cooktop from Camera_Drez_Corner
    drez_cam = bpy.data.objects.get("Camera_Drez_Corner")
    if drez_cam:
        scene.camera = drez_cam
        drez_out = os.path.join(artifact_dir, "render_kitchen_sink_and_hob.png")
        scene.render.filepath = drez_out
        print(f">>> Rendering kitchen closeup to {drez_out}...")
        bpy.ops.render.render(write_still=True)

    # 2. Re-render master overview floorplan
    if iso_cam:
        scene.camera = iso_cam
        master_out = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_overview.png"
        scene.render.filepath = master_out
        print(f">>> Rendering master overview floorplan...")
        bpy.ops.render.render(write_still=True)
        shutil.copy2(master_out, os.path.join(artifact_dir, "dum_pudorys_overview_updated.png"))

        # Pure daylight view (interior lights OFF)
        orig_nrgs = {}
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT' and obj.name != 'Sun_Fill':
                orig_nrgs[obj.name] = obj.data.energy
                obj.data.energy = 0.0

        daylight_out = os.path.join(artifact_dir, "dum_pudorys_daylight_final.png")
        scene.render.filepath = daylight_out
        print(f">>> Rendering pure daylight floorplan...")
        bpy.ops.render.render(write_still=True)

        # Restore light energies
        for name, nrg in orig_nrgs.items():
            o = bpy.data.objects.get(name)
            if o and 'tv' not in o.name.lower():
                o.data.energy = nrg

    # Save final blend file
    if iso_cam:
        scene.camera = iso_cam
    bpy.ops.wm.save_mainfile()
    print(">>> All updates and renders completed successfully!")

if __name__ == '__main__':
    apply_kitchen_and_lighting_adjustments()
