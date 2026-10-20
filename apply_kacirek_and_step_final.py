"""
apply_kacirek_and_step_final.py
================================
1. Sets up Mat_Kacirek_PBR with Gravel023 PBR textures (Color, AO, Roughness, NormalGL).
2. Sets up Mat_Entrance_Step with architectural smooth concrete.
3. Bisects Foundation_Slab cleanly at:
   - X = 0.00 (exterior west wall line)
   - X = 4.64 (entrance door left edge)
4. Assigns:
   - Mat_Kacirek_PBR to the left side perimeter:
     * Front left: X in [-1.20, 4.64], Y in [-1.20, 0.00]
     * West side: X in [-1.20, 0.00], Y in [0.00, 11.64]
     * North rear left (up to terrace): X in [-1.20, 5.00], Y in [11.64, 13.20]
   - Paving Stones to all other outdoor areas (front walkway/driveway, terrace, right side).
5. Sets world UV projection on Foundation_Slab for both materials so textures are perfectly scaled.
6. Builds Step_Front_Entrance:
   - X in [4.64, 5.85], Y in [-0.55, 0.14], Z in [0.00, 0.14]
   - Top edge beveled, material Mat_Entrance_Step
7. Saves dum_pudorys.blend
"""

import bpy, bmesh, os
from mathutils import Vector

