import PySimpleGUI as gui

layout = [[gui.Text("test")]]

window = gui.Window("Whisk", layout, finalize=True)
window.Size = (960,540)

while True:
	event, values = window.read()
	if event is None:
		break

window.close();
