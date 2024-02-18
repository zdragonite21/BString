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
bpy.context.collection.objects.link(obj1)

curve1.dimensions = "3D"
curve1.bevel_depth = depth

# nurbs1 transformations
nurbs1.points.add(stringPts1 - 1)

nurbs1.points[0].co = [0, 0, 0, 1]
nurbs1.points[1].co = [dist / 4, 0, 0, 1]
nurbs1.points[2].co = [dist / 2, 0, 0, 1]

nurbs1.use_endpoint_u = True
nurbs1.order_u = stringPts1

# obj1 transformations
obj1.location = (start + end) / 2
objDir1 = end - start
obj1.rotation_euler = objDir1.to_track_quat("X", "Z").to_euler()

# string 2
stringPts2 = 2
curve2 = bpy.data.curves.new("String", "CURVE")
nurbs2 = curve2.splines.new("NURBS")
obj2 = bpy.data.objects.new("String.01.02", curve2)
bpy.context.collection.objects.link(obj2)

curve2.dimensions = "3D"
curve2.bevel_depth = depth

# nurbs2 transformations
nurbs2.points.add(stringPts2 - 1)

nurbs2.points[0].co = [-dist / 2, 0, 0, 1]
nurbs2.points[1].co = [0, 0, 0, 1]

nurbs2.use_endpoint_u = True
nurbs2.order_u = stringPts2

# obj2 transformations
obj2.location = (start + end) / 2
objDir2 = end - start
obj2.rotation_euler = objDir2.to_track_quat("X", "Z").to_euler()
