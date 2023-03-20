import sqlite3


def progress(status, remaining, total):
    print(f'Copied {total - remaining} of {total} pages')


current_db_path = '/Users/williamhbelew/Hacking/MSWN/instance/mswnapp.sqlite'
backup_db_path = '/Users/williamhbelew/Hacking/MSWN/instance/mswnapp_backup.sqlite'

try:
    # existing DB
    sqliteCon = sqlite3.connect(current_db_path)
    # backup DB connection/creation
    backUpCon = sqlite3.connect(backup_db_path)
    with backUpCon:
        sqliteCon.backup(backUpCon, pages=3, progress=progress)
    print("backup successful!")
except sqlite3.Error as error:
    print("Error while taking the backup: ", error)
finally:
    if backUpCon:
        backUpCon.close()
        sqliteCon.close()
