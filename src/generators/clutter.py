import bpy
import random
import math
from mathutils import Vector

class ClutterGenerator:
    """Spawns unlabeled distractor objects to provide visual context.
    
    Attributes:
        objects (list) : List of spawned clutter objects.
    """

    def __init__(self) -> None:
        """Initializes the ClutterGenerator."""
        self.objects = []

    def clear(self) -> None:
        """Removes all clutter objects and their materials from the scene."""
        for obj in self.objects:
            if obj.name in bpy.data.objects:
                bpy.data.objects.remove(obj, do_unlink=True)
        self.objects.clear()
        
        # Clean up orphaned materials
        for mat in list(bpy.data.materials):
            if mat.name.startswith("ClutterMat") and not mat.users:
                bpy.data.materials.remove(mat)

    def spawn(self, count: int = 5) -> None:
        """Spawns random primitives around the scene origin.
        
        Args:
            count (int) : Number of objects to spawn.
        """
        self.clear()
        
        for i in range(count):
            obj_type = random.choice(['CUBE', 'CYLINDER', 'SPHERE', 'TORUS'])
            
            if obj_type == 'CUBE':
                bpy.ops.mesh.primitive_cube_add()
            elif obj_type == 'CYLINDER':
                bpy.ops.mesh.primitive_cylinder_add()
            elif obj_type == 'SPHERE':
                bpy.ops.mesh.primitive_uv_sphere_add()
            else:
                bpy.ops.mesh.primitive_torus_add()
                
            obj = bpy.context.active_object
            obj.name = f"Clutter_{i}"
            
            # Random Scale (Small to medium distractors)
            s = random.uniform(0.1, 0.6)
            obj.scale = (s, s, s)
            
            # Random Position (Ring around origin, avoid center)
            dist  = random.uniform(1.5, 4.0)
            angle = random.uniform(0, 2 * math.pi)
            obj.location = Vector((
                dist * math.cos(angle),
                dist * math.sin(angle),
                random.uniform(0.05, 0.8)
            ))
            
            # Random Rotation
            obj.rotation_euler = (
                random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi),
                random.uniform(0, 2 * math.pi)
            )
            
            # Ensure it is ignored by segmentation (pass_index 0)
            obj.pass_index = 0
            
            # Random Material
            mat = bpy.data.materials.new(name=f"ClutterMat_{i}")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes['Principled BSDF']
            bsdf.inputs['Base Color'].default_value = (
                random.uniform(0.1, 0.8),
                random.uniform(0.1, 0.8),
                random.uniform(0.1, 0.8),
                1.0
            )
            bsdf.inputs['Roughness'].default_value = random.uniform(0.2, 0.9)
            obj.data.materials.append(mat)
            
            self.objects.append(obj)
