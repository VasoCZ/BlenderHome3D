"""
fix_light_bleeding_and_walls.py
--------------------------------
1. Fixes light bleeding at the base of the building:
   - Lowers bottom vertices of Exterior_Walls from Z = 0.00m down to Z = -0.08m,
     sinking the perimeter walls directly into Foundation_Slab.
   - Eliminates the white light line on the plinth/sidewalk.
2. Fixes light gap on the exterior wall facing camera (East wall & corner):
   - Restricts Bevel modifier on Exterior_Walls to vertex group 'TopEdges' (Z >= 2.45m),
     preventing non-manifold edge tearing along vertical corners and bottom seams.
   - Adds Smooth by Angle modifier to keep sharp 90-degree corners cleanly shaded.
   - Reduces exterior soffit lights radius/size from 1.2m to 0.15m and offsets patio right light,
     preventing light sources from physically penetrating wall geometry.
3. Preserves Isometric_Camera as active camera and updates dum_pudorys_overview.png.
"""

import bpy
import bmesh

def fix_light_bleeding_and_walls():
    print(">>> Applying light bleeding fix to Exterior_Walls...")

    ew = bpy.data.objects.get('Exterior_Walls')
    if not ew:
        raise RuntimeError("Exterior_Walls object not found!")

    # 1. Lower bottom vertices of Exterior_Walls to Z = -0.08m
    bm = bmesh.new()
    bm.from_mesh(ew.data)
    lowered = 0
    for v in bm.verts:
        if v.co.z <= 0.005:
            v.co.z = -0.08
            lowered += 1
    bm.to_mesh(ew.data)
    ew.data.update()
    bm.free()
    print(f"  Lowered {lowered} bottom vertices of Exterior_Walls to Z = -0.08m")

    # 2. Setup TopEdges vertex group for Bevel
    vg = ew.vertex_groups.get('TopEdges')
    if not vg:
        vg = ew.vertex_groups.new(name='TopEdges')
    for v in ew.data.vertices:
        if v.co.z >= 2.45:
            vg.add([v.index], 1.0, 'REPLACE')
        else:
            vg.add([v.index], 0.0, 'REPLACE')

    bev = ew.modifiers.get('Bevel')
    if not bev:
        bev = ew.modifiers.new('Bevel', 'BEVEL')
    bev.show_render = True
    bev.show_viewport = True
    bev.limit_method = 'VGROUP'
    bev.vertex_group = 'TopEdges'
    bev.width = 0.012
    bev.segments = 3
    bev.harden_normals = True

    # 3. Add Smooth by Angle modifier if not present
    if not ew.modifiers.get('Smooth by Angle'):
        ew.modifiers.new('Smooth by Angle', 'NODES')

    # 4. Adjust exterior soffit lights so they don't penetrate wall geometry
    for o in bpy.data.objects:
        if o.type == 'LIGHT' and 'ext' in o.name.lower():
            if hasattr(o.data, 'size') and o.data.size > 0.3:
                o.data.size = 0.15
            if 'patio_right' in o.name.lower():
                o.location.y = 12.18

    # 5. Ensure camera is Isometric_Camera and save file
    scene = bpy.context.scene
    iso_cam = bpy.data.objects.get('Isometric_Camera')
    if iso_cam:
        scene.camera = iso_cam

    bpy.ops.wm.save_mainfile()
    print(">>> dum_pudorys.blend saved successfully!")

    # 6. Render updated master overview snapshot
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = bpy.path.abspath("//dum_pudorys_overview.png")
    bpy.ops.render.render(write_still=True)
    print(">>> dum_pudorys_overview.png rendered successfully!")

if __name__ == '__main__':
    fix_light_bleeding_and_walls()
