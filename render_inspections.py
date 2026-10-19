import bpy
import os
from mathutils import Vector

def render_ortho_inspections():
    scene = bpy.context.scene
    
    # Cam 1: Front view of West Wall (camera at X = 2.0, Y = 10.76, Z = 0.9, looking at X = 0.365, Y = 10.76, Z = 0.9)
    cam_data1 = bpy.data.cameras.new('Inspect_West')
    cam_obj1 = bpy.data.objects.new('Inspect_West', cam_data1)
    scene.collection.objects.link(cam_obj1)
    cam_obj1.location = Vector((2.2, 10.76, 0.9))
    target1 = Vector((0.365, 10.76, 0.9))
    direction1 = target1 - cam_obj1.location
    cam_obj1.rotation_euler = direction1.to_track_quat('-Z', 'Y').to_euler()
    cam_data1.type = 'PERSP'
    cam_data1.lens = 35
    scene.camera = cam_obj1
    scene.render.filepath = os.path.abspath('inspect_west_wall.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj1, do_unlink=True)
    bpy.data.cameras.remove(cam_data1, do_unlink=True)

    # Cam 2: Front view of South Wall (camera at X = 1.2, Y = 11.2, Z = 0.9, looking at X = 1.2, Y = 9.900, Z = 0.9)
    cam_data2 = bpy.data.cameras.new('Inspect_South')
    cam_obj2 = bpy.data.objects.new('Inspect_South', cam_data2)
    scene.collection.objects.link(cam_obj2)
    cam_obj2.location = Vector((1.2, 11.2, 0.9))
    target2 = Vector((1.2, 9.900, 0.9))
    direction2 = target2 - cam_obj2.location
    cam_obj2.rotation_euler = direction2.to_track_quat('-Z', 'Y').to_euler()
    cam_data2.type = 'PERSP'
    cam_data2.lens = 35
    scene.camera = cam_obj2
    scene.render.filepath = os.path.abspath('inspect_south_wall.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj2, do_unlink=True)
    bpy.data.cameras.remove(cam_data2, do_unlink=True)

    # Cam 3: Corner view (camera at X = 2.2, Y = 11.3, Z = 1.2, looking directly at inner corner X = 0.365, Y = 9.900, Z = 0.8)
    cam_data3 = bpy.data.cameras.new('Inspect_Corner')
    cam_obj3 = bpy.data.objects.new('Inspect_Corner', cam_data3)
    scene.collection.objects.link(cam_obj3)
    cam_obj3.location = Vector((2.2, 11.3, 1.2))
    target3 = Vector((0.365, 9.900, 0.8))
    direction3 = target3 - cam_obj3.location
    cam_obj3.rotation_euler = direction3.to_track_quat('-Z', 'Y').to_euler()
    cam_data3.type = 'PERSP'
    cam_data3.lens = 35
    scene.camera = cam_obj3
    scene.render.filepath = os.path.abspath('inspect_corner.png')
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam_obj3, do_unlink=True)
    bpy.data.cameras.remove(cam_data3, do_unlink=True)

    print("Inspection renders complete!")

if __name__ == '__main__':
    render_ortho_inspections()
