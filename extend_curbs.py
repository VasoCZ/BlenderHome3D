import bpy
import bmesh
import mathutils

def extend_curbs_and_adjust_slab():
    print("=== EXTENDING CURBS TO SEPARATE KAČÍREK AND DLAŽBA ===")
    
    curbs = bpy.data.objects.get("Garden_Curbs")
    slab = bpy.data.objects.get("Foundation_Slab")
    
    if not curbs or not slab:
        print("ERROR: Garden_Curbs or Foundation_Slab not found!")
        return

    # 1. Update Foundation_Slab:
    # On south: Face 2 (Beach Pebbles) east boundary should be at X = 2.110 (inner face of curb)
    # On north: Face 13 (Beach Pebbles) east boundary should be at X = 4.920 (inner face of curb)
    mw_slab = slab.matrix_world
    mw_slab_inv = mw_slab.inverted()
    
    # In Foundation_Slab, find vertices with X = 2.190 and Y in [-0.758, 0.000] on the kačírek face
    # Note: V7 is (2.190, 0.000), V3 was (2.190, -1.200) -> now (2.190, -0.758)
    # But wait, V7 and V3 are also shared by Face 86 (Paving Stones)!
    # If V7 is shared, we should NOT move V7 for Face 86, but split or move only the kačírek boundary!
    
    # Let's inspect vertices of Foundation_Slab near X=2.19 and X=5.0
    bm_slab = bmesh.new()
    bm_slab.from_mesh(slab.data)
    
    # 2. Let's inspect Garden_Curbs and add the curb extensions
    bm_curb = bmesh.new()
    bm_curb.from_mesh(curbs.data)
    
    mat_curb_idx = 0
    
    # South Extension Block:
    # X in [2.110, 2.190], Y in [-0.758, 0.000], Z in [-0.100, 0.035]
    # We can create a box from (2.110, -0.758, -0.100) to (2.190, 0.000, 0.035)
    # Let's create the 8 vertices for the south box:
    v_s_000 = bm_curb.verts.new((2.110, -0.758, -0.100))
    v_s_100 = bm_curb.verts.new((2.190, -0.758, -0.100))
    v_s_110 = bm_curb.verts.new((2.190,  0.000, -0.100))
    v_s_010 = bm_curb.verts.new((2.110,  0.000, -0.100))
    
    v_s_001 = bm_curb.verts.new((2.110, -0.758,  0.035))
    v_s_101 = bm_curb.verts.new((2.190, -0.758,  0.035))
    v_s_111 = bm_curb.verts.new((2.190,  0.000,  0.035))
    v_s_011 = bm_curb.verts.new((2.110,  0.000,  0.035))
    
    # Faces for south box:
    f_s_top    = bm_curb.faces.new((v_s_001, v_s_101, v_s_111, v_s_011)) # Top Z=+0.035
    f_s_east   = bm_curb.faces.new((v_s_100, v_s_101, v_s_111, v_s_110)) # East X=2.190 (facing paving)
    f_s_west   = bm_curb.faces.new((v_s_010, v_s_011, v_s_001, v_s_000)) # West X=2.110 (facing kacirek)
    f_s_north  = bm_curb.faces.new((v_s_110, v_s_111, v_s_011, v_s_010)) # North Y=0.000 (against wall)
    f_s_bottom = bm_curb.faces.new((v_s_000, v_s_010, v_s_110, v_s_100)) # Bottom Z=-0.100
    # Note: south face at Y=-0.758 connects to existing curb, so we don't need a internal wall if remove_doubles merges it
    
    for f in [f_s_top, f_s_east, f_s_west, f_s_north, f_s_bottom]:
        f.material_index = mat_curb_idx

    # North Extension Block (Terrace):
    # X in [4.920, 5.000], Y in [12.000, 12.722], Z in [-0.100, 0.035]
    v_n_000 = bm_curb.verts.new((4.920, 12.000, -0.100))
    v_n_100 = bm_curb.verts.new((5.000, 12.000, -0.100))
    v_n_110 = bm_curb.verts.new((5.000, 12.722, -0.100))
    v_n_010 = bm_curb.verts.new((4.920, 12.722, -0.100))
    
    v_n_001 = bm_curb.verts.new((4.920, 12.000,  0.035))
    v_n_101 = bm_curb.verts.new((5.000, 12.000,  0.035))
    v_n_111 = bm_curb.verts.new((5.000, 12.722,  0.035))
    v_n_011 = bm_curb.verts.new((4.920, 12.722,  0.035))
    
    f_n_top    = bm_curb.faces.new((v_n_001, v_n_011, v_n_111, v_n_101)) # Top Z=+0.035
    f_n_east   = bm_curb.faces.new((v_n_100, v_n_110, v_n_111, v_n_101)) # East X=5.000 (facing terrace paving)
    f_n_west   = bm_curb.faces.new((v_n_010, v_n_000, v_n_001, v_n_011)) # West X=4.920 (facing kacirek)
    f_n_south  = bm_curb.faces.new((v_n_000, v_n_100, v_n_101, v_n_001)) # South Y=12.000 (against wall)
    f_n_bottom = bm_curb.faces.new((v_n_010, v_n_110, v_n_100, v_n_000)) # Bottom Z=-0.100
    
    for f in [f_n_top, f_n_east, f_n_west, f_n_south, f_n_bottom]:
        f.material_index = mat_curb_idx

    # Remove doubles to merge with existing curb vertices at Y=-0.758 and Y=12.722
    bmesh.ops.remove_doubles(bm_curb, verts=bm_curb.verts, dist=0.002)
    
    # Recalculate face normals
    bmesh.ops.recalc_face_normals(bm_curb, faces=bm_curb.faces)
    
    bm_curb.to_mesh(curbs.data)
    bm_curb.free()
    curbs.data.update()
    print("  Garden_Curbs extensions successfully added and merged.")

if __name__ == "__main__":
    extend_curbs_and_adjust_slab()
    bpy.ops.wm.save_as_mainfile(filepath="C:/Users/Vaso/Antigravity/Project blender/dum_pudorys.blend")
    print("Saved dum_pudorys.blend")
