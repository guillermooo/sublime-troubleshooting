A package for Sublime Text that helps you troubleshoot issues and generate complete error reports.

---

### For developers

**All**, do this once (adjust as necessary):

```python
PS> python -m venv venv
PS> ./venv/Scripts/activate.ps1
PS> (venv) pip install -r requirements.txt
```

**For OS X or Linux**, symlink *./src* as *Data/Packages/Troubleshooting*, and *./tests* as *Data/Packages/Troubleshootingtests*.

---

**For Windows**, run `pyb_ develop` once to have directory junctions set up automatically for you. Note that for any changes you make to the files, you'll have to restart Sublime Text to have them picked up. The project file includes a build system that will restart the editor for you on Windows.
