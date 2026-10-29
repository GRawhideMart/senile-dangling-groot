import bpy
import random
import colorsys
import math
from typing import Optional

class BoxGenerator:
    """Generates randomized boxes for the scene with realistic materials, bevels, and labels.
    
    Attributes:
        min_size    (float)              : The minimum scale limit.
        max_size    (float)              : The maximum scale limit.
        current_box (bpy.types.Object)   : The currently generated box object.
    """

    def __init__(
        self,
        min_size : float = 0.3,
        max_size : float = 1.2
    ) -> None:
        """Initializes the BoxGenerator.
        
        Args:
            min_size (float) : The minimum scale limit.
            max_size (float) : The maximum scale limit.
        """
        self.min_size    = min_size
        self.max_size    = max_size
        self.current_box = None

    def purge_scene(self) -> None:
        """Clears the generated box to maintain stateless execution without destroying the environment."""
        if self.current_box and self.current_box.name in bpy.data.objects:
            bpy.data.objects.remove(self.current_box, do_unlink=True)
        self.current_box = None
        
        # Clean up orphaned materials to prevent memory leaks
        for mat in bpy.data.materials:
            if getattr(mat, "use_fake_user", False):
                continue
            if not mat.users:
                bpy.data.materials.remove(mat)

    def apply_bevel(
        self,
        obj : bpy.types.Object
    ) -> None:
        """Applies a randomized bevel modifier to simulate cardboard edges.
        
        Args:
            obj (bpy.types.Object) : The object to apply the bevel to.
        """
        modifier = obj.modifiers.new(name="Bevel", type='BEVEL')
        modifier.width        = random.uniform(0.002, 0.01)
        modifier.segments     = random.randint(3, 5)
        modifier.limit_method = 'ANGLE'
        modifier.angle_limit  = math.radians(30)
        
        # Apply smooth shading
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()

    def apply_deformation(
        self,
        obj : bpy.types.Object
    ) -> None:
        """Applies a subtle displace modifier to simulate cardboard warping and dents.
        
        Args:
            obj (bpy.types.Object) : The object to deform.
        """
        # We need more geometry for displacement to work
        subdiv = obj.modifiers.new(name="Subdiv", type='SUBSURF')
        subdiv.levels            = 2
        subdiv.render_levels     = 2
        subdiv.subdivision_type  = 'SIMPLE'

        tex = bpy.data.textures.new(name="DentsTex", type='CLOUDS')
        tex.noise_scale = 0.5
        tex.intensity   = 0.5
        
        displace = obj.modifiers.new(name="Displace", type='DISPLACE')
        displace.texture   = tex
        displace.strength  = random.uniform(0.005, 0.015)
        displace.mid_level = 0.5

    def apply_material(
        self,
        obj : bpy.types.Object
    ) -> None:
        """Creates and applies a randomized cardboard material with procedural labels.
        
        Args:
            obj (bpy.types.Object) : The object to apply the material to.
        """
        mat = bpy.data.materials.new(name="RealisticCardboard")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        
        for node in nodes: nodes.remove(node)
            
        out_node  = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf_node = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        # 1. Base Cardboard Color
        h = random.uniform(0.06, 0.1)  # Hue: Warm browns
        s = random.uniform(0.4, 0.6)
        v = random.uniform(0.4, 0.6)
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        
        # 2. Add Procedural Labels
        # We use a Voronoi texture to create "blocks" of white labels
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        
        voronoi = nodes.new(type='ShaderNodeTexVoronoi')
        voronoi.feature = 'SMOOTH_F1'
        voronoi.inputs['Scale'].default_value = random.uniform(2.0, 5.0)
        
        # Threshold the voronoi to get sharp rectangles
        math_label = nodes.new(type='ShaderNodeMath')
        math_label.operation = 'LESS_THAN'
        math_label.inputs[1].default_value = random.uniform(0.1, 0.25)
        
        mix_rgb = nodes.new(type='ShaderNodeMixRGB')
        mix_rgb.inputs['Color1'].default_value = (r, g, b, 1.0)
        mix_rgb.inputs['Color2'].default_value = (0.8, 0.8, 0.8, 1.0) # White label
        
        # 3. Add Procedural "Text" on labels
        noise_text = nodes.new(type='ShaderNodeTexNoise')
        noise_text.inputs['Scale'].default_value = 500.0
        noise_text.inputs['Detail'].default_value = 15.0
        
        math_text = nodes.new(type='ShaderNodeMath')
        math_text.operation = 'GREATER_THAN'
        math_text.inputs[1].default_value = 0.6
        
        # Final color mix
        final_color = nodes.new(type='ShaderNodeMixRGB')
        final_color.inputs['Color1'].default_value = (0.1, 0.1, 0.1, 1.0) # Black text
        
        # 4. Links
        links.new(voronoi.outputs['Distance'], math_label.inputs[0])
        links.new(math_label.outputs[0], mix_rgb.inputs['Fac'])
        
        # Only show "text" where the label is
        links.new(noise_text.outputs['Fac'], math_text.inputs[0])
        
        # Mix base/label with text
        links.new(mix_rgb.outputs['Color'], final_color.inputs['Color1'])
        # Factor for text: label_mask AND text_noise
        text_mask = nodes.new(type='ShaderNodeMath')
        text_mask.operation = 'MULTIPLY'
        links.new(math_label.outputs[0], text_mask.inputs[0])
        links.new(math_text.outputs[0], text_mask.inputs[1])
        
        links.new(text_mask.outputs[0], final_color.inputs['Fac'])
        links.new(final_color.outputs['Color'], bsdf_node.inputs['Base Color'])
        
        # 5. Bump/Normal
        noise_bump = nodes.new(type='ShaderNodeTexNoise')
        noise_bump.inputs['Scale'].default_value = 200.0
        
        bump = nodes.new(type='ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.05
        
        links.new(noise_bump.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf_node.inputs['Normal'])
        
        links.new(bsdf_node.outputs['BSDF'], out_node.inputs['Surface'])
        
        obj.data.materials.append(mat)

    def spawn(
        self,
        pass_index : int = 1
    ) -> bpy.types.Object:
        """Spawns a new realistic package with randomized dimensions, textures, and dents.
        
        Args:
            pass_index (int) : The index to use for the object pass (segmentation).
            
        Returns:
            bpy.types.Object : The generated box object.
        """
        self.purge_scene()
        
        # Add the base asset
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
        self.current_box = bpy.context.active_object
        self.current_box.name = "RealisticBox"
        self.current_box.pass_index = pass_index
        
        # Random Dimensions
        self.current_box.scale.x = random.uniform(self.min_size, self.max_size)
        self.current_box.scale.y = random.uniform(self.min_size, self.max_size)
        self.current_box.scale.z = random.uniform(0.1, 0.8)
        
        # Random Rotation (Box might be slightly tilted or on its side)
        if random.random() > 0.7:
            # 90 degree flip
            self.current_box.rotation_euler.x = math.radians(random.choice([0, 90, 180]))
            
        # Refined setting: small random tilt
        self.current_box.rotation_euler.z = random.uniform(0, 2 * math.pi)
        
        # Apply features
        self.apply_bevel(self.current_box)
        self.apply_deformation(self.current_box)
        self.apply_material(self.current_box)
        
        bpy.context.view_layer.update()
        return self.current_box
