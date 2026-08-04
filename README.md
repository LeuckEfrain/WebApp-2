# Modular Web App v0.3

Clean UI foundation + read-only Package Manager module.

## Scope
- Detect winget, Chocolatey, pip, npm
- Detect common development tools
- Read-only installed software inventory through winget when available
- Search package repositories through their native read-only search commands
- No automatic install/uninstall/upgrade operations

## Run backend
```powershell
py -m pip install -r backend\requirements.txt
py -m uvicorn backend.main:app --reload
```

## Run frontend
Requires Node.js/npm for the React development server:
```powershell
npm install --prefix frontend
npm run dev --prefix frontend
```
