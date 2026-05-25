# Contributing

This is an academic project (University of Bath, GBDP Group 27). External contributions are welcome for bug fixes and improvements.

## Reporting Issues

Open a GitHub Issue and include:
- Python version (`python --version`)
- Error message or unexpected output
- The cell number where the failure occurred
- Whether you are using your own CSV files or the sample data

## Making Changes

1. Fork the repository
2. Create a branch: `git checkout -b fix/your-description`
3. Make your changes
4. Strip notebook outputs before committing (see below)
5. Open a Pull Request against `main`

## Stripping Notebook Outputs

Committed notebook outputs bloat the repo and create messy diffs. Strip them before every commit:

```bash
# Install once
pip install nbstripout

# Strip outputs from the notebook
nbstripout Downhole_Drilling_Analytics_GeoTorpedo_v3.ipynb
```

Or install as a git hook so it runs automatically:

```bash
nbstripout --install
```

## Code Style

- Follow PEP 8 for any standalone Python scripts
- Use descriptive variable names consistent with the existing `vib_`, `rpm_`, `temp_` prefix conventions
- Keep all ICS theme constants in the `ICS` dict (Cell 2 — do not hardcode colours elsewhere)

## Large Files

Do not commit files over 50 MB directly. Add them to `.gitattributes` for Git LFS tracking:

```
your_large_file.csv filter=lfs diff=lfs merge=lfs -text
```
