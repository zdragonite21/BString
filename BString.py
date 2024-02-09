import bpy
import numpy as np

from BPath import BPath 
from BEmpty import BEmpty


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
        self.center_empty.create()
        self.anim_empty = BEmpty("Empty", [self.dist / 4, 0, 0])
        self.anim_empty.create()

    def create_paths(self):
        self.anim_path = BPath(self.name, self.start, self.end, 3)
        self.anim_path.create([[0, 0, 0, 1], [self.anim_path.dist / 4, 0, 0, 1], [self.anim_path.dist / 2, 0, 0, 1]])
        self.still_path = BPath(self.name, self.start, self.end, 2)
        self.still_path.create([[0, 0, 0, 1], [-self.still_path.dist / 2, 0, 0, 1]])

    def create_hooks(self):
        self.anim_path.set_hook(self.center_empty, [0])
        self.still_path.set_hook(self.center_empty, [1])
        self.anim_path.set_hook(self.anim_empty, [1])

    def create_parent(self):
        loc = (self.start + self.end) / 2
        dir = self.end - self.start
        rot_euler = dir.to_track_quat("X", "Z").to_euler()

        self.parent = BEmpty("BString." + self.name, loc, rot_euler, display_type="CUBE", display_size=1)
        self.parent.create()

        parent_obj = self.parent.obj
        self.anim_path.obj.parent = parent_obj
        self.still_path.obj.parent = parent_obj
        self.center_empty.obj.parent = parent_obj
        self.anim_empty.obj.parent = parent_obj

    def create(self):
        self.create_empties()
        self.create_paths()
        self.create_hooks() 
        self.create_parent()

