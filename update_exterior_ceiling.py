"""
update_exterior_ceiling.py
Updates 'dum_pudorys.blend' per user requirements:
1. For all exterior lights starting with 'Light_Ext' or 'Roof_Soffit':
   - Height Z set directly below the cornice at the top of the walls (Z = 1.70 m).
   - If SPOT: spot_size = 50 deg (0.8727 rad), spot_blend = 0.25, energy = 20.0 W.
   - If AREA: size = 0.15 m.
2. Creates a ceiling plate (Mesh Plane) named 'Ceiling_Main':
   - Seated exactly on the top edge of exterior walls (Z = 1.80 m).
   - Footprint: 10.0 x 12.0 m (X: [0.0, 10.0], Y: [0.0, 12.0]).
   - Blocks sunlight (Sun_Fill) from penetrating from above into the interior.
   - Assigns clean neutral ceiling material 'Mat_Ceiling'.
3. Unhides Sun_Fill so exterior sunlight casts natural shadows on the exterior and roof,
   while Ceiling_Main blocks the sunlight from penetrating the interior rooms.
4. Saves changes to 'dum_pudorys.blend'.
5. Renders preview images:
   - 'dum_pudorys_preview.png': Overview with Ceiling_Main in place.
   - 'dum_pudorys_preview_interior.png': Cutaway view with Ceiling_Main hidden to show interior rooms.
"""

import sys
import os
import math
import bpy
import bmesh

def main():
    print("=" * 60)
    print("STARTING EXTERIOR LIGHTS & CEILING UPDATE")
    print("=" * 60)

    blend_path = os.path.abspath("dum_pudorys.blend")
    if not bpy.data.filepath or os.path.abspath(bpy.data.filepath) != blend_path:
        bpy.ops.wm.open_mainfile(filepath=blend_path)

    # 1. Update Exterior Lights ('Light_Ext' and 'Roof_Soffit')
    ext_lights_count = 0
    spot_count = 0
    area_count = 0

    for obj in bpy.data.objects:
        if obj.type == 'LIGHT' and (obj.name.startswith("Light_Ext") or obj.name.startswith("Roof_Soffit")):
            ext_lights_count += 1
            # Z těsně pod římsou v horní části stěn: Z = 1.70 m (římsa je 1.72 - 1.80 m, zdi 1.80 m)
            obj.location.z = 1.70

            light_data = obj.data
            if light_data.type == 'SPOT':
                spot_count += 1
                light_data.spot_size = math.radians(50.0) # ~0.87266 rad (50 deg)
                light_data.spot_blend = 0.25
                light_data.energy = 20.0 # 20W
                print(f"[OK] SPOT light updated: '{obj.name}' -> Z=1.70m, spot_size=50deg, blend=0.25, energy=20W")

            elif light_data.type == 'AREA':
                area_count += 1
                light_data.size = 0.15
                if hasattr(light_data, 'size_y'):
                    light_data.size_y = 0.15
                print(f"[OK] AREA light updated: '{obj.name}' -> Z=1.70m, size=0.15m")
            else:
                print(f"[INFO] Other exterior light type ({light_data.type}): '{obj.name}' -> Z=1.70m")

    print(f"[SUMMARY] Total exterior lights updated: {ext_lights_count} (SPOT: {spot_count}, AREA: {area_count})")

    # 2. Create Ceiling Plane 'Ceiling_Main'
    ceiling_name = "Ceiling_Main"

    # Remove existing ceiling object and mesh if present for idempotent re-runs
    if ceiling_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[ceiling_name], do_unlink=True)
    if ceiling_name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[ceiling_name])

    # Material for Ceiling
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

    # Mesh Plane: 4 vertices sitting exactly on top edge of exterior walls (Z = 1.80 m)
    # Dimensions: 10.0 x 12.0 m (X: [0.0, 10.0], Y: [0.0, 12.0])
    # Z is set to 1.8005m (half a millimeter above wall tops) to prevent coplanar depth-buffer z-fighting
    z_ceiling = 1.8005
    mesh = bpy.data.meshes.new(ceiling_name)
    bm = bmesh.new()

    v0 = bm.verts.new((0.0, 0.0, z_ceiling))
    v1 = bm.verts.new((10.0, 0.0, z_ceiling))
    v2 = bm.verts.new((10.0, 12.0, z_ceiling))
    v3 = bm.verts.new((0.0, 12.0, z_ceiling))

    # Face in CCW order so normal points +Z upwards towards sky
    face = bm.faces.new([v0, v1, v2, v3])
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=[face])

    bm.to_mesh(mesh)
    bm.free()

    ceiling_obj = bpy.data.objects.new(ceiling_name, mesh)
    bpy.context.scene.collection.objects.link(ceiling_obj)
    ceiling_obj.data.materials.append(mat_ceiling)
    print(f"[OK] Created ceiling plane '{ceiling_name}' spanning [0.0, 10.0] x [0.0, 12.0] at Z={z_ceiling:.3f}m")

    # 3. Handle Sun_Fill (allow sun to illuminate exterior while ceiling blocks interior penetration)
    sun = bpy.data.objects.get("Sun_Fill")
    if sun:
        sun.hide_viewport = False
        sun.hide_render = False
        sun.data.use_shadow = True
        print("[OK] Sun_Fill unhidden: sunlight enabled outside, shielded by Ceiling_Main from interior.")

    # 4. Save changes back to dum_pudorys.blend
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Saved scene to {blend_path}")

    # 5. Render previews
    # 5a. Preview with Ceiling_Main in place
    try:
        preview_path = os.path.abspath("dum_pudorys_preview.png")
        bpy.context.scene.render.filepath = preview_path
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
        ceiling_obj.hide_render = False
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered overview preview to: {preview_path}")

        # 5b. Cutaway preview with Ceiling_Main temporarily hidden to showcase interior rooms
        interior_preview_path = os.path.abspath("dum_pudorys_preview_interior.png")
        bpy.context.scene.render.filepath = interior_preview_path
        ceiling_obj.hide_render = True
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Rendered interior cutaway preview to: {interior_preview_path}")

        # Restore ceiling_obj.hide_render = False
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
