import bpy

class BPath:
    def __init__(self, collection, name, ct_point):
        self.ct_point = ct_point
        self.name = name
        self.curve = None
        self.nurbs = None
        self.obj = None
        self.collection = collection

    def create_curve(self):
        self.curve = bpy.data.curves.new(self.name, "CURVE")
        self.curve.dimensions = "3D"

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

class BEmpty:
    def __init__(
        self,
        collection,
        name,
        location,
        rot_euler=[0, 0, 0],
        display_type="SPHERE",
        display_size=1,
        hidden=False,
    ):
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

WIDTH = 1.5
LENGTH_FAC = 20
FRET_COUNT = 19
BEVEL_DEPTH = .05
FRET_RATIO = .945

FRET_FUNC = lambda x: FRET_RATIO ** x
WIDTH_FUNC = lambda x: x * .02 + WIDTH

fret_bpaths = []

empties = []

## Collection
collection = bpy.data.collections.new("GUITAR.01")
bpy.context.scene.collection.children.link(collection)
collection.color_tag = "COLOR_07"

bpath = BPath(collection, "frets.001", 2)
width = WIDTH_FUNC(19)
bpath.create([[0, -width/2, 0, 1], [0, width/2, 0, 1]])
fret_bpaths.append(bpath)
bpath.obj.location.x = 0

bpath = BPath(collection, "frets.001", 2)
width = WIDTH_FUNC(-1)
bpath.create([[0, -width/2, 0, 1], [0, width/2, 0, 1]])
fret_bpaths.append(bpath)
bpath.obj.location.x = LENGTH_FAC * FRET_FUNC(-1)


for i in range(FRET_COUNT + 1):
    bpath = BPath(collection, "frets.001", 2)
    width = WIDTH_FUNC(i)
    bpath.create([[0, -width/2, 0, 1], [0, width/2, 0, 1]])
    fret_bpaths.append(bpath)
    bpath.obj.location.x = LENGTH_FAC * FRET_FUNC(i)

    bempty = BEmpty(collection, "fret-markers.001", [0, 0, 0], display_size=.2)
    bempty.create()
    mid = (FRET_FUNC(i - 1) + FRET_FUNC(i)) / 2
    bempty.obj.location.x = LENGTH_FAC * mid
    empties.append(bempty)



for bpath in fret_bpaths:
    bpath.curve.bevel_depth = BEVEL_DEPTH
