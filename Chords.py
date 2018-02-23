from music21 import *
import glob, os


# Class for the chord, easier to manipulate over functions.
class Chord:

    def __init__(self,initia):
        (c, duration) = initia
        (root, color) = c
        self.root = root
        self.color = color
        self.duration = float(duration)

    # Id order to print nicely
    def __str__(self):
        return (self.root + self.color + "," + str(self.duration))

    # No methods for now, we can acces everyting without 
    # We can imagine here a method transpose(k) which transpose
    # the chord of k semitones.

def copy(Liste):
    Out = []
    for elem in Liste:
        Out.append(elem)
    return Out

# Return the name of the chord from a list of midi number if the chord is in first inversion
def getChord2(chord):
    # Remove multiple occurences of a note
    S = set(chord)
    chord = list(S)
    chord.sort()
    #save = copy(chord)
    root = str(pitch.Pitch(chord[0]).name)
    for i in range(1, len(chord)):
        chord[len(chord)-i] = str(int(chord[len(chord)-i] - chord[0]))
    chord.remove(chord[0])
    chord = "".join(chord)
    color = ""    
    #3-Tones Chords    
    
    #Major Chord
    if chord == "47":
        color = "maj"
    
    #Minor Chord
    elif chord == "37":
        color = "min"

    #Minor Chord
    elif chord == "38":
        color = "min#5"
    
    #Diminished Chord
    elif chord == "36":
        color = "dim"

    # + Chord
    elif chord == "48":
        color = "+"
    
    #4-Tones Chords
    
    #Minor7Chord
    elif chord == "3710":
        color = "min7"

    #MinorMajor7
    elif chord == "3711":
        color = "min(maj7)"
    
    #7Chord
    elif chord == "4710":
        color = "7"

    #7Chord
    elif chord == "5710":
        color = "7sus4"

    #7Chord
    elif chord == "4717":
        color = "7sus4"

    #7Chord
    elif chord == "4610":
        color = "7b5"

    #7ChordWithoutfifth
    elif chord == "410":
        color = "7"
        
     #Major7Chord
    elif chord == "4711":
        color = "maj7"

     #Major7Chord without third and fifth
    elif chord == "11":
        color = "maj7"
        
    #Half-DiminishedChord
    elif chord == "3610":
        color = "m7b5"
    
    #DiminishedChord
    elif chord == "369":
        color = "dim7"
        
    #AlteratedChord
    elif chord == "4810":
        color = "7+"

    #Minor6
    elif chord == "379":
        color = "min6"

    #Major6
    elif chord == "479":
        color = "6"

    #ChordsWithExtensions
        
    #7b9Chord
    elif chord == "471013":
        color = "7b9"

    #b57b9Chord
    elif chord == "461013":
        color = "7b5b9"

    #79Chord
    elif chord == "471014":
        color = "9"

    #sus49Chord
    elif chord == "5714":
        color = "sus49"

    #Minor9Chord
    elif chord == "371014":
        color = "m9"

    #79Chord
    elif chord == "471114":
        color = "maj9"

    # #59Chord
    elif chord == "481014":
        color = "#59"

    # #5b9Chord
    elif chord == "481013":
        color = "7#5b9"

    # #5#9Chord
    elif chord == "481015":
        color = "#5#9"

    # #59ChordWithoutSeventh
    elif chord == "4814":
        color = "#59"

    # #5#9ChordWithoutSeventh
    elif chord == "4815":
        color = "#5#9"
        
    #7#9Chord
    elif chord == "471015":
        color = "7#9"

    #7#9Chord
    elif chord == "471021":
        color = "713"

    #7b5#9Chord
    elif chord == "461015":
        color = "7b5#9"
        
    #m711Chord
    elif chord == "37101417":
        color = "min11"

    #7alt
    elif chord == "3610131620":
        color = "7alt"

    #13Chord
    elif chord == "47101421":
        color = "13"

    #13Chord
    elif chord == "4710141721":
        color = "13"

    #69Chord
    elif chord == "47914":
        color = "69"

    #Minor69Chord
    elif chord == "37914":
        color = "min69"

    elif chord == "47101417":
        color = "11"

    elif chord == "47101418":
        color = "9#11"

    elif chord == "471018":
        color = "7#11"

    elif chord == "471017":
        color = "7sus"

    elif chord == "45710":
        color = "7sus43"

    #LydianChord
    # This Chord is a strange chord : LydianChord or Maj7b5 depending on sources"
    # In any case it appears only once on the corpus, so I analysed it as Maj7b5
    elif chord == "471118":
        color = "maj7b5"

    else:   
        return "None"

    return (root,color)

