# MusicChordExtraction

This is the git for a project using Neural Networks to generate music. 
For now, we are working on extracting information from midi files in order to fill the Network with a good representation of the scores. 

We are using Python3, Music21 and Tensorflow.

CreateRepresentation.py is the starting point of the project. So, to get started :

	python3 CreateRepresentation.py

To extract informations from another dataset, you can change the name of the directory in CreateRepresentation.py

Attention, the program assume that the chords are in first inversion !!
