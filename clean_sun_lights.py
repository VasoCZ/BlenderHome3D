import bpy
import math

print(">>> Checking and cleaning SUN lights...")

removed_objects = []
for obj in list(bpy.data.objects):
    if obj.type == 'LIGHT':
        if obj.data.type == 'SUN':
            if obj.name != 'Sun_Fill':
                print(f"Removing SUN object: {obj.name}")
                removed_objects.append(obj.name)
                bpy.data.objects.remove(obj, do_unlink=True)

removed_lights = []
for l in list(bpy.data.lights):
    if l.type == 'SUN':
        if l.name != 'Sun_Fill':
            print(f"Removing orphan SUN light datablock: {l.name}")
            removed_lights.append(l.name)
            bpy.data.lights.remove(l, do_unlink=True)

# Ensure the original Sun_Fill is properly configured
sun_obj = bpy.data.objects.get("Sun_Fill")
if not sun_obj:
    print("Warning: Sun_Fill was not found, recreating original Sun_Fill...")
    sun_data = bpy.data.lights.new(name="Sun_Fill", type='SUN')
    sun_data.energy = 2.0
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.use_shadow = True
    sun_obj = bpy.data.objects.new(name="Sun_Fill", object_data=sun_data)
    sun_obj.location = (15.0, -10.0, 25.0)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-35))
    bpy.context.scene.collection.objects.link(sun_obj)
else:
    print(f"Found original Sun_Fill: {sun_obj.name}")
    sun_obj.hide_viewport = False
    sun_obj.hide_render = False
    sun_obj.data.type = 'SUN'
    sun_obj.data.energy = 2.0
    sun_obj.data.color = (1.0, 0.98, 0.95)
    sun_obj.data.use_shadow = True
    sun_obj.location = (15.0, -10.0, 25.0)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-35))

# Verification
all_suns = [o.name for o in bpy.data.objects if o.type == 'LIGHT' and o.data.type == 'SUN']
print(f"Verification - SUN lights currently in scene: {all_suns}")

# Save blend file
blend_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f">>> Successfully saved to: {blend_path}")
