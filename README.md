# Continuous Integration (CI) Server

## Project Overview
This CI server automates the process of compiling code, running unit tests, and sending notifications for each new commit pushed to a GitHub repository. It integrates with GitHub Webhooks and executes build steps asynchronously using a daemon thread, ensuring non-blocking behavior in the Flask web server.

## Key Features
- **Automatic Build Triggers**: CI jobs start when a new commit is pushed to a GitHub repository.
- **Code Compilation**: Syntax checking for Python files ensures code correctness.
- **Automated Testing**: Runs unit tests using `pytest`.
- **Email Notifications**: Developers receive build results via email.
- **Asynchronous Execution**: Jobs run in a separate thread, preventing server blockage.


## Implementation Details

### Compilation Implementation & Unit Testing

#### How Compilation Works
- The CI server checks for Python syntax errors in `.py` files using the `ast` module.
- If syntax errors are found, the build fails, and an email notification is sent.
- Otherwise, the pipeline proceeds to test execution.

#### Unit Testing Compilation
Unit tests for syntax checking are defined in `test_ci_pipeline.py`. They ensure:
- Valid Python files pass without errors.
- Syntax errors in a file cause the build to fail.

### Test Execution Implementation & Unit Testing

#### How Tests Are Run
- The CI server executes unit tests using `pytest`.
- The `tests` directory in the repository is checked.
- If tests exist, they are run; otherwise, the step is skipped.

#### Unit Testing Test Execution
`test_ci_pipeline.py` contains test cases for:
- Running tests on a repository with valid test files.
- Handling missing test directories gracefully.
- Capturing test output and build results.

### Notification System Implementation & Unit Testing

#### How Notifications Work
- After the CI process completes, an email is sent to the commit author.
- SMTP credentials are loaded from environment variables (`.env` file).
- Emails include build results and logs.

#### Unit Testing Email Notifications
`test_notifications.py` uses `unittest.mock.patch` to simulate SMTP interactions, ensuring:
- Emails are correctly formatted and sent.
- Errors in email delivery are handled gracefully.

## Project Dependencies
This project relies on the following dependencies:

### Python Libraries
- **Flask**: Web server for handling GitHub webhooks.
- **GitPython**: Cloning and managing repositories.
- **pytest**: Running unit tests.
- **smtplib**: Sending email notifications.
- **dotenv**: Managing environment variables.
- **unittest**: Unit testing framework.

### External Requirements
- **GitHub Webhook**: Must be configured to send events to the CI server.
- **Ngrok**: Used to expose the local Flask server to GitHub.
- **SMTP Server**: Required for sending email notifications.


##  Setting Up Virtual Environment (Mac/Linux)

### Running the Setup Script
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

##  Setting Up Virtual Environment (Windows)

### Running the Setup Script
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



## Statement of Contributions
This project was developed collaboratively, with contributions distributed as follows:

William Yu Stjernström: Worked on README, project setup (scripts, venv), ci_pipeline (test execution, cleanup), server (asynchronous thread for CI, process build) and  logging (printing) of status of ci server.

