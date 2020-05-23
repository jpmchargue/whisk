import os
import sys
import re
import time
import pronouncing as pro
from pydub import AudioSegment
from pydub.playback import play

projectName = "soldier"
targetString = "Whisk is a quick and easy tool for sentence mixing."
saveName = "about"

startTime = time.time()

projectPath = 'mixes/' + projectName
wordLibrary = {}
phoneLibrary = {}

def findSubsequence(master, sub):
	subLength = len(sub);
	for n in range(0, 1 + (len(master) - subLength)):
		#print("comparing " + str(master[n:n+subLength]) + " to " + str(sub))
		if master[n:n+subLength] == sub:
			return n
	return -1

# search through all word decomps for seq
	# if seq is found, return the corresponding stream segment and 1
	# otherwise
		# if seq only contains one element, call generatePhonemeSequence on its pronunciation and return that
		# otherwise iterate through all divisions of the sequence and return the one with the least splits
def generateWordSequence(seq):

	seqString = ' '.join(seq)
	if seqString in wordLibrary:
		return wordLibrary[seqString]

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
				sound = AudioSegment.from_wav(projectPath + "/streams/" + wordDCFile + ".wav")
				toReturn = (sound[wordStarts[loc]:wordEnds[loc + len(seq) - 1]], 1)
				wordLibrary[seqString] = toReturn
				return toReturn

	# if the sequence is only one word and it was not found, construct it
	sequenceLength = len(seq)
	if sequenceLength == 1:
		options = pro.phones_for_word(seq[0])
		if len(options) == 0:
			raise ValueError("No examples or pronunciations could be found for " + seq[0] + "! Don't use proper nouns- try replacing it with a similar-sounding word, or multiple shorter words.")
			
		else:
			phonemeString = ''.join([c for c in options[0] if not c.isdigit()])
			phonemeSequence = phonemeString.split(' ')
			result = generatePhonemeSequence(phonemeSequence)
			return (result[0] + AudioSegment.silent(duration=100), result[1])
	# multi-word sequence was not found in one piece- split and recurse
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generateWordSequence(seq[0:i])
		resultB = generateWordSequence(seq[i:sequenceLength])
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
			
	wordLibrary[seqString] = optimal
	return optimal

# search through all phoneme decomps for seq
	# if seq is found, return the corresponding stream segment and 1
	# otherwise
		# if seq contains only one element, throw an exception? ("The phoneme 'CH' is needed to assemble the desired output, but is not present in any input streams.")
		# otherwise iterate through all divisions of the sequence and return the one with the least splits
def generatePhonemeSequence(seq):

	seqString = ' '.join(seq)
	if seqString in phoneLibrary:
		return phoneLibrary[seqString]

	longest = (AudioSegment.silent(duration=1), 0)
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
				if length > longest[1]:
					sound = AudioSegment.from_wav(projectPath + "/streams/" + phoneDCFile + ".wav")
					longest = (sound[phoneStarts[loc]:phoneEnds[loc + len(seq) - 1]], length)
	
	if longest[1] > 0:
		phoneLibrary[seqString] = (longest[0], 1)
		return (longest[0], 1)
	
	sequenceLength = len(seq)
	if sequenceLength <= 1:
		raise ValueError("The phoneme (" + seq[0] + ") is needed for the desired output, but it is not present in any input streams!")
	
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generatePhonemeSequence(seq[0:i])
		resultB = generatePhonemeSequence(seq[i:sequenceLength])
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
	
	phoneLibrary[seqString] = optimal
	return optimal

#print(findSubsequence([1, 2, 3, 4, 5, 6], [4, 5]))
#print(findSubsequence([1, 2, 3, 4, 5, 6], [3, 5]))

# Clean up and/or mark punctuation
temp = targetString.upper()
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
		acc = acc + generateWordSequence(clause.split(' '))[0] + AudioSegment.silent(duration=200)
	acc = acc + AudioSegment.silent(duration=500)

totalTime = time.time() - startTime
print("SUCCESS! Mix completed in " + str(totalTime) + " seconds.")

play(acc)

acc.export(projectPath + "/outputs/" + saveName + ".wav", format="wav")
print("The mix was exported successfully to " + projectPath + "/outputs/" + saveName + ".wav!")
