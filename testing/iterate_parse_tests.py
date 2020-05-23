import os
from os import path
import gentle
import multiprocessing
from helpers import *

def parseStreamTranscriptPair(projectName, stream):

	print('Parsing "' + stream + '" for ' + projectName + '...')

	projectPath = "mixes/" + projectName
	phonemes = []
	words = []

	# Alignment setup
	resources = gentle.Resources()

	# Read transcript
	with open(projectPath + "/transcripts/" + stream + ".txt", encoding="utf-8") as tx:
		transcript = tx.read()

	# Perform forced alignment
	with gentle.resampled(projectPath + "/streams/" + stream + ".wav") as wavfile:
	    aligner = gentle.ForcedAligner(resources, transcript, nthreads=multiprocessing.cpu_count(), disfluency=False, conservative=False)
	    result = aligner.transcribe(wavfile)

	end = 0
	for w in result.words:
		if w.start is not None:
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

for fileName in os.listdir('mixes/soldier/streams'):
	parseStreamTranscriptPair('soldier', fileName.split('.')[0])

		
