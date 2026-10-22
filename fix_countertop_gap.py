import bpy
import bmesh
import shutil
import os

def fix_gap_and_render():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> Fixing Countertop_North_Right gap...")
    cn_right = bpy.data.objects.get("Countertop_North_Right")
    if cn_right:
        bm = bmesh.new()
        bm.from_mesh(cn_right.data)
        count = 0
        for v in bm.verts:
            if v.co.x < 4.35:
                v.co.x = 4.210
                count += 1
        bm.to_mesh(cn_right.data)
        cn_right.data.update()
        bm.free()
        print(f"  Updated {count} vertices of Countertop_North_Right to X=4.210")

    # Ensure camera is Camera_Drez_Corner for the closeup verification render
    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 48
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    drez_cam = bpy.data.objects.get("Camera_Drez_Corner")
    if drez_cam:
        scene.camera = drez_cam
        drez_out = os.path.join(artifact_dir, "render_kitchen_sink_and_hob.png")
        scene.render.filepath = drez_out
        print(">>> Re-rendering kitchen closeup...")
        bpy.ops.render.render(write_still=True)

    # Now set back to Isometric_Camera for master floorplan
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam
        master_out = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys_overview.png"
        scene.render.filepath = master_out
        print(">>> Re-rendering master overview floorplan...")
        bpy.ops.render.render(write_still=True)
        shutil.copy2(master_out, os.path.join(artifact_dir, "dum_pudorys_overview_fixed.png"))

        # Re-render pure daylight floorplan
        orig_nrgs = {}
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT' and obj.name != 'Sun_Fill':
                orig_nrgs[obj.name] = obj.data.energy
                obj.data.energy = 0.0

        daylight_out = os.path.join(artifact_dir, "dum_pudorys_daylight_final.png")
        scene.render.filepath = daylight_out
        print(">>> Re-rendering pure daylight floorplan...")
        bpy.ops.render.render(write_still=True)

        for name, nrg in orig_nrgs.items():
            o = bpy.data.objects.get(name)
            if o and 'tv' not in o.name.lower():
                o.data.energy = nrg

    # Save final blend file
    if iso_cam:
        scene.camera = iso_cam
    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend cleanly finalized and saved!")

if __name__ == '__main__':
    fix_gap_and_render()
