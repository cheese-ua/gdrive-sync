import logging
import os
import sys
import time
import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

#root_photo_folder = '0B0o5FIq3lVzcR3ozSjc4cW44VXc'
root_photo_folder='17FaEl_ggnPaj932nqs5qEP42BU9Tqzql3NHZLZ_hVs8'
def AuthGDrive():
    gauth = GoogleAuth()
    #gauth.LocalWebserverAuth()
    # 'data/service_acc.json'
    gauth.LoadCredentialsFile('data/google.obj')
    drive = GoogleDrive(gauth)
    return drive


def FolderList(drive):
    for file1 in drive.ListFile({'q': "'"+root_photo_folder+"' in parents and trashed=false"}).GetList():
        logging.info(file1['title'] + ': ' + file1['id'])


def FindGDriveFolderID(gdrive, local_file_path, hash, first):
    # {u'2016-10-28 00': u'0B0o5FIq3lVzcREZmNjk5anhlUzA'}
    drive_folder_name = time.strftime("%Y-%m-%d %H", time.localtime(os.path.getctime(local_file_path)))
    logging.info('search folder for ' + drive_folder_name)
    if drive_folder_name in hash:
        logging.info('gfolder from hash (%s) => (%s)' ,drive_folder_name, hash[drive_folder_name])
        return hash[drive_folder_name],hash
    if(first == 0):
        return '', hash
    logging.info('create new folder for ' + drive_folder_name)
    new_folder_google = gdrive.CreateFile({'name': drive_folder_name, 'title': drive_folder_name, 'mimeType': 'application/vnd.google-apps.folder', "parents": [{"id": root_photo_folder}]})
    new_folder_google.Upload()
    logging.info('create success ' + new_folder_google['id'])
    hash[drive_folder_name] = new_folder_google['id']
    return hash[drive_folder_name],hash


def UploadOneFile(drive, file_title, file_path, hash):
    try:
        logging.info("Start upload: " + file_title)
        local_file_path = os.path.join(file_path, file_title)
        if not os.path.exists(local_file_path):
            logging.info('Not exist: '+local_file_path)
            return hash

        res = FindGDriveFolderID(drive, local_file_path, hash, 1)
        gdive_folder_id = res[0]
        hash = res[1]
        if gdive_folder_id == '':
            logging.info('GFolder not found')
            return hash
        file_google = drive.CreateFile({'title': file_title,"mimeType":"application/vnd.google-apps.photo", "parents":  [{"id": gdive_folder_id}]})
        file_google.SetContentFile(local_file_path)
        file_google.Upload()
        os.remove(local_file_path)
        logging.info('Upload ok %s => %s ' ,file_title, file_google['id'])
        return hash
    except OSError as e:
        logging.info("OSError: " + str(e))
        return hash
    except KeyboardInterrupt:
        logging.info("Interrupt copy" )
        return 0
    except:
        logging.info("Unexpected error: " + str(sys.exc_info()[0]))
        return hash


def FolderHashRead(drive):
    hash = {}
    for file1 in drive.ListFile({'q': "'"+root_photo_folder+"' in parents and trashed=false"}).GetList():
        hash[file1['title']] = file1['id']
    logging.info(hash)
    return hash


def FolderHashWrite(hash):
    f = open('data/hash.txt', 'w')
    for key in hash:
        f.write(key + ':' + hash[key] + '\n')


def Main():
    logFormatter = logging.Formatter("%(asctime)s [%(process)d] %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler("log/grdive-logger.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    gdrive = AuthGDrive()
    hash = FolderHashRead(gdrive)
    OneIteration(gdrive, hash)

def OneIteration(gdrive, hash):
    try:
        path_from = "/home/hikvision/Camera"

        file_list = [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]
        file_list = sorted(file_list)
        size = len(file_list)
        idx=0
        for file_title in file_list:
            idx+=1
            logging.info('')
            logging.info("Files "+str(idx)+"/"+str(size)+" - " + str(idx*100/size)+"%")
            hash = UploadOneFile(gdrive, file_title, path_from, hash)
            if hash==0:
                logging.info("Interupt iteration")
                return 0
        return 1
    except:
        logging.info("Unexpected error: " + str(sys.exc_info()[0]))
        return 0

def ListRootGDrive():
    gdrive = AuthGDrive()
    for file1 in gdrive.ListFile({'q': "'root' in parents and trashed=false"}).GetList():
        print file1['title'] + ': ' + file1['id']

Main()
