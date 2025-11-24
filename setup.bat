@echo off
echo Creating Python virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete! To activate the environment, run:
echo venv\Scripts\activate
echo.
echo Make sure to set your OPENAI_API_KEY:
echo setx OPENAI_API_KEY "yourkey"
echo.
pause

