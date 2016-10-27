import os
import time

path_from = "/home/hikvision/Camera"
path_to = "/home/cheese/camera.dp.ua@gmail.com/Camera"

time.tzset()
for file in [f for f in os.listdir(path_from) if os.path.isfile(os.path.join(path_from, f)) and f.endswith('.jpg')]:
    file_from = os.path.join(path_from, file)
    filedate = time.localtime(os.path.getctime(file_from))
    dirname = os.path.join(path_to, time.strftime("%Y-%m-%d/%H", filedate))
    print dirname
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    file_to =os.path.join(dirname, file)
    os.rename(file_from, file_to)
