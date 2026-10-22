import bpy
import math

# Camera matching reference photo
cam_name = "Camera_Pokoj_106_Photo_Match"
cam_obj = bpy.data.objects.get(cam_name)
if not cam_obj:
    cam_data = bpy.data.cameras.new(cam_name)
    cam_obj = bpy.data.objects.new(cam_name, cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

cam_obj.location = (3.4, 3.2, 1.45)
# Target point around desk/kallax corner
target = (1.1, 0.9, 0.6)
dx = target[0] - cam_obj.location.x
dy = target[1] - cam_obj.location.y
dz = target[2] - cam_obj.location.z

yaw = math.atan2(dx, -dy) # rotation around Z
dist_xy = math.sqrt(dx*dx + dy*dy)
pitch = math.atan2(-dz, dist_xy) # tilt down

cam_obj.rotation_euler = (math.pi/2 - pitch, 0, yaw)
cam_obj.data.lens = 24 # wide angle matching phone camera
cam_obj.data.sensor_width = 36

bpy.context.scene.camera = cam_obj
bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 540
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 24
bpy.context.scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\test_cam_106_angle.png"

bpy.ops.render.render(write_still=True)
print("Photo match angle rendered!")
