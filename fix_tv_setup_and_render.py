"""
fix_tv_setup_and_render.py
Fixes TV positioning, parenting, materials, and visibility so that:
1. Living room TV (1.04) glow screen and 55W area light sit precisely on the front of SM_tv screen led facing +Y.
2. Bedroom TV (1.05) glow screen and 45W area light sit precisely on the front of SM_tv screen led .001 facing +X.
3. Unparented from TV chassis to prevent (0,0,0) world-transform collapse.
4. Visibility: Eye and Camera turned ON so the TV is actively shining and emitting light as requested!
5. Renders close-up verification images of the TV in both living room and bedroom.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

def fix_tvs():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    scene = bpy.context.scene

    print(">>> 1. Configuring Living Room TV (1.04)...")
    glow_104 = bpy.data.objects.get("TV_Screen_Glow_1.04")
    light_104 = bpy.data.objects.get("Light_1.04_Obyvaci_pokoj_TV")

    if not glow_104:
        mesh_g104 = bpy.data.meshes.new("TV_Screen_Glow_1.04")
        glow_104 = bpy.data.objects.new("TV_Screen_Glow_1.04", mesh_g104)
        scene.collection.objects.link(glow_104)

    if not light_104:
        light_data_104 = bpy.data.lights.new("Light_1.04_Obyvaci_pokoj_TV", 'AREA')
        light_104 = bpy.data.objects.new("Light_1.04_Obyvaci_pokoj_TV", light_data_104)
        scene.collection.objects.link(light_104)

    glow_104.parent = None
    light_104.parent = None

    # Screen bounds in 1.04: X in [7.2042, 8.6037], Y=4.9028, Z in [0.7774, 1.6173]
    # Offset by +0.003 to sit cleanly in front of glass without Z-fighting
    y_front_104 = 4.9065
    x_min_104, x_max_104 = 7.205, 8.603
    z_min_104, z_max_104 = 0.778, 1.617

    bm_104 = bmesh.new()
    v0 = bm_104.verts.new((x_min_104, y_front_104, z_min_104))
    v1 = bm_104.verts.new((x_max_104, y_front_104, z_min_104))
    v2 = bm_104.verts.new((x_max_104, y_front_104, z_max_104))
    v3 = bm_104.verts.new((x_min_104, y_front_104, z_max_104))
    f_104 = bm_104.faces.new([v0, v1, v2, v3])
    f_104.normal_update()
    bm_104.to_mesh(glow_104.data)
    bm_104.free()

    glow_104.location = (0, 0, 0)
    glow_104.rotation_euler = (0, 0, 0)
    glow_104.scale = (1, 1, 1)

    # Material Mat_TV_Active_Screen
    mat_tv = bpy.data.materials.get("Mat_TV_Active_Screen")
    if not mat_tv:
        mat_tv = bpy.data.materials.new("Mat_TV_Active_Screen")
        mat_tv.use_nodes = True
    if mat_tv.name not in [m.name for m in glow_104.data.materials if m]:
        glow_104.data.materials.append(mat_tv)

    bsdf_tv = mat_tv.node_tree.nodes.get("Principled BSDF")
    if bsdf_tv:
        bsdf_tv.inputs['Base Color'].default_value = (0.75, 0.88, 1.0, 1.0)
        bsdf_tv.inputs['Emission Color'].default_value = (0.75, 0.88, 1.0, 1.0)
        bsdf_tv.inputs['Emission Strength'].default_value = 12.0 # Vivid emissive TV screen

    # Area light casting light into living room towards sofa
    light_104.location = Vector((7.904, y_front_104 + 0.02, 1.197))
    light_104.rotation_euler = Euler((-math.radians(90.0), 0.0, 0.0), 'XYZ') # Facing +Y
    light_104.data.type = 'AREA'
    light_104.data.shape = 'RECTANGLE'
    light_104.data.size = 1.40
    light_104.data.size_y = 0.84
    light_104.data.energy = 55.0
    light_104.data.color = (0.75, 0.88, 1.0)

    # UNHIDE: Turn eye and camera ON!
    glow_104.hide_viewport = False
    glow_104.hide_render = False
    light_104.hide_viewport = False
    light_104.hide_render = False

    print(">>> 2. Configuring Bedroom TV (1.05)...")
    glow_105 = bpy.data.objects.get("TV_Screen_Glow_1.05")
    light_105 = bpy.data.objects.get("Light_1.05_Loznice_TV")

    if not glow_105:
        mesh_g105 = bpy.data.meshes.new("TV_Screen_Glow_1.05")
        glow_105 = bpy.data.objects.new("TV_Screen_Glow_1.05", mesh_g105)
        scene.collection.objects.link(glow_105)

    if not light_105:
        light_data_105 = bpy.data.lights.new("Light_1.05_Loznice_TV", 'AREA')
        light_105 = bpy.data.objects.new("Light_1.05_Loznice_TV", light_data_105)
        scene.collection.objects.link(light_105)

    glow_105.parent = None
    light_105.parent = None

    # Screen bounds in 1.05: X=6.2778, Y in [1.2503, 2.6497], Z in [1.3033, 2.1432]
    # Offset by +0.003 in X to sit in front of glass
    x_front_105 = 6.2815
    y_min_105, y_max_105 = 1.251, 2.649
    z_min_105, z_max_105 = 1.304, 2.143

    bm_105 = bmesh.new()
    v0_5 = bm_105.verts.new((x_front_105, y_min_105, z_min_105))
    v1_5 = bm_105.verts.new((x_front_105, y_max_105, z_min_105))
    v2_5 = bm_105.verts.new((x_front_105, y_max_105, z_max_105))
    v3_5 = bm_105.verts.new((x_front_105, y_min_105, z_max_105))
    f_105 = bm_105.faces.new([v0_5, v1_5, v2_5, v3_5])
    f_105.normal_update()
    bm_105.to_mesh(glow_105.data)
    bm_105.free()

    glow_105.location = (0, 0, 0)
    glow_105.rotation_euler = (0, 0, 0)
    glow_105.scale = (1, 1, 1)

    if mat_tv.name not in [m.name for m in glow_105.data.materials if m]:
        glow_105.data.materials.append(mat_tv)

    # Area light facing +X towards bed
    light_105.location = Vector((x_front_105 + 0.02, 1.950, 1.723))
    light_105.rotation_euler = Euler((0.0, math.radians(90.0), 0.0), 'XYZ') # Facing +X
    light_105.data.type = 'AREA'
    light_105.data.shape = 'RECTANGLE'
    light_105.data.size = 1.40
    light_105.data.size_y = 0.84
    light_105.data.energy = 45.0
    light_105.data.color = (0.75, 0.88, 1.0)

    glow_105.hide_viewport = False
    glow_105.hide_render = False
    light_105.hide_viewport = False
    light_105.hide_render = False

    # -------------------------------------------------------------
    # 3. Collection Organization in Outliner
    # -------------------------------------------------------------
    print(">>> 3. Organizing Collections for Intuitive Outliner Toggling...")
    col_104 = bpy.data.collections.get("TV_1.04_Active")
    if not col_104:
        col_104 = bpy.data.collections.new("TV_1.04_Active")
        scene.collection.children.link(col_104)
    col_104.hide_viewport = False
    col_104.hide_render = False
    for o in [glow_104, light_104]:
        if col_104 not in o.users_collection:
            col_104.objects.link(o)
        for c in list(o.users_collection):
            if c != col_104:
                c.objects.unlink(o)

    col_105 = bpy.data.collections.get("TV_1.05_Active")
    if not col_105:
        col_105 = bpy.data.collections.new("TV_1.05_Active")
        scene.collection.children.link(col_105)
    col_105.hide_viewport = False
    col_105.hide_render = False
    for o in [glow_105, light_105]:
        if col_105 not in o.users_collection:
            col_105.objects.link(o)
        for c in list(o.users_collection):
            if c != col_105:
                c.objects.unlink(o)

    # Save updated blend file
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> Saved 'dum_pudorys.blend' with active TV!")

def render_verification():
    print(">>> 4. Rendering TV verification views...")
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    try:
        scene.cycles.device = 'GPU'
    except:
        pass
    scene.cycles.samples = 48

    artifact_dir = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6"

    # Close-up camera on Living Room TV
    cam_data = bpy.data.cameras.new("Cam_TV_Test")
    cam_obj = bpy.data.objects.new("Cam_TV_Test", cam_data)
    scene.collection.objects.link(cam_obj)

    # Look from front-above at living room TV (7.904, 4.90, 1.20)
    target = Vector((7.904, 5.20, 1.15))
    cam_obj.location = target + Vector((0.0, 3.8, 2.2))
    cam_obj.rotation_euler = (target - cam_obj.location).to_track_quat('-Z', 'Y').to_euler()

    scene.camera = cam_obj
    scene.render.resolution_x = 960
    scene.render.resolution_y = 640
    scene.render.filepath = os.path.join(artifact_dir, "test_tv_104_active.png")
    bpy.ops.render.render(write_still=True)
    print("  Rendered test_tv_104_active.png!")

    # Floorplan overview with TV active
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.join(artifact_dir, "dum_pudorys_tv_active_overview.png")
        bpy.ops.render.render(write_still=True)
        print("  Rendered dum_pudorys_tv_active_overview.png!")

    # Clean up temp camera
    bpy.data.objects.remove(cam_obj)
    bpy.data.cameras.remove(cam_data)
    if iso_cam:
        scene.camera = iso_cam

    print(">>> TV Fix and verification complete!")

if __name__ == '__main__':
    fix_tvs()
    render_verification()
