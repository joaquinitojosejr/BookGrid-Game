import os
import json
import random

# Built-in Master Seed Library (Acts as a Bulletproof Fallback if API fails)
FALLBACK_MASTER_LIBRARY = [
    {
        "en": { "quote": "Real courage is when you know you're licked before you begin.", "author": "Harper Lee", "title": "To Kill a Mockingbird", "published": "July 11, 1960", "trivia": "Spoken by Atticus Finch in Chapter 11.", "category": "Classic Literature", "subCategory": "Fiction" },
        "es": { "quote": "El verdadero valor es cuando sabes que estás vencido antes de empezar.", "author": "Harper Lee", "title": "Matar a un ruiseñor", "published": "11 de julio de 1960", "trivia": "Dicho por Atticus Finch en el capítulo 11.", "category": "Literatura Clásica", "subCategory": "Ficción" }
    },
    {
        "en": { "quote": "Not all those who wander are lost.", "author": "J.R.R. Tolkien", "title": "The Fellowship of the Ring", "published": "July 29, 1954", "trivia": "Part of Bilbo Baggins' poem regarding Aragorn.", "category": "Fantasy", "subCategory": "Fiction" },
        "es": { "quote": "No todos los que vagan están perdidos.", "author": "J.R.R. Tolkien", "title": "La Comunidad del Anillo", "published": "29 de julio de 1954", "trivia": "Parte del poema de Bilbo Bolsón sobre Aragorn.", "category": "Fantasía", "subCategory": "Ficción" }
    },
    {
        "en": { "quote": "In a village of La Mancha, the name of which I have no desire to call to mind.", "author": "Miguel de Cervantes", "title": "Don Quixote", "published": "1605", "trivia": "The iconic opening line of Cervantes' masterpiece.", "category": "Classic Literature", "subCategory": "Fiction" },
        "es": { "quote": "En un lugar de la Mancha, de cuyo nombre no quiero acordarme.", "author": "Miguel de Cervantes", "title": "Don Quijote de la Mancha", "published": "1605", "trivia": "La famosísima frase inicial de Cervantes.", "category": "Literatura Clásica", "subCategory": "Ficción" }
    },
    {
        "en": { "quote": "God does not play dice with the universe.", "author": "Albert Einstein", "title": "Letter to Max Born", "published": "1926", "trivia": "Einstein's objection to quantum probability.", "category": "Science", "subCategory": "Physics" },
        "es": { "quote": "Dios no juega a los dados con el universo.", "author": "Albert Einstein", "title": "Carta a Max Born", "published": "1926", "trivia": "La objeción de Einstein a la probabilidad cuántica.", "category": "Ciencia", "subCategory": "Física" }
    },
    {
        "en": { "quote": "Let us cut the living child in two, and give half to the one, and half to the other.", "author": "King Solomon", "title": "First Book of Kings", "published": "c. 950 BC", "trivia": "Solomon's famous judgment of maternal wisdom.", "category": "Scripture", "subCategory": "Ancient History" },
        "es": { "quote": "Partid en dos al niño vivo, y dad la mitad a la una y la mitad a la otra.", "author": "Rey Salomón", "title": "Primer Libro de los Reyes", "published": "c. 950 a. C.", "trivia": "El célebre juicio de Salomón sobre la sabiduría materna.", "category": "Escritura", "subCategory": "Historia Antigua" }
    },
    {
        "en": { "quote": "Ask not what your country can do for you – ask what you can do for your country.", "author": "John F. Kennedy", "title": "Inaugural Address", "published": "January 20, 1961", "trivia": "Call to civic service in American history.", "category": "Speeches", "subCategory": "Political Oratory" },
        "es": { "quote": "No preguntes qué puede hacer tu país por ti; pregúntate qué puedes hacer tú por tu país.", "author": "John F. Kennedy", "title": "Discurso Inaugural", "published": "20 de enero de 1961", "trivia": "Inspirador llamado al servicio cívico.", "category": "Discursos", "subCategory": "Oratoria Política" }
    },
    {
        "en": { "quote": "He who has a why to live can bear almost any how.", "author": "Friedrich Nietzsche", "title": "Twilight of the Idols", "published": "1889", "trivia": "Found in Maxims and Arrows.", "category": "Philosophy", "subCategory": "Non-Fiction" },
        "es": { "quote": "Quien tiene un porqué para vivir puede soportar casi cualquier cómo.", "author": "Friedrich Nietzsche", "title": "El crepúsculo de los ídolos", "published": "1889", "trivia": "Encontrado en Máximas y flechas.", "category": "Filosofía", "subCategory": "No Ficción" }
    }
]

