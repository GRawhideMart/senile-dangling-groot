import bpy
from typing import Tuple

class RenderEngine:
    """Handles Blender render settings configuration.
    
    Attributes:
        render_path (str)               : Directory path to save renders.
        resolution  (Tuple[int, int])   : The X and Y resolution of the output.
        samples     (int)               : The number of render samples for Cycles.
    """

    def __init__(
        self,
        render_path : str = "renders/",
        resolution  : Tuple[int, int] = (1920, 1080),
        samples     : int = 128
    ) -> None:
        """Initializes the RenderEngine.
        
        Args:
            render_path (str)             : Directory path to save renders.
            resolution  (Tuple[int, int]) : The X and Y resolution of the output.
            samples     (int)             : The number of render samples for Cycles.
        """
        self.render_path = render_path
        self.resolution  = resolution
        self.samples     = samples

    def setup_render_settings(self) -> None:
        """Configures the scene's render engine, resolution, and output path."""
        scene = bpy.context.scene
        
        # Set render engine to Cycles for better quality
        scene.render.engine = 'CYCLES'
        
        # Set output path
        scene.render.filepath = self.render_path
        
        # Set resolution
        scene.render.resolution_x = self.resolution[0]
        scene.render.resolution_y = self.resolution[1]
        scene.render.resolution_percentage = 100
        
        # Set samples for rendering
        scene.cycles.samples = self.samples
        
        print(f"Render settings configured: Path={self.render_path}, Resolution={self.resolution}, Samples={self.samples}")
