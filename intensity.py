import bmusic
import bpy

obj = bpy.data.objects["anim_empty"]
midi = bmusic.parse_midi("assets/OneNote.mid")

anim = bmusic.Animator(obj, "pass_index")

animkey = bmusic.AnimKey([anim], [0])
animkey["on"] = [100]

fade_func = lambda x: bmusic.utils.EXPONENTIAL(1, x)

proc = bmusic.proc.IntensityFade(
    midi=midi, animkey=animkey, duration=0.2, fade_func=fade_func
)
proc.animate()
