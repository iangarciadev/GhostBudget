# GhostBudget

A personal finance desktop app built with Python and Flet.

## Features

- Monthly dashboard with income, expenses, and balance summary
- Add and edit transactions (income and expenses)
- Customizable categories with color and icon
- Month navigation
- Backup and restore via Google Drive (optional)

## Tech stack

- [Python 3.11+](https://www.python.org/)
- [Flet](https://flet.dev/) — desktop UI framework for Python
- SQLite — local database
- Google Drive API — optional sync

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/GhostBudget.git
cd GhostBudget
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the app**

```bash
python main.py
```

## Google Drive sync (optional)

Google Drive allows you to back up and restore the database across devices. Setup is done once.

### Prerequisites

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the **Google Drive API** (APIs & Services → Library)
4. Create OAuth 2.0 credentials (APIs & Services → Credentials → Create Credentials → OAuth client ID → Desktop app)
5. Download the generated JSON file and rename it to `credentials.json`
6. Place `credentials.json` in the GhostBudget root folder

The expected file structure is documented in `credentials.example.json`.

### Linking your account

With `credentials.json` in place, open the app, go to **Settings**, and click **Link Google account**. A browser window will open for authorization — once confirmed, the app is ready to upload and restore backups.

> The access token is saved to `data/gdrive_token.json` and refreshed automatically. The app only accesses files it created itself in your Drive.

## Project structure

```
GhostBudget/
├── main.py                  # Entry point
├── state.py                 # Global app state
├── requirements.txt
├── credentials.example.json # Template for Google Drive setup
├── models/                  # Database access
├── controllers/             # Business logic
├── views/                   # App screens
├── components/              # Reusable UI components (navbar)
├── sync/                    # Google Drive integration
└── data/                    # Local database (auto-generated)
```

## Local data

The SQLite database is stored at `data/budget.db` and created automatically on first run. The `data/` folder is not versioned.
