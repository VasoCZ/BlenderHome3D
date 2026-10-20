import bpy
import bmesh
import mathutils

def adjust_entrance_door():
    print("[1] Adjusting entrance door height to Step_Front_Entrance...")
    ram = bpy.data.objects.get("ram")
    step = bpy.data.objects.get("Step_Front_Entrance")
    dvere = bpy.data.objects.get("dvere")
    dvere_handle = bpy.data.objects.get("dvere.001")
    
    if not ram or not step:
        print("ERROR: ram or Step_Front_Entrance not found!")
        return

    # Step top is at Z = 0.1400
    # Wall lintel is at Z = 2.0500
    # Target ram bounds: Z in [0.1400, 2.0500] -> height = 1.9100m
    # In check_door_hierarchy, ram local mesh Z: min=-0.0036, max=2.0773, span=2.0809
    z_min_local = min(v.co.z for v in ram.data.vertices)
    z_max_local = max(v.co.z for v in ram.data.vertices)
    unscaled_h = z_max_local - z_min_local
    
    target_z_bottom = 0.1400
    target_z_top = 2.0500
    target_h = target_z_top - target_z_bottom
    
    new_scale_z = target_h / unscaled_h
    new_loc_z = target_z_bottom - new_scale_z * z_min_local
    
    ram.scale.z = new_scale_z
    ram.location.z = new_loc_z
    
    # Update depsgraph to calculate world matrices
    bpy.context.view_layer.update()
    
    ram_bb = [ram.matrix_world @ mathutils.Vector(c) for c in ram.bound_box]
    dvere_bb = [dvere.matrix_world @ mathutils.Vector(c) for c in dvere.bound_box]
    print(f"  ram new Z bounds: [{min(v.z for v in ram_bb):.4f}, {max(v.z for v in ram_bb):.4f}], scale.z={ram.scale.z:.4f}, loc.z={ram.location.z:.4f}")
    print(f"  dvere new Z bounds: [{min(v.z for v in dvere_bb):.4f}, {max(v.z for v in dvere_bb):.4f}]")


def fix_paving_stone_face_86_uv():
    print("\n[2] Fixing Paving Stone UV on Face 86 and Step_Front_Entrance...")
    slab = bpy.data.objects.get("Foundation_Slab")
    if not slab:
        print("ERROR: Foundation_Slab not found!")
        return
        
    uv_layer = slab.data.uv_layers.active
    mw = slab.matrix_world
    
    # Face 86 is X in [2.19, 4.64], Y in [-1.20, 0.00]
    for poly in slab.data.polygons:
        if poly.normal.z > 0.5:
            mat_name = slab.material_slots[poly.material_index].name
            if mat_name == "Paving Stones":
                verts = [mw @ slab.data.vertices[v_idx].co for v_idx in poly.vertices]
                poly_min_x = min(v.x for v in verts)
                poly_max_x = max(v.x for v in verts)
                poly_min_y = min(v.y for v in verts)
                poly_max_y = max(v.y for v in verts)
                
                if 2.18 <= poly_min_x and poly_max_x <= 4.65 and -1.25 <= poly_min_y and poly_max_y <= 0.05:
                    print(f"  Found Face {poly.index} (X=[{poly_min_x:.2f}, {poly_max_x:.2f}], Y=[{poly_min_y:.2f}, {poly_max_y:.2f}])")
                    for loop_idx in poly.loop_indices:
                        v_idx = slab.data.loops[loop_idx].vertex_index
                        co = mw @ slab.data.vertices[v_idx].co
                        uv_layer.data[loop_idx].uv = mathutils.Vector((co.x, co.y))
                        
    # Also update cubic projection on Step_Front_Entrance so risers don't stretch
    step = bpy.data.objects.get("Step_Front_Entrance")
    if step:
        step_uv = step.data.uv_layers.active or step.data.uv_layers.new(name="UVMap")
        for poly in step.data.polygons:
            n = poly.normal
            for loop_idx in poly.loop_indices:
                v_idx = step.data.loops[loop_idx].vertex_index
                co = step.data.vertices[v_idx].co
                if abs(n.z) > 0.7:
                    step_uv.data[loop_idx].uv = mathutils.Vector((co.x, co.y))
                elif abs(n.y) > 0.7:
                    step_uv.data[loop_idx].uv = mathutils.Vector((co.x, co.z))
                elif abs(n.x) > 0.7:
                    step_uv.data[loop_idx].uv = mathutils.Vector((co.y, co.z))
        step.data.update()
        print("  Step_Front_Entrance UV updated with cubic mapping.")


