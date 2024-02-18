import bpy
import bmusic

# ============================================================================ #
#                                     SETUP                                    #
# ============================================================================ #
pluck = bpy.data.objects["anim_empty"]
center = bpy.data.objects["center_empty"]

# clear animation data
pluck.animation_data_clear()
center.animation_data_clear()

# ============================================================================ #
#                                   ANIMATION                                  #
# ============================================================================ #
DAMPENING = 10
midi = bmusic.parse_midi("assets/OneNote.mid")

anim = bmusic.Animator(pluck, "pass_index")

animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [100]

fade_func = lambda x: bmusic.utils.EXPONENTIAL(DAMPENING, x)

proc = bmusic.proc.IntensityFade(
    midi=midi, animkey=animkey, duration=0.2, fade_func=fade_func
)
proc.animate()

# ---------------------------------- drivers --------------------------------- #

s_driver = pluck.driver_add("location", 1)

s_driver.driver.type = "SCRIPTED"

pass_ind = s_driver.driver.variables.new()

pass_ind.name = "pass_ind"
pass_ind.type = "SINGLE_PROP"
pass_ind.targets[0].id = pluck
pass_ind.targets[0].data_path = "pass_index"

s_driver.driver.expression = "5*sin(frame*11)*pass_ind/100"