import bpy
import mathutils

scene = bpy.context.scene
cam_dir = mathutils.Vector((0.5, 0.5, -0.70710678)).normalized()

def setup_cam(name, target, scale, dir_vec=cam_dir):
    existing = bpy.data.objects.get(name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)
    cdata = bpy.data.cameras.new(name)
    cdata.type = 'ORTHO'
    cdata.ortho_scale = scale
    cobj = bpy.data.objects.new(name, cdata)
    cobj.location = target - dir_vec * 30.0
    # Point camera at target
    direction = (target - cobj.location).normalized()
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cobj.rotation_euler = rot_quat.to_euler()
    scene.collection.objects.link(cobj)
    return cobj

# 1. South transition closeup: where the curb divides kačírek under 1.06 from driveway paving
cam_south_trans = setup_cam('Cam_V_South_Trans', mathutils.Vector((2.15, -0.4, 0.2)), 3.0)
scene.camera = cam_south_trans
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_curb_transition_south.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_curb_transition_south.png")

# 2. North transition closeup: looking from North-West at the terrace boundary (X=5.0, Y=12.0 to 12.72)
# Let's point from north-east or north looking towards terrace junction
north_cam_dir = mathutils.Vector((-0.5, -0.5, -0.6)).normalized()
cam_north_trans = setup_cam('Cam_V_North_Trans', mathutils.Vector((5.0, 12.35, 0.2)), 3.5, north_cam_dir)
scene.camera = cam_north_trans
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_curb_transition_north.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_curb_transition_north.png")

# 3. Full house overview
scene.camera = bpy.data.objects['Isometric_Camera']
scene.render.filepath = r'C:\Users\Vaso\Antigravity\Project blender\kacirek_full_house_overview.png'
bpy.ops.render.render(write_still=True)
print("Rendered: kacirek_full_house_overview.png")
