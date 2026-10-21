"""
update_dining_table_lights.py
-----------------------------
Softens the spotlight lighting directly above the dining table:
1. spot_blend = 1.0 (smooth falloff to avoid harsh edges)
2. shadow_soft_size = 0.40 m (soft diffused shadows under table and chairs)
3. spot_size = 72.0 deg (wide cone covering table and surrounding chairs)
4. Preserves warm white 3000 K color and energy 85.0 W
"""

import bpy
import math

def update_dining_table_lights():
    print(">>> Softening dining table spotlights...")
    lights = ["Light_Dining_Spot_1", "Light_Dining_Spot_2"]
    
    for name in lights:
        obj = bpy.data.objects.get(name)
        if not obj or obj.type != 'LIGHT':
            print(f"Warning: {name} not found!")
            continue
        
        lamp = obj.data
        lamp.spot_blend = 1.0
        lamp.shadow_soft_size = 0.40
        lamp.spot_size = math.radians(72.0)
        print(f"Updated {name}: spot_blend={lamp.spot_blend}, shadow_soft_size={lamp.shadow_soft_size}m, spot_size={math.degrees(lamp.spot_size):.1f} deg")

    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam
        print(f"Camera verified: {bpy.context.scene.camera.name}")
        
    bpy.ops.wm.save_mainfile()
    print("Saved to dum_pudorys.blend successfully!")

if __name__ == '__main__':
    update_dining_table_lights()
