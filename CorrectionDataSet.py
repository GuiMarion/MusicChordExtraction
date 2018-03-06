from music21 import *
import os
import numpy as np
import glob


def getFirstChord(song):
	for n in song.flat.notes:
		if str(type(n)) == "<class 'music21.chord.Chord'>":
			return n


for file in glob.glob("Levée/*.mid"):

	song=converter.parse(file)
	instrument.partitionByInstrument(song) 

	print(file, ":", getFirstChord(song).beat)



#fp = s.write('midi', fp='pathToWhereYouWantToWriteIt')

