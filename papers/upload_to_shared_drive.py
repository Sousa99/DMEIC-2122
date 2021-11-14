import os
import time
import pytz
import datetime
import dateutil.parser
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = './credentials/google_api_secret.json'

# ==================================== PARAMETERS ====================================
DRIVE_FOLDER = '1CUmXm65yHfqrMogHHsq5yL4UiTmNkVZW'

UPLOAD_DIRECTORIES = ['./pdf', './stats']
BLACKLIST_FILES = []
# ==================================== ========== ====================================

# ==================================== OBJECT ====================================

class FileInfo:
    title: str
    createdDate: datetime.datetime
    fileRef: any

    def __init__(self, file):
        self.title = file['title']
        self.createdDate = convertDriveDate(file.get('createdDate'))
        self.fileRef = file

def convertDriveDate(drive_date_string):

    convertDate = dateutil.parser.isoparse(drive_date_string);
    convertDate = convertDate + datetime.timedelta(hours = 0);
    return convertDate

# ==================================== ====== ====================================


# ==================================== AUX FUNCTIONS ====================================

def upload_file(drive, file_path, file_name):
    gfile = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': DRIVE_FOLDER}]
    })

    gfile.SetContentFile(file_path)
    gfile.Upload(param={'supportsTeamDrives': True})
    print("💾 {0}".format(file_name))

def get_files(drive):
    file_list = drive.ListFile({
        'q': "'{0}' in parents and trashed=false".format(DRIVE_FOLDER),
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }).GetList()

    file_infos = []
    for file in file_list: 
        file_info = FileInfo(file)
        file_infos.append(file_info)

    return file_infos

def delete_file(file):
    file.Trash(param={'supportsTeamDrives': True})
    print("🗑️  {0}".format(file['title']))


def update_file(drive, files_info, file_path, filename, modified_date):

    updated = False
    for file_info in files_info:
        if (file_info.title == filename and file_info.createdDate >= modified_date):
            updated = True
        elif (file_info.title == filename):
            delete_file(file_info.fileRef)

    if (not updated):
        upload_file(drive, file_path, filename)
        print()


# ==================================== === ========= ====================================

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

file_infos = get_files(drive)
current_files = []

for directory_path in UPLOAD_DIRECTORIES:
    directory = os.fsencode(directory_path)
    for file in os.listdir(directory):

        filename = os.fsdecode(file)
        if filename in BLACKLIST_FILES: continue

        modified_time_untreated = os.path.getmtime(os.path.join(directory, file))
        modified_time = datetime.datetime.strptime(time.ctime(modified_time_untreated), "%a %b %d %H:%M:%S %Y")
        modified_time = modified_time.replace(tzinfo=pytz.UTC)

        # Auxiliary variables
        extension = filename.split('.')[-1]
        filename_without_extension = filename.replace('.' + extension, '')
        filename_with_path = directory_path + '/' + filename

        update_file(drive, file_infos, filename_with_path, filename, modified_time)