YOUCUBE BACKEND SERVER - PUBLIC RELEASE
=======================================

This package runs a YouCube backend for CC:Tweaked and includes the custom
video, audio-only, playlist/Mix, and media-cache behavior used by this build.

SUPPORTED HOST
--------------
Windows 10/11 is the intended host for the included setup and GUI scripts.

QUICK SETUP
-----------
1. Extract this ZIP to a normal folder.
   Example:
       C:\YouCubeBackend

2. Install Python 3.11 or 3.12 if you do not already have Python.
   Download:
       https://www.python.org/downloads/

   During the Python installer, enable:
       Add Python to PATH

3. Run:
       SETUP_SERVER.bat

   The setup script will:
   - create a private Python virtual environment;
   - install the required Python packages;
   - attempt to download Sanjuuni;
   - check for FFmpeg and optionally install it with winget.

4. SETUP_SERVER.bat automatically builds:
       YouCubeServer.exe

5. For normal use from now on, simply double-click:
       YouCubeServer.exe

   This opens only the YouCube Backend GUI. No command window is needed.

   START_SERVER.bat remains available only as a fallback.

6. In the YouCube Server GUI:
   - Host should normally stay:
         0.0.0.0
   - Port should normally stay:
         5000
   - confirm FFmpeg and Sanjuuni show valid paths;
   - click:
         Check Setup
   - then click:
         Start Server

6. Your CC:Tweaked computer must point its YouCube client at this server.


NORMAL DAILY USE
----------------
After the one-time setup, you should NOT need to run a BAT file each time.

Simply launch:

    YouCubeServer.exe

The EXE opens the backend hosting GUI directly. When you click Start Server,
the Python/Sanic backend is started in the background without opening another
console window.

LOCAL NETWORK
-------------
If Minecraft and the backend are on the same home network, use the LAN IP
shown in the server GUI.

Example:
    ws://192.168.1.100:5000

The GUI's "Copy CC Command" button copies the normal CC:Tweaked settings
command using the detected LAN address.

INTERNET / REMOTE PLAY
----------------------
If the Minecraft server or CC:Tweaked computer is outside your home network:

1. Forward TCP port 5000 on your router to the Windows PC running this backend.
2. Allow the server/Python through Windows Firewall.
3. Use your public IP or DNS hostname in the CC:Tweaked Lua.

Example:
    ws://your-hostname.example:5000

Do not publish your private LAN address as though it were an Internet address.

PLAYLISTS / YOUTUBE MIXES
-------------------------
Playlist and YouTube Mix resolution is built directly into the main server:

    http://SERVER:5000/playlist?url=...

No separate playlist-helper process or port is required in this release.

A playlist is currently capped at 50 resolved entries per request.

VIDEO MODE
----------
Video mode:
- downloads/normalizes the source with yt-dlp + FFmpeg;
- converts monitor frames with Sanjuuni;
- uses cached render files by video ID and display size;
- validates that converted videos contain multiple frames.

A larger Advanced Monitor requires more converted frame data and more CC
network/render work than a small monitor.

AUDIO-ONLY MODE
---------------
Audio-only mode:
- downloads audio with yt-dlp;
- converts it to mono DFPWM audio for CC:Tweaked speakers;
- supports the direct audio path used by the current custom Lua clients;
- safely handles empty playlist/search results instead of crashing.

MEDIA CACHE
-----------
Converted media is cached under:

    server-src\src\youcube\data

The GUI shows the current cache size.

"Open Cache"
    Opens the cache folder.

"Clear Cache"
    Deletes generated cached media. The next playback must download/convert
    those items again.

Normally, you should leave the cache alone. It is what prevents repeated
conversion of the same media.

PORTS
-----
Default main server:
    TCP 5000

The WebSocket player and /playlist HTTP endpoint both use this same port.

WINDOWS FIREWALL
----------------
The first time Python or YouCubeServer.exe listens for incoming connections,
Windows may ask for firewall permission.

Allow access on the network profile you actually use.

If CC:Tweaked cannot connect:
- confirm the GUI says Running;
- confirm the correct IP/hostname;
- confirm TCP 5000 is allowed;
- confirm router port forwarding when connecting from outside the LAN.

BUILDING THE OPTIONAL EXE
-------------------------
SETUP_SERVER.bat automatically builds the normal GUI executable:

    YouCubeServer.exe

For everyday use, launch that EXE directly.

If the GUI source changes later and you want to rebuild it manually, run:

    BUILD_GUI_EXE.bat

IMPORTANT:
Keep YouCubeServer.exe in the release folder beside:
    server-src\
    tools\

The EXE is a launcher/manager. The backend Python source remains external so
it can be updated without rebuilding the EXE.

UPDATING YT-DLP
---------------
YouTube changes frequently. If extraction suddenly fails, update yt-dlp:

    .venv\Scripts\python.exe -m pip install -U yt-dlp

Then restart the backend.

COMMON ERRORS
-------------
"Requested format is not available"
    Update yt-dlp first. Also confirm FFmpeg is installed.

"FFmpeg missing"
    Install FFmpeg or place ffmpeg.exe in tools\.

"Sanjuuni missing"
    Run SETUP_SERVER.bat again or place sanjuuni.exe in tools\.

"Too many websockets already open"
    This is normally a CC:Tweaked client-side socket lifecycle problem rather
    than a server capacity error. Restart the affected CC computer and make
    sure the client closes old WebSockets before opening new ones.

"No playable media found for this request"
    yt-dlp returned an empty search/playlist result. Check the submitted URL
    and update yt-dlp if a valid YouTube URL unexpectedly fails.

SECURITY
--------
This server has no authentication layer.

If you expose TCP port 5000 directly to the Internet, anyone who can reach
that address may be able to submit media conversion requests.

For a private server, restrict access with your firewall/router or place the
service behind infrastructure you control.

FILES
-----
YouCubeServer.exe
    Normal public launcher. Opens the backend GUI without a command window.
    It is generated automatically by SETUP_SERVER.bat.

START_SERVER.bat
    Fallback launcher. Prefers YouCubeServer.exe when available.

START_SERVER_SILENT.vbs
    Console-free Python fallback if the EXE build is unavailable.

SETUP_SERVER.bat / SETUP_SERVER.ps1
    Installs Python dependencies and checks third-party tools.

BUILD_GUI_EXE.bat
    Optional PyInstaller build for the Windows GUI launcher.

YouCubeServerGUI.py
    Start/stop/status/cache manager.

server-src\src\youcube\
    Backend source.

tools\
    Location for local FFmpeg/Sanjuuni executables.

LICENSE / THIRD-PARTY
---------------------
See THIRD_PARTY.txt.

This package contains modified YouCube-derived backend source. Before public
distribution, make sure you comply with the upstream project's GPL license
requirements, including providing the applicable license text and source.
