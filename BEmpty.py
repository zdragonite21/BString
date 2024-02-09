import bpy


class BEmpty:
    def __init__(self, name, location, rot_euler = [0,0,0], display_type="SPHERE", display_size=0.1):
        self.name = name
        self.location = location
        self.rot_euler = rot_euler
        self.obj = None
        self.display_type = display_type
        self.display_size = display_size

    def create(self):
        self.obj = bpy.data.objects.new(self.name, None)
        bpy.context.collection.objects.link(self.obj)
        self.obj.empty_display_type = self.display_type
        self.obj.location = self.location
        self.obj.rotation_euler = self.rot_euler