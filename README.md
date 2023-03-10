# Flask proyect

## First commands

```powershell
# Create enviroment
virtualenv .venv
# O
python -m venv .venv

# Activate enviroment
.\.venv\Scripts\activate

# Install dependencies
pip install -r .\requirements.txt
```

## Execute application

```powershell
python .\application.py
```

## Save new dependencies from the enviroment

```powershell
pip freeze > .\requirements.txt
```
