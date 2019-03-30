"""
ks.py

Wykorzystuje algorytm Karplus-Stronga do generowania dźwięków 
w skali pentatonicznej.

Autor: Mahesh Venkitachalam
"""

import sys, os
import time, random 
import wave, argparse, pygame 
import numpy as np
import curses
from collections import deque
from matplotlib import pyplot as plt

# pokazać wykres algorytmu w akcji?
gShowPlot = False

# dźwięki pentatonicznej skali molowej
# C4-E(b)-F-G-B-C5
pmNotes = {'C4': 262, 'Eb': 311, 'F': 349, 'G':391, 'B':466}

# zapisywanie pliku WAVE
def writeWAVE(fname, data):
    # otwarcie pliku 
    file = wave.open(fname, 'wb')
    # parametry pliku WAV 
    nChannels = 1
    sampleWidth = 2
    frameRate = 44100
    nFrames = 44100
    # ustawienie parametrów
    file.setparams((nChannels, sampleWidth, frameRate, nFrames,
                    'NONE', 'noncompressed'))
    file.writeframes(data)
    file.close()

# generowanie dźwięku o danej częstotliwości
def generateNote(freq):
    nSamples = 44100
    sampleRate = 44100
    N = int(sampleRate/freq)
    # inicjowanie bufora pierścieniowego
    buf = deque([random.random() - 0.5 for i in range(N)])
    # wykres ustawionej flagi 
    if gShowPlot:
        axline, = plt.plot(buf)
    # inicjowanie bufora próbek
    samples = np.array([0]*nSamples, 'float32')
    for i in range(nSamples):
        samples[i] = buf[0]
        avg = 0.995*0.5*(buf[0] + buf[1])
        buf.append(avg)
        buf.popleft()  
        # wykres ustawionej flagi 
        if gShowPlot:
            if i % 1000 == 0:
                axline.set_ydata(buf)
                plt.draw()
      
    # konwertowanie próbek na 16-bitowe wartości, a następnie na łańcuch znaków
    # dla 16-bitów maksymalna wartość to 32767
    samples = np.array(samples * 32767, 'int16')
    return samples.tostring()

# odtwarzanie pliku WAV
class NotePlayer:
    # konstruktor
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1, 2048)
        pygame.init()
        # słownik dźwięków
        self.notes = {}
    # dodawanie dźwięku
    def add(self, fileName):
        self.notes[fileName] = pygame.mixer.Sound(fileName)
    # odgrywanie dźwięku
    def play(self, fileName):
        try:
            self.notes[fileName].play()
        except:
            print(fileName + ' nie został znaleziony!')
    def playRandom(self):
        """odgrywanie losowego dźwięku"""
        index = random.randint(0, len(self.notes)-1)
        note = list(self.notes.values())[index]
        note.play()

# funkcja main()
def main():
    # deklarowanie zmiennej globalnej
    global gShowPlot

    parser = argparse.ArgumentParser(description="Generowanie dźwięków za pomocą algorytmu Karplusa-Stronga.")
    # dodanie argumentów
    parser.add_argument('--display', action='store_true', required=False)
    parser.add_argument('--play', action='store_true', required=False)
    parser.add_argument('--piano', action='store_true', required=False)
    args = parser.parse_args()

    if args.display:
        gShowPlot = True
#        plt.show()

    # tworzenie odtwarzacza dźwięków
    nplayer = NotePlayer()

    print('tworzenie dzwiękow...')
    for name, freq in list(pmNotes.items()):
        fileName = name + '.wav' 
        if not os.path.exists(fileName) or args.display:
            data = generateNote(freq) 
            print('tworzenie ' + fileName + '...')
            writeWAVE(fileName, data) 
        else:
            print(fileName + ' zostal juz utworzony. pomijanie...')
        
        # dodanie dźwięku do odtwarzacza
        nplayer.add(name + '.wav')
        
        # odegranie dźwięku, jeśli została ustawiona flaga display
        if args.display:
            nplayer.play(name + '.wav')
            time.sleep(0.5)
    
    # odegranie losowej melodii
    if args.play:
        while True:
            try: 
                nplayer.playRandom()
                # pauza — od 1 ćwierćnuty do 8 ćwierćnut
                rest = np.random.choice([1, 2, 4, 8], 1, 
                                        p=[0.15, 0.7, 0.1, 0.05])
                time.sleep(0.25*rest[0])
            except KeyboardInterrupt:
                exit()

    # losowy tryb pianina
    if args.piano:
     window = curses.initscr()
     window.nodelay(1)
     while True:
      ch = window.getch()
      if ch >= 0:
        
#            for event in pygame.event.get():
#                if (event.type == pygame.KEYUP):
                    print("wciśnięty klawisz")
                    nplayer.playRandom()
                    time.sleep(0.5)
     # curses.endwin()

    # pokazanie wykresu, jeśli została ustawiona flaga
    if args.display:
#        gShowPlot = True
        plt.show()


# wywołanie main
if __name__ == '__main__':
    main()
