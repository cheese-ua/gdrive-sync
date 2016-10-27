import os
import time

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def AuthGDrive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
    return drive

def FolderList(drive):
    file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        print file1['title']+': '+file1['id']

def FindGDriveFolderID(gdrive, local_file_path):
    return "0B0o5FIq3lVzcR3ozSjc4cW44VXc"
    #filedate = time.localtime(os.path.getctime(file_name_full))
    #dirname = os.path.join(path_to, time.strftime("%Y-%m-%d/%H", filedate))
    #file_to =os.path.join(dirname, file_name)
    #return ""


def UploadOneFile(drive, file_title, file_path, hash):
    print "Start upload: "+file_title
    local_file_path = os.path.join(file_path, file_title)
    gdive_folder_id = FindGDriveFolderID(drive, local_file_path)
    file_google = drive.CreateFile({'title': file_title, "parents":  [{"id": gdive_folder_id}]})
    file_google.SetContentFile(local_file_path)
    file_google.Upload()
    print('Upload ok %s => %s ' % (file_title, file_google['id']))

def FolderHashRead():
    f = open('data/hash.txt')
    for line in f.readlines():
        arr = line.rstrip(':')
        hash[arr[0]]=arr[1]
    return hash

def FolderHashWrite(hash):
    f = open('data/hash.txt','w')
    for key in hash:
        f.write(key+':'+hash[key]+'\n')


def Main():
    drive = AuthGDrive()
    hash = FolderHashRead()
    path_from = "/home/cheese/tmp/Cameratest"
    for file_title in [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]:
        UploadOneFile(drive, file_title, path_from, hash)

#Main()
hash=FolderHashRead()
