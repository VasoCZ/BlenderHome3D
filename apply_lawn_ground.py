import bpy
import bmesh
import mathutils
import os

def main():
    blend_path_asset = r'C:\Users\Vaso\blenderkit_data\materials\grass_0d3a2b51-7036-4083-a6b3-dc0cb7e0e7f5\grass_2K_1edd5445-fe57-4266-99b6-c11be039d53e.blend'
    
    # 1. Load Grass material
    if 'Grass' not in bpy.data.materials:
        with bpy.data.libraries.load(blend_path_asset) as (data_from, data_to):
            data_to.materials = ['Grass']
    grass_mat = bpy.data.materials['Grass']
    
    # Set realistic mapping scale: (0.5, 0.5, 0.5) -> 2m tile repeat
    mapping_node = grass_mat.node_tree.nodes.get('Mapping')
    if mapping_node:
        mapping_node.inputs['Scale'].default_value = (0.5, 0.5, 0.5)
        print("Set Mapping scale to (0.5, 0.5, 0.5)")

    # 2. Clean up existing Lawn_Ground if present
    if 'Lawn_Ground' in bpy.data.objects:
        obj_old = bpy.data.objects['Lawn_Ground']
        mesh_old = obj_old.data
        bpy.data.objects.remove(obj_old)
        bpy.data.meshes.remove(mesh_old)

    # 3. Create Lawn_Ground grid
    # Bounds: X in [-8.0, 20.0], Y in [-15.0, 25.0], Z = -0.025m
    x_min, x_max = -8.0, 20.0
    y_min, y_max = -15.0, 25.0
    z_level = -0.025

    mesh_plane = bpy.data.meshes.new('Lawn_Ground')
    bm = bmesh.new()
    
    x_segs = int(round(x_max - x_min))
    y_segs = int(round(y_max - y_min))
    
    bmesh.ops.create_grid(bm, x_segments=x_segs, y_segments=y_segs, size=1.0)
    
    x_center = (x_min + x_max) / 2.0
    x_half = (x_max - x_min) / 2.0
    y_center = (y_min + y_max) / 2.0
    y_half = (y_max - y_min) / 2.0
    
    for v in bm.verts:
        v.co.x = x_center + v.co.x * x_half
        v.co.y = y_center + v.co.y * y_half
        v.co.z = z_level
        
    bm.to_mesh(mesh_plane)
    bm.free()

    lawn_obj = bpy.data.objects.new('Lawn_Ground', mesh_plane)
    bpy.context.scene.collection.objects.link(lawn_obj)

    # 4. Create Cutter object for the property footprint (inset 2cm into 8cm curbs)
    cutter_mesh = bpy.data.meshes.new('CutterMesh')
    bm = bmesh.new()
    poly_pts = [
        (2.130, -9.060),
        (8.250, -9.060),
        (8.250, -1.260),
        (11.260, -1.260),
        (11.260, 13.260),
        (10.060, 13.260),
        (10.060, 18.060),
        (4.940, 18.060),
        (4.940, 12.782),
        (-0.675, 12.782),
        (-0.675, -0.818),
        (2.130, -0.818),
    ]
    verts_bottom = [bm.verts.new((x, y, -1.0)) for x, y in poly_pts]
    face_bottom = bm.faces.new(verts_bottom)
    geom = bmesh.ops.extrude_face_region(bm, geom=[face_bottom])
    verts_top = [ele for ele in geom['geom'] if isinstance(ele, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=mathutils.Vector((0, 0, 2.0)), verts=verts_top)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(cutter_mesh)
    bm.free()

    cutter_obj = bpy.data.objects.new('Cutter', cutter_mesh)
    bpy.context.scene.collection.objects.link(cutter_obj)

    # 5. Apply Boolean Difference
    mod = lawn_obj.modifiers.new('Boolean', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.operand_type = 'OBJECT'
    mod.object = cutter_obj
    mod.solver = 'EXACT'

    bpy.context.view_layer.objects.active = lawn_obj
    bpy.ops.object.modifier_apply(modifier='Boolean')
    
    bpy.data.objects.remove(cutter_obj)
    bpy.data.meshes.remove(cutter_mesh)

    # 6. Planar UV unwrap: U = X, V = Y
    mesh = lawn_obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name='UVMap')
    uv_layer = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        for loop_idx in poly.loop_indices:
            v_idx = mesh.loops[loop_idx].vertex_index
            v = mesh.vertices[v_idx].co
            uv_layer[loop_idx].uv = (v.x, v.y)

    # 7. Assign Grass material
    if not lawn_obj.material_slots:
        lawn_obj.data.materials.append(grass_mat)
    else:
        lawn_obj.material_slots[0].material = grass_mat

    print(f"Lawn_Ground successfully created and configured:")
    print(f"  Vertices: {len(lawn_obj.data.vertices)}")
    print(f"  Faces: {len(lawn_obj.data.polygons)}")
    print(f"  Bounds: X=[{min(v.co.x for v in lawn_obj.data.vertices):.2f}, {max(v.co.x for v in lawn_obj.data.vertices):.2f}], Y=[{min(v.co.y for v in lawn_obj.data.vertices):.2f}, {max(v.co.y for v in lawn_obj.data.vertices):.2f}], Z={z_level:.3f}")
    print(f"  Material: {lawn_obj.material_slots[0].material.name}")

    # 8. Save mainfile
    bpy.ops.wm.save_mainfile()
    print("Mainfile 'dum_pudorys.blend' saved successfully.")

if __name__ == '__main__':
    main()
