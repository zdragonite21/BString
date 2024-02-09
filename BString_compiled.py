import bpy
import numpy as np

"""
BPath: NURBS path on the world plane
"""
class BPath:
    def __init__(self, collection, name, dist, ct_point):
        self.dist = dist
        self.depth = self.dist / 500
        self.ct_point = ct_point
        self.name = name
        self.curve = None
        self.nurbs = None
        self.obj = None
        self.collection = collection

    def create_curve(self):
        self.curve = bpy.data.curves.new(self.name, "CURVE")
        self.curve.dimensions = "3D"
        self.curve.bevel_depth = self.depth

    def create_nurbs(self):
        self.nurbs = self.curve.splines.new("NURBS")
        self.nurbs.points.add(self.ct_point - 1)
        self.nurbs.use_endpoint_u = True
        self.nurbs.order_u = self.ct_point
    
    def create_obj(self):
        self.obj = bpy.data.objects.new(self.name, self.curve)
        self.collection.objects.link(self.obj)

    def set_nurbs_points(self, points):
        for i, point in enumerate(points):
            self.nurbs.points[i].co = point

    def set_hook(self, empty, vertex_indices=[1]):
        hook = self.obj.modifiers.new(name="Hook-" + empty.name, type="HOOK")
        hook.object = empty.obj
        hook.vertex_indices_set(vertex_indices)

    def create(self, points):
        self.create_curve()
        self.create_nurbs()
        self.set_nurbs_points(points)
        self.create_obj()

"""
BEmpty: Empty object with specific properties
"""
class BEmpty:
    def __init__(self, collection, name, location, rot_euler = [0,0,0], display_type="SPHERE", display_size=1, hidden=False):
        self.name = name
        self.location = location
        self.rot_euler = rot_euler
        self.obj = None
        self.display_type = display_type
        self.display_size = display_size
        self.hidden = hidden
        self.collection = collection

    def create(self):
        self.obj = bpy.data.objects.new(self.name, None)
        self.collection.objects.link(self.obj)
        self.obj.empty_display_type = self.display_type
        self.obj.empty_display_size = self.display_size
        self.obj.location = self.location
        self.obj.rotation_euler = self.rot_euler
        if self.hidden:
            self.obj.hide_viewport = True

"""
BString: Mechanism of two BPath objects to create a musical string
"""
class BString:
    def __init__(self, collection, name, start, end):
        self.start = start
        self.end = end
        self.name = name
        self.dist = np.linalg.norm(self.end - self.start)
        self.anim_path = None
        self.still_path = None
        self.center_empty = None
        self.anim_empty = None
        self.end_empty = None
        self.parent = None
        self.collection = collection

    def create_empties(self):
        self.center_empty = BEmpty(self.collection, "center_empty", [0, 0, 0])
        self.center_empty.create()
        self.anim_empty = BEmpty(self.collection, "anim_empty", [0, 0, 0])
        self.anim_empty.create()
        # temporary empty to set constraints
        self.end_empty = BEmpty(self.collection, "end_constraint", [self.dist / 2, 0, 0], hidden=True)
        self.end_empty.create()

        # set constraints for anim_empty to be in the middle
        loc_constraint_mid = self.anim_empty.obj.constraints.new("COPY_LOCATION")
        loc_constraint_end = self.anim_empty.obj.constraints.new("COPY_LOCATION")
        loc_constraint_mid.target = self.center_empty.obj
        loc_constraint_end.target = self.end_empty.obj
        loc_constraint_mid.use_y = False
        loc_constraint_end.use_y = False
        loc_constraint_mid.owner_space = "LOCAL"
        loc_constraint_end.owner_space = "LOCAL"
        loc_constraint_end.target_space = "LOCAL"
        loc_constraint_mid.target_space = "LOCAL"
        loc_constraint_end.influence = 0.5

    def create_paths(self):
        self.anim_path = BPath(self.collection, self.name, self.dist, 3)
        self.anim_path.create([[0, 0, 0, 1], [0, 0, 0, 1], [self.dist / 2, 0, 0, 1]])
        self.still_path = BPath(self.collection, self.name, self.dist, 2)
        self.still_path.create([[0, 0, 0, 1], [-self.dist / 2, 0, 0, 1]])

    def create_hooks(self):
        self.anim_path.set_hook(self.center_empty, [0])
        self.still_path.set_hook(self.center_empty, [0])
        self.anim_path.set_hook(self.anim_empty, [1])

    def create_parent(self):
        loc = (self.start + self.end) / 2
        dir = self.end - self.start
        rot_euler = dir.to_track_quat("X", "Z").to_euler()

        # transform parent
        self.parent = BEmpty(self.collection, "BString." + self.name, loc, rot_euler, display_type="CUBE", display_size=self.dist/10)
        self.parent.create()

        # parent objects
        parent_obj = self.parent.obj
        self.anim_path.obj.parent = parent_obj
        self.still_path.obj.parent = parent_obj
        self.center_empty.obj.parent = parent_obj
        self.anim_empty.obj.parent = parent_obj
        self.end_empty.obj.parent = parent_obj

    def create(self):
        self.create_empties()
        self.create_paths()
        self.create_hooks() 
        self.create_parent()

## Collection
collection = bpy.data.collections.new("BString.01")
bpy.context.scene.collection.children.link(collection)
collection.color_tag = 'COLOR_06'

## Usage   
start = bpy.data.objects["start"].location
end = bpy.data.objects["end"].location

## BString
bstring = BString(collection, "01", start, end)
bstring.create()
