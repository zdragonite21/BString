import bpy
import numpy as np

start = bpy.data.objects["start"].location
end = bpy.data.objects["end"].location
dist = np.linalg.norm(end - start)
depth = dist / 500

# string 1
stringPts1 = 3
curve1 = bpy.data.curves.new("String", "CURVE")
nurbs1 = curve1.splines.new("NURBS")
obj1 = bpy.data.objects.new("String.01.01", curve1)
empty1 = bpy.data.objects.new("Empty.01", None)
bpy.context.collection.objects.link(obj1)
bpy.context.collection.objects.link(empty1)

empty1.empty_display_type = "PLAIN_AXES"
empty1.location = [dist / 4, 0, 0, 1]

curve1.dimensions = "3D"
curve1.bevel_depth = depth

# nurbs1 transformations
nurbs1.points.add(stringPts1 - 1)

nurbs1.points[0].co = [0, 0, 0, 1]
nurbs1.points[1].co = [dist / 4, 0, 0, 1]
nurbs1.points[2].co = [dist / 2, 0, 0, 1]

nurbs1.use_endpoint_u = True
nurbs1.order_u = stringPts1

hook = obj1.modifiers.new(name="Hook-" + empty1.name, type="HOOK")
hook.object = obj1
hook.vertex_indices_set(1)
