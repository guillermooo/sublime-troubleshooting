A package for Sublime Text that helps you troubleshoot issues and generate complete error reports.

---

### For developers

**All**, do this once (adjust as necessary):

```powershell
# Using PowerShell on Windows
PS> python -m venv venv
PS> ./venv/Scripts/activate.ps1
PS> (venv) pip install -r requirements.txt
```

---

**For OS X or Linux**, symlink *./src* as *Data/Packages/Troubleshooting*, and *./tests* as *Data/Packages/Troubleshootingtests*.

---

**For Windows**, run `pyb_ develop` once to have directory junctions set up automatically for you. Note that you'll have to restart Sublime Text each time you make changes to the linked files. Sublime Text won't be able to refresh their contents automatically. The project file includes a build system that will restart the editor for you on Windows (press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>B</kbd> to see all available build systems).
