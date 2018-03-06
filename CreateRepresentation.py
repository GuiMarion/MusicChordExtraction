import os
import pickle
from music21 import converter
from metadata import *
from functions import *

metadatas = [TickMetadatas(SUBDIVISION), FermataMetadatas(), KeyMetadatas(window_size=1)]
dataset_path = "DataWithChords"
#dataset_path = "1fileData"
#dataset_path = "Triolets"

pickled_dataset = pickled_dataset_path(dataset_path)
initialization(dataset_path, metadatas=metadatas, voice_ids=[0,1,2])
#PrintRepresentation(dataset_path)

#PrintRepresentationSeparetly(dataset_path)
