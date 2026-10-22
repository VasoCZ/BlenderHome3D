import bpy
import os

paving_blends = [
    r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\concrete-pavemen_823f922e-07f4-4053-8c25-ac8ca3b20e87\concrete-pavement_2K_6c2f0874-eb6e-4281-b2d1-d519defcc55a.blend",
    r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\concrete-tiles_1be6b977-a7fb-40f5-94a1-fd5a050acf00\concrete-tiles_2K_a374b85c-dcfb-4a2c-9c25-dd4d35bebc4d.blend",
    r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\pavement-tiles_7685a795-0973-49cd-8c02-1fccec2facf8\pavement-tiles_2K_a9328d03-2f42-4eba-8d0b-0eed89a10d5e.blend",
    r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\paving_9263889a-9ba8-4d47-981a-ee646f24934c\paving_2K_981c669c-82a7-4de8-894c-c4155c980e00.blend",
    r"C:\Users\Vaso\Antigravity\Project blender\assets\materials\paving_fb9fd138-7841-42e3-94f5-c3c4706def68\paving_2K_6c0e5911-9006-40a8-a3a1-4b91d48a269b.blend",
]

for b_path in paving_blends:
    if os.path.exists(b_path):
        print(f"\n--- Checking: {os.path.basename(b_path)} ---")
        with bpy.data.libraries.load(b_path) as (data_from, data_to):
            print("  Materials:", data_from.materials)
            print("  Images:", data_from.images)