def run():
    print("=== Applying Kačírek (Gravel) and Entrance Step ===")
    
    # -------------------------------------------------------------------------
    # 1. PBR Gravel Material (Mat_Kacirek_PBR)
    # -------------------------------------------------------------------------
    gravel_dir = r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\gravel-023"
    mat_kacirek = bpy.data.materials.get("Mat_Kacirek_PBR")
    if not mat_kacirek:
        mat_kacirek = bpy.data.materials.new("Mat_Kacirek_PBR")
        
    mat_kacirek.use_nodes = True
    nodes = mat_kacirek.node_tree.nodes
    links = mat_kacirek.node_tree.links
    nodes.clear()
    
    out = nodes.new("ShaderNodeOutputMaterial")
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    
    tex_coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (3.5, 3.5, 1.0)
    links.new(tex_coord.outputs["UV"], mapping.inputs["Vector"])
    
    # Color + AO
    img_col = bpy.data.images.load(os.path.join(gravel_dir, "Gravel023_2K-JPG_Color.jpg"))
    node_col = nodes.new("ShaderNodeTexImage")
    node_col.image = img_col
    links.new(mapping.outputs["Vector"], node_col.inputs["Vector"])
    
    img_ao = bpy.data.images.load(os.path.join(gravel_dir, "Gravel023_2K-JPG_AmbientOcclusion.jpg"))
    node_ao = nodes.new("ShaderNodeTexImage")
    node_ao.image = img_ao
    node_ao.image.colorspace_settings.name = "Non-Color"
    links.new(mapping.outputs["Vector"], node_ao.inputs["Vector"])
    
    mix_ao = nodes.new("ShaderNodeMix")
    mix_ao.data_type = "RGBA"
    mix_ao.blend_type = "MULTIPLY"
    mix_ao.inputs["Factor"].default_value = 0.6
    links.new(node_col.outputs["Color"], mix_ao.inputs[6])
    links.new(node_ao.outputs["Color"], mix_ao.inputs[7])
    links.new(mix_ao.outputs[2], bsdf.inputs["Base Color"])
    
    # Roughness
    img_rough = bpy.data.images.load(os.path.join(gravel_dir, "Gravel023_2K-JPG_Roughness.jpg"))
    node_rough = nodes.new("ShaderNodeTexImage")
    node_rough.image = img_rough
    node_rough.image.colorspace_settings.name = "Non-Color"
    links.new(mapping.outputs["Vector"], node_rough.inputs["Vector"])
    links.new(node_rough.outputs["Color"], bsdf.inputs["Roughness"])
    
    # Normal
    img_norm = bpy.data.images.load(os.path.join(gravel_dir, "Gravel023_2K-JPG_NormalGL.jpg"))
    node_norm_img = nodes.new("ShaderNodeTexImage")
    node_norm_img.image = img_norm
    node_norm_img.image.colorspace_settings.name = "Non-Color"
    links.new(mapping.outputs["Vector"], node_norm_img.inputs["Vector"])
    
    node_norm = nodes.new("ShaderNodeNormalMap")
    node_norm.inputs["Strength"].default_value = 1.6
    links.new(node_norm_img.outputs["Color"], node_norm.inputs["Color"])
    links.new(node_norm.outputs["Normal"], bsdf.inputs["Normal"])
    
    # -------------------------------------------------------------------------
    # 2. Entrance Step Material (Mat_Entrance_Step)
    # -------------------------------------------------------------------------
    mat_step = bpy.data.materials.get("Mat_Entrance_Step")
    if not mat_step:
        mat_step = bpy.data.materials.new("Mat_Entrance_Step")
    mat_step.use_nodes = True
    ns = mat_step.node_tree.nodes
    ls = mat_step.node_tree.links
    ns.clear()
    out_s = ns.new("ShaderNodeOutputMaterial")
    bsdf_s = ns.new("ShaderNodeBsdfPrincipled")
    bsdf_s.inputs["Base Color"].default_value = (0.75, 0.75, 0.74, 1.0) # Architectural concrete
    bsdf_s.inputs["Roughness"].default_value = 0.40
    ls.new(bsdf_s.outputs["BSDF"], out_s.inputs["Surface"])
    
    # -------------------------------------------------------------------------
    # 3. Foundation_Slab bisect & material assignment
    # -------------------------------------------------------------------------
    slab = bpy.data.objects.get("Foundation_Slab")
    if not slab:
        raise ValueError("Foundation_Slab object not found!")
        
    mat_paving = bpy.data.materials.get("Paving Stones")
    
    # Ensure slots: Slot 0 = Paving Stones, Slot 1 = Mat_Kacirek_PBR
    slab.data.materials.clear()
    slab.data.materials.append(mat_paving)
    slab.data.materials.append(mat_kacirek)
    paving_slot_idx = 0
    kacirek_slot_idx = 1
    
    bm = bmesh.new()
    bm.from_mesh(slab.data)
    
    # Bisect at X = 0.00 (exterior west wall line)
    geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((0.0, 0.0, 0.0)), plane_no=Vector((1.0, 0.0, 0.0)), clear_inner=False, clear_outer=False)
    
    # Bisect at X = 4.64 (entrance door left edge)
    geom = bm.faces[:] + bm.edges[:] + bm.verts[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((4.64, 0.0, 0.0)), plane_no=Vector((1.0, 0.0, 0.0)), clear_inner=False, clear_outer=False)
    
    # Ensure UV layer
    uv_layer = bm.loops.layers.uv.verify()
    
    kacirek_count = 0
    paving_count = 0
    
    for f in bm.faces:
        cx = sum(v.co.x for v in f.verts) / len(f.verts)
        cy = sum(v.co.y for v in f.verts) / len(f.verts)
        
        is_kacirek = False
        # 1. Front left: from front door left edge (X <= 4.64) to west edge (X >= -1.20), Y in [-1.20, 0.00]
        if -1.21 <= cx <= 4.64 and -1.21 <= cy <= 0.01:
            is_kacirek = True
        # 2. West side strip: X in [-1.21, 0.00], Y in [0.00, 11.64]
        elif -1.21 <= cx <= 0.01 and -0.01 <= cy <= 12.01:
            is_kacirek = True
        # 3. North left strip: X in [-1.21, 5.00], Y in [11.64, 13.50] (up to left edge of terrace at X=5.00)
        elif -1.21 <= cx <= 5.01 and 11.63 <= cy <= 13.50:
            is_kacirek = True
            
        if is_kacirek:
            f.material_index = kacirek_slot_idx
            kacirek_count += 1
        else:
            f.material_index = paving_slot_idx
            paving_count += 1
            
        # World UV projection
        for loop in f.loops:
            co = loop.vert.co
            loop[uv_layer].uv = (co.x, co.y)
            
    bm.to_mesh(slab.data)
    bm.free()
    slab.data.update()
    print(f"Foundation_Slab updated: {kacirek_count} kačírek faces, {paving_count} paving faces.")
    
    # -------------------------------------------------------------------------
    # 4. Build Step_Front_Entrance object
    # -------------------------------------------------------------------------
    old_step = bpy.data.objects.get("Step_Front_Entrance")
    if old_step:
        bpy.data.objects.remove(old_step, do_unlink=True)
        
    x0, x1 = 4.64, 5.85
    y0, y1 = -0.55, 0.14
    z0, z1 = 0.00, 0.14 # 14cm riser
    
    bm_step = bmesh.new()
    v0 = bm_step.verts.new(Vector((x0, y0, z0)))
    v1 = bm_step.verts.new(Vector((x1, y0, z0)))
    v2 = bm_step.verts.new(Vector((x1, y1, z0)))
    v3 = bm_step.verts.new(Vector((x0, y1, z0)))
    v4 = bm_step.verts.new(Vector((x0, y0, z1)))
    v5 = bm_step.verts.new(Vector((x1, y0, z1)))
    v6 = bm_step.verts.new(Vector((x1, y1, z1)))
    v7 = bm_step.verts.new(Vector((x0, y1, z1)))
    
    bm_step.faces.new([v4, v5, v6, v7]) # Top
    bm_step.faces.new([v0, v1, v5, v4]) # Front riser
    bm_step.faces.new([v1, v2, v6, v5]) # Right cheek
    bm_step.faces.new([v2, v3, v7, v6]) # Back
    bm_step.faces.new([v3, v0, v4, v7]) # Left cheek
    bm_step.faces.new([v3, v2, v1, v0]) # Bottom
    
    uv_step = bm_step.loops.layers.uv.new("UVMap")
    for f in bm_step.faces:
        for l in f.loops:
            l[uv_step].uv = (l.vert.co.x, l.vert.co.y)
            
    me_step = bpy.data.meshes.new("Step_Front_Entrance")
    bm_step.to_mesh(me_step)
    bm_step.free()
    
    step_obj = bpy.data.objects.new("Step_Front_Entrance", me_step)
    step_obj.data.materials.append(mat_step)
    bpy.context.scene.collection.objects.link(step_obj)
    
    # Small bevel modifier for realistic concrete edge highlight
    bevel = step_obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.008 # 8mm bevel
    bevel.segments = 2
    
    print("Step_Front_Entrance created with architectural bevel and concrete material.")
    
    # Save blend file
    bpy.ops.wm.save_mainfile()
    print("dum_pudorys.blend successfully saved!")

if __name__ == "__main__":
    run()
