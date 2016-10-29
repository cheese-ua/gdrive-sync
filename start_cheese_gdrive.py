import logging
import os
import sys
import time
import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def AuthGDrive():
    gauth = GoogleAuth()
    #gauth.LocalWebserverAuth()
    # 'data/service_acc.json'
    gauth.LoadCredentialsFile('data/google.obj')
    drive = GoogleDrive(gauth)
    return drive


def FolderList(drive):
    for file1 in drive.ListFile({'q': "'0B0o5FIq3lVzcR3ozSjc4cW44VXc' in parents and trashed=false"}).GetList():
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
    new_folder_google = gdrive.CreateFile({'name': drive_folder_name, 'title': drive_folder_name, 'mimeType': 'application/vnd.google-apps.folder', "parents": [{"id": "0B0o5FIq3lVzcR3ozSjc4cW44VXc"}]})
    new_folder_google.Upload()
    logging.info('create success ' + new_folder_google['id'])
    hash = FolderHashRead(gdrive)
    return FindGDriveFolderID(gdrive, local_file_path, hash, 0)


def UploadOneFile(drive, file_title, file_path, hash):
    try:
        logging.info('')
        logging.info("Start upload: " + file_title)
        local_file_path = os.path.join(file_path, file_title)
        res = FindGDriveFolderID(drive, local_file_path, hash, 1)
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
    except OSError:
        logging.info("OSError: "+ OSError.message)
        return hash
    except:
        logging.info("Unexpected error: " + sys.exc_info()[0])
        return hash


def FolderHashRead(drive):
    hash = {}
    for file1 in drive.ListFile({'q': "'0B0o5FIq3lVzcR3ozSjc4cW44VXc' in parents and trashed=false"}).GetList():
        hash[file1['title']] = file1['id']
    logging.info(hash)
    return hash


def FolderHashWrite(hash):
    f = open('data/hash.txt', 'w')
    for key in hash:
        f.write(key + ':' + hash[key] + '\n')


def Main():
    logging.basicConfig(format='%(asctime)s %(message)s', filename='/home/cheese/tmp/cheese-gdrive.log',level=logging.DEBUG)
    drive = AuthGDrive()
    hash = FolderHashRead(drive)
    path_from = "/home/hikvision/Camera"
    for file_title in [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]:
        hash = UploadOneFile(drive, file_title, path_from, hash)


Main()
# hash=FolderHashRead()
