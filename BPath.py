import bpy


class BPath:
    def __init__(self, name, dist, ct_point):
        self.dist = dist
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