def generate_via_ai(api_key):
    from google import genai
    client = genai.Client(api_key=api_key)
    
    prompt = """
    Generate a valid JSON array containing EXACTLY 7 NEW, unique literary quotes spanning classical literature, philosophy, science, scripture, speeches, and sci-fi.
    Each quote MUST be provided in both English ('en') and Spanish ('es').
    
    Strict JSON structure (Return ONLY a raw JSON array of objects, no markdown formatting):
    [
      {
        "en": { "quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..." },
        "es": { "quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..." }
      }
    ]
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    raw_text = response.text.strip()
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    if raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()
        
    return json.loads(raw_text)

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    output_path = os.path.join(os.path.dirname(__file__), '..', 'quotes.json')
    
    # 1. Load existing quotes.json so we never lose historical progress
    existing_data = {"daily": [], "presets": {}}
    if os.path.exists(output_path):
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                if isinstance(loaded, dict) and "daily" in loaded:
                    existing_data = loaded
        except Exception as e:
            print(f"Warning: Could not read existing quotes.json ({e}). Starting fresh archive.")

    new_quotes = []
    if api_key:
        try:
            print("Attempting AI quote generation via Gemini API...")
            new_quotes = generate_via_ai(api_key)
            print(f"Successfully generated {len(new_quotes)} new AI quotes.")
        except Exception as e:
            print(f"AI Generation failed ({e}). Skipping AI injection for this cycle.")
    else:
        print("No GEMINI_API_KEY found in environment secrets. Skipping automated fetch.")

    # 2. Append new quotes safely, avoiding exact duplicate quotes
    existing_quotes_texts = {item['en']['quote'] for item in existing_data["daily"]}
    
    added_count = 0
    for q in new_quotes:
        if 'en' in q and 'quote' in q['en']:
            if q['en']['quote'] not in existing_quotes_texts:
                existing_data["daily"].append(q)
                existing_quotes_texts.add(q['en']['quote'])
                added_count += 1

    # If the file was completely empty, seed it with fallback items first
    if not existing_data["daily"]:
        existing_data["daily"] = FALLBACK_MASTER_LIBRARY
        added_count = len(FALLBACK_MASTER_LIBRARY)

    # Rebuild simple presets dynamically from the massive cumulative pool
    existing_data["presets"] = {
        "philosophy": [q for q in existing_data["daily"] if q['en'].get('category') == 'Philosophy'],
        "science": [q for q in existing_data["daily"] if q['en'].get('category') == 'Science'],
        "scripture": [q for q in existing_data["daily"] if q['en'].get('category') == 'Scripture'],
        "speech": [q for q in existing_data["daily"] if q['en'].get('category') == 'Speeches'],
        "scifi": [q for q in existing_data["daily"] if q['en'].get('category') == 'Sci-Fi' or q['en'].get('category') == 'Fantasy'],
        "classic": [q for q in existing_data["daily"] if 'Classic' in q['en'].get('category', '')]
    }

    # Fallback for empty categories so UI dropdowns don't break
    for cat in ["philosophy", "science", "scripture", "speech", "scifi", "classic"]:
        if not existing_data["presets"][cat]:
            existing_data["presets"][cat] = [existing_data["daily"][0]]

    # 3. Save the cumulative expanded file back out
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully updated archive! Total cumulative quotes in pool: {len(existing_data['daily'])} (Added {added_count} new ones). Saved to: {output_path}")

if __name__ == "__main__":
    main()
