from PIL import Image
import os

img_path = r"C:\Users\Vaso\Antigravity\Project blender\realene foto\IMG_20261021_225705.jpg"
img = Image.open(img_path)
w, h = img.size
print(f"Image size: {w}x{h}")

# Save full resized version for easy reference if needed
img_resized = img.resize((1024, int(1024 * h / w)), Image.Resampling.LANCZOS)
img_resized.save(r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\room_106_full_reference.png")
print("Saved room_106_full_reference.png")
