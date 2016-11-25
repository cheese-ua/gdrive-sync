import logging
import os
import sys
import time
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def AuthGDrive():
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile('data/google.obj')
    drive = GoogleDrive(gauth)
    return drive


def FolderList(drive):
    for file1 in drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList():
        logging.info(file1['title'] + ': ' + file1['id'])

def SearchFolder(gdrive, folderRoot, folderName):
    allSubfolders = gdrive.ListFile({'q': "'"+folderRoot+"' in parents and trashed=false"}).GetList()
    for folder in allSubfolders:
        if folder['title'] == folderName:
            logging.info('Found \"'+folderName+'\": '+folder['id'])
            return folder['id']
    logging.info('Not found \"'+folderName+'\"')
    return ''

def GetFolderPrefixForImageType(local_file_path):
    if(local_file_path.upper().find('LINE_CROSS')>=0):
        return "Cross"
    return "Motion"

def GetFolderDateNameForImageType(local_file_path):
    return str(time.strftime("%Y-%m-%d %H", time.localtime(os.path.getctime(local_file_path))))

def CreateKeyHashForFolder(local_file_path):
    return GetFolderPrefixForImageType(local_file_path) + "#" + GetFolderDateNameForImageType(local_file_path)

def SearchOrCreateFolder(gdrive, rootFolderID, newFolderName):
    folderID = SearchFolder(gdrive, rootFolderID, newFolderName)
    if not (folderID == ''):
        return folderID
    folderNew = gdrive.CreateFile({'name': newFolderName, 'title': newFolderName, 'mimeType': 'application/vnd.google-apps.folder', "parents": [{"id": rootFolderID}]})
    folderNew.Upload()
    logging.info('create success '+newFolderName+ ': ' + folderNew['id'])
    return folderNew['id']

def FindGDriveFolderID(gdrive, local_file_path, hash):
    key = CreateKeyHashForFolder(local_file_path)
    logging.info('search folder for ' + key)
    if key in hash:
        logging.info('gfolder from hash (%s) => (%s)' ,key, hash[key])
        return hash[key],hash
    logging.info('start create new folder for ' + key)

    folderCamera = SearchFolder(gdrive, 'root', 'Camera')
    if(folderCamera == ''):
        return '',hash

    folderYearName = time.strftime("%Y", time.localtime(os.path.getctime(local_file_path)))
    folderYearID = SearchOrCreateFolder(gdrive, folderCamera, folderYearName)

    folderMonthName = time.strftime("%Y-%m", time.localtime(os.path.getctime(local_file_path)))
    folderMonthID = SearchOrCreateFolder(gdrive, folderYearID, folderMonthName)

    folderTypeName = GetFolderPrefixForImageType(local_file_path)
    folderTypehID = SearchOrCreateFolder(gdrive, folderMonthID, folderTypeName)

    folderDayName = time.strftime("%Y-%m-%d", time.localtime(os.path.getctime(local_file_path)))
    folderDayID = SearchOrCreateFolder(gdrive, folderTypehID, folderDayName)

    folderHourName = time.strftime("%Y-%m-%d %H", time.localtime(os.path.getctime(local_file_path)))
    folderDayID = SearchOrCreateFolder(gdrive, folderDayID, folderHourName)

    hash[key] = folderDayID
    return folderDayID, hash


def UploadOneFile(drive, file_title, file_path, hash):
    try:
        logging.info('')
        logging.info("Start upload: " + file_title)
        local_file_path = os.path.join(file_path, file_title)
        res = FindGDriveFolderID(drive, local_file_path, hash)
        gdive_folder_id = res[0]
        hash = res[1]
        if gdive_folder_id == '':
            logging.info('GFolder not found')
            return hash
        file_google = drive.CreateFile({'title': file_title, "parents":  [{"id": gdive_folder_id}]})
        file_google.SetContentFile(local_file_path)
        file_google.Upload()
        os.remove(local_file_path)
        logging.info('Upload ok %s => %s ' ,file_title, file_google['id'])
        return hash
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt: "+ UploadOneFile)
        return None
    except OSError:
        logging.info("OSError: "+ OSError.message)
        return hash
    except:
        logging.info("Unexpected error: " + str(sys.exc_info()[0]))
        return hash

def FolderHashWrite(hash):
    f = open('data/hash.txt', 'w')
    for key in hash:
        f.write(key + ':' + hash[key] + '\n')

def InitLog():
    logging.basicConfig(format='%(asctime)s %(message)s', filename='log/cheese-gdrive.log',level=logging.DEBUG)
    stderrLogger=logging.StreamHandler()
    stderrLogger.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logging.getLogger().addHandler(stderrLogger)

def Main():
    InitLog()
    drive = AuthGDrive()
    hash = {}
    path_from = "/home/cheese/Camera"
    file_list = [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]
    for file_title in sorted(file_list, reverse=True):
        hash = UploadOneFile(drive, file_title, path_from, hash)
        if hash == None:
            logging.info("KeyboardInterrupt: Main")
            break


Main()
