import os
import time
import gentle
import multiprocessing
import shutil
import subprocess
import sys
import re
import pronouncing as pro
from pydub import AudioSegment
from pydub.playback import play
import PySimpleGUI as gui

def setUpProject(name):
	createDirectory("mixes/" + name)
	createDirectory("mixes/" + name + "/streams")
	createDirectory("mixes/" + name + "/transcripts")
	createDirectory("mixes/" + name + "/words")
	createDirectory("mixes/" + name + "/phonemes")
	createDirectory("mixes/" + name + "/outputs")

def createDirectory(path):
	try:
		os.mkdir(path)
	except OSError as error:
		pass

def parseStream(project, name):
	print('Parsing "' + name + '" for ' + project + '...')
	projectPath = "mixes/" + project
	phonemes = []
	words = []

	# Alignment setup
	resources = gentle.Resources()

	# Read transcript
	with open(projectPath + "/transcripts/" + name + ".txt", encoding="utf-8") as tx:
		transcript = tx.read()

	# Perform forced alignment
	with gentle.resampled(projectPath + "/streams/" + name + ".wav") as wavfile:
	    aligner = gentle.ForcedAligner(resources, transcript, nthreads=multiprocessing.cpu_count(), disfluency=False, conservative=False)
	    result = aligner.transcribe(wavfile)

	# Assemble word and phoneme timestamp lists
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

	# save phoneme timestamp list
	with open(projectPath + "/phonemes/" + name, "w") as phonemeFile:
		for p in phonemes:
			phonemeFile.write(p + "\r\n")
		phonemeFile.close()
			
	# save word timestamp list
	with open(projectPath + "/words/" + name, "w") as wordFile:
		for w in words:
			wordFile.write(w + "\r\n")
		wordFile.close()

def importStream(project, streamPath):
	fileName = streamPath.split('/')[-1].split('.')[0]
	fileType = streamPath.split('.')[-1]
	if fileType == "wav":
		shutil.copy(streamPath, 'mixes/' + project + '/streams/' + fileName + '.wav')
		return 1
	elif fileType == "mp3":
		subprocess.call(['ffmpeg', '-i', streamPath, 'mixes/' + project + '/streams/' + fileName + '.wav'])
		return 1
	return 0
	
def importStreamFolder(project, streamFolderPath):
	for stream in os.listdir(streamFolderPath):
		importStream(project, streamFolderPath + '/' + stream)
		
def importTranscript(project, transcriptPath):
	fileName = transcriptPath.split('/')[-1].split('.')[0]
	fileType = transcriptPath.split('.')[-1]
	if fileType == "txt":
		shutil.copy(transcriptPath, 'mixes/' + project + '/transcripts/' + fileName + '.txt')
		return 1
	return 0
	
def importTranscriptFolder(project, transcriptFolderPath):
	for transcript in os.listdir(transcriptFolderPath):
		importTranscript(project, transcriptFolderPath + '/' + transcript)
	
def createTranscript(project, streamName, text):
	with open('mixes/' + project + '/transcripts/' + streamName + '.txt', 'w') as transcript:
		transcript.write(text)

def findSubsequence(master, sub):
	subLength = len(sub);
	for n in range(0, 1 + (len(master) - subLength)):
		#print("comparing " + str(master[n:n+subLength]) + " to " + str(sub))
		if master[n:n+subLength] == sub:
			return n
	return -1
	
def generateWordSequence(seq, window):
	seqString = ' '.join(seq)
	if seqString in wordLibrary:
		return wordLibrary[seqString]

	longest = (AudioSegment.silent(duration=1), 0)
	secondLongest = (AudioSegment.silent(duration=1), 0)
	shortest = (AudioSegment.silent(duration=1), sys.maxsize)
	for wordDCFile in os.listdir(projectPath + '/words'):
		inputWords = []
		wordStarts = []
		wordEnds = []
		with open(projectPath + '/words/' + wordDCFile, "r") as wordDC:
			for line in wordDC:
				row = line.split(':')
				inputWords.append(row[0])
				wordStarts.append(int(row[1]))
				wordEnds.append(int(row[2]))
			loc = findSubsequence(inputWords, seq)
			if loc > -1: # the entire sequence was found intact
				print('Found instance of "' + seqString + '"!')
				window.refresh() # I hate that I have to do this, but it works
				length = wordEnds[loc + len(seq) - 1] - wordStarts[loc]
				if length < shortest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + wordDCFile + ".wav")
					shortest = (sound[wordStarts[loc]:wordEnds[loc + len(seq) - 1]], length)
				if length > longest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + wordDCFile + ".wav")
					secondLongest = longest
					longest = (sound[wordStarts[loc]:wordEnds[loc + len(seq) - 1]], length)
				elif length > secondLongest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + wordDCFile + ".wav")
					secondLongest = (sound[wordStarts[loc]:wordEnds[loc + len(seq) - 1]], length)
	
	# Return the second-longest instance of the word.
	# Generally, longer instances of words are better for mixes, as they tend to be spoken more clearly.
	# However, Gentle's alignment has a few bugs, and what appears to be the longest instance of a word 
	# is occasionally an incorrect outliar that 'stole' some of the following word.
	# Using these buggy words produces low-quality results, since they introduce garbage syllables into the mix.
	# So, to avoid this Whisk always attempts to use the second-longest instance of a word.
	# If only one instance was found, it uses that.
	if returnLongest is True:
		if longest[1] > 0:
			wordLibrary[seqString] = (longest[0], 1)
			return (longest[0], 1)
	else:
		if secondLongest[1] > 0 and secondLongest[1] != shortest[1]:
			wordLibrary[seqString] = (secondLongest[0], 1)
			return (secondLongest[0], 1)
		elif longest[1] > 0:
			wordLibrary[seqString] = (longest[0], 1)
			return (longest[0], 1)

	# if the sequence is only one word and it was not found, construct it
	sequenceLength = len(seq)
	if sequenceLength == 1:
		options = pro.phones_for_word(seq[0])
		if len(options) == 0:
			raise ValueError("No examples or pronunciations could be found for " + seq[0] + "! Don't use proper nouns- try replacing it with a similar-sounding word, or multiple shorter words.")
		else:
			phonemeString = ''.join([c for c in options[0] if not c.isdigit()])
			phonemeSequence = phonemeString.split(' ')
			result = generatePhonemeSequence(phonemeSequence, window)
			return (result[0] + AudioSegment.silent(duration=75), result[1])
	# multi-word sequence was not found in one piece- split and recurse
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generateWordSequence(seq[0:i], window)
		resultB = generateWordSequence(seq[i:sequenceLength], window)
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
	wordLibrary[seqString] = optimal
	return optimal