# Guess the chord name from midi numbers and figure out if the inversion of the chord 
# if there is, a / will notice the bass note. Amin/C means a Amin chord with C as bass.
def getChord(chord):

    chord.sort()
    root = str(pitch.Pitch(chord[0]).name)

    ret = getChord2(chord)

    if  ret != "None":
        return ret

    else :
        invertion = copy(chord)
        invertion[0] += 12
        invertion.sort()

        inv = getChord2(invertion)
        withoutRoot = getChord2(chord[1:])

        if  inv != "None" :
            return (inv[0], inv[1] + '/' + root)

        elif  withoutRoot != "None":
            return (withoutRoot[0], withoutRoot[1] + "/" + root)

        else :
            print("This chord is unknow, please update this function in order to fix that : ")
            print(chord)
            return "None"


# This function help to fix the misunderstood notes of music21: Ab should not be seen as G#.
# We think that is a big problem for a neural network training because the root of a chord
# alors five his function in the key, and this is something we want out NN to learn.
def replaceinKey(String, nbsharps):

    ## TODO ##
    # Make sure that all the alterations are good : for example 
    # D7 should be followed by Gb and not F#

    nbsharps = int(float(nbsharps))
    Sharps = ['F#', 'C#', 'G#', 'D#', 'A#', 'E#', 'B#']
    #Corresponding Flats for sharps order
    CFlats = ['Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C']


    Flats = ['Bb','Eb','Ab','Db','Gb','Cb','Fb']
    # Corresponding Sharps for flats order
    CSharps = ['A#','D#','G#','C#','F#','B','E']

    # The key contains sharps, not flats
    if nbsharps >0:
        for i in range(nbsharps+2):
            if i<len(Sharps):
                String = String.replace(CFlats[i], Sharps[i])

    # The key contrains flats
    if nbsharps < 0 :
        for i in range(+2-nbsharps):
            if i<len(Flats):
                String = String.replace(CSharps[i], Flats[i])

    if nbsharps == 0:
        String = String.replace(CSharps[0], Flats[0])
        String = String.replace(CFlats[0], Sharps[0])
        String = String.replace(CSharps[1], Flats[1])
        String = String.replace(CFlats[1], Sharps[1])

    if nbsharps < 3 and nbsharps > -3:
        String = String.replace(CSharps[0], Flats[0])
        String = String.replace(CFlats[0], Sharps[0]) 

    # This is in order to remove the double alterations that doesn't make any sense in terms 
    # of Jazz chords and are due to errors from music21
    double = ['B#', 'Fb','E#','Cb', 'Gbb', 'Abb', 'Bbb', 'Cbb', 'Dbb', 'Ebb','F##', 'G##', 'A##', 'B##', 'C##', 'D##', 'E##']
    Cdouble = ['C', 'E', 'F','B', 'F', 'G', 'A', 'Bb', 'C', 'D','G', 'A', 'B', 'C#', 'D', 'E', 'F#']
    for i in range(len(double)):
        String = String.replace(double[i], Cdouble[i])
    return String    


# Return all the chords from a music21 Stream
def getChords(song): 

    #We analyse only the chords not the melody (this is for speed reasons and also 
    # because it can appen that there is a chord in the melody section, and we don't 
    # want to take it in account)
    instrument.partitionByInstrument(song) 
    song = song.parts[0]
    key = song.analyze('key')
    nbsharps = key.sharps
    Output = []
    if (str(type(song[2])) == "<class 'music21.note.Rest'>"):
        r = ('rest','')
        c = Chord((r,str(song[2].duration.quarterLength)))
        Output.append(c)
    for n in song.flat.notes:
        #print(n.pitches)
        if str(type(n)) == "<class 'music21.chord.Chord'>":
            chord2 = []
            for note in n.pitches:
                chord2.append(note.ps)

            out = getChord(chord2)
            out = (replaceinKey(out[0].replace("-","b"), nbsharps), replaceinKey(out[1].replace("-","b"), nbsharps))
            out = Chord((out, str(n.duration.quarterLength)))
            Output.append(out)    
    return Output


#Print all chords of all midi files in a nice way
def printChordsinDirectory(dir):
    if dir[-1] == '/':
        dir = dir[:-1]
    for file in glob.glob(dir+"/*.mid"):
        print(file)  
        song = converter.parse(file)
        for chord in getChords(song):
            print(chord, end = " | ")
        print()

#Print all chords of a midi file in a nice way
def printChordsinFile(file):
    print(file)  
    song = converter.parse(file)
    for chord in getChords(song):
        print(chord, end = " | ")
    print()

#printChordsinDirectory("DataWithChords/")
#printChordsinFile("DataWithChords/watermelon_man.mid")


