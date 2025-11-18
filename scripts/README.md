# Development Scripts

This directory contains utility scripts for development, deployment, and setup tasks.

## Available Scripts

### Development
- **dev_start.ps1** - Start development servers (backend + frontend)

### Deployment
- **deploy.ps1** - Windows deployment script
- **deploy.sh** - Linux/Mac deployment script

### Setup & Installation
- **install_database.ps1** - Install database dependencies
- **install_excel_support.ps1** - Install Excel file support
- **setup_database.py** - Initialize database tables

---

## dev_start.ps1

Automated script to start both backend and frontend development servers in separate PowerShell windows.

### Quick Start

```powershell
# From project root
.\scripts\dev_start.ps1
```

This will:
1. ✅ Check for virtual environment
2. ✅ Check for .env file
3. ✅ Open new window for backend API (http://localhost:8000)
4. ✅ Open new window for frontend (http://localhost:5173)
5. ✅ Automatically activate virtual environment
6. ✅ Show helpful URLs

### Usage Examples

**Basic usage (recommended):**
```powershell
.\scripts\dev_start.ps1
```

**Custom backend port:**
```powershell
.\scripts\dev_start.ps1 -BackendPort 8080
```

**Run in current window (blocks):**
```powershell
.\scripts\dev_start.ps1 -RunInCurrentWindow
```

**Disable auto-reload:**
```powershell
.\scripts\dev_start.ps1 -Reload:$false
```

**Get help:**
```powershell
Get-Help .\scripts\dev_start.ps1 -Full
Get-Help .\scripts\dev_start.ps1 -Examples
```

### What It Does

#### Backend Window
- Changes to project root directory
- Activates `.venv` virtual environment
- Runs: `uvicorn backend.api.main:app --reload --port 8000 --host 0.0.0.0`
- Shows startup logs

#### Frontend Window
- Changes to `frontend/` directory
- Detects package manager (npm/yarn/pnpm)
- Runs: `npm run dev` (or yarn/pnpm equivalent)
- Shows Vite dev server logs

### Prerequisites

Before running the script, ensure:

1. **Virtual environment exists:**
   ```powershell
   python -m venv .venv
   ```

2. **Python dependencies installed:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Frontend dependencies installed:**
   ```powershell
   cd frontend
   npm install
   cd ..
   ```

4. **Environment variables configured:**
   ```powershell
   # Create .env file
   "GEMINI_API_KEY=your-key-here" | Out-File -FilePath .env -Encoding utf8
   ```

### Troubleshooting

**Issue: "Virtual environment not found"**
```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Issue: "node_modules not found"**
```powershell
cd frontend
npm install
cd ..
```

**Issue: ".env file not found"**
```powershell
# Copy example and edit
Copy-Item env.example .env
# Then edit .env and add your GEMINI_API_KEY
```

**Issue: "Port already in use"**
```powershell
# Use different port
.\scripts\dev_start.ps1 -BackendPort 8080

# Or kill process on port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

**Issue: Windows opens but closes immediately**
- Check the error message in the window before it closes
- Try running in current window to see errors:
  ```powershell
  .\scripts\dev_start.ps1 -RunInCurrentWindow
  ```

### Manual Alternative

If the script doesn't work, you can start services manually:

**Terminal 1 - Backend:**
```powershell
.\.venv\Scripts\Activate.ps1
python run.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Features

- ✅ Automatic virtual environment activation
- ✅ Checks for prerequisites (.venv, .env, node_modules)
- ✅ Detects package manager (npm/yarn/pnpm)
- ✅ Opens separate windows for easy monitoring
- ✅ Shows helpful URLs after startup
- ✅ Configurable ports and options
- ✅ Comprehensive help documentation

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `BackendModule` | String | `backend.api.main:app` | Python module path for FastAPI |
| `BackendPort` | Int | `8000` | Port for backend API |
| `Reload` | Switch | `$true` | Enable auto-reload |
| `RunInCurrentWindow` | Switch | `$false` | Run in current window |

### URLs After Startup

Once started, access:
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc
- **Frontend:** http://localhost:5173

### Stopping Services

To stop the services:
1. Close the PowerShell windows, or
2. Press `Ctrl+C` in each window

---

**Need help?** Run `Get-Help .\scripts\dev_start.ps1 -Full`
