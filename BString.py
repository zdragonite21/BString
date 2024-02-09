import bpy
import numpy as np

class BPath:
    def __init__(self, name, start, end, ct_point):
        self.start = start
        self.end = end
        self.dist = np.linalg.norm(self.end - self.start)
        self.depth = self.dist / 500
        self.ct_point = ct_point
        self.name = name
        self.curve = None
        self.nurbs = None
        self.obj = None

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
        bpy.context.collection.objects.link(self.obj)
        self.obj.location = (self.start + self.end) / 2
        self.objDir = self.end - self.start
        self.obj.rotation_euler = self.objDir.to_track_quat("X", "Z").to_euler()

    def set_nurbs_points(self, points):
        for i, point in enumerate(points):
            self.nurbs.points[i].co = point

    def set_hook(self, empty, vertex_indices=[1]):
        hook = self.obj.modifiers.new(name="Hook-" + empty.name, type="HOOK")
        hook.object = empty
        hook.vertex_indices_set(vertex_indices)

    def create(self, points):
        self.create_curve()
        self.create_nurbs()
        self.set_nurbs_points(points)
        self.create_obj()

class BEmpty:
    def __init__(self, name, location, display_type="SPHERE", display_size=0.1):
        self.name = name
        self.location = location
        self.empty = None
        self.display_type = display_type
        self.display_size = display_size

    def create(self):
        self.empty = bpy.data.objects.new(self.name, None)
        bpy.context.collection.objects.link(self.empty)
        self.empty.empty_display_type = self.display_type
        self.empty.location = self.location


class BString:
    def __init__(self, name, start, end):
        self.start = start
        self.end = end
        self.name = name
        self.dist = np.linalg.norm(self.end - self.start)
        self.anim_path = None
        self.still_path = None
        self.center_empty = None
        self.anim_empty = None
        self.parent = None

    def create_empties(self):
        self.center_empty = BEmpty("Empty", [0, 0, 0])
        self.anim_empty = BEmpty("Empty", [self.dist / 4, 0, 0])

    def create_parent(self):
        self.parent = BEmpty("BString." + self.name, [0,0,0], display_type="CUBE", display_size=1)
        
    def create_paths(self):
        self.anim_path = BPath(self.name, self.start, self.end, 3)
        self.anim_path.create([[0, 0, 0, 1], [self.anim_path.dist / 4, 0, 0, 1], [self.anim_path.dist / 2, 0, 0, 1]])
        self.still_path = BPath(self.name, self.start, self.end, 2)
        self.still_path.create([[0, 0, 0, 1], [self.still_path.dist / 2, 0, 0, 1]])

    def create_hooks(self):
        self.anim_path.set_hook(self.center_empty, [0])
        self.still_path.set_hook(self.center_empty, [1])
        self.anim_path.set_hook(self.anim_empty, [1])

    def create(self):
        self.create_empties()
        self.create_parent()
        self.create_paths()
        self.create_hooks() 

start = bpy.data.objects["start"].location
end = bpy.data.objects["end"].location
bstring = BString("01", start, end)
bstring.create()
