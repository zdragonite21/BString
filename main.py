import bpy

# from BString import BString
from BPath import BPath 
# from BEmpty import BEmpty

start = bpy.data.objects["start"].location
end = bpy.data.objects["end"].location

# # BPath
path = BPath("String", start, end, 3)
path.create([[0, 0, 0, 1], [path.dist / 4, 0, 0, 1], [path.dist / 2, 0, 0, 1]])

# BString
# bstring = BString("01", start, end)
# bstring.create()