import os
from dotenv import load_dotenv

load_dotenv()

# ================================
# Email Settings
# ================================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_TO = os.getenv("EMAIL_TO")

# ================================
# Logging
# ================================
LOG_FILE = "news_agent.log"
LOG_LEVEL = "INFO"

# ================================
# Scraper
# ================================
MAX_ARTICLES_PER_SOURCE = 5
REQUEST_TIMEOUT = 10
RATE_LIMIT_DELAY = 3

# ================================
# LLM Settings
# ================================
MAX_RETRIES = 3
OLLAMA_URL = "http://localhost:11434"  # Base Ollama URL
OLLAMA_HOST = OLLAMA_URL
OLLAMA_MODEL = "gemma3:4b"
OLLAMA_TIMEOUT = 300  # seconds

# ================================
# Data Limits
# ================================
MIN_CONTENT_LENGTH = 50  # Minimum characters to analyze

# ================================
# AI PROMPTS
# ================================

USE_CASE_PROMPT_TEMPLATE = """
You are an expert business analyst specializing in AI-driven enterprise transformation.

Analyze the following article and extract **specific, actionable use cases** related to AI, automation, or digital transformation that could benefit large enterprises (like Aurigo’s products).

Title: {title}

Content:
{content}

Instructions:
- Each use case should describe a specific problem and a possible AI/tech-based solution.
- Focus on **practical, implementable use cases**.
- Avoid generic or vague statements.
- Return only a JSON list of strings.
- Example output:
["AI-powered contract validation", "Predictive maintenance using IoT data", "Automated invoice classification"]

Return ONLY the JSON list.
"""

PRODUCT_IDEA_PROMPT_TEMPLATE = """
You are a creative product manager at Aurigo, an enterprise software company.

Based on the following AI/tech use cases, suggest **product ideas or features** that Aurigo could build or integrate.

Use Cases:
{use_cases_str}

Guidelines:
- Each idea should be specific, practical, and enterprise-relevant.
- Focus on AI, automation, predictive analytics, or process optimization.
- Avoid repeating use cases; instead, translate them into possible **product ideas**.
- Do NOT include any explanation or preface.
- Return ONLY a JSON array of concise product ideas.

Example:
["AI-driven project risk analyzer", "Automated compliance audit engine", "Intelligent document approval assistant"]
"""
