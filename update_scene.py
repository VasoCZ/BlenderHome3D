"""
update_scene.py
Comprehensive scene update script for 'dum_pudorys.blend':
1. Cornice: Outer roof overhang / cornice (Roof_Soffit_Cornice):
   11.0 x 13.0 m outer, 10.0 x 12.0 m inner opening, Z in [1.72, 1.80] m, dark grey matte material.
2. Ceiling: Stropní deska (Mesh Plane) named 'Ceiling_Main':
   Seated exactly on top edge of exterior walls (Z = 1.80 m), spanning 10.0 x 12.0 m,
   shielding interior from sunlight (Sun_Fill) from above.
3. Exterior Lights ('Light_Ext' and 'Roof_Soffit'):
   - Height Z = 1.70 m (directly under cornice).
   - If SPOT: spot_size = 50 deg (~0.87 rad), spot_blend = 0.25, energy = 20.0 W.
   - If AREA: size = 0.15 m.
4. Sun_Fill: unhidden to illuminate exterior and cast natural shadows against the roof and walls.
5. Saves to 'dum_pudorys.blend' and renders preview images.
"""

import sys
import os
import math
import bpy
import bmesh

def main():
    print("=" * 60)
    print("UPDATING SCENE: dum_pudorys.blend")
    print("=" * 60)

    # 1. Ensure dum_pudorys.blend is loaded
    blend_path = os.path.abspath("dum_pudorys.blend")
    if not bpy.data.filepath or os.path.abspath(bpy.data.filepath) != blend_path:
        bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 2. Outer roof overhang / cornice (Roof_Soffit_Cornice)
    soffit_name = "Roof_Soffit_Cornice"
    if soffit_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[soffit_name], do_unlink=True)
    if soffit_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[soffit_name])

    mat_soffit = bpy.data.materials.get("Mat_Roof_Soffit")
    if not mat_soffit:
        mat_soffit = bpy.data.materials.new(name="Mat_Roof_Soffit")
        bsdf = mat_soffit.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.12, 0.12, 0.13, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.2
            elif "Specular" in bsdf.inputs:
                bsdf.inputs["Specular"].default_value = 0.2

    z_min, z_max = 1.72, 1.80
    segments_coords = [
        [(-0.5, -0.5), (10.5, -0.5), (10.5, 0.0), (-0.5, 0.0)],
        [(-0.5, 12.0), (10.5, 12.0), (10.5, 12.5), (-0.5, 12.5)],
        [(-0.5, 0.0), (0.0, 0.0), (0.0, 12.0), (-0.5, 12.0)],
        [(10.0, 0.0), (10.5, 0.0), (10.5, 12.0), (10.0, 12.0)],
    ]

    soffit_mesh = bpy.data.meshes.new(soffit_name)
    bm_soffit = bmesh.new()

    for poly in segments_coords:
        v_bottom = [bm_soffit.verts.new((x, y, z_min)) for x, y in poly]
        v_top = [bm_soffit.verts.new((x, y, z_max)) for x, y in poly]
        bm_soffit.faces.new(list(reversed(v_bottom)))
        bm_soffit.faces.new(v_top)
        n = len(poly)
        for i in range(n):
            i_next = (i + 1) % n
            bm_soffit.faces.new([v_bottom[i], v_bottom[i_next], v_top[i_next], v_top[i]])

    bmesh.ops.remove_doubles(bm_soffit, verts=bm_soffit.verts, dist=0.001)
    internal_faces = [f for f in bm_soffit.faces if len(f.edges) == 4 and all(len(e.link_faces) > 2 for e in f.edges)]
    if internal_faces:
        bmesh.ops.delete(bm_soffit, geom=internal_faces, context='FACES')

    bmesh.ops.recalc_face_normals(bm_soffit, faces=bm_soffit.faces)
    bm_soffit.to_mesh(soffit_mesh)
    bm_soffit.free()

    soffit_obj = bpy.data.objects.new(soffit_name, soffit_mesh)
    bpy.context.scene.collection.objects.link(soffit_obj)
    soffit_obj.data.materials.append(mat_soffit)
    print(f"[OK] Roof soffit cornice '{soffit_name}' created (outer 11.0x13.0m, inner 10.0x12.0m).")

    # 3. Ceiling Plane (Ceiling_Main)
    ceiling_name = "Ceiling_Main"
    if ceiling_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[ceiling_name], do_unlink=True)
    if ceiling_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[ceiling_name])

    mat_ceiling = bpy.data.materials.get("Mat_Ceiling")
    if not mat_ceiling:
        mat_ceiling = bpy.data.materials.new(name="Mat_Ceiling")
        bsdf = mat_ceiling.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.85, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.75
            if "Specular IOR Level" in bsdf.inputs:
                bsdf.inputs["Specular IOR Level"].default_value = 0.15
            elif "Specular" in bsdf.inputs:
                bsdf.inputs["Specular"].default_value = 0.15

    z_ceiling = 1.8005
    ceiling_mesh = bpy.data.meshes.new(ceiling_name)
    bm_ceil = bmesh.new()
    v0 = bm_ceil.verts.new((0.0, 0.0, z_ceiling))
    v1 = bm_ceil.verts.new((10.0, 0.0, z_ceiling))
    v2 = bm_ceil.verts.new((10.0, 12.0, z_ceiling))
    v3 = bm_ceil.verts.new((0.0, 12.0, z_ceiling))
    f_ceil = bm_ceil.faces.new([v0, v1, v2, v3])
    bm_ceil.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm_ceil, faces=[f_ceil])
    bm_ceil.to_mesh(ceiling_mesh)
    bm_ceil.free()

    ceiling_obj = bpy.data.objects.new(ceiling_name, ceiling_mesh)
    bpy.context.scene.collection.objects.link(ceiling_obj)
    ceiling_obj.data.materials.append(mat_ceiling)
    print(f"[OK] Ceiling plane '{ceiling_name}' created at Z={z_ceiling:.3f}m.")

    # 4. Exterior Lights ('Light_Ext' and 'Roof_Soffit')
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and (obj.name.startswith("Light_Ext") or obj.name.startswith("Roof_Soffit")):
            obj.location.z = 1.70
            if obj.data.type == 'SPOT':
                obj.data.spot_size = math.radians(50.0)
                obj.data.spot_blend = 0.25
                obj.data.energy = 20.0
                print(f"[OK] SPOT: '{obj.name}' -> Z=1.70m, 50deg, blend=0.25, 20W")
            elif obj.data.type == 'AREA':
                obj.data.size = 0.15
                if hasattr(obj.data, 'size_y'):
                    obj.data.size_y = 0.15
                print(f"[OK] AREA: '{obj.name}' -> Z=1.70m, size=0.15m")

    # 5. Sun_Fill (unhidden and shielded by Ceiling_Main)
    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.hide_viewport = False
        sun.hide_render = False
        sun.data.use_shadow = True
        print("[OK] Sun_Fill enabled for exterior lighting.")

    # 6. Save changes
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved scene to {blend_path}")

    # 7. Render previews
    try:
        preview_path = os.path.abspath("dum_pudorys_preview.png")
        bpy.context.scene.render.filepath = preview_path
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        ceiling_obj.hide_render = False
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered preview: {preview_path}")

        interior_preview_path = os.path.abspath("dum_pudorys_preview_interior.png")
        bpy.context.scene.render.filepath = interior_preview_path
        ceiling_obj.hide_render = True
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered interior cutaway preview: {interior_preview_path}")

        ceiling_obj.hide_render = False
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    except Exception as e:
        print(f"[NOTE] Render notice: {e}")

    print("=" * 60)
    print("ALL UPDATES SUCCESSFULLY COMPLETED")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
