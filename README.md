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
2. [Install Python](#2-install-python)
3. [Download the project](#3-download-the-project)
4. [Open a terminal in the project folder](#4-open-a-terminal-in-the-project-folder)
5. [Create the virtual environment](#5-create-the-virtual-environment)
6. [Install the requirements](#6-install-the-requirements)
7. [Run the app](#7-run-the-app)
8. [Using the app](#8-using-the-app)
9. [Next time you want to run it](#9-next-time-you-want-to-run-it)
10. [Troubleshooting](#10-troubleshooting)
11. [How it works](#11-how-it-works)
12. [Project structure](#12-project-structure)
13. [Limitations and disclaimer](#13-limitations-and-disclaimer)

---

## 1. What you need

| Thing | Details |
|---|---|
| Computer | Windows 10/11, macOS, or Linux |
| Python | Version **3.10 or newer** (3.11, 3.12 and 3.13 all work) |
| Internet | Needed every time you run an analysis (it fetches live prices and news) |
| Git | Optional. You can download a ZIP instead |
| Disk space | About 500 MB |

---

## 2. Install Python

Check whether you already have it. Open a terminal (see [step 4](#4-open-a-terminal-in-the-project-folder) for how) and run:

**Windows**
```powershell
python --version
```

**macOS / Linux**
```bash
python3 --version
```

If it prints `Python 3.10` or higher (for example `Python 3.12.4`), skip to step 3.

If you get an error like *"Python was not found"* or the version is older than 3.10:

- **Windows:** go to <https://www.python.org/downloads/>, click the big yellow **Download Python** button, run the installer, and **tick the box "Add python.exe to PATH" on the first screen** before clicking *Install Now*. Close and reopen your terminal afterwards.
- **macOS:** download the installer from <https://www.python.org/downloads/macos/>, or with Homebrew run `brew install python`.
- **Linux (Ubuntu/Debian):**
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip
  ```

---

## 3. Download the project

Pick **one** of these two ways.

### Option A: with Git (recommended)

```bash
git clone https://github.com/Butcherboy7/ASIM-AD.git
```

Don't have Git? Get it from <https://git-scm.com/downloads> (accept the default options), then reopen your terminal.

### Option B: without Git (ZIP)

1. Open <https://github.com/Butcherboy7/ASIM-AD> in your browser.
2. Click the green **Code** button, then **Download ZIP**.
3. Right-click the downloaded file and choose **Extract All** (Windows) or double-click it (macOS).
4. Move the extracted folder somewhere easy, such as your Desktop.

---

## 4. Open a terminal in the project folder

A *terminal* is a window where you type commands. You need one that is "inside" the project folder.

### Windows

**Easiest way (File Explorer):**
1. Open the project folder in File Explorer (the folder that contains `app.py`).
2. Click the address bar at the top, type `powershell`, and press **Enter**.
3. A blue PowerShell window opens already inside the right folder.

**Or from the Start menu:**
1. Press the **Windows key**, type `PowerShell`, press **Enter**.
2. Go to the project folder. If you cloned it to your Desktop, type:
   ```powershell
   cd $HOME\Desktop\ASIM-AD
   ```
   (Change `ASIM-AD` to whatever your folder is called.)

### macOS

1. Press **Cmd + Space**, type `Terminal`, press **Enter**.
2. Go to the project folder. If it is on your Desktop:
   ```bash
   cd ~/Desktop/ASIM-AD
   ```

Tip: you can also type `cd ` (with a space), then drag the folder from Finder into the Terminal window and press Enter.

### Linux

1. Press **Ctrl + Alt + T**.
2. Go to the folder:
   ```bash
   cd ~/Desktop/ASIM-AD
   ```

### Using VS Code instead

1. Open VS Code, choose **File > Open Folder**, and pick the project folder.
2. Open a terminal with **Terminal > New Terminal** (or press **Ctrl + `**). It opens already inside the project folder.

### Check you are in the right place

Run this. You should see `app.py` and `requirements.txt` in the list.

**Windows:** `dir`  
**macOS / Linux:** `ls`

---

## 5. Create the virtual environment

A virtual environment keeps this project's libraries separate from the rest of your computer. You only create it once.

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If you see a red error about *"running scripts is disabled on this system"*, run this once and then try the activate line again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Windows (Command Prompt / cmd)

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

Your browser should open by itself. If it does not, open it and go to:

**<http://localhost:8501>**

Leave the terminal window open while you use the app. Closing it stops the app.

**The first analysis is slower** (around 10 to 30 seconds) because it downloads a small sentiment dictionary once and fetches fresh data. After that, results are cached and repeat runs are quick.

To stop the app, click the terminal and press **Ctrl + C**.

---

## 8. Using the app

1. **Sector:** pick one from the dropdown. That is all you need to do.
2. **Or type your own stocks (optional):** type company names or ticker symbols separated by commas, for example `Infosys, Reliance, HDFC Bank`. If this box has anything in it, it is used instead of the sector.
3. **How many sector stocks:** how many companies from the sector to compare (1 to 5).
4. **Weight on fundamentals:** how much the company's own numbers count versus the news. `60` means 60% numbers, 40% news. Not sure? Leave it at 60.
5. Press **Run analysis** and watch the four agents work.
6. Read the **ranked table**. The bar in each row shows how much of the score came from company numbers (teal) and news (black). The thin lines mark 40 and 70.
7. Click a stock name under **Inspect a stock** for its full breakdown, a plain-English summary, a chart, and the news headlines it was based on.

Hover over (or tap) any small `?` to see what a term means.

**Reading the result**

| Score | Signal | Meaning |
|---|---|---|
| 70 to 100 | **Buy** | Looks attractive on this formula |
| 40 to 69 | **Hold** | Neither clearly good nor clearly bad |
| 0 to 39 | **Sell** | Looks weak on this formula |

---

## 9. Next time you want to run it

You do **not** repeat the install. Open a terminal in the project folder (step 4), then:

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

Want it updated to the latest code? Run `git pull` first, then `pip install -r requirements.txt` again.

---

## 10. Troubleshooting

**`python` is not recognized / command not found**
Windows: try `py -m venv .venv` instead of `python -m venv .venv`. If that also fails, reinstall Python and tick *Add python.exe to PATH*. macOS / Linux: use `python3`.

**`streamlit` is not recognized**
Your virtual environment is not active. Run the activate command from step 5 (you should see `(.venv)`), or run the app with:
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

## 11. How it works

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

## 12. Project structure

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

## 13. Limitations and disclaimer

- Built for a college demo, not for real trading.
- Focused on NSE-listed Indian stocks.
- Needs a working internet connection. Free data sources can be slow, incomplete or rate-limited.
- Scores come from a simple formula over public data. They do not predict the future.

**This is not financial advice.** Do not make investment decisions based on this tool. Speak to a qualified financial adviser.

## License

MIT. See [LICENSE](LICENSE).
