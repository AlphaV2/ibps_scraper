# 🕵️ IBPS Recruitment Scraper

A Python-based **web scraping utility** that extracts public job listings from the [Institute of Banking Personnel Selection (IBPS)](https://www.ibps.in/index.php/recruitment/) website.  
This script automates the extraction of **recruitment notifications**, saving key details into a structured CSV file using **Pandas**.

---

## 🚀 Overview

The scraper fetches and parses the IBPS Recruitment page to extract:

- ✅ **Job Title**  
- ✅ **Location** (if available)  
- ✅ **Post/Publish Date**  
- ✅ **Link** to detailed job description  

It then saves the data in a timestamped CSV file for easy tracking and versioning.

---

## 🧠 Key Features

- Uses **Requests** for fetching web content.
- Parses the HTML using **BeautifulSoup4**.
- Automatically deduplicates job entries by link.
- Outputs a **clean CSV** with timestamped filename.
- Includes logging for transparent execution and debugging.

---

## 🧩 Tech Stack

| Component       | Library / Tool          |
|-----------------|--------------------------|
| Language        | Python 3.10+             |
| HTTP Client     | `requests`               |
| Parser          | `beautifulsoup4`         |
| Data Handling   | `pandas`                 |
| Logging         | `logging` (built-in)     |
| Date/Time Mgmt  | `datetime`               |

---

## 🏗️ Project Structure
```bash
web_scraper/
│
├── scrape_ibps.py # Main scraper script
├── data/ # Output CSV files are stored here
├── requirements.txt # Dependencies
└── README.md # Project documentation
```


---

## ⚙️ Setup Instructions


```bash
1️⃣ Clone the Repository
git clone https://github.com/<your_username>/ibps-scraper.git
cd ibps-scraper

2️⃣ Create & Activate Virtual Environment
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Script
python scrape_ibps.py

📊 Output Example

After running, a CSV file is generated under the data/ directory:
data/
└── ibps_recruitments_2025-11-07_18-49-38.csv

🧾 Logging Output Example
2025-11-07 23:17:19,176 [INFO] Fetching recruitment page: https://www.ibps.in/index.php/recruitment/
2025-11-07 23:17:23,662 [INFO] Extracted 8 raw entries.
2025-11-07 23:17:23,662 [INFO] Deduplicated to 8 unique entries.
2025-11-07 23:17:23,699 [INFO] Saved 8 rows to data\ibps_recruitments_2025-11-07_23-17-23.csv
