AI-Tech-News-Agent

An AI-powered autonomous agent that automatically:
- Scrapes the latest technology and AI news from selected sources  
- Extracts practical AI use cases from each article  
- Generates enterprise-level product ideas from those use cases  
- Emails a daily report to your inbox  

Features

| Function | Description |
|-----------|--------------|
| Scraper | Collects the latest AI and tech-related articles from multiple news feeds |
| Use Case Extraction | Uses an LLM to identify specific, actionable AI or automation use cases |
| Product Idea Generation | Translates those use cases into potential enterprise product ideas |
| Scheduler | Runs automatically every day or at a custom interval |
| Email Notifier | Sends a formatted report with all findings to selected recipients |
| Logs & Configs | Fully configurable through `config.py` with detailed logs |


Project Structure

AI-Tech-News-agent/
│
├── config.py  Configuration settings and LLM prompts
├── main.py  Main orchestrator that runs the pipeline
├── scraper.py  Collects and filters AI-related news
├── ollama_processor.py  Extracts use cases from article text
├── ollama_product_generator.py Generates product ideas from use cases
├── notifier.py  Sends summary email
├── scheduler.py  Handles task scheduling
├── requirements.txt  Python dependencies
├── LICENSE  MIT License
└── README.md  Project documentation


 Installation

 1. Clone the Repository
    git clone https://github.com/rsvikas/AI-Tech-News-agent.git
    cd AI-Tech-News-agent
2. Create Virtual Environment
    python -m venv venv
    source venv/bin/activate    For Mac/Linux
    venv\Scripts\activate       For Windows
3. Install Dependencies
    pip install -r requirements.txt
4. Set Up Environment Variables
  Create a .env file in the project folder with:
    EMAIL_USER=youremail@example.com
    EMAIL_PASS=yourpassword
    EMAIL_TO=recipient1@example.com,recipient2@example.com

Running the Agent
Manual Run
  python main.py
Scheduled (Automatic) Run
  If you enabled scheduler.py, the agent runs automatically at defined intervals.
  You can also set it up as a GitHub Action (see below).

Model Settings
By default, the project uses a local Ollama model (gemma3:4b) for both use case and product idea generation.
You can change this in config.py:
  OLLAMA_MODEL = "mistral:7b"    or "phi3:mini" for faster performance
  For remote APIs (like OpenAI or Gemini), you can modify the LLM call to use an API endpoint instead.

Architecture Overview

        ┌────────────┐
        │  Scraper   │
        └─────┬──────┘
              │
              ▼
        ┌────────────┐
        │  Use Case  │   → Extracts AI/automation ideas
        │  Extractor │
        └─────┬──────┘
              │
              ▼
        ┌────────────┐
        │  Product   │   → Suggests enterprise-grade features
        │  Generator │
        └─────┬──────┘
              │
              ▼
        ┌────────────┐
        │  Notifier  │   → Sends summarized email
        └────────────┘
Learnings & Insights
This project shows how:
  Agents can automate content analysis using local LLMs
  The biggest challenge is LLM inference on limited hardware
  Solutions include chunking, summarization, and prompt optimization
  Combining scraping + reasoning + reporting makes a powerful autonomous workflow

License
MIT License © 2025 rsvikas

Future Enhancements
  Hybrid local + cloud model fallback
  Smarter caching and incremental scraping
  Auto-publish to a Notion dashboard or website

Credits
Developed by Vikas R.S.
A thinker, philosopher, and business analyst passionate about automation and real-world AI use cases.

GitHub Workflow (Daily Automation)

Create a new file at:
.github/workflows/daily-agent.yml

And add this 👇

```
name: Daily AI Tech News Agent

on:
  schedule:
    - cron: "0 4 * * *"   Runs every day at 4 AM UTC
  workflow_dispatch:       Allow manual trigger

jobs:
  run-agent:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run AI News Agent
        env:
          EMAIL_USER: ${{ secrets.EMAIL_USER }}
          EMAIL_PASS: ${{ secrets.EMAIL_PASS }}
          EMAIL_TO: ${{ secrets.EMAIL_TO }}
        run: |
          python main.py
```

Then go to your repo → Settings → Secrets and Variables → Actions,
and add:
- EMAIL_USER
- EMAIL_PASS
- EMAIL_TO

This will allow GitHub to run your agent automatically every day and send the email report — all hosted on GitHub’s infrastructure (no local machine needed).

