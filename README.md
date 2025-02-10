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


# Current Server configuration (adress might change in the future)
URL: feasible-robin-vaguely.ngrok-free.app 

Port: 8004

## ngrok setup

### Start online server [temporary adress] (Currently test_ngrok_connection.py does not work with this)
`ngrok http http://localhost:8004`

### Start online server [static adress]
`ngrok http --url=feasible-robin-vaguely.ngrok-free.app 8004`

The adress can be found under Static Domain on
https://dashboard.ngrok.com/get-started/setup/linux

####
The static server adress is 
feasible-robin-vaguely.ngrok-free.app

### Error/sucess codes in a web-browser: 
- ERR_NGROK_3200: If the ngrok server is not on
- ERR_NGROK_8012: Our server is not on
- If both are on it should say something else.
    - It should say in JSON: `message	"CI Server is running!"`

### How to run server
While in folder GROUP4_2 run:

`python -m src.server`
