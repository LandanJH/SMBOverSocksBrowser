# SMB SOCKS Proxy Browser & Scanner

## Overview

This application is a graphical utility built with Python and PySide6 that provides a secure and flexible way to browse and scan for SMB (Windows file sharing) shares, with all traffic routed through a SOCKS proxy. It is designed to be a robust tool for network administrators and security professionals who need to interact with SMB services from a protected or remote network segment.

The application is split into two main functional tabs: a **Share Browser** for deep interaction with a known share, and a **Subnet Scanner** for discovering available shares across a network range.

---

## Features

### Core Features
- **Tabbed Interface:** A clean, organized UI with separate tabs for browsing and scanning.
- **SOCKS Proxy Integration:** All network traffic can be routed through a configurable SOCKS proxy, ensuring that the connection to the target network originates from the proxy server, not the local machine.
- **Direct Connection:** Users can choose to bypass the proxy for direct local network scanning and browsing.
- **External Configuration:** Proxy profiles are not hardcoded. They are loaded from an easy-to-edit `config.json` file, which is automatically created with defaults on first launch.

---

### Share Browser Tab
The Share Browser allows you to connect to and interact with a specific, known SMB share.

![Browser tab with example data](https://github.com/LandanJH/SMBOverSocksBrowser/blob/main/images/Browser.png?raw=true)

- **Direct Connection:** Connect to any SMB host by providing its IP address, the share name, and credentials.
- **File System Navigation:** Double-click on directories to navigate the share's folder structure. A `..` entry is provided to navigate back up.
- **Multi-File Preview:**
  - **Office Documents:** `.docx`, `.doc`, `.xlsx`, and `.xls` files are automatically converted in the background and rendered as PDFs for preview (requires LibreOffice to be installed).
  - **PDFs:** Rendered natively within the application.
  - **Images:** `.png`, `.jpg`, `.gif`, and `.bmp` files are displayed directly.
  - **Text Files:** All other files are treated as text and their content is displayed.
- **Non-Blocking Previews:** Previews for large Office documents are handled in a background thread, preventing the main application from freezing.
- **File Download:** Select any file and download it to your local machine.
- **Cached File Search:**
  - **Initial Search:** The first time you use the search bar on a share, the application performs a one-time, full recursive scan of all files and folders to build an in-memory index. This may take a moment on very large shares.
  - **Subsequent Searches:** All future searches on that same share are performed against the in-memory cache, providing instantaneous results without any further network traffic.
  - The cache is automatically cleared when you disconnect or close the application.

---

### Subnet Scanner Tab
The Subnet Scanner discovers active SMB hosts and their available shares across a given network range (in CIDR format, e.g., `192.168.1.0/24`).

![Scanner tab with example data](https://github.com/LandanJH/SMBOverSocksBrowser/blob/main/images/Scanner.png?raw=true)

- **Fully Asynchronous & Non-Blocking:** The entire scanning operation is launched as a **separate process**. This guarantees the main user interface will **never freeze or become unresponsive**, even when scanning very large subnets.
- **Two-Stage Scanning:**
  1.  **Port Scan:** First, it performs a rapid, multi-threaded port scan to identify only the hosts that have port 445 open.
  2.  **Enumeration:** It then performs a more detailed SMB enumeration only on the hosts that were found to be alive, saving significant time.
- **Quick Scan vs. Deep Scan:**
  - **Quick Scan (Default):** Gets the list of available shares from hosts very quickly. It does not verify permissions, which is faster and more reliable.
  - **Deep Scan (Checkbox unchecked):** After finding shares, it attempts to check for `READ` and `WRITE` permissions. This is slower and the results may vary depending on the server's configuration and the credentials used.
- **"Open in Browser" Functionality:** Right-click or select any discovered share and click "Open in Browser" to automatically populate the connection details in the Share Browser tab for immediate access.

---

## Setup & Usage

### 1. Requirements
This application is built with Python 3. You will need to install the following libraries using pip:
```bash
pip install PySide6 pysmb PySocks PyMuPDF python-docx openpyxl
```
For full Office document preview functionality, you must have LibreOffice installed and accessible in your system's PATH.
2. File Structure

The application requires two files to be in the same directory:
```
    SMBOverSocksBrowser.py (The main application script provided)

    scanner_process.py (The dedicated scanner script provided)
```
3. Configuration

The first time you run the main application, a config.json file will be automatically created in the same directory. This file contains the proxy profiles.

Example config.json:
```json
{
    "example1": 1337,
    "example2": 1338,
    "example3": 1339
}
```
You can edit this file to add, remove, or modify proxy profiles. The "key" (e.g., "example1") is the name that appears in the dropdown menu, and the "value" (e.g., 1337) is the port number. The application assumes the proxy host is 127.0.0.1.

4. Running the Application

To run the application, simply execute the main script:
```bash
python3 SMBOverSocksBrowser.py
```

5. Using the tool
**Scanning for shares**
![Scanner tab with example data](https://github.com/LandanJH/SMBOverSocksBrowser/blob/main/images/Scanning4Shares.png?raw=true)

In the browser tab select the proxy that you want to use, next fill out all the fields with the information you are trying to use. For a quick scan that doesn't look for the permissions of the shares you can toggle the 'Quick Scan' checkbox, for a more detailed scan that provides with the permission of the shares you will need to uncheck that box. As you can see from the screenshot above we can select a share and hit the 'Open in Browser' button to auto fill all the required information to connect to that share in the Browser tab

**Browsing shares**
![Scanner tab with example data](https://github.com/LandanJH/SMBOverSocksBrowser/blob/main/images/BrowsingShares.png?raw=true)

Once you hit the connect button you can use this tool to look through all the files and directories in the share either through the local net or through the specified socks proxy. Here you can download the files on to your local host or just preview the contents of the file if you would like to (as shown below). You can also use the search feature to recursively search for files with the specified keyword in the file name. Using the search feature will cache the file names for more responsive searching after the 1st initial search, then the application will clear the cache once you either disconnect or close the application

![Scanner tab with example data](https://github.com/LandanJH/SMBOverSocksBrowser/blob/main/images/PreviewDocuments.png?raw=true)

## Other Information

Compatibility

So far this tool has only been tested using Ubuntu 24.04, the tool works great in that environment but there seems to be weird issues on other OSs

**Works**
- Ubunbtu 24.04
- Kali

**Issues**
- MacOS 14.6.1

**Not Tested**
- everything else...

Possible Future Updates
- Better Compatibility with other OSs.
- "Reporting" ability, essentially compile files that you would like to keep track of. In the case of an penetration test, you may want to save the paths of a file so that you can put it in a report for a client.
- Windows Binary. I've never done this but it is supposidly possible using Nuitka. Ill see if I can get this to work...

## Remember that this tool is still in development, there ARE issues and hopefully ill keep track of them as I personally intend to use this for my own purposes. So please be patient as I am very new to this idea of creating tools like this.
