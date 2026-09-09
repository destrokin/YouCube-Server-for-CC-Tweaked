Option Explicit

Dim fso, shell, root, pythonw, gui
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

root = fso.GetParentFolderName(WScript.ScriptFullName)
pythonw = root & "\.venv\Scripts\pythonw.exe"
gui = root & "\YouCubeServerGUI.py"

If fso.FileExists(pythonw) Then
    shell.Run """" & pythonw & """ """ & gui & """", 0, False
Else
    MsgBox "YouCube is not set up yet. Run SETUP_SERVER.bat first.", 48, "YouCube Backend"
End If
