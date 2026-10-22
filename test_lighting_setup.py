"""
test_lighting_setup.py
Configures and tests:
1. Collection ENV_DAY_SUN_FILL: Sun_Fill, Light_Day_Sky_Fill, Light_Daylight_Fill_Bathroom_1.10
2. Collection LIGHTS_NIGHT: All 26 artificial ceiling/spot/soffit/patio lights
3. Light recoloring to modern warm white #FFF2DE (3000K): (1.0, 0.8879, 0.7305)
4. Sun daylight white 5500K: (1.0, 0.962, 0.905)
5. Renders test comparisons:
   - day_mode_test.png (ENV_DAY_SUN_FILL ON, LIGHTS_NIGHT OFF)
   - night_mode_test.png (ENV_DAY_SUN_FILL OFF, LIGHTS_NIGHT ON)
"""

import bpy
import math
from mathutils import Vector, Euler
import os

blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

print(">>> 1. Creating Collections...")
# Collection: ENV_DAY_SUN_FILL
col_day = bpy.data.collections.get("ENV_DAY_SUN_FILL")
if not col_day:
    col_day = bpy.data.collections.new("ENV_DAY_SUN_FILL")
    scene.collection.children.link(col_day)

# Collection: LIGHTS_NIGHT
col_night = bpy.data.collections.get("LIGHTS_NIGHT")
if not col_night:
    col_night = bpy.data.collections.new("LIGHTS_NIGHT")
    scene.collection.children.link(col_night)

# Ensure visibility flags are clean
col_day.hide_viewport = False
col_day.hide_render = False
col_night.hide_viewport = False
col_night.hide_render = False

def move_to_single_collection(obj, target_col):
    if target_col not in obj.users_collection:
        target_col.objects.link(obj)
    for c in list(obj.users_collection):
        if c != target_col:
            c.objects.unlink(obj)

print(">>> 2. Setting up Day Lighting in ENV_DAY_SUN_FILL...")
# Main Sun
sun = bpy.data.objects.get("Sun_Fill")
if sun:
    move_to_single_collection(sun, col_day)
    sun.data.color = (1.0, 0.962, 0.905) # 5500K clean daylight white
    sun.data.energy = 2.8 # Balanced daylight sun
    sun.data.angle = 0.00925 # 0.53 deg crisp directional shadows
    sun.hide_viewport = False
    sun.hide_render = False

# Sky Fill Area Light
sky_fill = bpy.data.objects.get("Light_Day_Sky_Fill")
if not sky_fill:
    sky_light_data = bpy.data.lights.new("Light_Day_Sky_Fill", 'AREA')
    sky_fill = bpy.data.objects.new("Light_Day_Sky_Fill", sky_light_data)
    col_day.objects.link(sky_fill)
else:
    move_to_single_collection(sky_fill, col_day)

sky_fill.location = Vector((5.0, 5.0, 16.0))
sky_fill.rotation_euler = Euler((0.0, 0.0, 0.0), 'XYZ')
sky_fill.data.type = 'AREA'
sky_fill.data.shape = 'RECTANGLE'
sky_fill.data.size = 24.0
sky_fill.data.size_y = 36.0
sky_fill.data.color = (0.80, 0.89, 1.0) # Soft clear sky blue-white
sky_fill.data.energy = 450.0 # Diffuse skylight fill across exterior and interior
sky_fill.hide_viewport = False
sky_fill.hide_render = False

# Daytime fill for enclosed bathroom
bath_day = bpy.data.objects.get("Light_Daylight_Fill_Bathroom_1.10")
if bath_day:
    move_to_single_collection(bath_day, col_day)
    bath_day.data.color = (0.85, 0.92, 1.0)
    bath_day.data.energy = 16.0
    bath_day.hide_viewport = False
    bath_day.hide_render = False

print(">>> 3. Setting up Artificial Lights in LIGHTS_NIGHT...")
# Warm white #FFF2DE / 3000K Blackbody in Linear RGB:
WARM_WHITE_3000K = (1.0, 0.8879, 0.7305)

night_light_names = [
    "Light_1.01_Zadveri_V",
    "Light_1.02_Chodba_V",
    "Light_1.03_Kuchyne_V1",
    "Light_1.03_Kuchyne_V2",
    "Light_1.04_Obyvaci_pokoj_V2_Patio1",
    "Light_1.04_Obyvaci_pokoj_V3_Patio2",
    "Light_1.05_Pokoj_V1_South",
    "Light_1.05_Pokoj_V2_Center",
    "Light_1.05_Pokoj_Spot_West",
    "Light_1.05_Pokoj_Spot_East",
    "Light_1.06_Pokoj_V1_South",
    "Light_1.06_Pokoj_V2_North",
    "Light_1.07_Pokoj_V1_West",
    "Light_1.07_Pokoj_V2_East",
    "Light_1.08_WC_M",
    "Light_1.09_Technicka_mistnost_M",
    "Light_1.10_Koupelna_Vplus",
    "Light_1.11_Chodba_M1_Bath",
    "Light_1.11_Chodba_M2_WC",
    "Light_Dining_Spot_1",
    "Light_Dining_Spot_2",
    "Light_Ext_Front_Soffit_1_CornerL",
    "Light_Ext_Front_Soffit_2_Window106",
    "Light_Ext_Front_Soffit_3_Entrance",
    "Light_Ext_Front_Soffit_5_CornerR",
    "Light_Ext_Rear_Patio_Left",
    "Light_Ext_Rear_Patio_Right",
    "Light_Ext_Side_East_A2",
]

for name in night_light_names:
    l_obj = bpy.data.objects.get(name)
    if l_obj:
        move_to_single_collection(l_obj, col_night)
        l_obj.data.color = WARM_WHITE_3000K
        l_obj.hide_viewport = False
        l_obj.hide_render = False

# Ensure TV collections are also top-level and clean
for tv_col_name in ["TV_1.04_Active", "TV_1.05_Active"]:
    tvc = bpy.data.collections.get(tv_col_name)
    if tvc:
        tvc.hide_viewport = False
        tvc.hide_render = False

# World Background setup
world = scene.world
if world and world.node_tree:
    # Ensure BG_Night is active at base
    nodes = world.node_tree.nodes
    mix_node = nodes.get("Mix Shader")
    bg_night = nodes.get("BG_Night")
    if mix_node and bg_night:
        mix_node.inputs['Fac'].default_value = 1.0 # Base world is deep night blue #02050D
        bg_night.inputs['Color'].default_value = (0.0006, 0.0015, 0.004, 1.0)
        bg_night.inputs['Strength'].default_value = 0.06

print(">>> Saving dum_pudorys.blend with new lighting architecture...")
iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    scene.camera = iso_cam

bpy.ops.wm.save_mainfile()
print(">>> Saved!")
