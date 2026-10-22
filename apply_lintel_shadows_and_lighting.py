"""
apply_lintel_shadows_and_lighting.py
Comprehensive fix for:
1. Entrance lintel (Z-fighting removal, clean geometry, clean wall cap material).
2. Elimination of burnt/charred wall shadows at all window/door reveals via Auto Smooth (30 deg).
3. Calibration of Day Mode: Sun_Fill reduced to 3.0W, soft bathroom daylight fill.
4. Calibration of Night Mode: Rich blue-black night sky (0.07, 0.14, 0.30) with strength 0.035.
5. Mode controller function to easily switch between Day and Night modes.
"""

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler

def fix_entrance_lintel_and_wall_shading():
    print(">>> 1. Fixing Exterior_Walls geometry and normal shading...")
    ext = bpy.data.objects.get("Exterior_Walls")
    if not ext:
        raise RuntimeError("Object 'Exterior_Walls' not found!")

    bm = bmesh.new()
    bm.from_mesh(ext.data)

    # A. Identify and remove redundant overlapping duplicate faces above entrance door (Face 98-102)
    # The duplicate box has X in [4.640, 5.740], Y in [0.000, 0.365], Z in [2.050, 2.500]
    to_delete = []
    for f in bm.faces:
        c = f.calc_center_median()
        # Find the duplicate box faces
        if 4.63 <= c.x <= 5.75 and -0.01 <= c.y <= 0.37 and 2.04 <= c.z <= 2.51:
            # Check if this face is one of the redundant box faces
            # Redundant top face at Z=2.500: verts all at Z=2.500 with X in [4.64, 5.74]
            if abs(c.z - 2.500) < 0.005 and 4.63 <= min(v.co.x for v in f.verts) and max(v.co.x for v in f.verts) <= 5.75:
                to_delete.append(f)
            # Redundant front face at Y=0.000:
            elif abs(c.y - 0.000) < 0.005 and 4.63 <= min(v.co.x for v in f.verts) and max(v.co.x for v in f.verts) <= 5.75 and min(v.co.z for v in f.verts) >= 2.04:
                to_delete.append(f)
            # Redundant back face at Y=0.365:
            elif abs(c.y - 0.365) < 0.005 and 4.63 <= min(v.co.x for v in f.verts) and max(v.co.x for v in f.verts) <= 5.75 and min(v.co.z for v in f.verts) >= 2.04:
                to_delete.append(f)
            # Redundant side faces at X=4.640 and X=5.740:
            elif (abs(c.x - 4.640) < 0.005 or abs(c.x - 5.740) < 0.005) and min(v.co.z for v in f.verts) >= 2.04:
                to_delete.append(f)

    print(f"  Found {len(to_delete)} duplicate faces to delete in entrance lintel.")
    bmesh.ops.delete(bm, geom=to_delete, context='FACES_ONLY')

    # Remove loose vertices
    loose = [v for v in bm.verts if not v.link_faces]
    bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    bm.to_mesh(ext.data)
    bm.free()
    ext.data.update()
    print("  Exterior_Walls geometry cleaned successfully!")

    # B. Material slot: Ensure Mat_Interior_Wall is on Exterior_Walls for top cut faces
    mat_int = bpy.data.materials.get("Mat_Interior_Wall")
    if mat_int:
        if mat_int.name not in [m.name for m in ext.data.materials if m]:
            ext.data.materials.append(mat_int)
        int_mat_idx = [i for i, m in enumerate(ext.data.materials) if m and m.name == mat_int.name][0]
        # Assign Mat_Interior_Wall to all horizontal top cut faces (Z=2.500, normal.z > 0.9)
        top_count = 0
        for p in ext.data.polygons:
            if p.normal.z > 0.9 and p.center.z > 2.40:
                p.material_index = int_mat_idx
                top_count += 1
        print(f"  Assigned {mat_int.name} to {top_count} top cut faces on Exterior_Walls.")

    # C. Setup Auto Smooth modifier on Exterior_Walls
    as_ng = bpy.data.node_groups.get("Auto Smooth")
    if not as_ng:
        raise RuntimeError("Geometry node group 'Auto Smooth' not found!")

    mod_ext = ext.modifiers.get("Smooth by Angle")
    if not mod_ext:
        mod_ext = ext.modifiers.new(name="Smooth by Angle", type='NODES')
    mod_ext.node_group = as_ng
    if hasattr(mod_ext, "properties") and hasattr(mod_ext.properties, "inputs"):
        if hasattr(mod_ext.properties.inputs, "Socket_2"):
            mod_ext.properties.inputs.Socket_2.value = math.radians(30.0)
    print("  Exterior_Walls: Auto Smooth set to 30 degrees.")

    # D. Setup Auto Smooth modifier on Interior_Walls
    int_w = bpy.data.objects.get("Interior_Walls")
    if int_w:
        mod_int = int_w.modifiers.get("Auto Smooth")
        if not mod_int:
            mod_int = int_w.modifiers.new(name="Auto Smooth", type='NODES')
        mod_int.node_group = as_ng
        if hasattr(mod_int, "properties") and hasattr(mod_int.properties, "inputs"):
            if hasattr(mod_int.properties.inputs, "Socket_2"):
                mod_int.properties.inputs.Socket_2.value = math.radians(30.0)
        print("  Interior_Walls: Auto Smooth set to 30 degrees.")

