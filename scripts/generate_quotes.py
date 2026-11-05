import os
import json
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is missing.")
        exit(1)

    # Initialize the Google GenAI client with a strict 30-second timeout (in milliseconds)
    # This prevents the script from hanging indefinitely if network traffic stalls.
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=30000)
    )

    # File path for quotes.json (relative to scripts/ directory)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    quotes_path = os.path.join(current_dir, "../quotes.json")

    # Load existing quotes archive safely
    existing_data = {"daily": [], "presets": {}}
    if os.path.exists(quotes_path):
        try:
            with open(quotes_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    existing_data = json.loads(content)
                else:
                    print("Warning: quotes.json is empty. Starting fresh archive.")
        except Exception as e:
            print(f"Warning: Could not read existing quotes.json ({e}). Starting fresh archive.")
    else:
        print("Notice: quotes.json not found. Creating a new one.")

    # Prompt instructing Gemini to generate fresh, unique quotes in English and Spanish
    prompt_text = (
        "Generate 7 unique, profound, and famous literary, philosophical, scientific, "
        "or historical quotes. Each quote must include both English and Spanish translations, "
        "along with the author, book title/source, publication date, a short trivia/context note, "
        "category, and subCategory. "
        "Format the output strictly as a JSON object matching this exact structure, with no markdown code blocks around it: "
        '{"daily": [{"en": {"quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..."}, '
        '"es": {"quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..."}}]}'
    )

    print("Attempting AI quote generation via Gemini API...")
    
    max_retries = 5
    new_quotes = []

    for attempt in range(max_retries):
        try:
            print(f"-> Sending request to Gemini (Attempt {attempt + 1}/{max_retries})...")
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt_text
            )
            
            raw_text = response.text.strip()
            # Clean up potential markdown formatting if the model wraps it
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            parsed_json = json.loads(raw_text)
            if "daily" in parsed_json and isinstance(parsed_json["daily"], list):
                new_quotes = parsed_json["daily"]
                break  # Success! Exit loop.
                
        except (APIError, TimeoutError, Exception) as e:
            error_str = str(e)
            print(f"⚠️ Attempt {attempt + 1} failed: {error_str}")
            
            # Check if it's a retryable error (503, UNAVAILABLE, or timeout/socket stall)
            if "503" in error_str or "UNAVAILABLE" in error_str or "timeout" in error_str.lower():
                if attempt < max_retries - 1:
                    sleep_time = (attempt + 1) * 5  # 5s, 10s, 15s, 20s backoff delay
                    print(f"Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    continue
            
            # If retries ran out or it's a permanent error, break out
            if attempt == max_retries - 1:
                print("Max retry attempts reached. Skipping AI injection for this cycle.")
            break

    # Accumulate new quotes into the daily pool without wiping historical entries
    if new_quotes:
        if "daily" not in existing_data or not isinstance(existing_data["daily"], list):
            existing_data["daily"] = []
        
        existing_data["daily"].extend(new_quotes)
        print(f"Successfully fetched {len(new_quotes)} new quotes!")
    else:
        print("Skipping AI injection for this cycle due to persistent server unavailability.")

    # Save cumulative pool back to quotes.json
    os.makedirs(os.path.dirname(quotes_path), exist_ok=True)
    with open(quotes_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    total_count = len(existing_data.get("daily", []))
    print(f"Successfully updated archive! Total cumulative quotes in pool: {total_count}. Saved to: {quotes_path}")

if __name__ == "__main__":
    main()
