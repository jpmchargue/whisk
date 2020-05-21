import os
from os import path
import gentle
import multiprocessing
from helpers import *

projectName = "soldier"
projectPath = "mixes/" + projectName
libPath = establishLibrary(projectName)
library = []
with open(libPath, "r") as libFile:
	for line in libFile:
		library.append(line[:-1])
	libFile.close()
decomp = []

# Alignment setup
stream = "nothingleft"
resources = gentle.Resources()

# create mapping from ARPAbet phone to index in library
indices = {
	'AA': 0, 'AE': 1, 'AH': 2, 'AO': 3, 'AW': 4,
	'AY': 5, 'B': 6, 'CH': 7, 'D': 8, 'DH': 9,	
	'EH': 10, 'ER': 11, 'EY': 12, 'F': 13, 'G': 14,
	'HH': 15, 'IH': 16, 'IY': 17, 'JH': 18, 'K': 19,	
	'L': 20, 'M': 21, 'N': 22, 'NG': 23, 'OW': 24,
	'OY': 25, 'P': 26, 'R': 27, 'S': 28, 'SH': 29,	
	'T': 30, 'TH': 31, 'UH': 32, 'UW': 33, 'V': 34,
	'W': 35, 'Y': 36, 'Z': 37, 'ZH': 38
}

# Read transcript
with open(projectPath + "/transcripts/" + stream + ".txt", encoding="utf-8") as tx:
	transcript = tx.read()

# Perform forced alignment
with gentle.resampled(projectPath + "/streams/" + stream + ".wav") as wavfile:
    aligner = gentle.ForcedAligner(resources, transcript, nthreads=multiprocessing.cpu_count(), disfluency=False, conservative=False)
    result = aligner.transcribe(wavfile)

# JSON output for debugging
#print(result.to_json(indent=2))

# Read the result, and save the data to the temporary project library
for w in result.words:
	start = int(w.start * 1000)
	end = int(w.end * 1000)
	decomp.append(w.word + ":" + str(start) + ":" + str(end))
	for p in w.phones:
		syllable = p.get('phone').split('_')[0].upper()
		phoneStart = start
		start = start + int(p.get('duration') * 1000)
		bookmarkString = stream + ":" + str(phoneStart) + ":" + str(start)
		print(syllable + "   " + str(phoneStart) + "ms   " + str(start) + "ms")
		if syllable in indices:
			if bookmarkString not in library[indices[syllable]]:
				library[indices[syllable]] = library[indices[syllable]] + " " + bookmarkString

print(library)

# save temp library back to persistent library
with open(libPath, "w") as libFile:
	for nl in library:
		libFile.write(nl + "\r\n")
	libFile.close()
		
# generate decomposed transcript
with open(projectPath + "/decomps/" + stream, "w") as decompFile:
	for d in decomp:
		decompFile.write(d + "\r\n")
	decompFile.close()

	
