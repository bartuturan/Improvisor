from music21 import *
from itertools import permutations
import random

def cellgenerator(cellnumbers,key,quality='major'):
    if quality=='major':
        basescale=scale.MajorScale(key).getPitches('C4','C5')
    if quality=='minor':
        basescale=scale.DorianScale(key).getPitches()
    if quality=='dominant':
        basescale=scale.MixolydianScale(key).getPitches()
    melodic_cell=[]
    for i in cellnumbers :
        if i>=8:
            melodic_cell.append(note.Note(basescale[(i)%8].transpose('P8')))
        elif i<0:
            melodic_cell.append(note.Note(basescale[(i%8)-1].transpose('-P8')))
        else:
            melodic_cell.append(note.Note(basescale[i-1]))
    return melodic_cell
def inversions(cell):
    inversions=[cell]
    for i in range(len(inversions[0])):
        inversions.append(inversions[i][1:] + [inversions[i][0].transpose('P8')])
    return inversions

def determinekeyandquality(chord):
    key=chord[0]
    flag=0
    quality=''
    if chord[1]=='-' or chord[1]=='#':
        flag=1
    if chord[(1+flag):]=='m':
        quality='minor'
    if chord[(1+flag):]=='7':
        quality='dominant'
    if chord[(1+flag):]=='Maj':
        quality='major'
    if quality=='':
        return -1
    return key,quality
    
def determinerootsandqualities(chordstring):
    chords=chordstring.split(',')
    rootsandqualities=[]
    for chord in chords:
        rootsandqualities.append(determinekeyandquality(chord))        
    return rootsandqualities
#generates which chord tones to voicelead to in each bar
def generate_voiceleading_scheme(rootsandqualities):
    voiceleading_scheme=[]
    for x in rootsandqualities:
        voiceleading_scheme.append(cellgenerator([1,3,5],x[0],x[1]))
    return voiceleading_scheme
#given a note and chord leads the note to chord
def voicelead(nte,chord):
    halfstep=[]
    wholestep=[]
    unison=[]
    for x in chord:
        if abs(nte.pitch.midi-x.pitch.midi)%12==0:
            unison.append(nte)
        if abs(nte.pitch.midi-x.pitch.midi)%12==1 or abs(int(nte.pitch.midi-x.pitch.midi))%12==11:
            if abs(nte.pitch.midi-x.pitch.midi)%12==1:
                halfstep.append(nte.transpose('-m2'))
            else:
                halfstep.append(nte.transpose('m2'))
        if abs(int(nte.pitch.midi-x.pitch.midi))%12==2 or abs(int(nte.pitch.midi-x.pitch.midi))%12==10 :
            if abs(nte.pitch.midi-x.pitch.midi)%12==2:
                halfstep.append(nte.transpose('-M2'))
            else:
                halfstep.append(nte.transpose('M2'))
    if  halfstep :
        return random.choice(halfstep)
    if wholestep:
        return random.choice(wholestep)
    if unison:
        return nte
    return -1
#creates list of cells that make sense on that chord
def create_possiblecells_for_chord(key,quality,cell_scheme):
    possiblecells_scheme=[]
    possiblecells=[]
    possiblecells_with_inversions=[]
    for i in range(len(cell_scheme)):
        for x in permutations(cell_scheme[i]):
            possiblecells_scheme.append(list(x))
    for x in possiblecells_scheme:
        cell=cellgenerator(x,key,quality)
        tempcell=[]
        for n in cell:
            tempcell.append(n.transpose('-P8'))
        possiblecells.append(cell)
        possiblecells.append(tempcell)
    for x in possiblecells:
        for y in inversions(x):
            possiblecells_with_inversions.append(y)
    return possiblecells_with_inversions

    
        
progression_unformatted='Am,D7,GMaj,B7,EMaj'
giantsteps_progression='D-Maj,E7,AMaj,C7,FMaj,FMaj,Bm,E7,AMaj,C7,FMaj,A-7,D-Maj,D-Maj,Gm,C7,FMaj,FMaj,Bm,E7,AMaj,E-m,A-7,D-Maj,D-Maj,Gm,C7,FMaj,FMaj,E-m,A-7'
progression_unformatted=giantsteps_progression
sheet=stream.Stream()
cell_scheme=[[1,2,3,5],[1,-2,-1,1],[1,3,5,-1],[4,3,2,1],[5,4,3,1],[1,2,3,1],[3,2,1,-1],[5,6,7,8],[3,4,5,7],[9,7,5,3],[5,7,9,11],[5,6,7,8]]
rootsandqualities=determinerootsandqualities(progression_unformatted)
voiceleading_scheme=generate_voiceleading_scheme(rootsandqualities)
possiblecells_for_progression=[]
#####converts the progression from text format to tuples
for kq in rootsandqualities:
    possiblecells_for_progression.append(create_possiblecells_for_chord(kq[0],kq[1],cell_scheme))
current_cell=random.choice(possiblecells_for_progression[0])
sheet.append(current_cell)
next_cell=[]
possible_next_cells=[]
choruses=5
for j in range(choruses):
    for i in range(len(rootsandqualities)-1):
        ledtone=voicelead(current_cell[3],voiceleading_scheme[i+1])
        if(ledtone==current_cell[3]):
            ledtone=voicelead(current_cell[0],voiceleading_scheme[i+1])  
        for x in possiblecells_for_progression[i+1]:
            if (x[0].pitch.midi-ledtone.pitch.midi)==0:
                possible_next_cells.append(x)
        if not possible_next_cells:
            ledtone=voicelead(current_cell[0],voiceleading_scheme[i+1])
        for x in possiblecells_for_progression[i+1]:
            if (x[0].pitch.midi-ledtone.pitch.midi)==0:
                possible_next_cells.append(x)
        if not possible_next_cells :
            possible_next_cells.append(current_cell)   
        next_cell=random.choice(possible_next_cells)
        possible_next_cells=[]
        temp=stream.Stream()
        for n in next_cell:
            temp.append(note.Note(n.pitch,quarterLength=0.5))
        sheet.append(temp)
        current_cell=next_cell
sheet.show()
    
    







