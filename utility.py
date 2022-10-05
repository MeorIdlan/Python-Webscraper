import os
import datetime

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