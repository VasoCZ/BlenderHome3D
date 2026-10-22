import bpy

print("=== INSPECTING EXTERIOR LIGHTS ===")
for o in bpy.data.objects:
    if "ext" in o.name.lower():
        print(f"Object: {o.name}")
        print(f"  Location: {o.location}")
        print(f"  Rotation: {o.rotation_euler}")
        if o.type == 'LIGHT':
            l = o.data
            print(f"  Type: {l.type}, Shape: {getattr(l, 'shape', None)}, Size: ({getattr(l, 'size', None)}, {getattr(l, 'size_y', None)})")
            print(f"  Energy: {l.energy}, Color: {l.color[:]}, Radius: {getattr(l, 'shadow_soft_size', None)}")

# Let's also check if there are other lights near the exterior walls
for o in bpy.data.objects:
    if o.type == 'LIGHT' and "ext" not in o.name.lower():
        loc = o.location
        # Check if near exterior perimeter
        if loc.x < 0.5 or loc.x > 9.5 or loc.y < 0.5 or loc.y > 11.5:
            print(f"Other light near exterior: {o.name} at {loc}")
