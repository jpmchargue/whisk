import os
import sys
import re
import pronouncing as pro
from pydub import AudioSegment
from pydub.playback import play

projectName = "soldier"
targetString = "whisk is a quick and easy tool for mixing sentences"
saveName = "about"

projectPath = 'mixes/' + projectName

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
				print('Found instance of "' + ' '.join(seq) + '" at ' + wordDCFile + ':' + str(wordStarts[loc]) + ':' + str(wordEnds[loc + len(seq) - 1]) + '!')
				sound = AudioSegment.from_wav(projectPath + "/streams/" + wordDCFile + ".wav")
				return (sound[wordStarts[loc]:wordEnds[loc + len(seq) - 1]], 1)
	# if the sequence is only one word and it was not found, construct it
	sequenceLength = len(seq)
	if sequenceLength == 1:
		print("Could not find one word sequence " + str(seq) + "- assembling from phonemes...")
		options = pro.phones_for_word(seq[0])
		if len(options) == 0:
			print("No pronunciations could be found for " + seq[0] + "!")
		else:
			phonemeString = ''.join([c for c in options[0] if not c.isdigit()])
			phonemeSequence = phonemeString.split(' ')
			print("Found pronunciation " + str(phonemeSequence))
			result = generatePhonemeSequence(phonemeSequence)
			return (result[0] + AudioSegment.silent(duration=50), result[1])
	# multi-word sequence was not found in one piece- split and recurse
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generateWordSequence(seq[0:i])
		resultB = generateWordSequence(seq[i:sequenceLength])
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
	return optimal

# search through all phoneme decomps for seq
	# if seq is found, return the corresponding stream segment and 1
	# otherwise
		# if seq contains only one element, throw an exception? ("The phoneme 'CH' is needed to assemble the desired output, but is not present in any input streams.")
		# otherwise iterate through all divisions of the sequence and return the one with the least splits
def generatePhonemeSequence(seq):
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
				print('Found instance of "' + ' '.join(seq) + '"!')
				sound = AudioSegment.from_wav(projectPath + "/streams/" + phoneDCFile + ".wav")
				return (sound[phoneStarts[loc]:phoneEnds[loc + len(seq) - 1]], 1)
				
	sequenceLength = len(seq)
	if sequenceLength <= 1:
		raise Error("The phoneme " + seq[0] + " is needed for the desired output, but it is not present in any input streams!")
	
	optimal = (AudioSegment.silent(duration=1), sys.maxsize)
	for i in range(1, sequenceLength):
		resultA = generatePhonemeSequence(seq[0:i])
		resultB = generatePhonemeSequence(seq[i:sequenceLength])
		if (resultA[1] + resultB[1]) < optimal[1]:
			optimal = (resultA[0] + resultB[0], resultA[1] + resultB[1])
	return optimal

#print(findSubsequence([1, 2, 3, 4, 5, 6], [4, 5]))
#print(findSubsequence([1, 2, 3, 4, 5, 6], [3, 5]))

# Clean up and/or mark punctuation
temp = targetString.upper()
temp = temp.replace('*', ' ')
temp = temp.replace('-', ' ')
temp = temp.replace('. ', ' *LONGPAUSE* ')
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

# Padding
acc = acc + AudioSegment.silent(duration=1000)

play(acc)

acc.export(projectPath + "/outputs/" + saveName + ".wav", format="wav")
print("The mix was exported successfully to " + projectPath + "/outputs/" + saveName + ".wav!")
