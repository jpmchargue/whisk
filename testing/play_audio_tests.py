from pydub import AudioSegment
from pydub.playback import play

sound = AudioSegment.from_wav("mixes/soldier/streams/realgood.wav")
modified = sound[1000:2000]
modified = modified + modified
play(modified)

modified = sound[785:1150]
rev = modified.reverse()
modified = modified + rev
play(modified)
