# Group4_2





#  Setting Up Virtual Environment (Mac/Linux)

## Running the Setup Script
First, navigate to the `scripts/` folder and run:
```bash
cd scripts
chmod +x setup.sh  # (Only needed once)
./setup.sh
```

It will create the virtual environment and install all dependencies from requirements.txt.

After running the script, activate the virtual environment:
```bash
source venv/bin/activate
```

#  Setting Up Virtual Environment (Windows)

## Running the Setup Script
First, navigate to the `scripts/` folder and run:
```powershell
cd scripts
.\setup.ps1
```
If you get a permission error, allow script execution by running:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then, rerun:
```powershell
.\setup.ps1
```
After running the script, activate the virtual environment:
```powershell
venv\Scripts\Activate
```

## Notes 
The venv/ folder is created inside the repository but ignored by GitHub.

If you create a new branch, develop a feature, push changes, and delete the branch, the venv/ folder will not be removed.

The venv/ folder only exists locally for you and does not get uploaded to GitHub.

Every time before you start coding, activate venv