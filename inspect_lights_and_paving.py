import bpy

print("=== EXTERIOR LIGHT DETAILS ===")
for o in bpy.data.objects:
    if "ext" in o.name.lower() or "soffit" in o.name.lower() or "patio" in o.name.lower():
        print(f"Name: {o.name}, Type: {o.type}, Loc: {o.location}, Rot: {o.rotation_euler}, Scale: {o.scale}")
        if o.type == 'LIGHT':
            l = o.data
            print(f"  Light type: {l.type}, Energy: {l.energy}, Color: {tuple(round(c, 3) for c in l.color)}")
            if l.type == 'SPOT':
                print(f"  Spot size: {l.spot_size}, Spot blend: {l.spot_blend}")
            elif l.type == 'POINT':
                print(f"  Shadow soft size / radius: {getattr(l, 'shadow_soft_size', None)}")

print("\n=== CHECKING ALL OBJECTS WITH 'LAMP' OR 'SVITIDLO' OR 'LIGHT' OR 'FIXTURE' ===")
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ['lamp', 'svit', 'fixt', 'sconce', 'wall_light']):
        print(f"Object: {o.name} ({o.type}), Loc: {o.location}, Rot: {o.rotation_euler}, Scale: {o.scale}")

# Check exterior paving mesh and material
print("\n=== EXTERIOR PAVING / DLAZBA OBJECTS & MATERIALS ===")
for o in bpy.data.objects:
    if any(k in o.name.lower() for k in ['paving', 'dlazba', 'chodnik', 'patio', 'driveway', 'terasa', 'ground', 'exterior']):
        print(f"Object: {o.name} ({o.type}), Loc: {o.location}, Dim: {o.dimensions}, Mats: {[m.name for m in o.data.materials if m] if hasattr(o.data, 'materials') else []}")
