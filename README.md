A package for Sublime Text
that helps you troubleshoot issues
and generate complete error reports.

---

### For developers

**All**, do this once (adjust as necessary):

```powershell
# Using PowerShell on Windows
PS> python -m venv venv
PS> ./venv/Scripts/activate.ps1
PS> (venv) pip install -r requirements.txt
```

Run `pyb_ develop` once
to have symlinks (Linux, OS X)
or directory junctions (Windows)
set up automatically for you in Data/Packages.

 **On Windows**,
 note that you'll have to restart Sublime Text
 each time you make changes to the linked files.
 Sublime Text won't be able to automatically refresh
 the contents of directories linked via directory junction.
 The project file includes a build system
 that will restart the editor for you on Windows
 (press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> to see all available build systems).
