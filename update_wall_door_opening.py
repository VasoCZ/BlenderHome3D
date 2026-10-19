"""
update_wall_door_opening.py
Adjusts the structural wall opening in 'Exterior_Walls' to precisely contour and enclose
the installed entrance door assembly ('Door', 'ram', 'dvere', 'dvere.001'), eliminating
all gaps and covering the top of the door so it is no longer exposed from above.
"""

import os
import bpy
import bmesh
from mathutils import Vector

def main():
    blend_path = os.path.abspath("dum_pudorys.blend")
    print(f"Opening: {blend_path}")
    bpy.ops.wm.open_mainfile(filepath=blend_path)

    ew = bpy.data.objects.get("Exterior_Walls")
    if not ew:
        raise RuntimeError("Object 'Exterior_Walls' not found in scene!")

    bm = bmesh.new()
    bm.from_mesh(ew.data)

    def add_box(bm, x0, x1, y0, y1, z0, z1, mat_idx=0):
        verts = [
            bm.verts.new((x0, y0, z0)),
            bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)),
            bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)),
            bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)),
            bm.verts.new((x0, y1, z1)),
        ]
        faces = [
            [verts[0], verts[1], verts[2], verts[3]],  # bottom
            [verts[4], verts[7], verts[6], verts[5]],  # top
            [verts[0], verts[4], verts[5], verts[1]],  # front (-Y)
            [verts[2], verts[6], verts[7], verts[3]],  # back (+Y)
            [verts[0], verts[3], verts[7], verts[4]],  # left (-X)
            [verts[1], verts[5], verts[6], verts[2]],  # right (+X)
        ]
        created = []
        for fverts in faces:
            f = bm.faces.new(fverts)
            f.material_index = mat_idx
            created.append(f)
        return created

    # 1. Left tongue: enters the frame's side groove, eliminating the 6.5 cm side gap
    add_box(bm, 4.640, 4.705, 0.015, 0.123, 0.000, 1.745, mat_idx=0)

    # 2. Right tongue: enters the frame's side groove, eliminating the 6.5 cm side gap
    add_box(bm, 5.675, 5.740, 0.015, 0.123, 0.000, 1.745, mat_idx=0)

    # 3. Top wall lintel (nadpraží): spans across the full 0.365 m wall thickness at Z in [1.745, 1.800] m,
    # seamlessly enclosing the door header from above and unifying the wall top face at Z = 1.800 m.
    add_box(bm, 4.640, 5.740, 0.000, 0.365, 1.745, 1.800, mat_idx=0)

    # Merge coincident vertices and clean normals
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    bm.to_mesh(ew.data)
    bm.free()
    ew.data.update()
    print("Updated Exterior_Walls mesh successfully!")

    # Preserve Isometric_Camera
    iso_cam = bpy.data.objects.get("Isometric_Camera")
    if iso_cam:
        bpy.context.scene.camera = iso_cam

    # Save blend file
    bpy.ops.wm.save_mainfile()
    print("Saved 'dum_pudorys.blend'!")

    # Render verification views
    render_views(iso_cam)

def render_views(iso_cam):
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'PNG'

    # 1. Orthographic top-down view of entrance area
    cam_data1 = bpy.data.cameras.new("Cam_TopDown")
    cam_data1.type = 'ORTHO'
    cam_data1.ortho_scale = 3.2
    cam_obj1 = bpy.data.objects.new("Cam_TopDown", cam_data1)
    scene.collection.objects.link(cam_obj1)
    cam_obj1.location = Vector((5.19, 0.2, 5.0))
    cam_obj1.rotation_euler = (0, 0, 0)
    scene.camera = cam_obj1
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 800
    scene.render.filepath = os.path.abspath("wall_opening_topdown.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: wall_opening_topdown.png")

    # 2. Zoomed isometric view showing the enclosed door in room 1.01
    cam_data2 = bpy.data.cameras.new("Cam_IsoZoom")
    cam_data2.type = 'PERSP'
    if iso_cam:
        cam_data2.lens = iso_cam.data.lens
    cam_obj2 = bpy.data.objects.new("Cam_IsoZoom", cam_data2)
    scene.collection.objects.link(cam_obj2)
    target = Vector((5.19, 0.18, 0.9))
    if iso_cam:
        cam_dir = (iso_cam.location - Vector((5.0, 6.0, 0.0))).normalized()
        cam_obj2.location = target + cam_dir * 8.0
        cam_obj2.rotation_euler = iso_cam.rotation_euler
    scene.camera = cam_obj2
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("wall_opening_isometric.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: wall_opening_isometric.png")

    # 3. Full floor plan overview using user's Isometric_Camera
    if iso_cam:
        scene.camera = iso_cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = os.path.abspath("dum_pudorys_overview.png")
        bpy.ops.render.render(write_still=True)
        print("Rendered: dum_pudorys_overview.png")

    # 4. Front check view from driveway
    cam_data3 = bpy.data.cameras.new("Cam_Front")
    cam_obj3 = bpy.data.objects.new("Cam_Front", cam_data3)
    scene.collection.objects.link(cam_obj3)
    cam_obj3.location = Vector((5.19, -3.5, 1.3))
    cam_obj3.rotation_euler = (Vector((5.19, 0.2, 0.9)) - cam_obj3.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = cam_obj3
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.filepath = os.path.abspath("door_front_view.png")
    bpy.ops.render.render(write_still=True)
    print("Rendered: door_front_view.png")

    # Clean up temporary cameras
    for c in [cam_obj1, cam_obj2, cam_obj3]:
        bpy.data.objects.remove(c, do_unlink=True)
    for cd in [cam_data1, cam_data2, cam_data3]:
        bpy.data.cameras.remove(cd)

    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print("Final blend file resaved cleanly.")

if __name__ == "__main__":
    main()
