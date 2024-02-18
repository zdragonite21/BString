import bpy
import numpy as np

"""
BConstraint: Helper to create constraints for an object
"""
class BConstraint:
    def __init__(self, obj):
        self.obj = obj

    def create_copy_loc(self, target, axis, influence):
        constraint = self.obj.constraints.new("COPY_LOCATION")

        props = {
            "owner_space": "LOCAL",
            "target_space": "LOCAL",
            "target": target,
            "influence": influence,
            "use_x": True if 0 in axis else False,
            "use_y": True if 1 in axis else False,
            "use_z": True if 2 in axis else False,
        }

        for prop, value in props.items():
            setattr(constraint, prop, value)

    def create_limit_loc(self, axis, min, max):
        constraint = self.obj.constraints.new("LIMIT_LOCATION")

        props = {
            "owner_space": "LOCAL",
            "use_min_x": True if 0 in axis else False,
            "use_min_y": True if 1 in axis else False,
            "use_min_z": True if 2 in axis else False,
            "use_max_x": True if 0 in axis else False,
            "use_max_y": True if 1 in axis else False,
            "use_max_z": True if 2 in axis else False,
            "min_x": min[0],
            "min_y": min[1],
            "min_z": min[2],
            "max_x": max[0],
            "max_y": max[1],
            "max_z": max[2],
        }

        for prop, value in props.items():
            setattr(constraint, prop, value)

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
BEmpty: Empty object with specific props
"""
class BEmpty:
    def __init__(
        self,
        collection,
        name,
        location,
        rot_euler=[0, 0, 0],
        display_type="SPHERE",
        display_size=1,
        show_name=False,
        hidden=False,
    ):
        self.name = name
        self.obj = None
        self.collection = collection

        self.props = {
            "location" : location,
            "rotation_euler" : rot_euler,
            "empty_display_type" : display_type,
            "empty_display_size" : display_size,
            "hide_viewport" : hidden,
            "show_name" : show_name,
        }

    def create(self):
        self.obj = bpy.data.objects.new(self.name, None)
        self.collection.objects.link(self.obj)

        for prop, value in self.props.items():
            setattr(self.obj, prop, value)
"""
BString: Mechanism of two BPath objects to create a musical string
"""
class BString:
    def __init__(self, collection, name, start, end):
        self.start = start
        self.end = end
        self.name = name
        self.dist = np.linalg.norm(self.end - self.start)
        self.collection = collection

        self.parent = None
        self.pluck_path = None
        self.fret_path = None
        self.empties = {}

    def create_empties(self):
        # pluck empty for plucking motion
        fret = BEmpty(self.collection, "fret_ct", [0, 0, 0], show_name=True)
        fret.create()
        self.empties["fret"] = fret
        # fret empty for "pressing down" motion
        pluck = BEmpty(self.collection, "pluck_ct", [0, 0, 0], show_name=True)
        pluck.create()
        self.empties["pluck"] = pluck
        # start and end empties for constraints
        start = BEmpty(
            self.collection, "start_constraint", [-self.dist / 2, 0, 0], hidden=True
        )
        start.create()
        self.empties["start"] = start
        end = BEmpty(
            self.collection, "end_constraint", [self.dist / 2, 0, 0], hidden=True
        )
        end.create()
        self.empties["end"] = end

        # -------------------------------- Constraints ------------------------------- #

        # set constraints for pluck_empty to be in the middle
        pluck_constraint = BConstraint(self.empties["pluck"].obj)
        pluck_constraint.create_copy_loc(self.empties["fret"].obj, [0, 2], 1)
        pluck_constraint.create_copy_loc(self.empties["end"].obj, [0, 2], 0.5)

        # set constraints for fret empty
        fret_constraint = BConstraint(self.empties["fret"].obj)
        fret_constraint.create_limit_loc([1], [0, 0, 0], [0, 0, 0])
        fret_constraint.create_copy_loc(self.empties["start"].obj, [0], 1)
        fret_constraint.create_copy_loc(self.empties["end"].obj, [0], 0.5)

    def create_paths(self):
        self.pluck_path = BPath(self.collection, "pluck_path", self.dist, 3)
        self.pluck_path.create([[0, 0, 0, 1], [0, 0, 0, 1], [self.dist / 2, 0, 0, 1]])
        self.fret_path = BPath(self.collection, "fret_path", self.dist, 2)
        self.fret_path.create([[0, 0, 0, 1], [-self.dist / 2, 0, 0, 1]])

    def create_hooks(self):
        self.pluck_path.set_hook(self.empties["fret"], [0])
        self.fret_path.set_hook(self.empties["fret"], [0])
        self.pluck_path.set_hook(self.empties["pluck"], [1])

    def create_parent(self):
        loc = (self.start + self.end) / 2
        dir = self.end - self.start
        rot_euler = dir.to_track_quat("X", "Z").to_euler()

        # transform parent
        self.parent = BEmpty(
            self.collection,
            self.name,
            loc,
            rot_euler,
            display_type="CUBE",
            display_size=self.dist / 10,
        )
        self.parent.create()

        # parent paths
        parent_obj = self.parent.obj
        self.pluck_path.obj.parent = parent_obj
        self.fret_path.obj.parent = parent_obj
        # parent empties
        for empty in self.empties.values():
            empty.obj.parent = parent_obj

    def create(self):
        self.create_empties()
        self.create_paths()
        self.create_hooks()
        self.create_parent()

# ============================================================================ #
#                                     USAGE                                    #
# ============================================================================ #

## Collection
name = "BString"
collection = bpy.data.collections.new(name)
bpy.context.scene.collection.children.link(collection)
collection.color_tag = "COLOR_06"

## Usage
start = bpy.data.objects["start"].location
end = bpy.data.objects["end"].location

## BString
bstring = BString(collection, name, start, end)
bstring.create()
