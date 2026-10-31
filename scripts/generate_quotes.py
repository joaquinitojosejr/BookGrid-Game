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

FALLBACK_PRESETS = {
    "philosophy": [FALLBACK_MASTER_LIBRARY[6]],
    "science": [FALLBACK_MASTER_LIBRARY[3]],
    "scripture": [FALLBACK_MASTER_LIBRARY[4]],
    "speech": [FALLBACK_MASTER_LIBRARY[5]],
    "scifi": [FALLBACK_MASTER_LIBRARY[1]],
    "classic": [FALLBACK_MASTER_LIBRARY[0], FALLBACK_MASTER_LIBRARY[2]]
}

def generate_via_ai(api_key):
    from google import genai
    client = genai.Client(api_key=api_key)
    
    prompt = """
    Generate a valid JSON object containing 7 unique quotes spanning classical literature, philosophy, science, scripture, speeches, and sci-fi.
    Each quote MUST be provided in both English ('en') and Spanish ('es').

    Strict JSON structure:
    {
      "daily": [
        {
          "en": { "quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..." },
          "es": { "quote": "...", "author": "...", "title": "...", "published": "...", "trivia": "...", "category": "...", "subCategory": "..." }
        }
      ],
      "presets": {
        "philosophy": [],
        "science": [],
        "scripture": [],
        "speech": [],
        "scifi": [],
        "classic": []
      }
    }
    Include at least 1-2 items inside each category in presets. Output valid raw JSON only without markdown formatting blocks.
    """
    
    response = client.models.generate_content(
        model='gemini-2.0-flash',
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

def generate_via_fallback():
    print("Using built-in static seed library fallback...")
    daily_selection = random.sample(FALLBACK_MASTER_LIBRARY, min(7, len(FALLBACK_MASTER_LIBRARY)))
    return {
        "daily": daily_selection,
        "presets": FALLBACK_PRESETS
    }

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    payload = None

    if api_key:
        try:
            print("Attempting AI quote generation via Gemini API...")
            payload = generate_via_ai(api_key)
            print("Successfully generated AI quotes payload.")
        except Exception as e:
            print(f"AI Generation failed ({e}). Falling back to static seeds.")
            payload = generate_via_fallback()
    else:
        print("No GEMINI_API_KEY found. Falling back to static seed pool.")
        payload = generate_via_fallback()

    output_path = os.path.join(os.path.dirname(__file__), '..', 'quotes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        
    print(f"Successfully created payload at: {output_path}")

if __name__ == "__main__":
    main()

