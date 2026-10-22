import bpy
import os

blends = [
    (r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\concrete-pavemen_823f922e-07f4-4053-8c25-ac8ca3b20e87\concrete-pavement_2K_6c2f0874-eb6e-4281-b2d1-d519defcc55a.blend", "Concrete pavement"),
    (r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\concrete-tiles_1be6b977-a7fb-40f5-94a1-fd5a050acf00\concrete-tiles_2K_a374b85c-dcfb-4a2c-9c25-dd4d35bebc4d.blend", "Concrete tiles"),
    (r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\pavement-tiles_7685a795-0973-49cd-8c02-1fccec2facf8\pavement-tiles_2K_a9328d03-2f42-4eba-8d0b-0eed89a10d5e.blend", "Pavement Tiles"),
    (r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\paving_9263889a-9ba8-4d47-981a-ee646f24934c\paving_2K_981c669c-82a7-4de8-894c-c4155c980e00.blend", "Paving"),
    (r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\paving_fb9fd138-7841-42e3-94f5-c3c4706def68\paving_2K_6c0e5911-9006-40a8-a3a1-4b91d48a269b.blend", "Paving"),
]

# Create a simple test scene to render small material balls
for b_path, mat_name in blends:
    if os.path.exists(b_path):
        with bpy.data.libraries.load(b_path, link=False) as (data_from, data_to):
            if mat_name in data_from.materials:
                data_to.materials = [mat_name]

for m in bpy.data.materials:
    print(f"Loaded mat: {m.name}")
    if m.use_nodes:
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                print(f"  Texture: {n.image.name}, size: {n.image.size[:]}")
                # Save out image texture preview
                out_path = rf"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\tex_preview_{m.name}_{n.image.name}.png"
                try:
                    n.image.filepath_raw = out_path
                    n.image.file_format = 'PNG'
                    n.image.save()
                    print(f"    Saved preview to {out_path}")
                except Exception as e:
                    print(f"    Could not save: {e}")
