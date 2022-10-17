import os
import datetime
from playsound import playsound

def getInputFile():
    currDir = os.getcwd()
    inputDir = os.path.join(currDir, 'inputs')
    files = os.listdir(inputDir)

    print('Please select a file as input for the webscraper:')
    for i,f in enumerate(files):
        print(f'{i+1}. {f}')
    select = int(input('Select a file (0 to cancel)(ex: 1): '))
    while select < 0 or select > len(files):
        select = int(input('Select a file (0 to cancel)(ex: 1): '))

    if select != 0:
        return files[select-1]
    return ''

def createCSV(df,query):
    currDir = os.getcwd()
    dataDirectoryName = 'data'
    dataDir = os.path.join(currDir, dataDirectoryName)
    if not os.path.isdir(dataDir):
        print('Creating data folder...')
        os.mkdir(dataDir)

    currDate_day = datetime.datetime.now().strftime('%d.%m.%Y')
    dayDir = os.path.join(dataDir, currDate_day)
    if not os.path.isdir(dayDir):
        print('Creating a folder to store today\'s data...')
        os.mkdir(dayDir)

    dataFileName = os.path.join(dayDir, f'items-{query}.csv')
    df.to_csv(dataFileName, index=False, encoding='utf8')

def notify():
    currDir = os.getcwd()
    soundDir = 'assets/sound/pop.wav'
    fullPath = os.path.join(currDir, soundDir)
    playsound(fullPath)