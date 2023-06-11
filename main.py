import subprocess
import math
import time
from os import system

def noOverlap(notes):
    print('')
    gap2 = math.floor(24 / const)
    print(const)
    times = []
    for n in notes:
        times.append(n[1])
    for i in range(len(times)-1):
        x = times[i+1:]
        t = times[i]
        while t in x:
            e = x.index(t)
            x[e] += 2
            times[i+1+e] += gap2
        print("{} / {}".format(i + 1, len(times) - 1), end='\r')
    print('')
    for i in range(len(notes)):
        if times[i] != notes[i][1]:
            notes[i][1] = times[i]
            if times[i] > notes[i][2]: notes[i][2] = times[i] + 1
        print("{} / {}".format(i + 1, len(notes) - 1), end='\r')

def startTime(l): return l[1]

def beep(freq, length, start, t):
    while (time.time() - start) * 1000 < t: i = 0
    subprocess.Popen(['./beep/beep', '-f', str(freq), '-l', str(length)])

csv = open('input.csv', 'r').readlines()
split = []
notes = []
curNotes = []
noteNums = []
noteLines = []
playNotes = []

track = -1 # -1 = all
exclude = []

tracks = [track]
if track == -1: tracks = list(range(1, 129))
for i in range(len(tracks) - 1, 0, -1):
    if tracks[i] in exclude: del tracks[i]
for i in range(len(tracks)): tracks[i] = str(tracks[i])

for l in csv:
    split.append(l.split(', '))
    if split[len(split) - 1][2] == 'Tempo':
        tempo = int(split[len(split) - 1][3])

ppqn = int(split[0][5])
bpm = 60000000 / tempo
const = 60000 / (bpm * ppqn)
gap = 16

for i in range(len(split)):
    print("{} / {}".format(i + 1, len(split)), end='\r')
    if split[i][0] in tracks and split[i][2] in ['Note_on_c', 'Note_off_c']:
#        if int(split[i][5]) == 0:
        if split[i][2] == 'Note_off_c':
            j = noteNums.index(int(split[i][4]))
            curNotes[j].append(int(split[i][1]))
            notes.append(curNotes[j])
            noteLines[j].append(i)
            del curNotes[j]
            del noteNums[j]
        else:
            curNotes.append([
                int(split[i][4]),
                int(split[i][1])
            ])
            noteNums.append(int(split[i][4]))
            noteLines.append([i])

notes.sort(key=startTime)
noOverlap(notes)

header = [
    "0, 0, Header, 1, 3, {}\n".format(ppqn),
    "1, 0, Start_track\n",
    "1, 0, End_track\n",
    "2, 0, Start_track\n",
    "2, 0, Title_t, \"Export\"\n",
    "2, 0, Tempo, {}\n".format(tempo),
    "2, 0, Instrument_name_t, \"Piano\"\n",
    "2, 0, MIDI_port, 0\n"
]

outCsv = open('output.csv', 'w')
csvNotes = []
notesOn = []
notesOff = []

for i in range(len(notes)):
    notesOn.append((
        notes[i][0],
        notes[i][1],
        1
    ))
    notesOff.append((
        notes[i][0],
        max((notes[i][1] + gap) - gap, gap + notes[i][1]),
        0
    ))
csvNotes = notesOn + notesOff
csvNotes.sort(key = startTime)

footer = [
    "2, {}, End_track\n".format(csvNotes[len(csvNotes) - 1][1]),
    "0, 0, End_of_file"
]

outCsv.writelines(header)
for n in csvNotes:
    outCsv.write("2, {}, Note_on_c, 1, {}, {}\n".format(n[1], n[0], n[2] * 100))
outCsv.writelines(footer)
outCsv.close()

system("csvmidi output.csv output.mid")
print("Outputed MIDI!")

for n in notes:
    playNotes.append((
        (440 / 32) * (2 ** ((n[0] - 9) / 12)),
        max(math.floor(n[2] * const) - math.floor(n[1] * const) - gap, gap),
        math.floor(n[1] * const)
    ))

print("Number of notes: {}".format(len(notes)))
input("Ready!")

start = time.time()
for i in range(len(playNotes)):
    beep(playNotes[i][0], playNotes[i][1], start, playNotes[i][2])
    print(notes[i])
