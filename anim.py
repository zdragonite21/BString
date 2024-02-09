import bpy
import math

st_frame = bpy.context.scene.frame_start
ed_frame = bpy.context.scene.frame_end

# Create an empty object
empty1 = bpy.data.objects.new("Empty.01", None)
bpy.context.collection.objects.link(empty1)

empty1.empty_display_type = "SPHERE"
empty1.location = [0, 0, 0]


def falloff(frame, tot_frames):
    return math.exp(-frame / 100)


# Animate the empty object
for frame in range(st_frame, ed_frame):  # Animate for 100 frames
    empty1.location[2] = falloff(frame, ed_frame - st_frame) * math.sin(
        frame * 10
    )  # Change the z-coordinate according to a sine function
    empty1.keyframe_insert(
        data_path="location", frame=frame, index=2
    )  # Insert a keyframe
