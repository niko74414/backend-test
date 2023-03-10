# Proyecto base flask

## Primeros comandos
```powershell
# Crear entorno
virtualenv .venv
# O
python -m venv .venv

# Activar entorno
.\.venv\Scripts\activate

# Instalar dependencias en el entorno
pip install -r .\requirements.txt
```

## Ejecutar aplicacion
```powershell
python .\application.py
```

## Guardar nuevas dependencias del entorno virtual
```powershell
pip freeze > .\requirements.txt
```

## Despliegue
```powershell
eb deploy <nombre-del-ambiente>
```

## Push - subrir al repo
```powershell
git checkout <rama-a-subir>
git push <nombre-remoto> <rama-local>:<rama-remota>
```

### Ejemplo:
```powershell
git checkout David
git push origin David:David
```

## Pull - traer del repo
```powershell
git checkout <rama-local-donde-quedaran-los-cambios>
git pull <nombre-remoto> <rama-remota>
```

### Ejemplo:
```powershell
git checkout David
git push origin David
```