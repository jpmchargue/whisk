import os
import re
import pronouncing as pro
from pydub import AudioSegment
from pydub.playback import play

projectName = "soldier"
targetString = "Woe. Yank key with no brim"
saveName = "yankeewithnobrim"

def generateWordSound(word, phonemes):
	print("Generating " + word + "...")
	for stream in os.listdir(projectPath + '/decomps'):
		with open(projectPath + '/decomps/' + stream) as decomp:
			for line in decomp:
				bookmarkParts = line.split(":")
				w = bookmarkParts[0]
				if w == word:
					baseSound = AudioSegment.from_wav(projectPath + "/streams/" + stream + ".wav")
					return baseSound[int(bookmarkParts[1]):int(bookmarkParts[2])]
	# The complete word can't be found, so assemble it from phones
	print("Full word can't be found, assembling from phonemes...")
	subacc = AudioSegment.silent(duration=1)
	for p in phonemes:
		bookmark = library[p][0].replace('\n', '')
		bookmarkParts = bookmark.split(':')
		addSound = AudioSegment.from_wav(projectPath + "/streams/" + bookmarkParts[0] + ".wav")
		subacc = subacc + addSound[int(bookmarkParts[1]):int(bookmarkParts[2])]
	return subacc

print(targetString)

# Clean up and/or mark punctuation
temp = targetString
temp = temp.replace('*', ' ')
temp = temp.replace('-', ' ')
temp = temp.replace('. ', ' *LONGPAUSE* ')
temp = temp.replace(', ', ' *SHORTPAUSE* ')
temp = temp.replace(': ', ' *LONGPAUSE* ')
temp = temp.replace('; ', ' *LONGPAUSE* ')
temp = temp.replace('.', '')

words = temp.split(' ')

# Generate set of pronunciations
print("Preparing backup pronunciations...")
specials = ('*SHORTPAUSE*', '*LONGPAUSE*')
pronunciations = []
for w in words:
	if w not in specials:
		phones = pro.phones_for_word(w)[0]
		strip = ''.join([c for c in phones if not c.isdigit()])
		pronunciations.append(strip.split(' '))
	else:
		pronunciations.append(w)
print(pronunciations)

# Get library
projectPath = 'mixes/' + projectName
libPath = projectPath + "/library"
library = {}
with open(libPath, "r") as libFile:
	for line in libFile:
		instances = line.split(' ')
		library[instances[0]] = instances[1:]
	libFile.close()
#print(library)

# Assemble the output
acc = AudioSegment.silent(duration=1)
for x in range(0, len(words)):
	if words[x] == '*SHORTPAUSE*':
		acc = acc + AudioSegment.silent(duration=200)
	elif words[x] == '*LONGPAUSE*':
		acc = acc + AudioSegment.silent(duration=500)
	else:
		acc = acc + generateWordSound(words[x], pronunciations[x])
	# Short pause between words
	acc = acc + AudioSegment.silent(duration=50)
acc = acc + AudioSegment.silent(duration=500)

play(acc)

acc.export(projectPath + "/outputs/" + saveName + ".wav", format="wav")
print("The mix was exported successfully to " + projectPath + "/outputs/" + saveName + ".wav!")
