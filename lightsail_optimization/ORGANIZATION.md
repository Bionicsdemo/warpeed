# PROJECT ORGANIZATION GUIDE

**Date:** October 17, 2025
**Status:** Complete Reorganization

---

## 📂 QUICK REFERENCE

### Need to find something? Use this guide:

| What are you looking for? | Where to find it |
|---------------------------|------------------|
| **Python code (quantum)** | `src/quantum/` |
| **Python code (optimization)** | `src/optimization/` |
| **Python code (analysis)** | `src/analysis/` |
| **Python code (validation)** | `src/validation/` |
| **Run a script** | `scripts/` |
| **Technical docs** | `docs/engineering/` |
| **Business plans** | `docs/business/` |
| **Validation reports** | `docs/validations/` |
| **Research papers** | `docs/research/` |
| **Website files** | `website/` |
| **Images & media** | `assets/images/` |
| **Presentations** | `assets/presentations/` |
| **Results (quantum)** | `results/quantum/` |
| **Results (simulations)** | `results/simulations/` |
| **Log files** | `logs/` |
| **Tests** | `tests/` |

---

## 🎯 COMMON TASKS

### Run Quantum Optimization

```bash
cd /Users/heinzjungbluth/Desktop/Warp/lightsail_optimization
python3 src/quantum/quantum_material_structure_validator.py
```

### Run IBM Torino Optimization

```bash
cd /Users/heinzjungbluth/Desktop/Warp/lightsail_optimization
python3 scripts/run_ibm_torino_optimization.py
```

### Run Full Test Suite

```bash
cd /Users/heinzjungbluth/Desktop/Warp/lightsail_optimization
bash scripts/run_all_tests.sh
```

### View Website Locally

```bash
cd /Users/heinzjungbluth/Desktop/Warp/lightsail_optimization/website
open index.html
```

### Find a Specific Document

```bash
# Search in all docs
find docs/ -name "*.md" -type f | xargs grep -l "your_search_term"

# List all engineering specs
ls docs/engineering/

# List all validation reports
ls docs/validations/
```

---

## 📁 DETAILED DIRECTORY STRUCTURE

### `src/` - Source Code

All Python source code is organized by function:

#### `src/quantum/` - Quantum Optimization (13 files)
- `quantum_material_structure_validator.py` - Main material validator
- `quantum_comm_optimizer.py` - Communication system optimizer
- `quantum_comm_optimizer_v2.py` - V2 of comm optimizer
- `quantum_comm_rf_optimizer_ibm_torino.py` - RF optimizer for IBM Torino
- `quantum_comm_solutions_advanced.py` - Advanced comm solutions
- `quantum_hybrid_comm_optimizer.py` - Hybrid quantum-classical comm
- `quantum_integrated_optimizer.py` - Integrated system optimizer
- `quantum_integrated_system_ibm_torino.py` - IBM Torino integration
- `quantum_laser_corrected_optimizer.py` - Corrected laser optimizer
- `quantum_laser_system_optimizer.py` - Laser system optimizer
- `quantum_power_optimizer.py` - Power system optimizer
- `quantum_rf_optimizer.py` - RF optimizer
- `quantum_rf_optimizer_v2_realistic.py` - Realistic RF optimizer V2

#### `src/analysis/` - Analysis Scripts (4 files)
- `analyze_integrated_results.py` - Analyze integrated system results
- `analyze_quantum_results.py` - Analyze quantum computing results
- `cost_analysis.py` - Cost breakdown & analysis
- `rf_analysis_report.py` - RF analysis report generator

#### `src/optimization/` - Classical Optimization (4 files)
- `lightsail_optimizer_local.py` - Local CPU optimization
- `modal_lightsail_optimizer.py` - Modal A100 GPU optimization
- `power_system_recommendations.py` - Power system recommendations
- `power_system_sizing.py` - Power system sizing calculations

#### `src/validation/` - Validation Scripts (2 files)
- `validate_power_system.py` - Power system validator
- `validate_quantum_solution.py` - Quantum solution validator

---

### `scripts/` - Executable Scripts

Runner scripts for common operations:

- `run_all_tests.sh` - Execute full test suite
- `run_ibm_torino_optimization.py` - Run IBM Quantum optimization

**Usage:**
```bash
bash scripts/run_all_tests.sh
python3 scripts/run_ibm_torino_optimization.py
```

---

### `docs/` - Documentation

All project documentation organized by category:

#### `docs/engineering/`
Technical specifications, engineering documents, physics corrections, manufacturing processes.

#### `docs/business/`
Business plans, investor presentations, cost analyses, roadmaps, target investor lists.

