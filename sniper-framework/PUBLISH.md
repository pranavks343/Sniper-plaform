# Publishing Sniper Framework to PyPI

Guide for maintainers to publish new versions to PyPI.

## Prerequisites

1. **PyPI Account**: Register at [pypi.org](https://pypi.org)
2. **Authentication**: Create API token at [pypi.org/manage/account/tokens/](https://pypi.org/manage/account/tokens/)
3. **Build Tools**: Install build and twine
   ```bash
   pip install build twine
   ```

## Publishing Steps

### 1. Update Version

Edit `pyproject.toml`:
```toml
[project]
version = "1.1.0"  # Update version number
```

Edit `sniper/__init__.py`:
```python
__version__ = "1.1.0"  # Match pyproject.toml
```

### 2. Update Changelog

Add entry to `CHANGELOG.md`:
```markdown
## [1.1.0] - 2025-02-18

### Added
- Feature 1
- Feature 2

### Fixed
- Bug fix 1
```

### 3. Commit & Tag

```bash
git add -A
git commit -m "release: v1.1.0 — feature descriptions"
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main
git push origin v1.1.0
```

### 4. Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel and source distribution
python -m build
```

Verify files in `dist/`:
- `sniper_framework-1.1.0-py3-none-any.whl`
- `sniper_framework-1.1.0.tar.gz`

### 5. Test Upload (Recommended)

Upload to TestPyPI first to catch issues:
```bash
twine upload --repository testpypi dist/*
```

Then test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ sniper-framework
```

### 6. Upload to PyPI

```bash
twine upload dist/*
```

You'll be prompted for:
- Username: `__token__`
- Password: Paste your API token (starting with `pypi-`)

Or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...
twine upload dist/*
```

### 7. Verify

Check that version appears on PyPI within ~5 minutes:
https://pypi.org/project/sniper-framework/

Install and test:
```bash
pip install --upgrade sniper-framework
python -c "import sniper; print(sniper.__version__)"
```

---

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking API changes
- **MINOR** (0.X.0): New features (backward compatible)
- **PATCH** (0.0.X): Bug fixes (backward compatible)

Examples:
- `1.0.0` → `1.1.0` (new feature) — MINOR
- `1.0.0` → `1.0.1` (bug fix) — PATCH
- `1.0.0` → `2.0.0` (breaking change) — MAJOR

---

## Pre-Release Versions

For beta/release candidate versions:

```toml
version = "1.1.0rc1"  # Release candidate
```

or

```toml
version = "1.1.0b2"   # Beta
```

These appear as "Pre-release" on PyPI.

---

## Troubleshooting

### "Invalid distribution filename"
- Ensure version matches regex: `[0-9]+(\.[0-9]+)*`
- Check pyproject.toml and __init__.py match

### "File already exists"
- Each version can only be uploaded once
- To fix a bad release, increment to next patch version

### "403 Client Error"
- Check API token is valid and not expired
- Verify username is `__token__`

### Build fails
```bash
# Verify pyproject.toml syntax
pip install toml
python -c "import toml; toml.load('pyproject.toml')"

# Check no duplicate dependencies
grep -i "dependencies" pyproject.toml
```

---

## Post-Release

1. **GitHub Release**: Create release on GitHub with changelog
2. **Announce**: Share on Twitter, Reddit r/algotrading, etc.
3. **Update Docs**: Point to new version in documentation
4. **Deprecations**: If removing features, announce in README first

---

## CI/CD Automation

To automate releases with GitHub Actions, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install build twine
      - run: python -m build
      - uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
```

Then releases automatically publish when you create a GitHub release.

---

## Maintenance

### Yanking a Version

If a version has critical bugs:

```bash
twine yank sniper-framework==1.0.5
```

This removes it from PyPI but keeps it visible with warning.

### Security Update

For security fixes, use PATCH bump:
- `1.0.0` → `1.0.1` (critical security fix)

Announce immediately and ask users to upgrade.

---

## Resources

- [PyPI Help](https://pypi.org/help/)
- [Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)

---

Last updated: 2025-02-18
