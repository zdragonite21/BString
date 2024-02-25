import bpy
import bmusic
import numpy as np

# ============================================================================ #
#                                    BSTRING                                   #
# ============================================================================ #
"""
BDriver: Helper driver presets for animation
"""


class BDriver:
    def __init__(self, obj, controller, prop):
        self.obj = obj
        # objects, constraints, etc
        self.controller = controller
        self.prop = prop

    def create_mirror(self, prop_name, custom=False):
        props = {
            "type": "SCRIPTED",
            "expression": prop_name,
        }
        driver = self.controller.driver_add(self.prop)
        for prop, value in props.items():
            setattr(driver.driver, prop, value)

        mirror = driver.driver.variables.new()
        mirror.name = prop_name
        mirror.type = "SINGLE_PROP"
        mirror.targets[0].id = self.obj
        mirror.targets[0].data_path = prop_name if not custom else f'["{prop_name}"]'


# ============================================================================ #
#                                     SETUP                                    #
# ============================================================================ #
pluck = bpy.data.objects["pluck_ct"]
fret = bpy.data.objects["fret_ct"]
fret_ct = fret.constraints["fret_ct"]

# clear animation data
pluck.animation_data_clear()
fret.animation_data_clear()

# create custom property
fret["fret_pos"] = 0.0

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


# ------------------------------- fret position ------------------------------ #
OFFSET = 60


def calc_fret_pos(fret_num):
    FRET_RATIO = 0.945
    FRET_FUNC = lambda x: FRET_RATIO**x
    return (FRET_FUNC(fret_num + 1) + FRET_FUNC(fret_num)) / 2


anim = bmusic.Animator(fret, '["fret_pos"]')
animkey = bmusic.AnimKey([anim], [0])

for i in range(20):
    animkey[f"{i + OFFSET}"] = [calc_fret_pos(i)]

proc = bmusic.proc.ToNote(animkey)

# creating a mirror driver
fret_driver = BDriver(fret, fret_ct, "influence")
fret_driver.create_mirror("fret_pos", True)

# -------------------------------- fret height ------------------------------- #
anim = bmusic.Animator(fret, "location", 2)
animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [-0.1]

proc = bmusic.proc.IntensityOnOff(midi=midi, animkey=animkey)
proc.animate()
