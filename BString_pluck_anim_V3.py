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
    def __init__(self, obj, controller, prop, index=-1):
        self.obj = obj
        # objects, constraints, etc
        self.controller = controller
        self.prop = prop
        self.index = index

    def create_mirror(self, prop_name, custom=False):
        props = {
            "type": "SCRIPTED",
            "expression": prop_name,
        }
        driver = self.controller.driver_add(self.prop, self.index)
        for prop, value in props.items():
            setattr(driver.driver, prop, value)

        mirror = driver.driver.variables.new()
        mirror.name = prop_name
        mirror.type = "SINGLE_PROP"
        mirror.targets[0].id = self.obj
        mirror.targets[0].data_path = prop_name if not custom else f'["{prop_name}"]'

    def create_oscillation(self, prop_name, amp=0.5, freq=11, custom=False):
        props = {
            "type": "SCRIPTED",
            "expression": f"{amp}*cos({freq}*frame)*{prop_name}",
        }
        driver = self.controller.driver_add(self.prop, self.index)
        for prop, value in props.items():
            setattr(driver.driver, prop, value)

        osc = driver.driver.variables.new()
        osc.name = prop_name
        osc.type = "SINGLE_PROP"
        osc.targets[0].id = self.obj
        osc.targets[0].data_path = prop_name if not custom else f'["{prop_name}"]'


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
pluck["pluck_fade"] = 0.0
fret["fret_pos"] = 0.0

# ============================================================================ #
#                                   ANIMATION                                  #
# ============================================================================ #

# ---------------------------------- bmusic ---------------------------------- #
midi = bmusic.parse_midi("assets/a-string_1.mid")

# ----------------------------------- pluck ---------------------------------- #
DAMPENING = 0.3

anim = bmusic.Animator(pluck, '["pluck_fade"]')
animkey = bmusic.AnimKey([anim], [0])

animkey["on"] = [1]

fade_func = lambda t: bmusic.utils.EXPONENTIAL(DAMPENING, t)

proc = bmusic.proc.IntensityFade(
    midi=midi, animkey=animkey, fade_func=fade_func, duration=0.2
)
proc.animate()

# creating the oscillation driver
pluck_driver = BDriver(pluck, pluck, "location", 1)
pluck_driver.create_oscillation("pluck_fade", custom=True)


# ------------------------------- fret position ------------------------------ #
OFFSET = 69


def calc_fret_pos(fret_num):
    FRET_RATIO = 0.945
    FRET_FUNC = lambda x: FRET_RATIO**x
    return (FRET_FUNC(fret_num + 1) + FRET_FUNC(fret_num)) / 2


# for msg in midi:
#     print(msg.note)

anim = bmusic.Animator(fret, '["fret_pos"]')
animkey = bmusic.AnimKey([anim], [0])

for i in range(20):
    animkey[f"{i + OFFSET}"] = [1 - calc_fret_pos(i)]

proc = bmusic.proc.ToNote(midi=midi, animkey=animkey, idle_time=0.01)
proc.animate()

# creating a mirror driver
fret_driver = BDriver(fret, fret_ct, "influence")
fret_driver.create_mirror("fret_pos", custom=True)

# -------------------------------- fret height ------------------------------- #
anim = bmusic.Animator(fret, "location", 2)
animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [-0.15]

proc = bmusic.proc.IntensityOnOff(midi=midi, animkey=animkey, duration=0.05)
proc.animate()
