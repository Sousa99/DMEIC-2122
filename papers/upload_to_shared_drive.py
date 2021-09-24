import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = './credentials/google_api_secret.json'

# ==================================== PARAMETERS ====================================
DRIVE_FOLDER = '1CUmXm65yHfqrMogHHsq5yL4UiTmNkVZW'

UPLOAD_DIRECTORIES = ['./pdf', './stats']
BLACKLIST_FILES = ['Template.pdf']
# ==================================== ========== ====================================

# ==================================== AUX FUNCTIONS ====================================

def upload_file(drive, file_path, file_name):
    gfile = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': DRIVE_FOLDER}]
    })

    gfile.SetContentFile(file_path)
    gfile.Upload(param={'supportsTeamDrives': True})

def delete_current_files(drive):
    file_list = drive.ListFile({
        'q': "'{0}' in parents and trashed=false".format(DRIVE_FOLDER),
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }).GetList()

    for file in file_list:
        file.Trash(param={'supportsTeamDrives': True})
        print("🗑️  {0}".format(file['title']))

# ==================================== === ========= ====================================

gauth = GoogleAuth()
drive = GoogleDrive(gauth)

print()
delete_current_files(drive)
print()

for directory_path in UPLOAD_DIRECTORIES:
    directory = os.fsencode(directory_path)
    for file in os.listdir(directory):

        filename = os.fsdecode(file)
        if filename in BLACKLIST_FILES: continue

        # Auxiliary variables
        extension = filename.split('.')[-1]
        filename_without_extension = filename.replace('.' + extension, '')
        filename_with_path = directory_path + '/' + filename

        upload_file(drive, filename_with_path, filename_without_extension)
        print("💾 {0}".format(filename_with_path))