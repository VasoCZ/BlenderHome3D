import bpy
import math
from mathutils import Vector, Euler
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)

print("=== 1. Setup Dreame Active Lights Collection ===")
root = bpy.data.objects.get("Dreame_L40_Ultra")
coll_main = bpy.data.collections.get("Appliances_Robot_Vacuum")
if not coll_main:
    coll_main = bpy.context.scene.collection

coll_name = "Dreame_Active_Lights"
coll_active = bpy.data.collections.get(coll_name)
if not coll_active:
    coll_active = bpy.data.collections.new(coll_name)
    coll_main.children.link(coll_active)

# Clean existing objects in coll_active
for o in list(coll_active.objects):
    bpy.data.objects.remove(o, do_unlink=True)

# Also remove any leftover test lights/meshes
for name in ["Dreame_Glow_Headlight_L", "Dreame_Glow_Headlight_R", "Dreame_Glow_Button_LED", 
             "Dreame_Glow_LiDAR", "Light_Dreame_Headlights_Beam", "Light_Dreame_Headlight_L", 
             "Light_Dreame_Headlight_R"]:
    o = bpy.data.objects.get(name)
    if o:
        bpy.data.objects.remove(o, do_unlink=True)

print("=== 2. Setup Boosted Materials ===")
# Headlight emission material
mat_hl = bpy.data.materials.get("Mat_Dreame_Headlight_Active")
if not mat_hl:
    mat_hl = bpy.data.materials.new("Mat_Dreame_Headlight_Active")
mat_hl.use_nodes = True
nodes = mat_hl.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
emis_n = nodes.new('ShaderNodeEmission')
emis_n.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
emis_n.inputs['Strength'].default_value = 350.0  # Crisp brilliant white LED
mat_hl.node_tree.links.new(emis_n.outputs['Emission'], out_n.inputs['Surface'])

# Button emission material
mat_btn = bpy.data.materials.get("Mat_Dreame_Button_Active")
if not mat_btn:
    mat_btn = bpy.data.materials.new("Mat_Dreame_Button_Active")
mat_btn.use_nodes = True
nodes = mat_btn.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
emis_n = nodes.new('ShaderNodeEmission')
emis_n.inputs['Color'].default_value = (0.95, 0.98, 1.0, 1.0)
emis_n.inputs['Strength'].default_value = 120.0  # Clearly visible power status indicator
mat_btn.node_tree.links.new(emis_n.outputs['Emission'], out_n.inputs['Surface'])

# LiDAR rim emission material
mat_lidar = bpy.data.materials.get("Mat_Dreame_LiDAR_Active")
if not mat_lidar:
    mat_lidar = bpy.data.materials.new("Mat_Dreame_LiDAR_Active")
mat_lidar.use_nodes = True
nodes = mat_lidar.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
emis_n = nodes.new('ShaderNodeEmission')
emis_n.inputs['Color'].default_value = (0.92, 0.96, 1.0, 1.0)
emis_n.inputs['Strength'].default_value = 30.0
mat_lidar.node_tree.links.new(emis_n.outputs['Emission'], out_n.inputs['Surface'])

# Also boost base materials as fallback
mat_base_hl = bpy.data.materials.get("Mat_Dreame_Headlight")
if mat_base_hl and mat_base_hl.node_tree:
    for n in mat_base_hl.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            n.inputs['Emission Strength'].default_value = 150.0

mat_base_led = bpy.data.materials.get("Mat_Dreame_LED_Indicator")
if mat_base_led and mat_base_led.node_tree:
    for n in mat_base_led.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Emission Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            n.inputs['Emission Strength'].default_value = 50.0

print("=== 3. Create Glowing Overlay Meshes ===")
# Dual Headlights
for hl_src_name, glow_name in [("Dreame_LED_Headlight_-1", "Dreame_Glow_Headlight_L"), 
                               ("Dreame_LED_Headlight_1", "Dreame_Glow_Headlight_R")]:
    src = bpy.data.objects.get(hl_src_name)
    if src:
        glow_mesh = src.data.copy()
        glow_obj = bpy.data.objects.new(glow_name, glow_mesh)
        glow_obj.matrix_local = src.matrix_local.copy()
        glow_obj.parent = root
        glow_obj.data.materials.clear()
        glow_obj.data.materials.append(mat_hl)
        coll_active.objects.link(glow_obj)
        print(f"  Linked {glow_name}")

# Central Power Button
src_btn = bpy.data.objects.get("Dreame_Robot_Button_1")
if src_btn:
    btn_mesh = src_btn.data.copy()
    btn_glow = bpy.data.objects.new("Dreame_Glow_Button_LED", btn_mesh)
    btn_glow.matrix_local = src_btn.matrix_local.copy()
    btn_glow.location.z += 0.0006
    btn_glow.parent = root
    btn_glow.data.materials.clear()
    btn_glow.data.materials.append(mat_btn)
    coll_active.objects.link(btn_glow)
    print("  Linked Dreame_Glow_Button_LED")

