import bpy, mathutils

scene = bpy.context.scene
cam_dir = mathutils.Vector((0.5, 0.5, -0.70710678)).normalized()

def setup_cam(name, target, scale):
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
    cdata = bpy.data.cameras.new(name)
    cdata.type = 'ORTHO'
    cdata.ortho_scale = scale
    cobj = bpy.data.objects.new(name, cdata)
    cobj.location = target - cam_dir * 30.0
    cobj.rotation_euler = (0.785398, 0.0, -0.785398)
    scene.collection.objects.link(cobj)
    return cobj

# 1. Entrance step closeup (focused on door, step, and left kačírek)
cam_ent = setup_cam('Cam_V_Entrance', mathutils.Vector((5.2, -0.2, 0.2)), 4.5)
scene.camera = cam_ent
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_entrance_step_closeup.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_entrance_step_closeup.png")

# 2. West side view (focused on left wall and kačírek strip)
cam_west = setup_cam('Cam_V_West', mathutils.Vector((0.0, 6.0, 0.5)), 12.0)
scene.camera = cam_west
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_west_side_view.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_west_side_view.png")

# 3. Terrace transition view (rear wall, kačírek ending at terrace paving)
cam_terrace = setup_cam('Cam_V_Terrace', mathutils.Vector((5.5, 12.5, 0.5)), 7.0)
scene.camera = cam_terrace
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_terrace_transition_view.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_terrace_transition_view.png")

# 4. Full house overview
scene.camera = bpy.data.objects['Isometric_Camera']
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_full_house_overview.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_full_house_overview.png")