def generatePhonemeSequence(seq, window):
	seqString = ' '.join(seq)
	if seqString in phoneLibrary:
		return phoneLibrary[seqString]

	longest = (AudioSegment.silent(duration=1), 0)
	secondLongest = (AudioSegment.silent(duration=1), 0)
	for phoneDCFile in os.listdir(projectPath + '/phonemes'):
		inputPhones = []
		phoneStarts = []
		phoneEnds = []
		with open(projectPath + "/phonemes/" + phoneDCFile, "r") as phoneDC:
			for line in phoneDC:
				row = line.split(':')
				inputPhones.append(row[0])
				phoneStarts.append(int(row[1]))
				phoneEnds.append(int(row[2]))
			loc = findSubsequence(inputPhones, seq)
			if loc > -1:
				length = phoneEnds[loc + len(seq) - 1] - phoneStarts[loc]
				print('Found instance of (' + ' '.join(seq) + ') with length: ' + str(length))
				window.refresh()
				if length > longest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + phoneDCFile + ".wav")
					secondLongest = longest
					longest = (sound[phoneStarts[loc]:phoneEnds[loc + len(seq) - 1]], length)
				elif length > secondLongest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + phoneDCFile + ".wav")
					secondLongest = (sound[phoneStarts[loc]:phoneEnds[loc + len(seq) - 1]], length)
	
	if returnLongest is True:
		if longest[1] > 0:
			phoneLibrary[seqString] = (longest[0], 1)
			return (longest[0], 1)
	else:
		if secondLongest[1] > 0:
			phoneLibrary[seqString] = (secondLongest[0], 1)
			return (secondLongest[0], 1)
		elif longest[1] > 0:
			phoneLibrary[seqString] = (longest[0], 1)
			return (longest[0], 1)
	
	sequenceLength = len(seq)
	if sequenceLength <= 1:
		raise ValueError("The phoneme (" + seq[0] + ") is needed for the desired output, but it is not present in any input streams!")
	
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generatePhonemeSequence(seq[0:i], window)
		resultB = generatePhonemeSequence(seq[i:sequenceLength], window)
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
	phoneLibrary[seqString] = optimal
	return optimal
	
def assembleMix(projectName, targetString, rL, doExport, saveName, window):
	global wordLibrary
	global phoneLibrary
	global projectPath
	global returnLongest
	returnLongest = rL
	startTime = time.time()
	projectPath = 'mixes/' + projectName
	wordLibrary = {}
	phoneLibrary = {}
	
	# Clean up and/or mark punctuation
	temp = targetString.upper()
	temp = temp.replace('\n', ' ')
	temp = temp.replace('*', ' ')
	temp = temp.replace('-', ' ')
	temp = temp.replace('. ', ' *LONGPAUSE* ')
	temp = temp.replace('! ', ' *LONGPAUSE* ')
	temp = temp.replace('? ', ' *LONGPAUSE* ')
	temp = temp.replace(', ', ' *SHORTPAUSE* ')
	temp = temp.replace(': ', ' *LONGPAUSE* ')
	temp = temp.replace('; ', ' *LONGPAUSE* ')
	temp = temp.replace('.', '')
	
	acc = AudioSegment.silent(duration=1)
	for sentence in temp.split(' *LONGPAUSE* '):
		for clause in sentence.split(' *SHORTPAUSE* '):
			print('Assembling clause "' + clause + '"')
			window.refresh()
			acc = acc + generateWordSequence([c for c in clause.split(' ') if c != ''], window)[0] + AudioSegment.silent(duration=200)
		acc = acc + AudioSegment.silent(duration=500)

	totalTime = time.time() - startTime
	print("SUCCESS! Mix completed in " + str(totalTime) + " seconds.")
	window.refresh()

	if doExport is False:
		play(acc)
	else:
		acc.export(projectPath + "/outputs/" + saveName + ".wav", format="wav")
		print("The mix was exported successfully to " + projectPath + "/outputs/" + saveName + ".wav!")
		window.refresh()

def checkForPhoneme(project, phoneme):
	for phoneFile in os.listdir("mixes/" + project + "/phonemes"):
		with open("mixes/" + project + "/phonemes/" + phoneFile, 'r') as phoneList:
			for line in phoneList:
				if line.split(':')[0] == phoneme:
					return True
	return False

def getAvailableWords(project):
	words = set()
	for wordFile in os.listdir("mixes/" + project + "/words"):
		with open("mixes/" + project + "/words/" + wordFile, 'r') as wordList:
			for line in wordList:
				words.add(line.split(':')[0])
	return words
