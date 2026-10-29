import bpy
import bpy_extras
from typing import List, Tuple
from mathutils import Vector

class BoundingBoxExtractor:
    """Extracts 3D and 2D bounding boxes from Blender objects.

    Attributes:
        scene  (bpy.types.Scene)  : The current Blender scene.
        camera (bpy.types.Object) : The camera used for rendering.
    """

    def __init__(
        self,
        scene  : bpy.types.Scene,
        camera : bpy.types.Object
    ) -> None:
        """Initializes the BoundingBoxExtractor.

        Args:
            scene  (bpy.types.Scene)  : The current Blender scene.
            camera (bpy.types.Object) : The camera used for rendering.
        """
        self.scene  = scene
        self.camera = camera

    def get_3d_bbox_corners(
        self,
        obj : bpy.types.Object
    ) -> List[Vector]:
        """Gets the 8 corners of the 3D bounding box in world space.
        Uses evaluated depsgraph to account for modifiers like Bevel.

        Args:
            obj (bpy.types.Object) : The object to evaluate.

        Returns:
            List[Vector]           : A list of 8 vectors representing world-space corners.
        """
        depsgraph     = bpy.context.evaluated_depsgraph_get()
        eval_obj      = obj.evaluated_get(depsgraph)
        corners_local = eval_obj.bound_box
        matrix_world  = eval_obj.matrix_world
        corners_world = [matrix_world @ Vector(corner) for corner in corners_local]
        
        return corners_world

    def get_2d_projections(
        self,
        corners_world : List[Vector]
    ) -> List[Tuple[int, int]]:
        """Projects 3D world corners into 2D image pixel coordinates.

        Args:
            corners_world (List[Vector]) : The 8 corners in world space.

        Returns:
            List[Tuple[int, int]]        : The 2D pixel coordinates (x, y) for each corner.
        """
        render       = self.scene.render
        res_x        = render.resolution_x
        res_y        = render.resolution_y
        
        projected_2d = []
        for corner in corners_world:
            coord = bpy_extras.object_utils.world_to_camera_view(
                self.scene,
                self.camera,
                corner
            )
            pixel_x = int(coord.x * res_x)
            pixel_y = int(res_y - (coord.y * res_y))
            projected_2d.append((pixel_x, pixel_y))
            
        return projected_2d

    def get_2d_bounding_box(
        self,
        projected_2d : List[Tuple[int, int]]
    ) -> Tuple[int, int, int, int]:
        """Computes the 2D bounding box from projected corners.
        
        Args:
            projected_2d (List[Tuple[int, int]]) : Projected 2D corners.
            
        Returns:
            Tuple[int, int, int, int]            : x_min, y_min, x_max, y_max
        """
        x_coords = [p[0] for p in projected_2d]
        y_coords = [p[1] for p in projected_2d]
        
        x_min    = min(x_coords)
        x_max    = max(x_coords)
        y_min    = min(y_coords)
        y_max    = max(y_coords)
        
        return (x_min, y_min, x_max, y_max)
