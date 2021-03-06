import os
import PySimpleGUI as gui
import whisk

tabsize = (150, 20)
defaultFont = "Verdana"
headerFont = "Tahoma"
gui.theme("DarkBlue2")

project = "soldier_from_tf2"

phones = ["AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER", "EY", "F", "G", "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH", "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH"]
hasPhoneme = ['' for x in range(0, 39)]
wordsAvailable = set()
wordsAvailableString = ''

wordsAvailable = []
for n in range(0, 39):
	if whisk.checkForPhoneme(project, phones[n]):
		hasPhoneme[n] = "Y"
	else:
		hasPhoneme[n] = " "
wordsAvailable = whisk.getAvailableWords(project)
#wordsAvailableString = '\n'.join([w for w in wordsAvailable])

def refreshLibrary():
	global wordsAvailable
	global wordsAvailableString
	wordsAvailable = []
	for n in range(0, 39):
		if whisk.checkForPhoneme(project, phones[n]):
			hasPhoneme[n] = "Y"
		else:
			hasPhoneme[n] = " "
		window['_TEXT_' + phones[n] + '_'].Update(value = hasPhoneme[n])
	wordsAvailable = whisk.getAvailableWords(project)
	#wordsAvailableString = '\n'.join([w for w in wordsAvailable])
	#refreshTabTwo()
	window[4].Update(values = wordsAvailable)		

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
               [gui.Text(hasPhoneme[y], size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime', key = "_TEXT_" + phones[y] + "_") for y in range(0, 20)],
               [gui.Text(p, size=(3, 1), font=(defaultFont, 10), pad=(0,0), relief = gui.RELIEF_RIDGE, auto_size_text=False, justification='center') for p in phones[20:]],
               [gui.Text(hasPhoneme[y], size=(3, 1), font=(defaultFont, 10), pad=(0,0), auto_size_text=False, justification='center', text_color='lime', key = "_TEXT_" + phones[y] + "_") for y in range(20, 39)],
               ], font=(defaultFont, 20))],
               [gui.Text(' Available Words', font=("defaultFont", 20), justification='left')],
               [gui.Listbox(values = wordsAvailable, size=(110, 12))],
               [gui.Text('These words will sound more clear in output mixes, as they were spoken in one of the inputs.')],
               [gui.Text("However, even if a word doesn't appear in this list, Whisk may still be able to generate it if the necessary phonemes are available.")]
               ]
               
tab3_layout = [
               [gui.Text(' ', font=(defaultFont, 4))],# padding
		[gui.Text(' Preview and export sentence mixes.', font=(defaultFont, 16), justification='left')],
		[gui.Text(' ', font=(defaultFont, 2))],# padding
		[gui.Text(' Enter your desired message below.', font=(defaultFont, 20), justification='left')],
		[gui.Multiline(size=(150, 10))],
		[gui.Text(' ', size=(48,1)), gui.Checkbox(' Use second-longest instance of sounds')],
		[gui.Text("By default, Whisk generally uses the longest instance of words and phonemes. However, the 'longest' instance of a sound is occasionally a sound that was\nincorrectly extended due to a glitch in Gentle.")],
		[gui.Text("If this occurs, the above box can be checked to use the second-longest instance of each sound instead.")],
		[gui.Text('Export File Name', size=(34, 1), font=(defaultFont, 12), auto_size_text=False, justification='right'), gui.InputText()],
		[gui.Button('Preview'), gui.Button('Export')]
               ]

layout = [
	[gui.Text(project, font=(defaultFont, 32), justification='left', key='_PROJECT_TITLE_'), gui.Button('Close Project')],
	[gui.TabGroup([[gui.Tab(' Inputs ', tab1_layout), gui.Tab(' Library ', tab2_layout), gui.Tab(' Output ', tab3_layout)]], font=(headerFont, 30))],
	[gui.Output(size=(150, 16))]
	]

projectsFound = [d for d in os.listdir('mixes') if os.path.isdir(os.getcwd() + '/mixes/' + d)]

home_layout = [
		[gui.Text("Whisk", font=(headerFont, 60))],
		[gui.Text('New Project Name', size=(15, 1), font=(defaultFont, 12), auto_size_text=False, justification='right', key='_NEWNAME_'), gui.InputText(font=(defaultFont, 12)), gui.Button('+ New Project')],
		[gui.Listbox(values = projectsFound, size=(110, 5), font=(defaultFont, 30), enable_events=True, key='_PROJECTS_')],
		#[gui.Text('Path', size=(15, 1), font=(defaultFont, 12), auto_size_text=False, justification='right'), gui.InputText()],
		[gui.Text(' ', font=(defaultFont, 4))],# padding
		[gui.Button('Open')]#, gui.Button('Delete')
	]


window = gui.Window("Whisk", home_layout, finalize=True)
window.Size = (960,540)


while True:
	event, values = window.read()
	if event is None:
		break
	elif event == 'Import file':
		streamName = values['Browse'].split('/')[-1].split('.')[0]
		try:
			whisk.importStream(project, values['Browse'])
			whisk.createTranscript(project, streamName, values[1][:-1])
			print("Import of '" + streamName + "' successful.")
			window.refresh()
			whisk.parseStream(project, streamName)
			print("Parsed stream '" + streamName + "'.")
			refreshLibrary()
		except FileNotFoundError as e:
			print(e)
			print("Import failed.")
			window.refresh() 
	elif event == 'Import folders':
		try:
			whisk.importTranscriptFolder(project, values['Browse1'])
			whisk.importStreamFolder(project, values['Browse0'], window)
			print("Imports from '" + values['Browse0'] + "' and '" + values['Browse1'] + "' successful.")
			window.refresh()
			whisk.parseAllInFolder(project, values['Browse0'])
			print("Parsed all new streams.")
			refreshLibrary()
		except FileNotFoundError as e:
			print(e)
			print("Import failed.")
			window.refresh() 
	elif event == 'Preview':
		try:
			whisk.assembleMix(project, values[5][:-1], not values[6], False, 'nil', window)
			#print(values)
		except ValueError as e:
			print(e)
			print("Mix assembly failed.")
		window.refresh()
	elif event == 'Export':
		try:
			whisk.assembleMix(project, values[5][:-1], not values[6], True, values[7], window)
		except ValueError as e:
			print(e)
			print("Mix assembly failed.")
		window.refresh()
	elif event == 'Close Project':
		window.close()
		#window = gui.Window("Whisk", home_layout, finalize=True)
		#window.Size = (960, 540)
		#window.refresh()
	elif event == 'Open':
		if len(values['_PROJECTS_']) > 0:
			project = values['_PROJECTS_'][0]
			#print(project)
			window.close()
			window = gui.Window("Whisk", layout, finalize=True)
			window.Size = (960,720)
			window['_PROJECT_TITLE_'].Update(value = project)
			refreshLibrary()
	elif event == '+ New Project':
		whisk.setUpProject(values[0])
		project = values[0]
		window.close()
		window = gui.Window("Whisk", layout, finalize=True)
		window['_PROJECT_TITLE_'].Update(value = project)
		refreshLibrary()
	else:
		print(event)
		window.refresh()

window.close();
