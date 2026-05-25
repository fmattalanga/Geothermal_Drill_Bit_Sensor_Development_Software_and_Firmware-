# Pushing This Repo to GitHub

Step-by-step — run these commands in the terminal from inside your project folder.

---

## 0. Prerequisites (one-time installs)

```bash
# Git — https://git-scm.com/downloads
git --version

# Git LFS — https://git-lfs.com
git lfs install

# Python tools
pip install nbstripout pytest
```

---

## 1. Strip notebook outputs

Notebooks store rendered cell outputs (images, HTML, JSON) inline. These bloat commits and create noisy diffs. Strip them first.

```bash
# Install the git hook so stripping runs automatically on every commit
nbstripout --install

# Or strip manually (run once before the first commit)
nbstripout "Downhole_Drilling_Analytics_GeoTorpedo_v3.ipynb"
nbstripout "ICS_Core_Firmware0_Sensor IC_Assembly_Validation.ipynb"
nbstripout "ICS_Core_Firmware1_dsPIC33AK256MC205_Initilisation_Calibration_.ipynb"
nbstripout "ICS_Core_Firmware2_dsPIC33AK256MC205_DataGeneration.ipynb"
nbstripout "ICS_Core_Firmware3_CC2642R1TWFRTCRQ1_inertialcAndCSV.ipynb"
```

> After stripping, notebooks still open and run normally — outputs are just regenerated when you run the cells.

---

## 2. Create the GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it `ics-core-sensor-pipeline` (or similar)
3. Set visibility: **Public** or **Private**
4. **Do NOT** tick "Add a README file" — you already have one
5. Click **Create repository**

---

## 3. Initialise git locally

Navigate to your project folder in the terminal first:

```bash
cd "C:\Users\fmata\OneDrive - University of Bath\GBDP - Group 27 - Sensor IC Design\Github files"
```

Then:

```bash
git init
git branch -M main
```

---

## 4. Set up Git LFS for the 91 MB file

The file `Bath Uni project 2026/100Hz Sampled_converted.json` (91 MB) must go through LFS — GitHub will reject it otherwise.

The `.gitattributes` file already contains the tracking rule. Just confirm LFS is active:

```bash
git lfs install
git lfs track "Bath Uni project 2026/100Hz Sampled_converted.json"
git lfs track "Bath Uni project 2026/*.csv"
```

Check what LFS is tracking:

```bash
git lfs ls-files --all
```

---

## 5. Stage all files

```bash
git add .
```

Check what will be committed (make sure no huge files slip through):

```bash
git status
git diff --cached --stat | sort -t'|' -k2 -rn | head -20
```

If any file looks unexpectedly large (> 10 MB) in the staged list, add it to `.gitignore` or `.gitattributes` before continuing.

---

## 6. First commit

```bash
git commit -m "Initial commit — ICS Core sensor pipeline v1.0

- Firmware notebooks FW0–FW3 (assembly validation, init/cal, data gen, inertial processing)
- GeoTorpedo analytics notebook (11 interactive plots, HTML report, live dashboard)
- ics_sandbox: 5 sensor simulation models + pytest suite
- Sample data: ICS_SIM_20260401_120000 (100 Hz + 1 Hz)
- Reference docs: technical report PDF + pipeline reference DOCX
"
```

---

## 7. Connect to GitHub and push

Replace `<your-username>` with your GitHub username:

```bash
git remote add origin https://github.com/<your-username>/ics-core-sensor-pipeline.git
git push -u origin main
```

If LFS objects are large, the push may take a few minutes. You'll see a separate LFS upload progress bar.

---

## 8. Verify on GitHub

After pushing:

1. Open `https://github.com/<your-username>/ics-core-sensor-pipeline`
2. Check the README renders correctly (it should show the pipeline diagram)
3. Click on `Bath Uni project 2026/100Hz Sampled_converted.json` — it should show a Git LFS pointer file, not raw JSON
4. Check that `__pycache__/` and `.pytest_cache/` folders are **not** present in the repo tree

---

## 9. Run tests to confirm sandbox is intact

After cloning on a new machine:

```bash
pip install -r requirements.txt
cd ics_sandbox
pytest tests/ -v
```

All 5 test modules should pass.

---

## Ongoing workflow

```bash
# Before each commit — strip outputs if nbstripout hook isn't installed
nbstripout *.ipynb

# Normal commit flow
git add .
git commit -m "Your message"
git push
```

---

## What's excluded from the repo (`.gitignore`)

| Excluded | Reason |
|---|---|
| `__pycache__/`, `*.pyc` | Python bytecode — regenerated automatically |
| `.pytest_cache/` | pytest runtime cache |
| `*_run_report_*.html` | Generated HTML reports (reproduced by running the notebook) |
| `bha_live_dashboard.html` | Generated live dashboard |
| `ICS_notebook.html` | Generated static notebook export |
| `ics_raw_gen_output/` | Duplicate of `ics_gen_output/` |
| `ics_sandbox/reports/` | Generated test artefacts |

---

## What's tracked via Git LFS (`.gitattributes`)

| File | Size | Why LFS |
|---|---|---|
| `Bath Uni project 2026/100Hz Sampled_converted.json` | 91 MB | Exceeds GitHub's 50 MB soft limit |
| `Bath Uni project 2026/*.csv` | Up to 21 MB each | Large data files |
