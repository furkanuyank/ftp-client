import sys
import os
from ftplib import FTP, error_perm
from ftp_operations import FTPClient
from PyQt5.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QAbstractItemView, QMessageBox, QLabel, QMenu, QAction, QLineEdit, QInputDialog, QPushButton,
    QFormLayout, QDialog, QProgressDialog
)
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FTP Login")
        self.resize(400, 200)
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.server_input = QLineEdit("")
        self.port_input = QLineEdit("")
        self.username_input = QLineEdit("")
        self.password_input = QLineEdit("")
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout.addRow("Server:", self.server_input)
        form_layout.addRow("Port:", self.port_input)
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("Password:", self.password_input)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("Connect")
        self.quit_button = QPushButton("Quit")
        self.connect_button.clicked.connect(self.on_connect)
        self.quit_button.clicked.connect(self.reject)
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.quit_button)
        layout.addLayout(button_layout)

    def on_connect(self):
        self.progress_dialog = QProgressDialog("Connecting to FTP server...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowTitle("Connecting")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.accept()

    def get_credentials(self):
        default_port = 21
        port_text = self.port_input.text()
        try:
            port = int(port_text) if port_text else default_port
        except ValueError:
            port = default_port

        return {
            "server": self.server_input.text(),
            "port": port,
            "username": self.username_input.text(),
            "password": self.password_input.text()
        }

class DraggableListWidget(QListWidget):
    double_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item):
        text = item.text()
        self.double_clicked.emit(text)

    def mimeData(self, items):
        mime_data = QMimeData()
        texts = [item.text() for item in items]
        combined_text = "\n".join(texts)
        mime_data.setText(combined_text)
        return mime_data

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source_widget = event.source()
        mime_data = event.mimeData()
        main_window = self.window()

        if mime_data.hasUrls():
            for url in mime_data.urls():
                file_path = url.toLocalFile()
                if self.objectName() == "remotePanel":
                    main_window.upload_external_file(file_path)
                elif self.objectName() == "localPanel":
                    return

            event.acceptProposedAction()
            return

        if mime_data.hasText():
            dropped_text = mime_data.text().strip()
            if self.objectName() == "localPanel" and source_widget.objectName() == "remotePanel":
                main_window.download_file(dropped_text)

            elif self.objectName() == "remotePanel" and source_widget.objectName() == "localPanel":
                main_window.upload_file(dropped_text)

        event.acceptProposedAction()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTP Program")
        self.resize(1000, 600)
        self.local_current_path = os.getcwd()
        self.remote_current_path = "/"
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        top_bar = QHBoxLayout()
        self.btn_logout = QPushButton("❌ Logout")
        self.btn_logout.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.btn_logout.clicked.connect(self.logout)
        top_bar.addWidget(self.btn_logout)
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        panels_layout = QHBoxLayout()
        main_layout.addLayout(panels_layout)

        # Local
        left_panel = QVBoxLayout()
        self.local_path_label = QLabel("Local Dir:")
        self.localList = DraggableListWidget()
        self.localList.setObjectName("localPanel")
        local_header = QHBoxLayout()
        self.local_path_label = QLabel("Local Dir:")
        self.btn_new_local_folder = QPushButton("📁  Create Folder")
        self.btn_refresh_local = QPushButton("🔄 Refresh")
        self.btn_new_local_folder.clicked.connect(self.create_local_directory)
        local_header.addWidget(self.local_path_label)
        local_header.addWidget(self.btn_new_local_folder)
        local_header.addWidget(self.btn_refresh_local)
        left_panel.addLayout(local_header)
        left_panel.addWidget(self.localList)
        panels_layout.addLayout(left_panel)
        left_panel.addWidget(self.local_path_label)
        left_panel.addWidget(self.localList)
        panels_layout.addLayout(left_panel)
        self.localList.double_clicked.connect(self.on_local_item_double_clicked)
        self.btn_refresh_local.clicked.connect(lambda: FTPClient.refresh_local_list(self))

        # Server
        right_panel = QVBoxLayout()
        self.remote_path_label = QLabel("Remote Dir:")
        self.remoteList = DraggableListWidget()
        self.remoteList.setObjectName("remotePanel")
        remote_header = QHBoxLayout()
        self.remote_path_label = QLabel("Remote Dir:")
        self.btn_new_remote_folder = QPushButton("📁  Create Folder")
        self.btn_refresh_remote = QPushButton("🔄 Refresh")
        self.btn_new_remote_folder.clicked.connect(self.create_remote_directory)
        remote_header.addWidget(self.remote_path_label)
        remote_header.addWidget(self.btn_new_remote_folder)
        remote_header.addWidget(self.btn_refresh_remote)
        right_panel.addLayout(remote_header)
        right_panel.addWidget(self.remoteList)
        panels_layout.addLayout(right_panel)
        right_panel.addWidget(self.remote_path_label)
        right_panel.addWidget(self.remoteList)
        panels_layout.addLayout(right_panel)
        self.remoteList.double_clicked.connect(self.on_remote_item_double_clicked)
        self.btn_refresh_remote.clicked.connect(lambda: FTPClient.refresh_remote_list(self))

        # Menu
        self.localList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.localList.customContextMenuRequested.connect(self.show_local_context_menu)
        self.remoteList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.remoteList.customContextMenuRequested.connect(self.show_remote_context_menu)

        # Connection
        self.ftp = FTP()
        self.login_credentials = {}

    def logout(self):
        reply = QMessageBox.question(
            self,
            'Logout Confirmation',
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                if self.ftp and self.ftp.sock:
                    FTPClient.disconnect(self)
            except:
                pass
            self.hide()

            new_window, success = show_login_and_connect(self)
            if success:
                self.close()
            else:
                self.close()
                QApplication.quit()

    def show_local_context_menu(self, pos):
        item = self.localList.itemAt(pos)
        if item:
            menu = QMenu()
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_local_item(item))

            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.rename_local_item(item))

            menu.addAction(rename_action)
            menu.addAction(delete_action)
            menu.exec_(self.localList.mapToGlobal(pos))

    def show_remote_context_menu(self, pos):
        item = self.remoteList.itemAt(pos)
        if item:
            menu = QMenu()
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_remote_item(item))

            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self.rename_remote_item(item))

            menu.addAction(rename_action)
            menu.addAction(delete_action)
            menu.exec_(self.remoteList.mapToGlobal(pos))

    def on_local_item_double_clicked(self, text):
        if text == "..":
            try:
                parent = os.path.dirname(self.local_current_path)
                if parent and parent != self.local_current_path:
                    self.local_current_path = parent
                    FTPClient.refresh_local_list(self)
            except Exception as ex:
                QMessageBox.warning(self, "Error", f"Could not move to the parent directory.: {ex}")
                return

        if text.startswith("📁 "):
            folder_name = text.replace("📁 ", "")
            new_path = os.path.join(self.local_current_path, folder_name)
            try:
                if os.path.isdir(new_path):
                    self.local_current_path = new_path
                    FTPClient.refresh_local_list(self)
                else:
                    pass
            except Exception as ex:
                QMessageBox.warning(self, "Error", f"Error: {ex}")

    def on_remote_item_double_clicked(self, text):
        if text == "..":
            try:
                self.ftp.cwd("..")
                self.remote_current_path = self.ftp.pwd()
                FTPClient.refresh_remote_list(self)
            except Exception as ex:
                QMessageBox.warning(self, "Error", f"Could not move to the parent directory.: {ex}")
            return

        if text.startswith("📁 "):
            folder_name = text.replace("📁 ", "")
            try:
                self.ftp.cwd(folder_name)
                self.remote_current_path = self.ftp.pwd()
                FTPClient.refresh_remote_list(self)
            except Exception as ex:
                QMessageBox.warning(self, "Error", f"Error: {ex}")

    def connect_ftp(self, server, port, username, password):
        try:
            self.login_credentials = {
                "server": server,
                "port": port,
                "username": username,
                "password": password
            }

            FTPClient.connect(self, server, port, username, password)
            FTPClient.refresh_remote_list(self)
            FTPClient.refresh_local_list(self)
            return True

        except error_perm as e:
            QMessageBox.critical(self, "Error", "Credentials could be wrong. Try again.")
            return False

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect to FTP Server: {e}")
            return False

    def upload_file(self, filename):
        clean_name = filename.replace("📁 ", "") if filename.startswith("📁 ") else filename
        local_path = os.path.join(self.local_current_path, clean_name)
        if not os.path.exists(local_path):
            QMessageBox.warning(self, "Error", f"File not found.")
            return

        try:
            FTPClient.upload(self, local_path, clean_name)
            FTPClient.refresh_remote_list(self)
            QMessageBox.information(self, "Successful", f"{clean_name} has been uploaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed.:\n{e}")

    def upload_external_file(self, file_path):
        filename = os.path.basename(file_path)
        try:
            FTPClient.upload(self, file_path, filename)
            FTPClient.refresh_remote_list(self)
            QMessageBox.information(self, "Successful", "File has been uploaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed.:\n{e}")

    def download_file(self, filename):
        local_path = os.path.join(self.local_current_path, filename)
        try:
            FTPClient.download(self, local_path, filename)
            FTPClient.refresh_local_list(self)
            QMessageBox.information(self, "Successful", "File has been downloaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed:\n{e}")

    def delete_local_item(self, item):
        try:
            FTPClient.delete(self, item, True)
            FTPClient.refresh_local_list(self)
            QMessageBox.information(self, "Successful", f"Item has been deleted successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete: {str(e)}")

    def delete_remote_item(self, item):
        try:
            FTPClient.delete(self, item, False)
            FTPClient.refresh_remote_list(self)
            QMessageBox.information(self, "Successful", f"Item has been deleted successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not delete: {str(e)}")

    def rename_local_item(self, item):
        old_text = item.text()
        if old_text == "..":
            return
        is_dir = old_text.startswith("📁 ")
        old_name = old_text.replace("📁 ", "") if is_dir else old_text

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Local Item",
            "New name:",
            QLineEdit.Normal,
            old_name
        )

        if ok and new_name:
            try:
                FTPClient.rename(self, old_name, new_name, True)
                FTPClient.refresh_local_list(self)
                QMessageBox.information(self, "Successful", f"Item has been renamed successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename:\n{str(e)}")

    def rename_remote_item(self, item):
        old_text = item.text()
        if old_text == "..":
            return
        is_dir = old_text.startswith("📁 ")
        old_name = old_text.replace("📁 ", "") if is_dir else old_text

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Remote Item",
            "New name:",
            QLineEdit.Normal,
            old_name
        )

        if ok and new_name:
            try:
                FTPClient.rename(self, old_name, new_name, False)
                FTPClient.refresh_remote_list(self)
                QMessageBox.information(self, "Successful", f"Item has been renamed successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename:\n{str(e)}")

    def create_local_directory(self):
        dir_name, ok = QInputDialog.getText(
            self,
            "Create Local Directory",
            "Directory name:",
            QLineEdit.Normal
        )

        if ok and dir_name:
            try:
                FTPClient.create_directory(self, dir_name, True)
                FTPClient.refresh_local_list(self)
                QMessageBox.information(self, "Successful", f"Directory has been created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Directory creation failed:\n{str(e)}")

    def create_remote_directory(self):
        dir_name, ok = QInputDialog.getText(
            self,
            "Create Remote Directory",
            "Directory name:",
            QLineEdit.Normal
        )

        if ok and dir_name:
            try:
                FTPClient.create_directory(self, dir_name, False)
                FTPClient.refresh_remote_list(self)
                QMessageBox.information(self, "Successful", f"Directory has been created successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Directory creation failed:\n{str(e)}")

def show_login_and_connect(parent=None):
    login_dialog = LoginWindow(parent)
    if login_dialog.exec_() == QDialog.Accepted:
        credentials = login_dialog.get_credentials()

        progress_dialog = login_dialog.progress_dialog
        progress_dialog.setValue(30)
        main_window = MainWindow()
        progress_dialog.setValue(60)
        progress_dialog.setLabelText("Connecting to FTP server... Please wait")
        connect_result = main_window.connect_ftp(
            credentials["server"],
            credentials["port"],
            credentials["username"],
            credentials["password"]
        )
        progress_dialog.setValue(100)
        progress_dialog.close()

        if connect_result:
            main_window.show()
            return main_window, True
        else:
            return None, False
    else:
        return None, False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window, success = show_login_and_connect()
    if success:
        sys.exit(app.exec_())
    else:
        sys.exit()