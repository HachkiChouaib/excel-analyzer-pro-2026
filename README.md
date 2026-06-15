<h1 align="center">📊 Excel Analyzer Pro 2026</h1>

<p align="center">
  <b>A modern web app to import, analyze, clean, visualize and export Excel/CSV data.</b><br>
  Built with Python · Streamlit · Pandas · Plotly · ReportLab
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-1.39-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white" alt="Pandas">
  <img src="https://img.shields.io/badge/Plotly-5.24-3F4F75?logo=plotly&logoColor=white" alt="Plotly">
  <img src="https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white" alt="Tests">
  <img src="https://img.shields.io/badge/code%20style-PEP8-brightgreen" alt="PEP8">
</p>

<p align="center">
  <a href="https://excel-analyzer-pro-2026.streamlit.app">
    <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit">
  </a>
</p>

---

## 🚀 Live Demo

The app is deployed on **Streamlit Community Cloud**:

👉 **https://excel-analyzer-pro-2026.streamlit.app**

> _Demo note: the free tier uses ephemeral storage, so registered accounts and
> analysis history reset when the server restarts. Create an account to explore,
> then upload `samples/demo_sales.xlsx` to see every feature in action._

---

## 📝 Description

**Excel Analyzer Pro 2026** is a professional data-analysis platform aimed at
businesses, data analysts and students. Upload a spreadsheet and instantly get
quality diagnostics, descriptive statistics, interactive charts, an automated
analytical assessment and a downloadable PDF report — all from a clean,
Power BI-inspired web interface.

The codebase follows a strict **layered architecture**: the business logic
(`utils/`) is completely decoupled from the UI (`pages/`), which makes every
core function unit-testable without launching Streamlit.

---

## ✨ Features

| Module | Description |
| ------ | ----------- |
| **1. Upload** | Import `.xlsx`, `.xls` or `.csv` files; view name, size, rows, columns. |
| **2. Auto Analysis** | Column typing, missing values, duplicates, empty columns, numeric statistics (mean, median, min, max, std). |
| **3. Cleaning** | Remove duplicates, handle missing values (drop / mean / median / zero), rename columns, convert types. |
| **4. Dashboard** | Power BI-style KPI cards and live data preview. |
| **5. Visualization** | Histogram, pie, bar, scatter and correlation heatmap (Plotly). |
| **6. AI Assessment** | Rule-based engine: dataset summary, detected issues (missing values, outliers via IQR, strong correlations) and recommendations. |
| **7. PDF Report** | One-click professional report (summary, KPIs, statistics, recommendations) via ReportLab. |
| **8. Export** | Download the cleaned dataset as Excel or CSV, or the full PDF report. |
| **9. History** | Persistent log of past analyses (date, filename, dimensions). |
| **10. Modern UI/UX** | Responsive layout, custom sidebar navigation, light/dark theme. |
| **🎁 Bonus — Auth** | User registration & login with salted PBKDF2 password hashing; per-user analysis history. |

---

## 🛠️ Technologies

- **Language:** Python 3.11+
- **Web UI:** Streamlit
- **Data:** Pandas, NumPy, OpenPyXL
- **Visualization:** Plotly, Matplotlib
- **PDF:** ReportLab
- **Quality:** PEP 8, type hints, docstrings, pytest

---

## 📸 Screenshots

> _Add screenshots here after running the app (e.g. `assets/screenshot-dashboard.png`)._

| Dashboard | Visualization |
| --------- | ------------- |
| _coming soon_ | _coming soon_ |

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/excel-analyzer-pro.git
cd excel-analyzer-pro

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

```bash
streamlit run app.py
```

Then open the URL shown in the terminal (default: <http://localhost:8501>).

**First run:** create an account on the **Register** tab, then log in.

**Workflow:** Login → Dashboard (upload) → Analysis → Cleaning → Visualization → Report & Export.

### Try it with the demo dataset

A ready-to-use sample with missing values, duplicates, outliers and correlated
columns is provided (regenerate it any time):

```bash
python samples/generate_demo.py   # writes samples/demo_sales.xlsx
```

Upload `samples/demo_sales.xlsx` on the Dashboard page to explore every feature.

### Running the tests

```bash
python -m pytest -q
```

---

## 🗂️ Project structure

```
excel-analyzer-pro/
├── app.py                  # Streamlit entry point + sidebar router
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── config.toml         # Theme + disable auto multipage nav
├── assets/
│   └── styles.css          # Custom CSS (KPI cards, branding)
├── data/                   # Runtime data & analysis history
├── exports/                # Generated exports
├── reports/                # Generated reports
├── samples/                # Demo dataset + generator script
│   └── generate_demo.py
├── utils/                  # Business logic (no Streamlit, fully testable)
│   ├── file_handler.py     #   File I/O + validation
│   ├── analyzer.py         #   Statistics + rule-based AI assessment
│   ├── cleaner.py          #   Immutable cleaning operations
│   ├── charts.py           #   Plotly figure factories
│   ├── exporter.py         #   Excel / CSV / PDF export
│   ├── auth.py             #   Registration / login (PBKDF2)
│   └── helpers.py          #   Formatting, per-user history, column typing
├── pages/                  # UI layer (one render() per screen)
│   ├── login.py
│   ├── dashboard.py
│   ├── analysis.py
│   ├── cleaning.py
│   ├── visualization.py
│   └── report.py
└── tests/                  # pytest unit tests (23 passing)
    ├── test_analyzer.py
    ├── test_cleaner.py
    └── test_auth.py
```

---

## 🧭 Architecture

```
app.py ── routes to ──> pages/*.py ── call ──> utils/*.py
   │                        │                      │
 session state         presentation         pure business logic
                                            (unit-tested, no UI)
```

The golden rule: **`utils/` never imports Streamlit.** This keeps the core
logic portable and 100 % testable, while `pages/` only handles presentation.

---

## 📄 License

Released under the MIT License — free to use, modify and share.

---

<p align="center"><sub>Built as a portfolio project to demonstrate Python, data analysis and clean software architecture.</sub></p>