#### `docs/validations/`
- IBM Torino validation results
- Quantum material validation
- Laser system validation
- Communication system validation

#### `docs/research/`
Research papers, master documents, project summaries, performance comparisons.

#### `docs/company/`
Company information, team profiles, mission statements.

#### `docs/infrastructure/`
Infrastructure documentation, deployment guides, system architecture.

---

### `website/` - Warpeed Website

Complete website with interactive features:

- `index.html` - Main landing page
- `spectrix.html` - SPECTRIX mission page
- `laser.html` - Laser system visualization
- `material.html` - Material specifications
- `mission.html` - Mission overview
- `team.html` - Team profiles
- `research.html` - Research documentation
- `yc-application.html` - Y Combinator application
- `niac-application.html` - NIAC application
- `animations/` - Interactive 3D animations
  - `deployment_animation.html` - Deployment sequence
  - `mission_trajectory_svg.html` - Mission trajectory
  - `3d_lightsail_canvas.html` - 3D lightsail viewer
  - `VIDEO_AI_PROMPTS.md` - AI video generation guide
  - `README.md` - Animation documentation

---

### `assets/` - Media & Presentations

#### `assets/images/` (17 files)
All project images including:
- Lightsail renders
- Laser array visualizations
- Material layer diagrams
- Team photos
- Mission graphics

#### `assets/presentations/`
PowerPoint presentations, investor pitch decks, Keynote files.

---

### `results/` - Optimization Results

#### `results/quantum/`
Quantum computing results, circuit outputs, optimization solutions.

#### `results/simulations/`
Classical simulation outputs, performance data.

#### `results/` (root)
- `advanced_comm_solutions.json` - Communication system solutions

---

### `logs/` - Log Files

All execution logs:
- `quantum_run.log` - Quantum optimization execution logs

---

### `tests/` - Test Suite

Unit tests, integration tests, validation tests.

---

## 🔄 MIGRATION GUIDE

### Old Location → New Location

| Old Path | New Path |
|----------|----------|
| `quantum_*.py` | `src/quantum/quantum_*.py` |
| `analyze_*.py` | `src/analysis/analyze_*.py` |
| `lightsail_optimizer_local.py` | `src/optimization/lightsail_optimizer_local.py` |
| `validate_*.py` | `src/validation/validate_*.py` |
| `run_*.sh`, `run_*.py` | `scripts/run_*` |
| `*.md` (except README) | `docs/[category]/` |
| `*.html` | `website/*.html` |
| `*.png`, `*.jpg` | `assets/images/` |
| `*.pptx` | `assets/presentations/` |
| `*.json` | `results/` |
| `*.log` | `logs/` |

---

## 🎓 BEST PRACTICES

### For Developers

1. **New Python module?** → Put in appropriate `src/` subdirectory
2. **New script?** → Put in `scripts/` and make executable
3. **New documentation?** → Put in appropriate `docs/` subdirectory
4. **New test?** → Put in `tests/`
5. **New result?** → Save to `results/quantum/` or `results/simulations/`

### For Documentation

1. **Technical specs** → `docs/engineering/`
2. **Business docs** → `docs/business/`
3. **Validation reports** → `docs/validations/`
4. **Research papers** → `docs/research/`

### For Media

1. **Images** → `assets/images/`
2. **Presentations** → `assets/presentations/`
3. **Website assets** → Keep in `website/` if used directly

---

## 📊 PROJECT STATISTICS

- **Total Python files:** 24 (organized in `src/`)
- **Total documentation files:** 24+ (organized in `docs/`)
- **Total images:** 17 (in `assets/images/`)
- **Total HTML pages:** 8+ (in `website/`)
- **Total directories:** 20+
- **Root files:** 2 (README.md + ORGANIZATION.md)

---

## 🚀 ADVANTAGES OF NEW STRUCTURE

✅ **Clear separation of concerns**
- Code, docs, results, media all separated

✅ **Easy navigation**
- Find anything in <10 seconds

✅ **Scalable**
- Easy to add new modules/docs without clutter

✅ **Professional**
- Standard structure recognized by developers

✅ **Git-friendly**
- Clean .gitignore possibilities
- Easy to track changes by category

✅ **Collaboration-ready**
- New team members onboard quickly
- Clear where to add contributions

---

## 📞 QUESTIONS?

If you can't find something:

1. Check this ORGANIZATION.md file
2. Check README.md for project overview
3. Use `find` or `grep` commands above
4. Browse directories - they're logically organized!

---

**Last Updated:** October 17, 2025
**Version:** 1.0 (Initial organization)
