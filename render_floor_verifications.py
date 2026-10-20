import bpy

scene = bpy.context.scene

# Camera 1: Living room (North/South) & Kitchen transition
cam1_data = bpy.data.cameras.new('Cam_Living_Kitchen')
cam1_obj = bpy.data.objects.new('Cam_Living_Kitchen', cam1_data)
cam1_data.type = 'ORTHO'
cam1_data.ortho_scale = 7.0
# Center at (6.2, 7.5, 0.0)
cam1_obj.location = (6.2 - 17.5, 7.5 - 17.5, 24.75 + 1.0)
cam1_obj.rotation_euler = (0.785398, 0.0, -0.785398)
scene.collection.objects.link(cam1_obj)

scene.camera = cam1_obj
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\floor_transition_living_kitchen_view.png'
bpy.ops.render.render(write_still=True)
print("Rendered: floor_transition_living_kitchen_view.png")

# Camera 2: Hallway 1.02 and bedrooms 1.05 / 1.06 / 1.07 thresholds
cam2_data = bpy.data.cameras.new('Cam_Hallway_Bedrooms')
cam2_obj = bpy.data.objects.new('Cam_Hallway_Bedrooms', cam2_data)
cam2_data.type = 'ORTHO'
cam2_data.ortho_scale = 7.5
# Center at (5.2, 3.8, 0.0)
cam2_obj.location = (5.2 - 17.5, 3.8 - 17.5, 24.75 + 1.0)
cam2_obj.rotation_euler = (0.785398, 0.0, -0.785398)
scene.collection.objects.link(cam2_obj)

scene.camera = cam2_obj
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\floor_transition_hallway_bedrooms_view.png'
bpy.ops.render.render(write_still=True)
print("Rendered: floor_transition_hallway_bedrooms_view.png")

# Camera 3: Full Overview
iso_cam = bpy.data.objects.get('Isometric_Camera')
scene.camera = iso_cam
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\floor_full_house_overview.png'
bpy.ops.render.render(write_still=True)
print("Rendered: floor_full_house_overview.png")
