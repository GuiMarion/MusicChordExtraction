
import os
import pickle
import numpy as np
from music21 import corpus, converter, stream, note, duration, interval, instrument
from music21.analysis.floatingKey import FloatingKeyException
from tqdm import tqdm
from Chords import *

NUM_VOICES = 3

SUBDIVISION = 4  # quarter note subdivision
BEAT_SIZE = 4

SOP = 0
BASS = 1

OCTAVE = 12

PACKAGE_DIR = os.path.realpath(os.path.dirname(__file__))
BACH_DATASET = os.path.join(PACKAGE_DIR,
                            'datasets/raw_dataset/bach_dataset.pickle'
                            )

voice_ids_default = list(range(NUM_VOICES))  # soprano, alto, tenor, bass

SUBDIVISION = 4  # quarter note subdivision
SLUR_SYMBOL = '__'
START_SYMBOL = 'START'
END_SYMBOL = 'END'

def roots_to_input(song, length, index2note, note2index):

    Output = []
    chords = getChords(song)

    roots = [chord.root for chord in chords]
    colors = [chord.color for chord in chords]

    # We add root of chords to index2note and note2index
    for root in roots:
        if root not in index2note[1].values():
            new_index = len(index2note[1])
            index2note[1].update({new_index: root})
            note2index[1].update({root: new_index})

    for chord in chords:
        Output.append(note2index[1][chord.root])
        for i in range(int(chord.duration*4 - 1)):
            Output.append(note2index[1][SLUR_SYMBOL])

    return Output

def colors_to_input(song, length, index2note, note2index):

    Output = []
    chords = getChords(song)

    roots = [chord.root for chord in chords]
    colors = [chord.color for chord in chords]

    # We add color of chords to index2note and note2index
    for color in colors:
        if color not in index2note[2].values():
            new_index = len(index2note[2])
            index2note[2].update({new_index: color})
            note2index[2].update({color: new_index})

    for chord in chords:
        Output.append(note2index[2][chord.color])
        for i in range(int(chord.duration*4 - 1)):
            Output.append(note2index[2][SLUR_SYMBOL])

    return Output


def chorale_to_inputs(chorale, voice_ids, index2notes, note2indexes):
    """
    :param chorale: music21 chorale
    :param voice_ids:
    :param index2notes:
    :param note2indexes:
    :return: (num_voices, time) matrix of indexes
    """
    # we cannot assume all parts have the same length
    length = int(chorale.duration.quarterLength * SUBDIVISION)  # in 16th notes
    inputs = []

    # This is to separate chords and melody
    instrument.partitionByInstrument(chorale)   
    # we feed input with the melody first  
    inputs.append(part_to_inputs(chorale.parts[1], length, index2notes[0], note2indexes[0]))
    # We feed input with chords
    inputs.append(roots_to_input(chorale, length, index2notes, note2indexes))
    inputs.append(colors_to_input(chorale, length, index2notes, note2indexes))

    output = np.array(inputs)
    assert len(output.shape) == 2

    return output

def standard_note(note_or_rest_string):
    if note_or_rest_string == 'rest':
        return note.Rest()
    # treat other additional symbols as rests
    if note_or_rest_string == START_SYMBOL or note_or_rest_string == END_SYMBOL:
        return note.Rest()
    if note_or_rest_string == SLUR_SYMBOL:
        print('Warning: SLUR_SYMBOL used in standard_note')
        return note.Rest()
    else:
        return note.Note(note_or_rest_string)


def _min_max_midi_pitch(note_strings):
    """

    :param note_strings:
    :return:
    """
    all_notes = list(map(lambda note_string: standard_note(note_string),
                         note_strings))
    min_pitch = min(list(
        map(lambda n: n.pitch.midi if n.isNote else 128,
            all_notes
            )
    )
    )
    max_pitch = max(list(
        map(lambda n: n.pitch.midi if n.isNote else 0,
            all_notes
            )
    )
    )
    return min_pitch, max_pitch

def standard_name(note_or_rest):
    if isinstance(note_or_rest, note.Note):
        return note_or_rest.nameWithOctave
    if isinstance(note_or_rest, note.Rest):
        return note_or_rest.name
    if isinstance(note_or_rest, str):
        return note_or_rest

