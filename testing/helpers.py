import os
from os import path

def establishLibrary(projectName):
	libPath = "mixes/" + projectName + "/library"
	phones = ["AA", "AE", "AH", "AO", "AW", "AY", "B", "CH", "D", "DH", "EH", "ER", "EY", "F", "G", "HH", "IH", "IY", "JH", "K", "L", "M", "N", "NG", "OW", "OY", "P", "R", "S", "SH", "T", "TH", "UH", "UW", "V", "W", "Y", "Z", "ZH"]

	if path.exists(libPath) is False:
		lib = open(libPath, "w+");
		for p in phones:
			lib.write(p + "\r\n")
		lib.close()

	return libPath
