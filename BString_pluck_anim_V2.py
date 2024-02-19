import bpy
import bmusic
import numpy as np

# ============================================================================ #
#                                     SETUP                                    #
# ============================================================================ #
pluck = bpy.data.objects["pluck_ct"]
fret = bpy.data.objects["fret_ct"]
fret_ct = fret.constraints["fret_ct"]

# clear animation data
pluck.animation_data_clear()
fret.animation_data_clear()

# ============================================================================ #
#                                   ANIMATION                                  #
# ============================================================================ #

# ---------------------------------- bmusic ---------------------------------- #
midi = bmusic.parse_midi("assets/simple_scale.mid")

# ----------------------------------- pluck ---------------------------------- #
DAMPENING = 10

anim = bmusic.Animator(pluck, "location", 1)

animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [0.5]

fade_func = lambda t: bmusic.utils.EXPONENTIAL(0.2, t) * np.cos(t * 50)

proc = bmusic.proc.IntensityFade(
    midi=midi,
    animkey=animkey,
    fade_func=fade_func,
    key_interval=0.02,
    off_thres=-10,
    max_len=1,
)
proc.animate()


# ----------------------------------- fret ----------------------------------- #
def calc_fret_pos(fret_num):
    FRET_RATIO = 0.945
    FRET_FUNC = lambda x: FRET_RATIO**x
    return (FRET_FUNC(fret_num + 1) + FRET_FUNC(fret_num)) / 2


anim = bmusic.Animator(fret, "pass_index", 0)

OFFSET = 60

handle = "AUTO_CLAMPED"

for msg in midi:
    fret_num = msg.note - OFFSET
    pos = calc_fret_pos(fret_num) * 1000
    anim.animate(msg.start, pos, handle=handle)
    if msg.next() is not None:
        anim.animate(msg.next().start - 1, pos, handle=handle)
    # if msg.next() is not None:
    #     anim.animate(msg.end + 1, 1000, handle=handle)
    #     anim.animate(msg.next().start - 1, 1000, handle=handle)

anim = bmusic.Animator(fret, "location", 2)
animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [-0.1]

proc = bmusic.proc.IntensityOnOff(midi=midi, animkey=animkey)
proc.animate()

# ---------------------------------- drivers --------------------------------- #

# s_driver = pluck.driver_add("location", 1)

# s_driver.driver.type = "SCRIPTED"

# pass_ind = s_driver.driver.variables.new()

# pass_ind.name = "pass_ind"
# pass_ind.type = "SINGLE_PROP"
# pass_ind.targets[0].id = pluck
# pass_ind.targets[0].data_path = "pass_index"

# s_driver.driver.expression = "5*sin(frame*11)*pass_ind/100"