def create_index_dicts(chorale_list, voice_ids=voice_ids_default):
    """
    Returns two lists (index2notes, note2indexes) of size num_voices containing dictionaries
    :param chorale_list:
    :param voice_ids:
    :param min_pitches:
    :param max_pitches:
    :return:
    """
    # store all notes
    voice_ranges = []

    # We fill the voicerange of the melody
    #molodyVoice = [voice_ids[0]]
    for voice_id in [0,1,2]:
        voice_range = set()
        for chorale_path in chorale_list:
            # todo transposition
            chorale = converter.parse(chorale_path)
            part = chorale.parts[1].flat
            for n in part.notesAndRests:
                voice_range.add(standard_name(n))
        # add additional symbols
        voice_range.add(SLUR_SYMBOL)
        voice_range.add(START_SYMBOL)
        voice_range.add(END_SYMBOL)
        voice_ranges.append(voice_range)

    # We fill the voicerange of the chords

    # chordsRootRange = {'A','B','C','D','E','F','G','Ab','Bb',\
    # 'Cb','Db','Eb','Fb','Gb', 'A#','B#','C#','D#','E#','F#','G#'}
    # chordsRootRange.add(SLUR_SYMBOL)
    # chordsRootRange.add(START_SYMBOL)
    # chordsRootRange.add(END_SYMBOL)
    # voice_ranges.append(chordsRootRange)

    # # Maybe to reconsider, I used this document http://www.tsmp.org/keyboard/lias/pdf/symbols.pdf
    # chordsColorRange = {'','min', 'dim', '#5', 'maj7', 'min7', '7', 'dim7', 'm7b5', '9', 'm9', 'maj9', '11', '13'}
    # chordsColorRange.add(SLUR_SYMBOL)
    # chordsColorRange.add(START_SYMBOL)
    # chordsColorRange.add(END_SYMBOL)
    # voice_ranges.append(chordsColorRange)

    # create tables


    index2notes = []
    note2indexes = []
    for voice_index, _ in enumerate(voice_ids):
        l = list(voice_ranges[voice_index])
        index2note = {}
        note2index = {}
        for k, n in enumerate(l):
            index2note.update({k: n})
            note2index.update({n: k})
        index2notes.append(index2note)
        note2indexes.append(note2index)
    return index2notes, note2indexes


# def make_dataset(chorale_list, dataset_name, voice_ids=voice_ids_default,
#                  transpose=False, metadatas=None):
#     X = []
#     X_metadatas = []
#     index2notes, note2indexes = create_index_dicts(chorale_list,
#                                                    voice_ids=voice_ids)

#     # todo clean this part
#     min_max_midi_pitches = np.array(
#         list(map(lambda d: _min_max_midi_pitch(d.values()), index2notes)))
#     min_midi_pitches = min_max_midi_pitches[:, 0]
#     max_midi_pitches = min_max_midi_pitches[:, 1]
#     for chorale_file in tqdm(chorale_list):
#         try:
#             chorale = converter.parse(chorale_file)
#             if transpose:
#                 midi_pitches = [
#                     [n.pitch.midi for n in chorale.parts[voice_id].flat.notes]
#                     for voice_id in voice_ids]
#                 min_midi_pitches_current = np.array(
#                     [min(l) for l in midi_pitches])
#                 max_midi_pitches_current = np.array(
#                     [max(l) for l in midi_pitches])
#                 min_transposition = max(
#                     min_midi_pitches - min_midi_pitches_current)
#                 max_transposition = min(
#                     max_midi_pitches - max_midi_pitches_current)
#                 for semi_tone in range(min_transposition,
#                                        max_transposition + 1):
#                     try:
#                         # necessary, won't transpose correctly otherwise
#                         interval_type, interval_nature = interval.convertSemitoneToSpecifierGeneric(
#                             semi_tone)
#                         transposition_interval = interval.Interval(
#                             str(interval_nature) + interval_type)
#                         chorale_tranposed = chorale.transpose(
#                             transposition_interval)
#                         inputs = chorale_to_inputs(chorale_tranposed,
#                                                    voice_ids=voice_ids,
#                                                    index2notes=index2notes,
#                                                    note2indexes=note2indexes
#                                                    )
#                         md = []
#                         if metadatas:
#                             for metadata in metadatas:
#                                 # todo add this
#                                 if metadata.is_global:
#                                     pass
#                                 else:
#                                     md.append(
#                                         metadata.evaluate(chorale_tranposed))
#                         X.append(inputs)
#                         X_metadatas.append(md)
#                     except KeyError:
#                         print('KeyError: File ' + chorale_file + ' skipped')
#                     except FloatingKeyException:
#                         print(
#                             'FloatingKeyException: File ' + chorale_file + ' skipped')
#             else:
#                 print("Warning: no transposition! shouldn't be used!")
#                 inputs = chorale_to_inputs(chorale, voice_ids=voice_ids,
#                                            index2notes=index2notes,
#                                            note2indexes=note2indexes)
#                 X.append(inputs)

