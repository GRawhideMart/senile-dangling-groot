import bpy

class SceneCompositor:
    """Configures the Compositor to save a Multilayer EXR containing the Depth pass.
    
    Attributes:
        scene (bpy.types.Scene) : The Blender scene.
    """

    def __init__(self, scene: bpy.types.Scene) -> None:
        self.scene = scene
        self.view_layer = scene.view_layers["ViewLayer"]
        self.view_layer.use_pass_z = True

    def build_depth_output(self, output_dir: str) -> None:
        """Constructs a node tree to save the depth pass."""
        self.scene.use_nodes = True
        if not self.scene.compositing_node_group:
            self.scene.compositing_node_group = bpy.data.node_groups.new(name="SceneCompositor", type="CompositorNodeTree")
            
        tree = self.scene.compositing_node_group
        tree.nodes.clear()
        
        rl = tree.nodes.new('CompositorNodeRLayers')
        
        # File Output Node for Depth (Will save as Multilayer EXR in Blender 5)
        out = tree.nodes.new('CompositorNodeOutputFile')
        out.directory = output_dir
        out.file_name = "render_data_####"
        out.file_output_items.clear()
        out.file_output_items.new('FLOAT', 'Depth')
        
        tree.links.new(rl.outputs['Depth'], out.inputs[0])
        
        # Required output for the compositor to run properly
        comp_out = tree.nodes.new('NodeGroupOutput')
        if not any(item.name == "Image" for item in tree.interface.items_tree):
            tree.interface.new_socket(name="Image", in_out='INPUT', socket_type='NodeSocketColor')
        try:
            tree.links.new(rl.outputs['Image'], comp_out.inputs['Image'])
        except KeyError:
            tree.links.new(rl.outputs['Image'], comp_out.inputs[0])
