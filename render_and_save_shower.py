import bpy
import mathutils
import math

print("=== EXECUTING SHOWER BUILD SCRIPT ===")
exec(open(r"C:\Users\Vaso\Antigravity\Project blender\build_shower_screen.py").read())

# -------------------------------------------------------------------------
# Set up Cameras
# -------------------------------------------------------------------------
def setup_cam(cam_name, pos, target, lens=20.0):
    cam_obj = bpy.data.objects.get(cam_name)
    if not cam_obj:
        cam_data = bpy.data.cameras.new(cam_name)
        cam_obj = bpy.data.objects.new(cam_name, cam_data)
        bpy.context.scene.collection.objects.link(cam_obj)
    
    pos_vec = mathutils.Vector(pos)
    target_vec = mathutils.Vector(target)
    direction = target_vec - pos_vec
    rot_quat = direction.to_track_quat('-Z', 'Y')
    
    cam_obj.location = pos_vec
    cam_obj.rotation_euler = rot_quat.to_euler()
    cam_obj.data.lens = lens
    cam_obj.data.sensor_width = 36
    cam_obj.data.clip_start = 0.05
    cam_obj.data.clip_end = 100.0
    return cam_obj

# Camera 1: Photo match view (matching realne fotky/sprcha.jpg)
cam_photo = setup_cam("Camera_Shower_Photo_Match", pos=(1.95, 10.35, 1.42), target=(0.70, 10.45, 1.12), lens=19.0)

# Camera 2: Close-up of the top chrome clamp ("horni uchop chromovy")
cam_clamp = setup_cam("Camera_Shower_Clamp_Closeup", pos=(1.48, 10.65, 2.08), target=(1.250, 10.888, 2.018), lens=38.0)

# Camera 3: Wide bathroom view from the entrance door
cam_wide = setup_cam("Camera_Shower_Wide_View", pos=(2.40, 9.95, 1.65), target=(1.00, 10.80, 1.15), lens=17.5)

# -------------------------------------------------------------------------
# Render Settings
# -------------------------------------------------------------------------
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 36
bpy.context.scene.cycles.adaptive_threshold = 0.05

# 1. Render Photo Match
bpy.context.scene.camera = cam_photo
bpy.context.scene.render.resolution_x = 900
bpy.context.scene.render.resolution_y = 1600
render_path_photo = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\5dd5363d-d0f7-41a6-a8b9-f311aeeefac8\render_shower_photo_match.png"
bpy.context.scene.render.filepath = render_path_photo
print(f"Rendering {render_path_photo}...")
bpy.ops.render.render(write_still=True)
print("Finished render_shower_photo_match.png!")

# 2. Render Clamp Closeup
bpy.context.scene.camera = cam_clamp
bpy.context.scene.render.resolution_x = 1000
bpy.context.scene.render.resolution_y = 800
render_path_clamp = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\5dd5363d-d0f7-41a6-a8b9-f311aeeefac8\render_shower_clamp_closeup.png"
bpy.context.scene.render.filepath = render_path_clamp
print(f"Rendering {render_path_clamp}...")
bpy.ops.render.render(write_still=True)
print("Finished render_shower_clamp_closeup.png!")

# 3. Render Wide View
bpy.context.scene.camera = cam_wide
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
render_path_wide = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\5dd5363d-d0f7-41a6-a8b9-f311aeeefac8\render_shower_wide_view.png"
bpy.context.scene.render.filepath = render_path_wide
print(f"Rendering {render_path_wide}...")
bpy.ops.render.render(write_still=True)
print("Finished render_shower_wide_view.png!")

# Restore isometric camera as default
iso_cam = bpy.data.objects.get("Isometric_Camera")
if iso_cam:
    bpy.context.scene.camera = iso_cam

# Save blend file
save_path = r"C:\Users\Vaso\Antigravity\Project blender\dum_pudorys.blend"
print(f"Saving blend file to {save_path}...")
bpy.ops.wm.save_mainfile(filepath=save_path)
print("Blend file successfully saved!")
