import sys
import os
import bpy
import random
import cv2
import numpy as np
import OpenEXR
import Imath

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from generators.box import BoxGenerator
from generators.environment import EnvironmentRandomizer
from generators.clutter import ClutterGenerator
from core.engine import RenderEngine
from core.compositor import SceneCompositor
from core.bounding_box import BoundingBoxExtractor
from core.exporter import DataExporter

def main() -> None:
    print("--- Starting Final Mathematical Mask Pipeline ---")

    # 0. Clean up
    for obj in list(bpy.data.objects):
        if obj.type == 'MESH':
            bpy.data.objects.remove(obj, do_unlink=True)

    base_dir   = os.path.dirname(current_dir)
    render_dir = os.path.join(base_dir, "output", "images")
    mask_dir   = os.path.join(base_dir, "output", "masks")
    depth_dir  = os.path.join(base_dir, "output", "depth")
    debug_dir  = os.path.join(base_dir, "output", "debug")

    for d in [render_dir, mask_dir, depth_dir, debug_dir]:
        os.makedirs(d, exist_ok=True)

    engine = RenderEngine(render_path=render_dir + "/", resolution=(1024, 1024), samples=64)
    engine.setup_render_settings()

    camera = bpy.data.objects.get("Camera") or bpy.ops.object.camera_add() or bpy.context.active_object
    camera.name = "Camera"
    bpy.context.scene.camera = camera

    light = bpy.data.objects.get("Light") or bpy.ops.object.light_add(type='AREA') or bpy.context.active_object
    light.name = "Light"

    env_randomizer = EnvironmentRandomizer(bpy.context.scene, camera, light)
    clutter_gen    = ClutterGenerator()
    compositor     = SceneCompositor(bpy.context.scene)
    
    # We only need Depth pass in the compositor
    compositor.build_depth_output(depth_dir + "/")

    exporter  = DataExporter(output_dir=debug_dir)
    bbox_ext  = BoundingBoxExtractor(bpy.context.scene, camera)
    generator = BoxGenerator(min_size=0.6, max_size=0.9)

    for i in range(3): # Render 3 frames for testing
        bpy.context.scene.frame_set(i)
        frame_name = f"frame_{i:04d}"
        image_path = os.path.join(render_dir, f"{frame_name}.png")
        mask_path  = os.path.join(mask_dir, f"{frame_name}_mask.png")
        depth_path = os.path.join(depth_dir, f"{frame_name}_depth.exr")
        
        # 1. SETUP SCENE
        env_randomizer.apply_all()
        box = generator.spawn(pass_index=1)
        
        # Ground the box
        if env_randomizer.env_type == 'INDOOR':
            box.location.z = 0.15 + (box.scale.z * 0.5) # On Pallet
        else:
            box.location.z = box.scale.z * 0.5 # On Ground
            
        print(f"Frame {i}: Setting={env_randomizer.env_type}, BoxScaleZ={box.scale.z:.2f}")
        
        clutter_gen.spawn(count=random.randint(5, 12))
        bpy.context.view_layer.update()

        # 2. RENDER RGB & DEPTH (Cycles)
        bpy.context.scene.render.filepath = image_path
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.image_settings.color_mode = 'RGB'
        bpy.ops.render.render(write_still=True)
        
        # 3. MATHEMATICAL MASK EXTRACTION
        # Project 3D bounding box corners
        corners_world = bbox_ext.get_3d_bbox_corners(box)
        projected_2d  = bbox_ext.get_2d_projections(corners_world)
        bbox_2d       = bbox_ext.get_2d_bounding_box(projected_2d)
        
        # Generate pristine mathematical amodal mask
        mask_img = np.zeros((1024, 1024), dtype=np.uint8)
        hull = cv2.convexHull(np.array(projected_2d, dtype=np.int32))
        cv2.fillConvexPoly(mask_img, hull, 255)
        cv2.imwrite(mask_path, mask_img)

        # 4. Extract Depth from Compositor Output
        raw_depth_path = os.path.join(depth_dir, f"render_data_{i:04d}.exr")
        if os.path.exists(raw_depth_path):
            try:
                # The CompositorNodeOutputFile creates a Multilayer EXR. 
                # We extract the 'Depth.V' channel and save it cleanly.
                file = OpenEXR.InputFile(raw_depth_path)
                dw   = file.header()['dataWindow']
                size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
                pt   = Imath.PixelType(Imath.PixelType.FLOAT)
                
                channels = file.header()['channels'].keys()
                # Usually named 'Depth.V' or similar
                d_chan = next((c for c in channels if c.endswith('.V') or c.endswith('.R') or c == 'R' or c == 'V'), None)
                
                if d_chan:
                    s_depth = file.channel(d_chan, pt)
                    
                    header = OpenEXR.Header(size[0], size[1])
                    header['channels'] = {'Z': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))}
                    out_depth = OpenEXR.OutputFile(depth_path, header)
                    out_depth.writePixels({'Z': s_depth})
                    out_depth.close()
                    
                os.remove(raw_depth_path)
            except Exception as e:
                print(f"Failed to process EXR depth map: {e}")
        else:
            print(f"Raw depth file not found at {raw_depth_path}")

        # 5. Extract Annotations and Debug View
        if os.path.exists(image_path):
            exporter.save_bbox_txt(f"{frame_name}.txt", bbox_2d)
            exporter.draw_debug_image(image_path, bbox_2d, projected_2d, f"{frame_name}_debug.png")

if __name__ == "__main__":
    main()
