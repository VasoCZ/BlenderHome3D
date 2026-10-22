import bpy

mat = bpy.data.materials.get("Paving Stones")
if mat and mat.use_nodes:
    print("=== Paving Stones Material ===")
    for n in mat.node_tree.nodes:
        img_name = getattr(n, "image", None)
        if img_name:
            img_name = img_name.name
        print(f"  Node: {n.name} ({n.type}) -> Image: {img_name}")
    for link in mat.node_tree.links:
        print(f"  Link: {link.from_node.name}.{link.from_socket.name} -> {link.to_node.name}.{link.to_socket.name}")

print("\n=== Check Beach Pebbles Material ===")
mat2 = bpy.data.materials.get("Beach Pebbles")
if mat2 and mat2.use_nodes:
    for n in mat2.node_tree.nodes:
        img_name = getattr(n, "image", None)
        if img_name:
            img_name = img_name.name
        print(f"  Node: {n.name} ({n.type}) -> Image: {img_name}")

print("\n=== Check Foundation_Slab Mesh ===")
slab = bpy.data.objects.get("Foundation_Slab")
if slab:
    print(f"Slab: loc={slab.location}, dim={slab.dimensions}")
    for i, m in enumerate(slab.data.materials):
        print(f"  Slot {i}: {m.name if m else 'None'}")
