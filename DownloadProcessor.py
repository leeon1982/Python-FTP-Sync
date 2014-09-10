#!/Library/Frameworks/Python.framework/Versions/3.4/bin python3

import json
import shutil
import os

from ftpSync import FileSyncer
from Base import Base

class DownloadProcessor(Base):
    timeOut = 60 * 60
    download_queue = ""
    ftp_sync = None

    def __init__(self, localDownloadQueue):
        Base.__init__(self)
        self.download_queue = localDownloadQueue
        self.ftp_sync = FileSyncer(os.environ["FtpSyncServer"], os.environ["FtpSyncUser"], os.environ["FtpSyncPassword"], os.environ["FtpSyncPort"], os.environ["FtpSyncRemoteDirectory"], os.environ["FtpSyncLocalDirectory"])
        self.move_file_into_processing()

    def move_file_into_processing(self):
        if not os.path.isdir("ProcessingFiles"):
            os.mkdir("ProcessingFiles")

        processing_files = [f for f in os.listdir("ProcessingFiles") if f.endswith(".txt")]
        files_to_process = [f for f in os.listdir(self.download_queue) if f.endswith(".txt")]

        for single_file in processing_files:
            try:
                self.process_download_file(single_file)
            except Exception as e:
                print("Error - Unable to process: " + single_file + " " + str(e))
            finally:
                os.remove("ProcessingFiles" + self.directory_separator + single_file)

        for single_file in files_to_process:
            try:
                shutil.move("PendingDownloadQueue" + self.directory_separator + single_file, "ProcessingFiles")
                self.process_download_file(single_file)
            except OSError as e:
                print("Error - Unable to move: " + single_file + " into queue.  " + str(e))
                self.move_file_into_failed(single_file)
            finally:
                os.remove("ProcessingFiles" + self.directory_separator + single_file)



    def move_file_into_failed(self, failed_file):
        if not os.path.isdir("FailedFiles"):
            os.mkdir("FailedFiles")
        try:
            shutil.move("PendingDownloadQueue" + self.directory_separator + failed_file, "FailedFiles")
        except OSError as e:
            print("Error moving: " + failed_file + " into failed folder.")

    def map_download_directories(self, parent_directory, mapped_directory_data=""):
        if not os.path.isdir(os.environ["FtpSyncLocalDirectory"] + self.directory_separator + parent_directory):
            try:
                os.mkdir(os.environ["FtpSyncLocalDirectory"] + self.directory_separator + parent_directory)
            except OSError as e:
                print("Unable to create directory: " + os.mkdir(os.environ["FtpSyncLocalDirectory"] +
                        self.directory_separator + parent_directory) + " " + str(e))

    def process_download_file(self, file_to_process):
        with open("ProcessingFiles" + self.directory_separator + file_to_process, "r") as download_file:
            try:
                download_data = json.loads(download_file.read())
                for f in sorted(download_data["Files"]):
                    self.map_download_directories(f.replace(os.environ["FtpSyncRemoteDirectory"] + "/", ""))
                    # print(download_data["Files"][f])
            except Exception as e:
                print("Error - Unable to download file: " + str(download_file) + ", " + str(e))
                # for fi in download_data[f]:
                #     #we need to create all the random directories
                #     if fi == "Directories":
                #

                        #self.map_download_directories(f.replace(str(),  ""), fi)
                    #we need to download all the random files into the appropriate directories

                # objFtp.sendcmd("TYPE i")
                # logger("Status - Downloading file: " + fileToDownload + " " + str(objFtp.size(fileToDownload) / 1024 / 1024) + "MB\n")
                # file = open(fileToDownload, 'wb')
                # objFtp.retrbinary('RETR '+ fileToDownload, file.write)
                # file.close()
                # logger("Status - Download successful: " + fileToDownload)
                # self.moveFile(fileToDownload, destinationFolder)

processor = DownloadProcessor("/Users/jwisdom/Dev/Workspace/GitRepos/Python-FTP-Sync/PendingDownloadQueue")