#         except (AttributeError, IndexError):
#             pass

#     dataset = (X, X_metadatas, voice_ids, index2notes, note2indexes, metadatas)
#     pickle.dump(dataset, open(dataset_name, 'wb'), pickle.HIGHEST_PROTOCOL)
#     print(str(len(X)) + ' files written in ' + dataset_name)

def make_dataset(chorale_list, dataset_name, voice_ids=voice_ids_default,
                 transpose=False, metadatas=None):

    X = []
    X_metadatas = []
    index2notes, note2indexes = create_index_dicts(chorale_list,
                                                   voice_ids=voice_ids)

    for chorale_file in tqdm(chorale_list):
        try:
            chorale = converter.parse(chorale_file)
            inputs = chorale_to_inputs(chorale, voice_ids=voice_ids, index2notes=index2notes, note2indexes=note2indexes)
            X.append(inputs)
        except AssertionError:
            pass


    dataset = (X, X_metadatas, voice_ids, index2notes, note2indexes, metadatas)
    pickle.dump(dataset, open(dataset_name, 'wb'), pickle.HIGHEST_PROTOCOL)
    print(str(len(X)) + ' files written in ' + dataset_name)


def compute_min_max_pitches(file_list, voices=[0]):
    """
    Removes wrong chorales
    :param file_list:
    :type voices: list containing voices ids
    :returns: two lists min_p, max_p containing min and max pitches for each voice
    """
    min_p, max_p = [128] * len(voices), [0] * len(voices)
    to_remove = []
    for file_name in file_list:
        choral = converter.parse(file_name)
        for k, voice_id in enumerate(voices):
            try:
                c = choral.parts[voice_id]  # Retain only voice_id voice
                l = list(map(lambda n: n.pitch.midi, c.flat.notes))
                min_p[k] = min(min_p[k], min(l))
                max_p[k] = max(max_p[k], max(l))
            except AttributeError:
                to_remove.append(file_name)
    for file_name in set(to_remove):
        file_list.remove(file_name)
    return np.array(min_p), np.array(max_p)


def filter_file_list(file_list, num_voices=3):
    """
    Only retain num_voices voices chorales
    """
    l = []
    for k, file_name in enumerate(file_list):
        c = converter.parse(file_name)
        print(k, file_name, " ", len(c.parts))
        if len(c.parts) == num_voices:
            l.append(file_name)
    return l



def pickled_dataset_path(dataset_dir):
    # last non-empty part is the dataset name
    dataset_name = [el for el in dataset_dir.split('/') if el][-1]
    return os.path.join(PACKAGE_DIR,
                        'DeepBach/datasets/custom_dataset',
                        dataset_name + '.pickle')

def part_to_inputs(part, length, index2note, note2index):
    """
    Can modify note2index and index2note!
    :param part:
    :param note2index:
    :param index2note:
    :return:
    """

    list_notes = part.flat.notes
    list_note_strings = [n.nameWithOctave for n in list_notes]

    # add entries to dictionaries if not present
    # should only be called by make_dataset when transposing
    for note_name in list_note_strings:
        if note_name not in index2note.values():
            new_index = len(index2note)
            index2note.update({new_index: note_name})
            note2index.update({note_name: new_index})
    j = 0
    i = 0
    t = np.zeros((length, 2))
    is_articulated = True
    list_notes_and_rests = part.flat.notesAndRests
    num_notes = len(list_notes_and_rests)
    while i < length:
        if j < num_notes - 1:
            if list_notes_and_rests[j + 1].offset > i / SUBDIVISION:
                t[i, :] = [note2index[standard_name(list_notes_and_rests[j])],
                           is_articulated]
                i += 1
                is_articulated = False
            else:
                j += 1
                is_articulated = True
        else:
            t[i, :] = [note2index[standard_name(list_notes_and_rests[j])],
                       is_articulated]
            i += 1
            is_articulated = False

    return list(map(lambda pa: pa[0] if pa[1] else note2index[SLUR_SYMBOL], t))


