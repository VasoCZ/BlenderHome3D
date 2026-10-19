import bpy
import os
from mathutils import Vector

def render_all_previews():
    scene = bpy.context.scene

    # 1. Zoom top transition (where wood meets grey on west wall)
    c_data = bpy.data.cameras.new('C1')
    c_obj = bpy.data.objects.new('C1', c_data)
    scene.collection.objects.link(c_obj)
    c_obj.location = Vector((1.8, 10.890, 2.5))
    target = Vector((0.365, 10.890, 1.8))
    c_obj.rotation_euler = (target - c_obj.location).to_track_quat('-Z', 'Y').to_euler()
    c_data.type = 'PERSP'
    c_data.lens = 50
    scene.camera = c_obj
    scene.render.filepath = os.path.abspath('zoom_top_transition.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c_obj, do_unlink=True)
    bpy.data.cameras.remove(c_data, do_unlink=True)

    # 2. South wall overhead view (where wood meets grey on south wall)
    l_data = bpy.data.lights.new('L1', 'POINT')
    l_data.energy = 50.0
    l_obj = bpy.data.objects.new('L1', l_data)
    scene.collection.objects.link(l_obj)
    l_obj.location = Vector((1.5, 10.5, 2.5))

    c_data = bpy.data.cameras.new('C2')
    c_obj = bpy.data.objects.new('C2', c_data)
    scene.collection.objects.link(c_obj)
    c_obj.location = Vector((1.5, 11.2, 2.4))
    target = Vector((1.4, 9.9, 1.5))
    c_obj.rotation_euler = (target - c_obj.location).to_track_quat('-Z', 'Y').to_euler()
    c_data.type = 'PERSP'
    c_data.lens = 45
    scene.camera = c_obj
    scene.render.filepath = os.path.abspath('inspect_south_overhead.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c_obj, do_unlink=True)
    bpy.data.cameras.remove(c_data, do_unlink=True)
    bpy.data.objects.remove(l_obj, do_unlink=True)
    bpy.data.lights.remove(l_data, do_unlink=True)

    # 3. Viewport simulation render (LookDev with ambient top sun)
    l_data2 = bpy.data.lights.new('LookDev_Sun', 'SUN')
    l_data2.energy = 3.0
    l_obj2 = bpy.data.objects.new('LookDev_Sun', l_data2)
    scene.collection.objects.link(l_obj2)
    l_obj2.rotation_euler = (0.5, 0.2, 0.8)

    c_data3 = bpy.data.cameras.new('LookDev_Cam')
    c_obj3 = bpy.data.objects.new('LookDev_Cam', c_data3)
    scene.collection.objects.link(c_obj3)
    c_obj3.location = Vector((3.5, 9.0, 3.8))
    target3 = Vector((1.3, 10.7, 1.0))
    c_obj3.rotation_euler = (target3 - c_obj3.location).to_track_quat('-Z', 'Y').to_euler()
    c_data3.type = 'PERSP'
    c_data3.lens = 35
    scene.camera = c_obj3
    scene.render.filepath = os.path.abspath('viewport_sim_render.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c_obj3, do_unlink=True)
    bpy.data.cameras.remove(c_data3, do_unlink=True)
    bpy.data.objects.remove(l_obj2, do_unlink=True)
    bpy.data.lights.remove(l_data2, do_unlink=True)

    # 4. bathroom_closeup.png
    c_data4 = bpy.data.cameras.new('C4')
    c_obj4 = bpy.data.objects.new('C4', c_data4)
    scene.collection.objects.link(c_obj4)
    c_obj4.location = Vector((4.5, 8.5, 4.0))
    target4 = Vector((1.6, 10.7, 0.9))
    c_obj4.rotation_euler = (target4 - c_obj4.location).to_track_quat('-Z', 'Y').to_euler()
    c_data4.type = 'PERSP'
    c_data4.lens = 40
    scene.camera = c_obj4
    scene.render.filepath = os.path.abspath('bathroom_closeup.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c_obj4, do_unlink=True)
    bpy.data.cameras.remove(c_data4, do_unlink=True)

    # 5. bathroom_south_wall.png
    c_data5 = bpy.data.cameras.new('C5')
    c_obj5 = bpy.data.objects.new('C5', c_data5)
    scene.collection.objects.link(c_obj5)
    c_obj5.location = Vector((0.5, 12.5, 3.5))
    target5 = Vector((1.8, 10.0, 0.9))
    c_obj5.rotation_euler = (target5 - c_obj5.location).to_track_quat('-Z', 'Y').to_euler()
    c_data5.type = 'PERSP'
    c_data5.lens = 35
    scene.camera = c_obj5
    scene.render.filepath = os.path.abspath('bathroom_south_wall.png')
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(c_obj5, do_unlink=True)
    bpy.data.cameras.remove(c_data5, do_unlink=True)

    # 6. dum_pudorys_dobra_preview.png (Full overview with scene camera)
    orig_cam = bpy.data.objects.get('Isometric_Camera')
    if orig_cam:
        scene.camera = orig_cam
        scene.render.filepath = os.path.abspath('dum_pudorys_dobra_preview.png')
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        bpy.ops.render.render(write_still=True)

    print("All renders completed successfully!")

if __name__ == '__main__':
    render_all_previews()
