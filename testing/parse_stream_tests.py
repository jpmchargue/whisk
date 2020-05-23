import os
from os import path
import gentle
import multiprocessing
from helpers import *

projectName = "soldier"
projectPath = "mixes/" + projectName
#libPath = establishLibrary(projectName)
#library = []
#with open(libPath, "r") as libFile:
#	for line in libFile:
#		library.append(line[:-1])
#	libFile.close()
phonemes = []
words = []

# Alignment setup
stream = "Soldier_jeers06"
resources = gentle.Resources()

# Read transcript
with open(projectPath + "/transcripts/" + stream + ".txt", encoding="utf-8") as tx:
	transcript = tx.read()

# Perform forced alignment
with gentle.resampled(projectPath + "/streams/" + stream + ".wav") as wavfile:
    aligner = gentle.ForcedAligner(resources, transcript, nthreads=multiprocessing.cpu_count(), disfluency=False, conservative=False)
    result = aligner.transcribe(wavfile)

# JSON output for debugging
print(result.to_json(indent=2))

# Read the result, and save the data to the temporary project library

#for w in result.words:
#	start = int(w.start * 1000)
#	end = int(w.end * 1000)
#	decomp.append(w.word + ":" + str(start) + ":" + str(end))
#	for p in w.phones:
#		syllable = p.get('phone').split('_')[0].upper()
#		phoneStart = start
#		start = start + int(p.get('duration') * 1000)
#		bookmarkString = stream + ":" + str(phoneStart) + ":" + str(start)
#		print(syllable + "   " + str(phoneStart) + "ms   " + str(start) + "ms")
#		if syllable in indices:
#			if bookmarkString not in library[indices[syllable]]:
#				library[indices[syllable]] = library[indices[syllable]] + " " + bookmarkString

end = 0
for w in result.words:
	start = int(w.start * 1000)
	if start > end:
		phonemes.append("SIL:" + str(end) + ":" + str(start))
	end = int(w.end * 1000)
	words.append(w.word.upper() + ":" + str(start) + ":" + str(end))
	for p in w.phones:
		syllable = p.get('phone').split('_')[0].upper()
		phoneStart = start
		start = start + int(p.get('duration') * 1000)
		phonemes.append(syllable + ":" + str(phoneStart) + ":" + str(start))

# save decomposed phoneme list
with open(projectPath + "/phonemes/" + stream, "w") as phonemeFile:
	for p in phonemes:
		phonemeFile.write(p + "\r\n")
	phonemeFile.close()
		
# save decomposed word list
with open(projectPath + "/words/" + stream, "w") as wordFile:
	for w in words:
		wordFile.write(w + "\r\n")
	wordFile.close()

	
