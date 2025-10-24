# Cleanup & Repo Maintenance

This file lists recommended Git commands and actions to keep the repository clean.

1) Stop tracking `prediction_logs.csv` (if already committed):

```bash
# From project root
git rm --cached prediction_logs.csv
git commit -m "Stop tracking prediction_logs.csv"
```

2) Move large or non-runtime assets out of repository or into `data/`:

```bash
# Move dataset into data/ (example)
mkdir -p data
git mv credit_risk_dataset.csv data/
git commit -m "Move dataset to data/"
```

3) Move notebooks into `notebooks/`:

```bash
mkdir -p notebooks
git mv New_Agent.ipynb notebooks/
git commit -m "Organize notebooks"
```

4) If you want to stop tracking model binaries (optional):

```bash
# Make a backup first! Then:
# Add these lines to .gitignore: credit_risk_model.pkl scaler.pkl feature_names.pkl
# Then untrack them
git rm --cached credit_risk_model.pkl scaler.pkl feature_names.pkl
git commit -m "Stop tracking model artifacts; store them in releases or a model registry"
```

5) After edits to code, restart services:

```powershell
# Restart FastAPI
uvicorn api:app --reload

# Restart Streamlit
streamlit run app.py
```

6) Optional: create a small GitHub release for the model artifacts instead of storing in repo.


If you want, I can run through these steps interactively and apply safe changes (add .gitignore entries already applied). For any `git rm` or `git mv` commands I will need your approval because I cannot execute git in your environment automatically.