def setup_daylight_and_night_lighting():
    print(">>> 2. Calibrating Day Mode and Night Mode lighting...")
    scene = bpy.context.scene

    # A. Sun_Fill calibration for Day Mode (reduced from 5.8W to 3.0W)
    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.data.energy = 3.0
        sun.data.color = (1.0, 0.98, 0.95)
        sun['day_energy'] = 3.0
        print(f"  Sun_Fill calibrated to {sun.data.energy}W.")

    # B. Add/Tune dedicated soft daylight fill in Bathroom 1.10
    light_bath_name = "Light_Daylight_Fill_Bathroom_1.10"
    light_bath = bpy.data.objects.get(light_bath_name)
    if not light_bath:
        light_bath_data = bpy.data.lights.new(name=light_bath_name, type='AREA')
        light_bath = bpy.data.objects.new(name=light_bath_name, object_data=light_bath_data)
        # Place in scene collection or Lights
        lights_col = bpy.data.collections.get("Lights") or scene.collection
        lights_col.objects.link(light_bath)

    # Position at bathroom window opening pointing south into the bathroom
    light_bath.location = Vector((1.62, 11.60, 1.85))
    light_bath.rotation_euler = Euler((math.radians(-90.0), 0.0, 0.0), 'XYZ')
    light_bath.data.shape = 'RECTANGLE'
    light_bath.data.size = 1.0
    light_bath.data.size_y = 0.6
    light_bath.data.color = (0.85, 0.92, 1.0) # natural northern sky blue
    light_bath.data.energy = 16.0
    light_bath['day_energy'] = 16.0
    print("  Configured Light_Daylight_Fill_Bathroom_1.10 (16W soft skylight).")

    # C. Fast GI configuration
    scene.cycles.use_fast_gi = True
    scene.cycles.fast_gi_method = 'ADD'
    scene.cycles.ao_bounces = 1

def set_mode(mode='day'):
    scene = bpy.context.scene
    world = scene.world
    if not world or not world.use_nodes:
        return
    bg = world.node_tree.nodes.get("Background")
    if not bg:
        return

    sun = bpy.data.objects.get("Sun_Fill")
    bath_daylight = bpy.data.objects.get("Light_Daylight_Fill_Bathroom_1.10")

    if mode == 'day':
        # Day mode: soft natural sky
        bg.inputs["Color"].default_value = (0.82, 0.90, 1.0, 1.0)
        bg.inputs["Strength"].default_value = 0.85
        if sun:
            sun.data.energy = sun.get('day_energy', 3.0)
            sun.hide_render = False
        if bath_daylight:
            bath_daylight.data.energy = bath_daylight.get('day_energy', 16.0)
            bath_daylight.hide_render = False
        print("  Set scene mode to DAY (Sun ON @ 3.0W, Sky ON, Bath daylight ON).")
    elif mode == 'night':
        # Night mode: deep blue-black night sky
        bg.inputs["Color"].default_value = (0.07, 0.14, 0.30, 1.0)
        bg.inputs["Strength"].default_value = 0.035
        if sun:
            sun.data.energy = 0.0
            sun.hide_render = True
        if bath_daylight:
            bath_daylight.data.energy = 0.0
            bath_daylight.hide_render = True
        print("  Set scene mode to NIGHT (Sun OFF, Sky Blue-Black 0.035, Bath daylight OFF).")

def main():
    blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    fix_entrance_lintel_and_wall_shading()
    setup_daylight_and_night_lighting()

    # Save Day mode as standard default in blend file
    set_mode('day')

    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> Saved updated 'dum_pudorys.blend'!")

if __name__ == '__main__':
    main()
