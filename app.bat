@ECHO OFF
ECHO.
ECHO.
ECHO Welcome to Mitta Control
ECHO 1. Start Local Dev
ECHO 2. Deploy to AppEngine
ECHO 3. Logs from AppEngine
ECHO 4. Exit
ECHO.

CHOICE /C 1234 /M "Choose:  "

IF ERRORLEVEL 4 GOTO Exits
IF ERRORLEVEL 3 GOTO Logs
IF ERRORLEVEL 2 GOTO Deploy
IF ERRORLEVEL 1 GOTO Starts

:Logs
gcloud app logs tail -s default
GOTO End

:Deploy
gcloud app deploy ./app.yaml
GOTO End

:Starts
SET DEV='True'
SET GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
python ./main.py
GOTO End

:Exits
GOTO End

:End

