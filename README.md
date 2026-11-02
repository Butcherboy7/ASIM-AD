# StockSage

StockSage scores Indian (NSE) stocks from 0 to 100 and tells you **Buy, Hold or Sell**. Part of the score comes from the company's numbers (price, profit, debt) and part from how positive or negative the latest news is. You choose how much each part counts.

It is a college / hackathon project. It is **not financial advice**.

- Pick a sector (IT, Banking, Auto, Pharma, Green Energy, Diversified) **or** type company names like `Infosys, Reliance`. You do not need to know ticker symbols.
- Watch each agent work live: Screening, Fundamental, Sentiment and Aggregator.
- Read a ranked table, then open any stock for its numbers, a chart, a plain-English summary and the news behind its score.
- Small `?` icons explain every term in plain words.

No API keys, no accounts, no payment. Everything uses free public data.

---

## Table of contents

1. [What you need](#1-what-you-need)
2. [Install VS Code, Python and Git](#2-install-vs-code-python-and-git)
3. [Get the project into VS Code (clone or ZIP)](#3-get-the-project-into-vs-code-clone-or-zip)
4. [Open the terminal inside VS Code](#4-open-the-terminal-inside-vs-code)
5. [Create the virtual environment](#5-create-the-virtual-environment)
6. [Install the requirements](#6-install-the-requirements)
7. [Run the app](#7-run-the-app)
8. [Using the app](#8-using-the-app)
9. [Next time you want to run it](#9-next-time-you-want-to-run-it)
10. [Push your changes to GitHub](#10-push-your-changes-to-github)
11. [Troubleshooting](#11-troubleshooting)
12. [How it works](#12-how-it-works)
13. [Project structure](#13-project-structure)
14. [Limitations and disclaimer](#14-limitations-and-disclaimer)

---

## 1. What you need

| Thing | Details |
|---|---|
| Computer | Windows 10/11, macOS, or Linux |
| VS Code | Free editor from Microsoft |
| Python | Version **3.10 or newer** (3.11, 3.12 and 3.13 all work) |
| Git | Needed to clone and to push. Free |
| GitHub account | Needed only if you want to push your changes |
| Internet | Needed every time you run an analysis (it fetches live prices and news) |
| Disk space | About 500 MB |

---

## 2. Install VS Code, Python and Git

Skip any you already have.

**VS Code:** download from <https://code.visualstudio.com/> and install with the default options.

**Python:** download from <https://www.python.org/downloads/>.
- **Windows:** run the installer and **tick "Add python.exe to PATH" on the first screen** before clicking *Install Now*.
- **macOS:** use the installer from <https://www.python.org/downloads/macos/>.
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git
  ```

**Git:** download from <https://git-scm.com/downloads> and install with the default options.

**After installing, close VS Code completely and open it again.** Then add the Python extension:
1. Press **Ctrl + Shift + X** (Extensions).
2. Search for `Python` and install the one by **Microsoft**.

---

## 3. Get the project into VS Code (clone or ZIP)

Pick **one** option. **Use Option A if you plan to push changes to GitHub.**

### Option A: Clone inside VS Code (recommended)

1. Open VS Code.
2. Press **Ctrl + Shift + P** (**Cmd + Shift + P** on macOS) to open the Command Palette.
3. Type `Git: Clone` and press **Enter**.
4. Paste this address and press **Enter**:
   ```
   https://github.com/Butcherboy7/ASIM-AD.git
   ```
5. A window asks where to save it. Pick a folder such as your Desktop, then click **Select as Repository Destination**.
6. When VS Code asks *"Would you like to open the cloned repository?"* click **Open**.
7. If it asks *"Do you trust the authors of the files in this folder?"* click **Yes, I trust the authors**.

You will see the files (`app.py`, `README.md`, `agents`, and so on) in the left sidebar.

**Same thing from the terminal** (only if you prefer typing):
```bash
git clone https://github.com/Butcherboy7/ASIM-AD.git
cd ASIM-AD
code .
```

### Option B: Download the ZIP

1. Open <https://github.com/Butcherboy7/ASIM-AD> in your browser.
2. Click the green **Code** button, then **Download ZIP**.
3. Extract it: right-click the file and choose **Extract All** (Windows), or double-click it (macOS).
4. In VS Code choose **File > Open Folder**, pick the extracted folder (the one containing `app.py`), and click **Select Folder**.
5. Click **Yes, I trust the authors** if asked.

A ZIP has no Git history, so you cannot push from it directly. If you later want to push, clone the repository instead (Option A), or see the ZIP note in [step 10](#10-push-your-changes-to-github).

---

## 4. Open the terminal inside VS Code

The terminal is where you type the commands below.

1. In VS Code choose **Terminal > New Terminal** from the top menu. (Shortcut: **Ctrl + `**, the key under Esc.)
2. A panel opens at the bottom. It is already "inside" your project folder.

To open **another** terminal at any time, click the **+** icon at the top right of the terminal panel. To close one, click the trash-can icon.

**Check you are in the right place.** Run this. You should see `app.py` and `requirements.txt` in the list.

Windows: `dir`  
macOS / Linux: `ls`

If you do not, you are in the wrong folder. Use **File > Open Folder** and pick the folder that contains `app.py`, then open a new terminal.

**Which terminal type?** On Windows the terminal is normally **PowerShell** (shown at the top right of the panel). All commands below for "Windows" work in PowerShell. You can switch type with the small **down-arrow** next to the **+** icon.

---

## 5. Create the virtual environment

A virtual environment keeps this project's libraries separate from the rest of your computer. You only create it once.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you see a red error about *"running scripts is disabled on this system"*, run these two lines instead:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

If `python` is not recognised, use `py -m venv .venv` for the first line.

### Windows (Command Prompt)

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**How to tell it worked:** your terminal line now starts with `(.venv)`.

**VS Code may pop up** *"We noticed a new environment has been created. Do you want to select it?"* Click **Yes**. If it does not appear, press **Ctrl + Shift + P**, type `Python: Select Interpreter`, and choose the one that says `.venv`.

---

## 6. Install the requirements

With `(.venv)` showing, run:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This downloads the libraries (Streamlit, pandas, yfinance, Plotly, NLTK and a few more). It takes 1 to 5 minutes. Wait until you get your prompt back with no red error text.

---

## 7. Run the app

```bash
streamlit run app.py
```

After a few seconds you will see:

```
  Local URL: http://localhost:8501
```

Your browser should open by itself. If it does not, open a browser and go to:

**<http://localhost:8501>**

(In VS Code you can also hold **Ctrl** and click the link in the terminal.)

Leave the terminal running while you use the app. Closing it stops the app.

**The first analysis is slower** (around 10 to 30 seconds) because it downloads a small sentiment dictionary once and fetches fresh data. After that, results are cached and repeat runs are quick.

**To stop the app:** click inside the terminal and press **Ctrl + C**.

---

## 8. Using the app

1. **Sector:** pick one from the dropdown. That is all you need to do.
2. **Or type your own stocks (optional):** type company names or ticker symbols separated by commas, for example `Infosys, Reliance, HDFC Bank`. If this box has anything in it, it is used instead of the sector.
3. **How many sector stocks:** how many companies from the sector to compare (1 to 5).
4. **Weight on fundamentals:** how much the company's own numbers count versus the news. `60` means 60% numbers, 40% news. Not sure? Leave it at 60.
5. Press **Run analysis** and watch the four agents work.
6. Read the **ranked table**. The bar in each row shows how much of the score came from company numbers (teal) and news (black). The thin lines mark 40 and 70.
7. Click a stock under **Inspect a stock** for its full breakdown, a plain-English summary, a chart, and the news headlines it was based on.

Hover over (or tap) any small `?` to see what a term means.

**Reading the result**

| Score | Signal | Meaning |
|---|---|---|
| 70 to 100 | **Buy** | Looks attractive on this formula |
| 40 to 69 | **Hold** | Neither clearly good nor clearly bad |
| 0 to 39 | **Sell** | Looks weak on this formula |

---

## 9. Next time you want to run it

You do **not** repeat the install. Open VS Code, choose **File > Open Recent** and pick the project, open a new terminal (**Ctrl + `**), then:

**Windows (PowerShell)**
```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

**macOS / Linux**
```bash
source .venv/bin/activate
streamlit run app.py
```

To get the latest code from GitHub first, run `git pull`, then `pip install -r requirements.txt` again.

---

## 10. Push your changes to GitHub

Do this after you edit files (for example `app.py`) and want them on GitHub. You must have opened the project with **Option A (clone)** in step 3.

### One-time setup: tell Git who you are

Run these two lines once on your computer (use your own name and the email of your GitHub account):

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Method 1: Using the VS Code buttons (no commands)

1. Click the **Source Control** icon in the left bar (it looks like a branch), or press **Ctrl + Shift + G**.
2. You will see a list of changed files. Click the **+** next to each file to *stage* it, or click the **+** next to "Changes" to stage all of them.
3. Type a short message in the box, such as `Update README`.
4. Click **Commit**. (If VS Code asks to stage everything automatically, click **Always** or **Yes**.)
5. Click **Sync Changes** (or **Publish Branch / Push**). If a pop-up asks to confirm, click **OK**.

### Method 2: Using the terminal

Open a terminal (**Ctrl + `**) in the project folder and run these in order:

```bash
git status
git add .
git commit -m "Describe what you changed"
git push
```

What each line does:
- `git status` shows what changed.
- `git add .` stages every changed file. Your `.venv` folder is already ignored, so it will not be uploaded.
- `git commit -m "..."` saves a snapshot with your message.
- `git push` uploads it to GitHub.

### The first time you push, you will be asked to sign in

A browser window opens asking you to **sign in to GitHub** and **authorize Visual Studio Code / Git Credential Manager**. Click **Authorize**, then go back to VS Code. You only do this once.

### You must have permission to push

If you see `Permission denied` or `403`, your GitHub account is not allowed to write to this repository. Either:
- Ask the owner (**Butcherboy7**) to add you: GitHub repo > **Settings > Collaborators > Add people**, then accept the email invite; **or**
- Click **Fork** on the GitHub page to make your own copy, clone *your* copy, push there, and open a **Pull Request**.

### Always pull before you push if others also edit

```bash
git pull
```

### Using the ZIP (Option B) and want to push to your own repository

A ZIP has no Git history. To upload it to **your own new empty repository** on GitHub (create one at <https://github.com/new> first), run in the project folder:

```bash
git init
git add .
git commit -m "First commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

Replace `YOUR-USERNAME/YOUR-REPO` with your own. Do not use this to push into someone else's existing repository.

### Common push errors

| What you see | What to do |
|---|---|
| `not a git repository` | You opened the wrong folder, or used a ZIP. Open the cloned folder, or use the ZIP steps above. |
| `Author identity unknown` | Run the two `git config --global` lines above, then commit again. |
| `rejected ... fetch first` or `non-fast-forward` | Someone pushed before you. Run `git pull --rebase`, then `git push`. |
| `Authentication failed` | Sign in again when the browser opens, or run `git push` once more. |
| `Permission denied` / `403` | You are not a collaborator. See "You must have permission to push". |
| `nothing to commit` | You have no new changes. Edit and save a file first. |

---

## 11. Troubleshooting

**`python` is not recognized / command not found**
Windows: try `py -m venv .venv` instead of `python -m venv .venv`. If that also fails, reinstall Python and tick *Add python.exe to PATH*, then restart VS Code. macOS / Linux: use `python3`.

**`streamlit` is not recognized**
Your virtual environment is not active. Run the activate command from step 5 (you should see `(.venv)`), or run:
```bash
python -m streamlit run app.py
```

**"Running scripts is disabled" in PowerShell**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

**Port 8501 is already in use**
Another copy is running. Close it (Ctrl + C in its terminal), or use a different port:
```bash
streamlit run app.py --server.port 8502
```
Then open <http://localhost:8502>.

**`pip install` fails with a long red error**
Make sure Python is 3.10 or newer (`python --version`) and that you are using `requirements.txt` from this repository. Then retry:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**"No market data found for ..."**
The name or symbol was not recognised, or Yahoo Finance had no data for it. Check the spelling, or try the NSE ticker (for example `TCS`, `RELIANCE`, `HDFCBANK`).

**Lines such as `HTTP Error 404 ... Quote not found` in the terminal**
Yahoo Finance sometimes rejects a lookup and the app retries a different way. The result still appears. You can ignore these.

**Everything shows N/A or the news list is empty**
You may be offline, or a free data source is rate-limiting you. Wait a minute and run again.

**The page looks wrong or stale after updating the code**
Hard refresh the browser (**Ctrl + Shift + R**, or **Cmd + Shift + R** on macOS).

---

## 12. How it works

Four small agents run as a pipeline. Stocks are analysed in parallel, and the app shows each agent's progress live.

```
 Screening agent         Fundamental agent        Sentiment agent          Aggregator agent
 chooses the stocks  ->  price, P/E, ROE,     ->  reads recent news    ->  blends both scores with
                         debt, margins            headlines, scores        your weighting into
                         (Yahoo Finance)          their tone (VADER)       Buy / Hold / Sell
```

- **Fundamental score (0 to 100):** built from P/E, P/B, return on equity, debt to equity and profit margins.
- **Sentiment score (0 to 100):** built from how many articles were found and how positive or negative they are. Headlines come from Google News and Yahoo Finance RSS, scored locally with NLTK VADER.
- **Final score:** `fundamental score x your weight + sentiment score x (100 - your weight)`, then mapped to Buy (70+), Hold (40 to 69) or Sell (below 40).
- **Caching:** fundamentals are cached for 10 minutes and sentiment for 30 minutes, so repeat runs are fast.

Data sources: [yfinance](https://github.com/ranaroussi/yfinance), Google News RSS, Yahoo Finance RSS. No API keys are required.

---

## 13. Project structure

```
.
├── app.py                      # The Streamlit app (UI + wiring)
├── agents/
│   ├── screening_agent.py      # Stock selection
│   ├── fundamental_agent.py    # Company numbers from Yahoo Finance
│   ├── sentiment_agent.py      # News fetching + sentiment scoring
│   └── aggregator_agent.py     # Combines scores, makes the call
├── utils/
│   ├── cache_manager.py        # Caching helpers
│   └── data_normalizer.py      # Score normalisation
├── .streamlit/config.toml      # Light theme settings
├── requirements.txt            # Python libraries (install with pip)
├── PRODUCT.md                  # Short product description (design context)
└── README.md                   # This file
```

**Add a sector:** edit the `SECTORS` dictionary near the top of `app.py` and, optionally, add the company names to `COMPANY_NAMES` so typing the name works.

**Change the Buy / Hold / Sell cut-offs:** edit the thresholds at the top of `agents/aggregator_agent.py`.

---

## 14. Limitations and disclaimer

- Built for a college demo, not for real trading.
- Focused on NSE-listed Indian stocks.
- Needs a working internet connection. Free data sources can be slow, incomplete or rate-limited.
- Scores come from a simple formula over public data. They do not predict the future.

**This is not financial advice.** Do not make investment decisions based on this tool. Speak to a qualified financial adviser.

## License

MIT. See [LICENSE](LICENSE).
