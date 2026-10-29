import bpy
import math
import random
from mathutils import Vector

class EnvironmentRandomizer:
    """Randomizes the scene's camera, lighting, and background with realistic industrial context.
    
    Attributes:
        scene      (bpy.types.Scene)      : The Blender scene.
        camera     (bpy.types.Object)     : The main camera object.
        light      (bpy.types.Object)     : The main light object.
    """

    def __init__(
        self,
        scene  : bpy.types.Scene,
        camera : bpy.types.Object,
        light  : bpy.types.Object
    ) -> None:
        """Initializes the EnvironmentRandomizer."""
        self.scene      = scene
        self.camera     = camera
        self.light      = light
        self.env_type   = 'INDOOR'
        self.structural_elements = []

    def clear_environment(self) -> None:
        """Clears procedural environment elements."""
        for name in self.structural_elements:
            if name in bpy.data.objects:
                bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)
        self.structural_elements.clear()

    def spawn_pallet(self) -> None:
        """Spawns a realistic procedural wooden pallet."""
        pallet_parts = []
        
        # 3 Bottom runners
        for i in range(3):
            bpy.ops.mesh.primitive_cube_add(size=1, location=((i-1)*0.4, 0, 0.05))
            part = bpy.context.active_object
            part.scale = (0.06, 0.6, 0.05)
            pallet_parts.append(part)
            
        # 7 Top slats
        for i in range(7):
            bpy.ops.mesh.primitive_cube_add(size=1, location=(0, (i-3)*0.18, 0.12))
            part = bpy.context.active_object
            part.scale = (0.5, 0.07, 0.02)
            pallet_parts.append(part)
            
        bpy.ops.object.select_all(action='DESELECT')
        for part in pallet_parts:
            part.select_set(True)
            part.pass_index = 0
        bpy.context.view_layer.objects.active = pallet_parts[0]
        bpy.ops.object.join()
        
        pallet = bpy.context.active_object
        pallet.name = "Pallet"
        self.structural_elements.append(pallet.name)
        
        mat = bpy.data.materials.new(name="AgedWood")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes['Principled BSDF']
        bsdf.inputs['Base Color'].default_value = (0.2, 0.15, 0.1, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.95
        pallet.data.materials.append(mat)

    def spawn_factory_elements(self) -> None:
        """Adds beams and pillars for factory context."""
        # Main Pillar
        bpy.ops.mesh.primitive_cube_add(size=1, location=(4, 4, 5))
        pillar = bpy.context.active_object
        pillar.name = "Pillar"
        pillar.scale = (0.5, 0.5, 10)
        pillar.pass_index = 0
        self.structural_elements.append(pillar.name)
        
        # Ceiling Beam
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 4, 9))
        beam = bpy.context.active_object
        beam.name = "CeilingBeam"
        beam.scale = (10, 0.3, 0.3)
        beam.pass_index = 0
        self.structural_elements.append(beam.name)
        
        mat = bpy.data.materials.new(name="IndustrialSteel")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes['Principled BSDF']
        bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.12, 1.0)
        bsdf.inputs['Metallic'].default_value = 0.7
        pillar.data.materials.append(mat)
        beam.data.materials.append(mat)

    def randomize_camera(
        self,
        target_loc      : tuple = (0.0, 0.0, 0.0)
    ) -> None:
        """Randomizes the camera position."""
        radius    = random.uniform(3.5, 5.5)
        azimuth   = random.uniform(0.0, 360.0)
        elevation = random.uniform(15.0, 50.0)
        
        az = math.radians(azimuth)
        el = math.radians(elevation)
        
        self.camera.location = Vector((
            radius * math.cos(el) * math.cos(az),
            radius * math.cos(el) * math.sin(az),
            radius * math.sin(el) + 0.5
        ))
        
        direction = Vector(target_loc) - self.camera.location
        self.camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    def randomize_background(self) -> None:
        """Sets up the environment, choosing between OUTDOOR and INDOOR."""
        self.clear_environment()
        self.env_type = random.choice(['OUTDOOR', 'INDOOR'])
        
        world = self.scene.world or bpy.data.worlds.new("World")
        world = self.scene.world
        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        bg_node  = nodes.get('Background')   or nodes.new('ShaderNodeBackground')
        out_node = nodes.get('World Output') or nodes.new('ShaderNodeOutputWorld')

        if not any(link.to_node == out_node and link.to_socket.name == 'Surface' for link in links):
            links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])
        if "IndustrialFloor" not in bpy.data.objects:
            bpy.ops.mesh.primitive_plane_add(size=100)
            floor = bpy.context.active_object
            floor.name = "IndustrialFloor"
            floor.pass_index = 0
            mat = bpy.data.materials.new(name="ConcreteFloor")
            mat.use_nodes = True
            floor.data.materials.append(mat)
        floor = bpy.data.objects["IndustrialFloor"]
        
        # Walls
        wall_names = ["SceneWall_N", "SceneWall_E"]
        for name in wall_names:
            if name not in bpy.data.objects:
                bpy.ops.mesh.primitive_plane_add(size=100)
                wall = bpy.context.active_object
                wall.name = name
                wall.pass_index = 0
                if name == "SceneWall_N":
                    wall.location = (0, 50, 50)
                    wall.rotation_euler = (math.radians(90), 0, 0)
                else:
                    wall.location = (50, 0, 50)
                    wall.rotation_euler = (0, math.radians(90), 0)
                wall.data.materials.append(bpy.data.materials.get("ConcreteFloor"))

        if self.env_type == 'OUTDOOR':
            # Hide walls
            for name in wall_names: bpy.data.objects[name].hide_render = True
            
            # Grass or Dirt
            mat = floor.data.materials[0]
            if random.random() > 0.5:
                mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.01, 0.03, 0.0, 1.0)
            else:
                mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.04, 0.02, 0.01, 1.0)
            
            sky_node = nodes.get('Sky Texture') or nodes.new('ShaderNodeTexSky')
            sky_node.name = 'Sky Texture'
            if not any(link.to_node == bg_node and link.to_socket.name == 'Color' for link in links):
                links.new(sky_node.outputs['Color'], bg_node.inputs['Color'])

            sky_node.sky_type      = 'MULTIPLE_SCATTERING'
            sky_node.sun_elevation = math.radians(random.uniform(15.0, 45.0))
            sky_node.sun_rotation  = math.radians(random.uniform(0.0, 360.0))

            # CRITICAL: Tiny intensities to fix paradise effect
            sky_node.sun_intensity   = random.uniform(0.002, 0.005)
            bg_node.inputs['Strength'].default_value = random.uniform(0.02, 0.05)
            
            self.light.data.energy = random.uniform(50.0, 150.0)
            self.scene.view_settings.exposure = 0.0

        elif self.env_type == 'INDOOR':
            # Show walls
            for name in wall_names: bpy.data.objects[name].hide_render = False
            
            # Concrete
            mat = floor.data.materials[0]
            gray = random.uniform(0.02, 0.06)
            mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (gray, gray, gray, 1.0)

            # Dark world
            for link in bg_node.inputs['Color'].links: links.remove(link)
            bg_node.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
            bg_node.inputs['Strength'].default_value = 0.0

            self.light.data.energy = random.uniform(300.0, 600.0)
            self.light.location    = Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(4, 6)))
            self.scene.view_settings.exposure = 0.0

    def apply_all(self) -> None:
        """Applies all randomizations."""
        self.randomize_camera()
        self.randomize_background()
