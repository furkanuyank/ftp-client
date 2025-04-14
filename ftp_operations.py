import shutil
from ftplib import FTP
import os

class FTPClient:
    def __init__(self):
        self.ftp = FTP

    def connect(self, host, port, username, password):
        self.ftp.connect(host, port)
        self.ftp.login(username, password)
        self.ftp.cwd(self.remote_current_path)

    def disconnect(self):
        try:
            self.ftp.quit()
        except:
            self.ftp.close()

    def refresh_local_list(self):
        self.localList.clear()
        self.localList.addItem("..")
        entries = os.listdir(self.local_current_path)
        for e in entries:
            full_path = os.path.join(self.local_current_path, e)
            if os.path.isdir(full_path):
                self.localList.addItem("📁 " + e)
            else:
                self.localList.addItem(e)

        self.local_path_label.setText(f"Local Dir: {self.local_current_path}")

    def refresh_remote_list(self):
        self.remoteList.clear()
        current_dir = self.ftp.pwd()
        if current_dir != "/":
            self.remoteList.addItem("..")

        try:
            for name, facts in self.ftp.mlsd():
                if name in ('.', '..'):
                    continue

                if facts['type'] == 'dir':
                    self.remoteList.addItem(f"📁 {name}")
                else:
                    self.remoteList.addItem(name)

        #LIST command
        except Exception:
            lines = []
            self.ftp.retrlines('LIST', lines.append)

            for line in lines:
                parts = line.split()
                if not parts:
                    continue
                if len(parts) < 6:
                    continue
                is_dir = parts[0].startswith('d')
                name = ' '.join(parts[8:])

                if is_dir:
                    self.remoteList.addItem(f"📁 {name}")
                else:
                    self.remoteList.addItem(name)

        self.remote_path_label.setText(f"Remote Dir: {current_dir}")

    def upload(self, local_path, filename):
        try:
            self.ftp.cwd(self.remote_current_path)
            with open(local_path, "rb") as f:
                self.ftp.storbinary(f"STOR {filename}", f)
        except:
            raise

    def download(self, local_path, file_name):
        try:
            self.ftp.cwd(self.remote_current_path)
            with open(local_path, "wb") as f:
                self.ftp.retrbinary(f"RETR {file_name}", f.write)
        except:
            raise

    def delete(self, item, is_local):
        try:
            text = item.text()
            if text == "..":
                return

            is_dir = text.startswith("📁 ")
            name = text.replace("📁 ", "") if is_dir else text
            full_path = os.path.join(self.local_current_path, name)

            if is_local:
                if is_dir:
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
            else:
                if is_dir:
                    self.ftp.rmd(name)
                else:
                    self.ftp.delete(name)
        except:
            raise

    def rename(self, old_name, new_name, is_local):
        try:
            if is_local:
                old_path = os.path.join(self.local_current_path, old_name)
                new_path = os.path.join(self.local_current_path, new_name)
                os.rename(old_path, new_path)
            else:
                self.ftp.rename(old_name, new_name)

        except:
            raise

    def create_directory(self, dir_name, is_local):
        try:
            if is_local:
                full_path = os.path.join(self.local_current_path, dir_name)
                os.mkdir(full_path)
            else:
                self.ftp.mkd(dir_name)
        except:
            raise