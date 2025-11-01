import logging
import requests
import time
import json
import re
from typing import List, Dict, Optional
import config # Import the config module

logger = logging.getLogger(__name__)

class OllamaProcessor:
    def __init__(self, base_url: str = None):
        # Use the base URL from config (e.g., http://localhost:11434)
        # The script will append /api/chat internally
        self.base_url = base_url or config.OLLAMA_HOST # Use base URL from config if not provided
        # Read model name from config
        self.model_name = config.OLLAMA_MODEL # Now reads from config.OLLAMA_MODEL

    def _make_request(self, payload: Dict) -> Optional[Dict]:
        """Make a request to the Ollama API."""
        # Construct the full URL for the chat endpoint
        url = f"{self.base_url}/api/chat"
        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, timeout=config.OLLAMA_TIMEOUT) # Use timeout from config
                logger.debug(f"Ollama API request: {payload}")
                logger.debug(f"Ollama API response status: {response.status_code}")
                logger.debug(f"Ollama API response text: {response.text}")

                if response.status_code == 200:
                    try:
                        return response.json()
                    except requests.exceptions.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON response from Ollama: {e}")
                        logger.error(f"Response text was: {response.text}")
                        return None
                elif response.status_code == 404:
                     logger.error(f"Model {self.model_name} not found by Ollama. Please check the model name and ensure it's pulled.")
                     return None
                elif response.status_code == 500:
                    logger.error(f"Ollama error 500 on attempt {attempt + 1}: {response.text}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        logger.error("Max retries reached for Ollama 500 error.")
                        return None
                else:
                    logger.error(f"Ollama API error {response.status_code}: {response.text}")
                    return None

            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached due to request errors.")
                    return None

        return None

    def _extract_json_from_response(self, content_text: str) -> List[str]:
        """
        Extract the JSON list from the Ollama response content.
        Handles responses wrapped in markdown code blocks.
        """
        if not content_text:
            logger.error("Ollama response content is empty.")
            return []

        # Try to find a JSON array in the response, potentially within a markdown code block
        # Look for code blocks with optional language specifier
        code_block_pattern = r"```(?:json)?\s*\n?(.*?)\n?```"
        match = re.search(code_block_pattern, content_text, re.DOTALL)

        json_str = ""
        if match:
            # Extract the content inside the code block
            json_str = match.group(1).strip()
            logger.debug(f"Extracted JSON string from code block: {json_str}")
        else:
            # If no code block is found, assume the entire response is the JSON string
            json_str = content_text.strip()
            logger.debug(f"No code block found, using full response as JSON string: {json_str}")

        if not json_str:
            logger.error("No content found inside potential JSON code block.")
            return []

        try:
            # Attempt to parse the extracted string as JSON
            parsed_data = json.loads(json_str)
            if isinstance(parsed_data, list):
                logger.info(f"Successfully parsed JSON list from Ollama response.")
                return parsed_data
            else:
                logger.warning(f"Parsed JSON data is not a list: {parsed_data}")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse extracted string as JSON: {e}")
            logger.error(f"Extracted string was: {json_str}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during JSON extraction/parsing: {e}")
            return []


    def extract_use_cases(self, content: str, title: str = "") -> List[str]:
        """Extract use cases from content using the model specified in config."""
        if len(content.strip()) < config.MIN_CONTENT_LENGTH: # Use minimum length from config
            logger.warning(f"Content too short ({len(content)} chars), skipping")
            return []

        # Use the prompt template from config
        prompt = config.USE_CASE_PROMPT_TEMPLATE.format(title=title, content=content)

        payload = {
            "model": self.model_name, # Uses the model name from config
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False, # Ensure response is not streamed
            "options": {
                "temperature": 0.1 # Lower temperature for more consistent results
            }
        }

        response_data = self._make_request(payload)

        if response_data:
            try:
                # Access the 'message' -> 'content' field from the response object
                content_text = response_data.get('message', {}).get('content', '')
                # Use the new helper method to extract JSON
                use_cases = self._extract_json_from_response(content_text)
                return use_cases

            except Exception as e:
                logger.error(f"Unexpected error processing Ollama response: {e}")
                return []
        else:
            logger.error("No response received from Ollama API.")
            return []

    def generate_product_ideas(self, use_cases: List[str]) -> List[str]:
        """Generate product ideas based on use cases using the model specified in config."""
        if not use_cases:
            logger.info("No use cases provided, skipping product idea generation.")
            return []

        # Use the prompt template from config
        use_cases_str = "\n".join([f"- {uc}" for uc in use_cases])
        prompt = config.PRODUCT_IDEA_PROMPT_TEMPLATE.format(use_cases_str=use_cases_str)

        payload = {
            "model": self.model_name, # Uses the model name from config
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
             "options": {
                "temperature": 0.3 # Slightly higher for creativity, but still controlled
            }
        }

        response_data = self._make_request(payload)

        if response_data:
            try:
                # Access the 'message' -> 'content' field from the response object
                content_text = response_data.get('message', {}).get('content', '')
                # Use the new helper method to extract JSON
                product_ideas = self._extract_json_from_response(content_text)
                return product_ideas

            except Exception as e:
                logger.error(f"Unexpected error processing product idea response: {e}")
                return []
        else:
            logger.error("No response received from Ollama API for product ideas.")
            return []

# Example usage (for testing this module independently):
if __name__ == "__main__":
    processor = OllamaProcessor()
    sample_content = "AI is transforming businesses by automating routine tasks and providing deeper insights from data."
    sample_title = "AI Transformation"
    use_cases = processor.extract_use_cases(sample_content, sample_title)
    print("Extracted Use Cases:", use_cases)
    if use_cases:
        ideas = processor.generate_product_ideas(use_cases)
        print("Generated Product Ideas:", ideas)