# LiDAR Rim
src_lidar = bpy.data.objects.get("Dreame_Robot_LiDAR_Cap")
if src_lidar:
    lidar_mesh = src_lidar.data.copy()
    lidar_glow = bpy.data.objects.new("Dreame_Glow_LiDAR", lidar_mesh)
    lidar_glow.matrix_local = src_lidar.matrix_local.copy()
    lidar_glow.location.z += 0.0005
    lidar_glow.parent = root
    lidar_glow.data.materials.clear()
    lidar_glow.data.materials.append(mat_lidar)
    coll_active.objects.link(lidar_glow)
    print("  Linked Dreame_Glow_LiDAR")

print("=== 4. Create Forward Headlight Spotlights ===")
rot_forward = Euler((math.radians(82.0), 0.0, 0.0), 'XYZ')

# Wide ambient forward beam
sdata_beam = bpy.data.lights.new(name="Light_Dreame_Headlights_Beam", type='SPOT')
sdata_beam.color = (1.0, 1.0, 1.0)
sdata_beam.energy = 25.0
sdata_beam.spot_size = math.radians(80.0)
sdata_beam.spot_blend = 0.55
sdata_beam.shadow_soft_size = 0.04
sdata_beam.use_nodes = True
if sdata_beam.node_tree:
    for n in sdata_beam.node_tree.nodes:
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            n.inputs['Strength'].default_value = 25.0
sp_beam = bpy.data.objects.new("Light_Dreame_Headlights_Beam", sdata_beam)
sp_beam.parent = root
sp_beam.location = Vector((0.0, 0.360, 0.065))
sp_beam.rotation_euler = rot_forward
coll_active.objects.link(sp_beam)

# Left focused core spot
sdata_l = bpy.data.lights.new(name="Light_Dreame_Headlight_L", type='SPOT')
sdata_l.color = (1.0, 1.0, 1.0)
sdata_l.energy = 15.0
sdata_l.spot_size = math.radians(65.0)
sdata_l.spot_blend = 0.40
sdata_l.shadow_soft_size = 0.02
sdata_l.use_nodes = True
if sdata_l.node_tree:
    for n in sdata_l.node_tree.nodes:
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            n.inputs['Strength'].default_value = 15.0
sp_l = bpy.data.objects.new("Light_Dreame_Headlight_L", sdata_l)
sp_l.parent = root
sp_l.location = Vector((-0.022, 0.355, 0.055))
sp_l.rotation_euler = Euler((math.radians(82.0), 0.0, math.radians(2.0)), 'XYZ')
coll_active.objects.link(sp_l)

# Right focused core spot
sdata_r = bpy.data.lights.new(name="Light_Dreame_Headlight_R", type='SPOT')
sdata_r.color = (1.0, 1.0, 1.0)
sdata_r.energy = 15.0
sdata_r.spot_size = math.radians(65.0)
sdata_r.spot_blend = 0.40
sdata_r.shadow_soft_size = 0.02
sdata_r.use_nodes = True
if sdata_r.node_tree:
    for n in sdata_r.node_tree.nodes:
        if n.type == 'EMISSION':
            n.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
            n.inputs['Strength'].default_value = 15.0
sp_r = bpy.data.objects.new("Light_Dreame_Headlight_R", sdata_r)
sp_r.parent = root
sp_r.location = Vector((0.022, 0.355, 0.055))
sp_r.rotation_euler = Euler((math.radians(82.0), 0.0, math.radians(-2.0)), 'XYZ')
coll_active.objects.link(sp_r)

print("=== 5. Configure Scene & Save Blend ===")
scene = bpy.context.scene
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100
scene.render.film_transparent = True

cam = bpy.data.objects.get("Isometric_Camera")
if cam:
    scene.camera = cam

# Set viewport perspective to camera
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.region_3d.view_perspective = 'CAMERA'
                    space.camera = cam

# Set coll_active to visible by default so lights are active
coll_active.hide_render = False
coll_active.hide_viewport = False

# Save blend file
bpy.ops.wm.save_mainfile(filepath=blend_path)
print(f"Successfully saved {blend_path}")

print("=== 6. Render 4K Home Assistant Layer (renders_ha_2.0/vysavac.png) ===")
# To render the pure HA light overlay layer:
# Hide Sun_Fill and room lights so only Dreame lights illuminate the dark floor
sun = bpy.data.objects.get("Sun_Fill")
sun_orig = sun.hide_render if sun else False
if sun:
    sun.hide_render = True

# Also hide room ambient lights if any active
hidden_lights = []
for l_obj in bpy.data.objects:
    if l_obj.type == 'LIGHT' and l_obj.name not in ["Light_Dreame_Headlights_Beam", "Light_Dreame_Headlight_L", "Light_Dreame_Headlight_R"]:
        if not l_obj.hide_render:
            l_obj.hide_render = True
            hidden_lights.append(l_obj)

# Ensure film transparent is True
scene.render.film_transparent = True
scene.cycles.samples = 32

ha_out_path = r"C:\Users\Vaso\Antigravity\Project blender\renders_ha_2.0\vysavac.png"
scene.render.filepath = ha_out_path
bpy.ops.render.render(write_still=True)
print(f"Rendered 4K HA layer: {ha_out_path}")

# Restore original light states in scene
if sun:
    sun.hide_render = sun_orig
for l_obj in hidden_lights:
    l_obj.hide_render = False

# Save final state with lights restored
bpy.ops.wm.save_mainfile(filepath=blend_path)
print("Finished all tasks successfully!")
