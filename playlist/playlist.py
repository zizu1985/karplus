"""
playlist.py

Opis: zabawa z listami odtwarzania iTunes.

Autor: Mahesh Venkitachalam
Strona WWW: electronut.in

Changes:
    1) [DONE] Replace deprecated functions
    2) [DONE] Validacja liczby argumentow dla prametrow wejsciowych
    3) [DONE] Common tracks - utwory sa rowne jezeli poza nazwa maja tez wspolne
    4) [DONE] Replace hist() with own function in plotStats()
    5) [DONE] Calculate correlation between variables in rating/duration chart

"""

import argparse
from matplotlib import pyplot
import plistlib
import numpy as np
import pandas as pd


def findCommonTracks(fileNames):
    """
    Wyszukiwanie wspólnych utworów w danych plikach list odtwarzania 
    i zapisywanie ich w pliku common.txt.
    """    
    # lista zbiorów nazw utworów
    trackNameSets = []
    for fileName in fileNames:
        # tworzenie nowego zbioru
        trackNames = set()
        # wczytywanie listy odtwarzania
        plist = plistlib.load(open(fileName, 'rb'))
        # pobieranie utworów
        tracks = plist['Tracks']
        # iterowanie przez utwory
        for trackId, track in tracks.items():
            try:
                # dodawanie nazwy do zbioru
                trackNames.add((track['Name'], track['Total Time']//1000))
            except:
                # ignorowanie
                pass
        # dodawanie do listy. To jest lista zbiorow.
        trackNameSets.append(trackNames)    
    # pobieranie zbioru wspólnych utworów
    commonTracks = set.intersection(*trackNameSets)
    # zapisywanie w pliku
    if len(commonTracks) > 0:
        f = open("common.txt", 'wb')
        for val in commonTracks:
            s = "%s\n" % val[0]
            f.write(s.encode("UTF-8"))
            print("%s %s" % (val[0], val[1]))
        f.close()
        print("Znaleziono wspólnych utworów %d. "
              "Nazwy utworów zostały zapisane w pliku common.txt." % len(commonTracks))
    else:
        print("Nie ma żadnych wspólnych utworów!")

def plotStats(fileName):
    """
    Wykreślanie niektórych statystyk poprzez odczytywanie informacji o utworach z listy odtwarzania.
    """
    # wczytywanie listy odtwarzania
    plist = plistlib.load(open(fileName,'rb'))
    # pobieranie utworów
    tracks = plist['Tracks']
    # tworzenie list ocen i czasów trwania
    ratings = []
    durations = []
    # iterowanie przez utwory
    for trackId, track in tracks.items():
        try:
            ratings.append(track['Album Rating'])
            durations.append(track['Total Time'])
        except:
            # ignorowanie
            pass

    # upewnienie się, że zostały zgromadzone prawidłowe dane
    if ratings == [] or durations == []:
        print("Nie ma żadnych prawidłowych danych Album Rating/Total Time w %s." % fileName)
        return

    # wykres punktowy
    x = np.array(durations, np.int32)
    # konwersja na minuty
    x = x/60000.0
    y = np.array(ratings, np.int32)
    # Chcemy miec 3 wiersze w 1 kolumnie. Bedziemy rysowac w wykresie 1.
    pyplot.subplot(3, 1, 1)
    pyplot.plot(x, y, 'o')
    pyplot.axis([0, 1.05*np.max(x), -1, 110])
    pyplot.xlabel('Czas trwania utworu')
    pyplot.ylabel('Ocena utworu')

    print(calculate_corr(x,y))

    # rysowanie histogramu. Bedziemy rysowac w wykresie 2.
    pyplot.subplot(3, 1, 2)
    pyplot.hist(x, bins=20)
    pyplot.xlabel('Czas trwania utworu')
    pyplot.ylabel('Liczba utworów')

    # dodanie 3. podwykresu. Bedziemy rysowac w wykresie 3.
    pyplot.subplot(3, 1, 3)
    hist = my_hist(x)
    print(hist)
    pyplot.bar(hist.keys(),hist.values(),width=0.2)
    pyplot.xlabel('Czas trwania utworu - mine')
    pyplot.ylabel('Liczba utworów - mine')

    # wyświetlanie wykresu
    pyplot.show()

def my_hist(seq):
    """
        Create histogram using round to 0.5
        :param seq: Input array of numbers
        :return: Dictionary (key,sequence)
    """
    hist = {}
    for i in seq:
        hist[round(i*2)/2] = hist.get(round(i*2)/2, 0) + 1
    return hist

def calculate_corr(x,y):
    df = pd.DataFrame({'x' : x})
    df['y'] = y
    return df.corr().get_value('x','y')

def findDuplicates(fileName):
    """
    Wyszukiwanie zduplikowanych utworów na danej liście odtwarzania.
    """
    print('Wyszukiwanie zduplikowanych utworów w %s...' % fileName)
    # wczytywanie listy odtwarzania
    plist = plistlib.load(open(fileName, 'rb'))
    # pobieranie utworów
    tracks = plist['Tracks']
    # tworzenie słownika nazw utworów
    trackNames = {}
    # iterowanie przez utwory
    for trackId, track in tracks.items():
        try:
            name = track['Name']
            duration = track['Total Time']
            # czy istnieje już wpis?
            if name in trackNames:
                # jeśli nazwa i czas trwania pasują, zwiększanie licznika
                # zaokrąglanie czasu trwania do najbliższej sekundy
                if duration//1000 == trackNames[name][0]//1000:
                    count = trackNames[name][1]
                    trackNames[name] = (duration, count+1)
            else:
                # dodanie wpisu - czas trwania i licznik
                trackNames[name] = (duration, 1)
        except:
            # ignorowanie
            pass
    # przechowywanie duplikatów w postaci krotek (count, name)
    dups = []
    for k, v in trackNames.items():
        if v[1] > 1:
            dups.append((v[1], k))
    # zapisywanie dups w pliku
    if len(dups) > 0:
        print("Znaleziono duplikatów %d. Nazwy utworów zostały zapisane w pliku dup.txt" % len(dups))
    else:
        print("Nie znaleziono zduplikowanych utworów!")
    f = open("dups.txt", 'wt')
    for val in dups:
        f.write("[%d] %s\n" % (val[0], val[1]))
    f.close()

# Zebranie kodu w funkcji main()
def main():
    # tworzenie parsera
    descStr = """
    Ten program analizuje pliki list odtwarzania (.xml) wyeksportowane z iTunes.
    """
    parser = argparse.ArgumentParser(description=descStr)
    # dodanie wzajemnie wykluczającej się grupy argumentów
    group = parser.add_mutually_exclusive_group()

    # dodanie oczekiwanych argumentów
    group.add_argument('--common', nargs = '*', dest='plFiles', required=False)
    group.add_argument('--stats', nargs =1 , dest='plFile', required=False)
    group.add_argument('--dup', nargs = 1, dest='plFileD', required=False)

    # parsowanie args
    args = parser.parse_args()

    if args.plFiles:
        # Jezeli mniej niz 2 to komunikat i exit
        if len(args.plFiles) < 2:
            print("Do porownania potrzebne sa conajmniej 2 zbiory")
        else:
            # wyszukiwanie wspólnych utworów
            findCommonTracks(args.plFiles)
    elif args.plFile:
        # wykreślanie statystyk
        plotStats(args.plFile[0])
    elif args.plFileD:
        # wyszukiwanie zduplikowanych utworów
        findDuplicates(args.plFileD[0])
    else:
        print("To nie są utwory, których szukasz.")

# metoda main
if __name__ == '__main__':
    main()