def initialization(dataset_path=None, metadatas=None,
                   voice_ids=voice_ids_default):
    from glob import glob
    print('Creating dataset')
    if dataset_path:

        # We only keep files that are 2 voices (that's how we defined out dataset)
        # For now we are only able to deal with midi files
        fileList = filter_file_list(
            glob(dataset_path + '/*.mid'),
            num_voices=2)

        pickled_dataset = pickled_dataset_path(dataset_path)
        print(pickled_dataset)


    # remove wrong chorales for teissiture reasons :
    # TODO : Change this function in order to fit the best to the teissiture of Jazz songs
    #min_pitches, max_pitches = compute_min_max_pitches(fileList,
    #                                                   voices=voice_ids)
    make_dataset(fileList, pickled_dataset,
                 voice_ids=voice_ids,
                 transpose=True,
                 metadatas=metadatas)



# This function help you to print a graphical representation of the data, for our project 
# we use only two voices : the melody and the chords. So if you want to see if the process 
# has been well executed you should use this one. 
# It will print each bars on one line with the two voices whitout newline.
# If you want to print each voices separetly use PrintRepresentationSeparetly
def PrintRepresentation(pickled_dataset):
    print()
    print("Here is a graphical representation of the data")
    print()

    pickled_dataset = PACKAGE_DIR+"/DeepBach/datasets/custom_dataset/" + pickled_dataset + ".pickle"
    X, X_metadatas, voice_ids, index2notes, note2indexes, metadatas = pickle.load(
            open(pickled_dataset, 'rb'))
    #print("X : ")
    #print(X)
    #print()
    #print("X_metadatas : ")
    #print(X_metadatas)
    #print()
    #print("Voice_ids : ")
    #print(voice_ids)
    #print()
    #print("index2notes : ")
    #print(index2notes)
    #print()
    #print("note2indexes : ")
    #print(note2indexes)
    #print()
    #print("metadatas : ")
    #print(metadatas)

    print()
    print("This is One Song")
    print()
    for elem in X:
        Compt = 0

        for i in range(len(elem[0])):
            if Compt == 16:
                Compt = 0
                print()
                for e in range(i-16, i):
                    print(index2notes[1][int(elem[1][e])], end="")
                print()
                for e in range(i-16, i):
                    print(index2notes[2][int(elem[2][e])], end="")
                print()
                print()

            print(index2notes[0][int(elem[0][i])].replace("-","b"), end="")
            Compt+=1
        print()
        for e in range(len(elem[0])-16, len(elem[0])):
            print(index2notes[1][int(elem[1][e])], end="")
        print()
        for e in range(len(elem[0])-16, len(elem[0])):
            print(index2notes[2][int(elem[2][e])], end="")
        

        print()
        if (elem is not X[-1]):
            print()
            print("Another One")
        print()



def PrintRepresentationSeparetly(pickled_dataset):

    print()
    print("Here is a graphical representation of the data")
    print()
    pickled_dataset = PACKAGE_DIR+"/DeepBach/datasets/custom_dataset/" + pickled_dataset + ".pickle"
    X, X_metadatas, voice_ids, index2notes, note2indexes, metadatas = pickle.load(
            open(pickled_dataset, 'rb'))
    print()
    print("This is One Song")
    print()
    for elem in X:
        Compt = 0
        for i in range(len(elem)):
            print()
            print("This is voice :", i+1)
            for elem2 in elem[i]:
                if Compt == 16:
                    print()
                    Compt = 0
                print(index2notes[i][int(elem2)], end="")
                Compt += 1
        print()
        print()
        print("Another One")
        print()