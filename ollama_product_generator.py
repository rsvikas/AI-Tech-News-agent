import requests
import json
import logging
import time
import re
from typing import List
import config

logger = logging.getLogger(__name__)

def _extract_json_from_response(content_text: str) -> List[str]:
    """Extract JSON list from Ollama response (handles markdown-wrapped responses)."""
    if not content_text:
        logger.error("Ollama response content is empty.")
        return []

    # Match code block pattern
    code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
    match = re.search(code_block_pattern, content_text, re.DOTALL)

    json_str = match.group(1).strip() if match else content_text.strip()

    try:
        parsed_data = json.loads(json_str)
        if isinstance(parsed_data, list):
            logger.info(f"✅ Successfully parsed JSON with {len(parsed_data)} items.")
            return parsed_data
        else:
            logger.warning("Parsed JSON is not a list.")
            return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON parsing failed: {e}")
        logger.error(f"Raw text: {json_str[:500]}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error while parsing JSON: {e}")
        return []


def generate_product_ideas(use_case_strings: List[str]) -> List[str]:
    """Generate creative product ideas based on a list of use cases."""
    if not use_case_strings:
        logger.info("No use case strings provided, skipping idea generation.")
        return []

    use_cases_str = "\n".join([f"- {uc}" for uc in use_case_strings])
    prompt = config.PRODUCT_IDEA_PROMPT_TEMPLATE.format(use_cases_str=use_cases_str)

    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": 0.5}  # slightly more creative
    }

    url = f"{config.OLLAMA_URL}/api/chat"
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=config.OLLAMA_TIMEOUT)
            logger.debug(f"Request payload: {payload}")
            logger.debug(f"Ollama response status: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                content_text = response_data.get("message", {}).get("content", "")
                product_ideas = _extract_json_from_response(content_text)
                return product_ideas

            elif response.status_code == 404:
                logger.error(f"Model {config.OLLAMA_MODEL} not found. Run: ollama pull {config.OLLAMA_MODEL}")
                return []

            elif response.status_code == 500:
                logger.warning(f"Ollama 500 error (attempt {attempt + 1}). Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
                continue

            else:
                logger.error(f"Ollama API error {response.status_code}: {response.text}")
                return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error("Max retries reached due to network errors.")
                return []

        except Exception as e:
            logger.error(f"Unexpected error during Ollama product idea generation: {e}")
            return []

    logger.error("Failed to get a valid response after retries.")
    return []


if __name__ == "__main__":
    sample_use_cases = [
        "AI-based predictive maintenance for infrastructure projects",
        "Automated document approval workflow using NLP"
    ]
    ideas = generate_product_ideas(sample_use_cases)
    print("Generated Product Ideas:", ideas)
