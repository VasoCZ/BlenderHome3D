import bpy

# Set up a temporary camera to look at room 1.06
cam_data = bpy.data.cameras.new("Temp_Room_106_Cam")
cam_obj = bpy.data.objects.new("Temp_Room_106_Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)

# Position camera above room 1.06 looking down into it
cam_obj.location = (2.4, 2.1, 5.0)
cam_obj.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.scene.camera = cam_obj

# Set resolution for fast render
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 600
bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'

# Actually let's use Cycles with few samples for fidelity
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 32
bpy.context.scene.render.filepath = r"C:\Users\Vaso\.gemini\antigravity-cli\brain\f3c5abf3-eea0-4d65-81b3-b4401695e1c6\room_106_topdown_current.png"

bpy.ops.render.render(write_still=True)
print("Render completed!")
