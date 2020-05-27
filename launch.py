import os
import PySimpleGUI as gui
import whisk

tabsize = (150, 20)
defaultFont = "Verdana"
headerFont = "Tahoma"

project = "soldier"

phones = ["AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER", "EY", "F", "G", "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH", "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH"]
hasPhoneme = ['' for x in range(0, 39)]
wordsAvailable = set()
wordsAvailableString = ''

def refreshTabTwo():
	tab2_layout = [
		[gui.Text(' ', font=(defaultFont, 4))],# padding
		[gui.Text(' Keep track of the phonemes and words you have available.', font=(defaultFont, 16), justification='left')],
		[gui.Text(' ', font=(defaultFont, 2))],# padding
		#[gui.Text(' Available Phonemes', font=(defaultFont, 20), justification='left')],
		[gui.Frame(' Available Phonemes ', [
               [gui.Text(p, size=(3, 1), font=(defaultFont, 10), pad=(0,0), relief = gui.RELIEF_RIDGE, auto_size_text=False, justification='center') for p in phones[:20]],
               [gui.Text(y, size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime') for y in hasPhoneme[:20]],
               [gui.Text(p, size=(3, 1), font=(defaultFont, 10), pad=(0,0), relief = gui.RELIEF_RIDGE, auto_size_text=False, justification='center') for p in phones[20:]],

               [gui.Text(y, size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime') for y in hasPhoneme[20:]],
               ], font=(defaultFont, 20))],
               [gui.Text(' Available Words', font=("defaultFont", 20), justification='left')],
               [gui.Multiline(default_text = wordsAvailableString, size=(110, 12))],
               [gui.Text('These words will sound more clear in output mixes, as they were spoken in one of the inputs.')],
               [gui.Text("However, even if a word doesn't appear in this list, Whisk may still be able to generate it if the necessary phonemes are available.")]
        ]
        
	window = gui.Window("Whisk", layout, finalize=True)
	window.refresh()

def refreshLibrary():
	global wordsAvailable
	global wordsAvailableString
	wordsAvailable = []
	for n in range(0, 39):
		if whisk.checkForPhoneme(project, phones[n]):
			hasPhoneme[n] = "Y"
		else:
			hasPhoneme[n] = " "
	wordsAvailable = whisk.getAvailableWords(project)
	wordsAvailableString = '\n'.join([w for w in wordsAvailable])
	#refreshTabTwo()

refreshLibrary()

tab1_layout =  [
		[gui.Text(' ', font=("defaultFont", 4))],# padding
		[gui.Text(' Import audio and video streams for use in the final mix.', font=("defaultFont", 16), justification='left')],
		[gui.Frame(' Import individually ', [     
			[gui.Text('Stream File', size=(20, 1), font=(defaultFont, 12), auto_size_text=False, justification='right'), gui.InputText('...'), gui.FileBrowse()],  
			[gui.Text('Transcript', size=(20, 1), font=(defaultFont, 12), auto_size_text=False, justification='right'), gui.Multiline(default_text='(enter transcript here)', size=(50, 5))],
			[gui.Button('Import file')],
		], font=(defaultFont, 25))],
		[gui.Frame(' Import in bulk ', [  
			[gui.Text('The streams folder should only contain input stream files, and the transcripts folder should only contain transcripts corresponding to those streams.')],
			[gui.Text("Transcripts should be in .txt format, and each transcript should have the same name as the stream it corresponds to \n (e.g. the transcript for 'sample1.wav' should be named 'sample1.txt').")],
			[gui.Text('Streams Folder', size=(20, 1), font=("defaultFont", 12), auto_size_text=False, justification='right'), gui.InputText('...'), gui.FolderBrowse()],  
			[gui.Text('Transcripts Folder', size=(20, 1), font=("defaultFont", 12), auto_size_text=False, justification='right'), gui.InputText('...'), gui.FolderBrowse()],     
			[gui.Button('Import folders')]
		], font=(defaultFont, 25))]
]

tab2_layout = [
		[gui.Text(' ', font=(defaultFont, 4))],# padding
		[gui.Text(' Keep track of the phonemes and words you have available.', font=(defaultFont, 16), justification='left')],
		[gui.Text(' ', font=(defaultFont, 2))],# padding
		#[gui.Text(' Available Phonemes', font=(defaultFont, 20), justification='left')],
		[gui.Frame(' Available Phonemes ', [
               [gui.Text(p, size=(3, 1), font=(defaultFont, 10), pad=(0,0), relief = gui.RELIEF_RIDGE, auto_size_text=False, justification='center') for p in phones[:20]],
               [gui.Text(y, size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime') for y in hasPhoneme[:20]],
               [gui.Text(p, size=(3, 1), font=(defaultFont, 10), pad=(0,0), relief = gui.RELIEF_RIDGE, auto_size_text=False, justification='center') for p in phones[20:]],
               [gui.Text(y, size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime') for y in hasPhoneme[20:]],
               ], font=(defaultFont, 20))],
               [gui.Text(' Available Words', font=("defaultFont", 20), justification='left')],
               [gui.Multiline(default_text = wordsAvailableString, size=(110, 12))],
               [gui.Text('These words will sound more clear in output mixes, as they were spoken in one of the inputs.')],
               [gui.Text("However, even if a word doesn't appear in this list, Whisk may still be able to generate it if the necessary phonemes are available.")]
               ]
               
tab3_layout = [
               [gui.Text(' ', font=(defaultFont, 4))],# padding
		[gui.Text(' Preview and export sentence mixes.', font=(defaultFont, 16), justification='left')],
		[gui.Text(' ', font=(defaultFont, 2))],# padding
		[gui.Text(' Enter your desired message below.', font=(defaultFont, 20), justification='left')],
		[gui.Multiline(size=(150, 5))],
		[gui.Text(' ', size=(48,1)), gui.Checkbox(' Use longest instance of sounds')],
		[gui.Text("By default, Whisk generally uses the second-longest instance of words and phonemes, as the 'longest' instance of a sound is occasionally a sound that was\nincorrectly extended due to a glitch in Gentle.")],
		[gui.Text("However, when no errors are present, using the longest instance of sounds can sometimes result in a clearer mix.")],
		[gui.Text('Export File Name', size=(34, 1), font=(defaultFont, 12), auto_size_text=False, justification='right'), gui.InputText()],
		[gui.Button('Preview'), gui.Button('Export')]
               ]

layout = [
	[gui.Text(project, font=(defaultFont, 32), justification='left')],
	[gui.TabGroup([[gui.Tab(' Inputs ', tab1_layout), gui.Tab(' Library ', tab2_layout), gui.Tab(' Output ', tab3_layout)]], font=(headerFont, 30))],
	[gui.Output(size=(150, 16))]
	]

window = gui.Window("Whisk", layout, finalize=True)
window.Size = (960,720)

while True:
	event, values = window.read()
	if event is None:
		break
	elif event == 'Import file':
		streamName = values['Browse'].split('/')[-1].split('.')[0]
		whisk.importStream(project, values['Browse'])
		whisk.createTranscript(project, streamName, values[1][:-1])
		print("Import of '" + streamName + "' successful.")
		window.refresh()
		whisk.parseStream(project, streamName)
		print("Parsed stream '" + streamName + "'.")
		refreshLibrary()
	elif event == 'Import Folders':
		break
	elif event == 'Preview':
		try:
			whisk.assembleMix(project, values[5][:-1], values[6], False, 'nil', window)
			#print(values)
		except ValueError as e:
			print(e)
			print("Mix assembly failed.")
		window.refresh()
	elif event == 'Export':
		try:
			whisk.assembleMix(project, values[5][:-1], values[6], True, values[7], window)
		except ValueError as e:
			print(e)
			print("Mix assembly failed.")
		window.refresh()
	else:
		print(event)
		window.refresh()

window.close();
