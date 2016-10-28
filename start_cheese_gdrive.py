import os
import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def AuthGDrive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    # 'data/service_acc.json'
    # gauth.SaveCredentialsFile('data/google.obj')
    drive = GoogleDrive(gauth)
    return drive


def FolderList(drive):
    for file1 in drive.ListFile({'q': "'0B0o5FIq3lVzcR3ozSjc4cW44VXc' in parents and trashed=false"}).GetList():
        print file1['title'] + ': ' + file1['id']


def FindGDriveFolderID(gdrive, local_file_path, hash, first):
    # {u'2016-10-28 00': u'0B0o5FIq3lVzcREZmNjk5anhlUzA'}
    drive_folder_name = time.strftime("%Y-%m-%d %H", time.localtime(os.path.getctime(local_file_path)))
    print 'search folder for ' + drive_folder_name
    if drive_folder_name in hash:
        print 'gfolder from hash (%s) => (%s)' % (drive_folder_name, hash[drive_folder_name])
        return hash[drive_folder_name],hash
    if(first == 0):
        return '', hash
    print 'create new folder for ' + drive_folder_name
    new_folder_google = gdrive.CreateFile({'name': drive_folder_name, 'title': drive_folder_name, 'mimeType': 'application/vnd.google-apps.folder', "parents": [{"id": "0B0o5FIq3lVzcR3ozSjc4cW44VXc"}]})
    new_folder_google.Upload()
    print 'create success ' + new_folder_google['id']
    hash = FolderHashRead(gdrive)
    return FindGDriveFolderID(gdrive, local_file_path, hash, 0)


def UploadOneFile(drive, file_title, file_path, hash):
    print "Start upload: " + file_title
    local_file_path = os.path.join(file_path, file_title)
    res = FindGDriveFolderID(drive, local_file_path, hash, 1)
    gdive_folder_id = res[0]
    hash = res[1]
    if(gdive_folder_id == ''):
        print 'GFolder not found'
        return hash
    file_google = drive.CreateFile({'title': file_title, "parents":  [{"id": gdive_folder_id}]})
    file_google.SetContentFile(local_file_path)
    file_google.Upload()
    print('Upload ok %s => %s ' % (file_title, file_google['id']))
    return hash


def FolderHashRead(drive):
    hash = {}
    for file1 in drive.ListFile({'q': "'0B0o5FIq3lVzcR3ozSjc4cW44VXc' in parents and trashed=false"}).GetList():
        hash[file1['title']] = file1['id']
    print hash
    return hash


def FolderHashWrite(hash):
    f = open('data/hash.txt', 'w')
    for key in hash:
        f.write(key + ':' + hash[key] + '\n')


def Main():
    drive = AuthGDrive()
    hash = FolderHashRead(drive)
    path_from = "/home/cheese/tmp/Cameratest"
    for file_title in [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]:
        hash = UploadOneFile(drive, file_title, path_from, hash)


Main()
# hash=FolderHashRead()
