import os
import cv2
import numpy as np
from typing import Tuple, List

class DataExporter:
    """Handles saving of annotations and debugging visuals.
    
    Attributes:
        output_dir (str) : The directory to save output files.
    """

    def __init__(
        self,
        output_dir : str = "renders/debug/"
    ) -> None:
        """Initializes the DataExporter.
        
        Args:
            output_dir (str) : The directory to save output files.
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_bbox_txt(
        self,
        filename : str,
        bbox_2d  : Tuple[int, int, int, int]
    ) -> None:
        """Saves the 2D bounding box to a simple text file.
        
        Args:
            filename (str)                       : Name of the text file (e.g., 'frame_1.txt').
            bbox_2d  (Tuple[int, int, int, int]) : Bounding box coordinates (x_min, y_min, x_max, y_max).
        """
        path = os.path.join(self.output_dir, filename)
        with open(path, 'w') as f:
            f.write(f"Class: Box\n")
            f.write(f"x_min: {bbox_2d[0]}\n")
            f.write(f"y_min: {bbox_2d[1]}\n")
            f.write(f"x_max: {bbox_2d[2]}\n")
            f.write(f"y_max: {bbox_2d[3]}\n")

    def draw_debug_image(
        self,
        image_path   : str,
        bbox_2d      : Tuple[int, int, int, int],
        projected_2d : List[Tuple[int, int]],
        output_name  : str
    ) -> None:
        """Draws the 2D and 3D bounding boxes on the rendered image using OpenCV.
        
        Args:
            image_path   (str)                       : Path to the original rendered image.
            bbox_2d      (Tuple[int, int, int, int]) : 2D bounding box (x_min, y_min, x_max, y_max).
            projected_2d (List[Tuple[int, int]])     : 8 projected corners of the 3D bounding box.
            output_name  (str)                       : Name of the output debug image file.
        """
        if not os.path.exists(image_path):
            print(f"Warning: Rendered image not found at {image_path}. Cannot draw debug.")
            return

        img = cv2.imread(image_path)
        
        # Draw 2D bounding box (Red)
        pt1 = (bbox_2d[0], bbox_2d[1])
        pt2 = (bbox_2d[2], bbox_2d[3])
        cv2.rectangle(img, pt1, pt2, (0, 0, 255), 2)
        
        # Draw 3D bounding box corners (Green dots)
        for corner in projected_2d:
            cv2.circle(img, corner, 4, (0, 255, 0), -1)
            
        save_path = os.path.join(self.output_dir, output_name)
        cv2.imwrite(save_path, img)
