import bpy

def align_wood_floors():
    print("=== Aligning Wood Floors according to Floor_1.04_Obyvaci_pokoj_North ===")
    
    ref_obj = bpy.data.objects.get("Floor_1.04_Obyvaci_pokoj_North")
    if not ref_obj:
        raise ValueError("Reference object Floor_1.04_Obyvaci_pokoj_North not found!")
    
    mat_wood = bpy.data.materials.get("Wood floor.002")
    if not mat_wood:
        raise ValueError("Material Wood floor.002 not found!")
        
    print(f"Reference material: {mat_wood.name}")
    
    # Target objects to update
    target_rooms = [
        "Floor_1.04_Obyvaci_pokoj_South",
        "Floor_1.03_Kuchyne",
        "Floor_1.02_Chodba",
        "Floor_1.05_Pokoj",
        "Floor_1.06_Pokoj",
        "Floor_1.07_Pokoj",
        "Floor_Threshold_102_105",
        "Floor_Threshold_102_106",
        "Floor_Threshold_102_107",
    ]
    
    # Exact UV formula from Floor_1.04_Obyvaci_pokoj_North:
    # U = 0.5 * X - 3.2900000
    # V = 0.5 * Y - 4.1837500
    U_SCALE = 0.5
    U_OFFSET = -3.2900000
    V_SCALE = 0.5
    V_OFFSET = -4.1837500
    
    for name in target_rooms:
        obj = bpy.data.objects.get(name)
        if not obj:
            print(f"WARNING: Object {name} not found, skipping.")
            continue
            
        me = obj.data
        
        # 1. Ensure material is Wood floor.002
        if len(obj.material_slots) == 0:
            obj.data.materials.append(mat_wood)
        else:
            obj.material_slots[0].material = mat_wood
            
        # 2. Ensure automap UV layer exists and is active
        if "automap" not in me.uv_layers:
            me.uv_layers.new(name="automap")
        me.uv_layers["automap"].active = True
        me.uv_layers["automap"].active_render = True
        
        # Also sync UVMap if it exists so both layers are identical
        if "UVMap" not in me.uv_layers:
            me.uv_layers.new(name="UVMap")
            
        # 3. Calculate and apply UV coordinates to all UV layers
        for uv_layer in me.uv_layers:
            for poly in me.polygons:
                is_horizontal = abs(poly.normal.z) > 0.5
                is_y_side = abs(poly.normal.y) > abs(poly.normal.x)
                
                for li in poly.loop_indices:
                    vi = me.loops[li].vertex_index
                    co = me.vertices[vi].co
                    # Mesh coords equal world coords since location=(0,0,0) and scale=(1,1,1)
                    wx, wy, wz = co.x, co.y, co.z
                    
                    if is_horizontal:
                        u = U_SCALE * wx + U_OFFSET
                        v = V_SCALE * wy + V_OFFSET
                    elif is_y_side:
                        u = U_SCALE * wx + U_OFFSET
                        v = 0.49625 + (wz / 0.015) * 0.0075 if wz > 0 else 0.49625
                    else:
                        u = V_SCALE * wy + V_OFFSET
                        v = 0.49625 + (wz / 0.015) * 0.0075 if wz > 0 else 0.49625
                        
                    uv_layer.data[li].uv = (u, v)
                    
        me.update()
        print(f"  Successfully aligned: {name} (mat: {obj.material_slots[0].material.name}, UV layers: {[uv.name for uv in me.uv_layers]})")

    # Save blend file
    bpy.ops.wm.save_mainfile()
    print("Blend file dum_pudorys.blend successfully saved!")

if __name__ == "__main__":
    align_wood_floors()