def fix_garden_curbs():
    print("\n[3] Aligning Garden_Curbs vertical walls according to user-edited top bounds...")
    curbs = bpy.data.objects.get("Garden_Curbs")
    if not curbs:
        print("ERROR: Garden_Curbs not found!")
        return
        
    # The user adjusted top inner coordinates:
    # V8: (5.000, 12.722, 0.035)
    # V9: (-0.615, 12.722, 0.035)
    # V10: (-0.615, -0.758, 0.035)
    # V11: (2.190, -0.758, 0.035)
    # And top outer coordinates:
    # V44: (4.920, 12.802, 0.035)
    # V45: (-0.695, 12.802, 0.035)
    # V46: (-0.695, -0.838, 0.035)
    # V47: (2.110, -0.838, 0.035)
    
    # Target clean inner coordinates:
    # North: Y = 12.722
    # West:  X = -0.615
    # South: Y = -0.758
    # Terrace junction: X = 5.000
    # Driveway junction: X = 2.190
    
    # Outer coordinates (curb width 0.08m):
    # North: Y = 12.802
    # West:  X = -0.695
    # South: Y = -0.838
    # Terrace junction: X = 4.920
    # Driveway junction: X = 2.110
    
    # Inner bottom vertices at Z = 0.000 (V20, V21, V22, V23)
    curbs.data.vertices[20].co = mathutils.Vector((5.000, 12.722, 0.000))
    curbs.data.vertices[21].co = mathutils.Vector((-0.615, 12.722, 0.000))
    curbs.data.vertices[22].co = mathutils.Vector((-0.615, -0.758, 0.000))
    curbs.data.vertices[23].co = mathutils.Vector((2.190, -0.758, 0.000))
    
    # Inner footing vertices at Z = -0.100 (V32, V33, V34, V35)
    curbs.data.vertices[32].co = mathutils.Vector((5.000, 12.722, -0.100))
    curbs.data.vertices[33].co = mathutils.Vector((-0.615, 12.722, -0.100))
    curbs.data.vertices[34].co = mathutils.Vector((-0.615, -0.758, -0.100))
    curbs.data.vertices[35].co = mathutils.Vector((2.190, -0.758, -0.100))
    
    # Outer bottom vertices at Z = -0.100 (V56, V57, V58, V59)
    curbs.data.vertices[56].co = mathutils.Vector((4.920, 12.802, -0.100))
    curbs.data.vertices[57].co = mathutils.Vector((-0.695, 12.802, -0.100))
    curbs.data.vertices[58].co = mathutils.Vector((-0.695, -0.838, -0.100))
    curbs.data.vertices[59].co = mathutils.Vector((2.110, -0.838, -0.100))
    
    # Top inner vertices (V8, V9, V10, V11)
    curbs.data.vertices[8].co  = mathutils.Vector((5.000, 12.722, 0.035))
    curbs.data.vertices[9].co  = mathutils.Vector((-0.615, 12.722, 0.035))
    curbs.data.vertices[10].co = mathutils.Vector((-0.615, -0.758, 0.035))
    curbs.data.vertices[11].co = mathutils.Vector((2.190, -0.758, 0.035))
    
    # Top outer vertices (V44, V45, V46, V47)
    curbs.data.vertices[44].co = mathutils.Vector((4.920, 12.802, 0.035))
    curbs.data.vertices[45].co = mathutils.Vector((-0.695, 12.802, 0.035))
    curbs.data.vertices[46].co = mathutils.Vector((-0.695, -0.838, 0.035))
    curbs.data.vertices[47].co = mathutils.Vector((2.110, -0.838, 0.035))
    
    curbs.data.update()
    print("  Garden_Curbs vertices successfully aligned and verified vertical.")


def shorten_foundation_slab_and_kacirek():
    print("\n[4] Shortening Foundation_Slab and kačírek to fit inside new curbs...")
    slab = bpy.data.objects.get("Foundation_Slab")
    if not slab:
        print("ERROR: Foundation_Slab not found!")
        return
        
    mw = slab.matrix_world
    mw_inv = mw.inverted()
    
    # 1. West perimeter: move any vertex currently at X = -1.200 to X = -0.615
    # 2. South kačírek perimeter: move any vertex currently at Y = -1.200 and X <= 2.190 to Y = -0.758
    # 3. North kačírek perimeter: move any vertex currently at Y = 13.200 and X <= 5.000 to Y = 12.722
    
    count_west = 0
    count_south = 0
    count_north = 0
    
    for v in slab.data.vertices:
        co = mw @ v.co
        modified = False
        new_x = co.x
        new_y = co.y
        new_z = co.z
        
        # West edge:
        if abs(co.x - (-1.200)) < 0.01:
            new_x = -0.615
            modified = True
            count_west += 1
            
        # South kačírek edge:
        if abs(co.y - (-1.200)) < 0.01 and co.x <= 2.191:
            new_y = -0.758
            modified = True
            count_south += 1
            
        # North kačírek edge:
        if abs(co.y - 13.200) < 0.01 and co.x <= 5.001:
            new_y = 12.722
            modified = True
            count_north += 1
            
        if modified:
            v.co = mw_inv @ mathutils.Vector((new_x, new_y, new_z))
            
    print(f"  Updated vertices: {count_west} west, {count_south} south, {count_north} north.")
    
    # Update UV mapping on the Beach Pebbles faces so texture scale remains 1:1
    uv_layer = slab.data.uv_layers.active
    if uv_layer:
        for poly in slab.data.polygons:
            if poly.normal.z > 0.5:
                mat_name = slab.material_slots[poly.material_index].name
                if mat_name == "Beach Pebbles":
                    for loop_idx in poly.loop_indices:
                        v_idx = slab.data.loops[loop_idx].vertex_index
                        co = mw @ slab.data.vertices[v_idx].co
                        # UV scale 2.0 for Beach Pebbles as previously used
                        uv_layer.data[loop_idx].uv = mathutils.Vector((co.x * 2.0, co.y * 2.0))
                        
    slab.data.update()
    print("  Foundation_Slab geometry and UVs successfully updated.")


if __name__ == "__main__":
    adjust_entrance_door()
    fix_paving_stone_face_86_uv()
    fix_garden_curbs()
    shorten_foundation_slab_and_kacirek()
    
    # Save the blend file
    blend_path = "C:/Users/Vaso/Antigravity/Project blender/dum_pudorys.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"\nSaved updated file to {blend_path}")
