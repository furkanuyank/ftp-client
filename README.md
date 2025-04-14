# Table of Contents

- **[Installation](#installation)**
- **[Login Screen and FTP Server Connection](#login-screen-and-ftp-server-connection)**
- **[Using the Program](#using-the-program)**

<br>

# Installation
The project uses Python’s built-in FTP library, **ftplib**. However, you must install the **PyQt5** library for the interface by running:

<code> pip install pyqt5 </code>

<p> Afterward, run the following command to start the application, and wait for the login screen to appear </p>

<code> python client.py </code>

<br>

# Login Screen and FTP Server Connection

On the login screen, enter the FTP server information as described below and click the **Connect** button. After a short wait, the connection will be established. Clicking the **Quit** button will close the program.

- **Server:** The FTP server’s address or IP
- **Port:** The FTP server’s port (default is 21)
- **Username:** Your FTP username
- **Password:** Your FTP password

## Example Test Server Information

### [ftp.dlptest.com](https://dlptest.com/ftp-test/)
This server allows all operations (read, write, etc.) and deletes all data every 10 minutes.

- **Server:** ftp.dlptest.com
- **Port:** 21
- **Username:** dlpuser
- **Password:** rNrKYTX9g7z3RgJRmxWuGHbeu

### [test.rebex.net](https://test.rebex.net/)
This server is read-only.

- **Server:** test.rebex.net
- **Port:** 21
- **Username:** demo
- **Password:** password

<br>

# Using the Program

The program’s main window has two primary panels:

- **Local Dir (Local Directory):** Lists the files and folders on your local machine.
- **Remote Dir (Remote Directory):** Lists the files and folders on the connected FTP server.

### Uploading and Downloading Files

- To upload a file to the FTP server, drag it from the local panel (left) to the remote panel (right).
- To download a file from the FTP server, drag it from the remote panel (right) to the local panel (left).
- Drag-and-drop within the same panel does not work; drag-and-drop is only for transferring files between the local and remote panels.
- When files are dragged to upload or download, the operation is performed in the directory currently displayed in that panel.

### Navigating Directories

- Items with the **📁** icon at the beginning of their name are folders. You can **double-click** these folders in both the local and remote directories to open them. To go back (when possible), click the **..** item at the top.

### Creating a New Folder

- Click the **(📁 Create Folder)** button on the relevant panel to create a new folder in that directory.

### Refreshing Directories

- Directories are automatically refreshed after each operation. However, if needed, you can manually refresh a directory by clicking the **(🔄 Refresh)** button on the respective panel.

### Deleting and Renaming

- In both panels, **right-click** on a file to see options for **Rename** and **Delete**.
- When you click **Rename**, you will be prompted for a new name, and the file will be renamed.
- When you click **Delete**, the file will be deleted.

### Logging Out

- Click the **(❌ Logout)** button at the top-left corner of the program window to close the FTP connection and return to the login screen.

