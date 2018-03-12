import os
import pickle
from music21 import converter
from metadata import *
from functions import *
import sys

#dataset_path = "DataWithChords"
#dataset_path = "1fileData"
#dataset_path = "Triolets"


def main(dataset_path, print_true):
	metadatas = [TickMetadatas(SUBDIVISION), FermataMetadatas(), KeyMetadatas(window_size=1)]
	pickled_dataset = pickled_dataset_path(dataset_path)
	initialization(dataset_path, metadatas=metadatas, voice_ids=[0,1,2])
	
	if print_true:
		PrintRepresentation(dataset_path)

	#PrintRepresentationSeparetly(dataset_path)

if __name__ == "__main__":

	if len(sys.argv) == 2:
		main(sys.argv[1], False)
	elif len(sys.argv) == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print("Usage: Python3 CreateRepresentation <path to files>, PrintReprensation (optional)")
