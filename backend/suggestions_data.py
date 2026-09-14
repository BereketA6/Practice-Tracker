"""
Curated practice suggestions, organized by skill level and type.

Each entry tied to a real song includes "artist" and "search_title" fields
used to look up real metadata (artwork, preview clip) from the iTunes
Search API (see itunes_lookup.py). Pure technique/exercise entries with no
underlying song (e.g. "chromatic warm-up") leave those fields as None.
"""

SUGGESTIONS = [
    # --- BEGINNER ---
    {
        "id": 1,
        "title": "Horse with No Name",
        "search_title": "A Horse with No Name",
        "artist": "America",
        "type": "song",
        "skill_level": "beginner",
        "genre": "folk",
        "description": "Just two chords (Em and D6/F#), great for building strumming-hand rhythm confidence.",
    },
    {
        "id": 2,
        "title": "Chromatic warm-up (1-2-3-4 exercise)",
        "search_title": None,
        "artist": None,
        "type": "technique",
        "skill_level": "beginner",
        "genre": None,
        "description": "One finger per fret across all strings — builds independent finger strength and clean fretting.",
    },
    {
        "id": 3,
        "title": "Knockin' on Heaven's Door",
        "search_title": "Knockin' on Heaven's Door",
        "artist": "Bob Dylan",
        "type": "song",
        "skill_level": "beginner",
        "genre": "rock",
        "description": "Classic G-D-Am-C progression used across hundreds of songs — learning it unlocks a lot of other tunes.",
    },
    {
        "id": 4,
        "title": "Simple travis-picking pattern (thumb + 2 fingers)",
        "search_title": None,
        "artist": None,
        "type": "fingerstyle",
        "skill_level": "beginner",
        "genre": None,
        "description": "Alternating bass note with thumb while picking melody with fingers — the foundation of most fingerstyle playing.",
    },

    # --- INTERMEDIATE ---
    {
        "id": 5,
        "title": "Blackbird",
        "search_title": "Blackbird",
        "artist": "The Beatles",
        "type": "fingerstyle",
        "skill_level": "intermediate",
        "genre": "folk",
        "description": "Full fingerstyle arrangement with a moving bass line — great for independent thumb/finger coordination.",
    },
    {
        "id": 6,
        "title": "Minor pentatonic box 1 licks",
        "search_title": None,
        "artist": None,
        "type": "lick",
        "skill_level": "intermediate",
        "genre": "blues",
        "description": "The most common blues/rock lick shapes — bends, hammer-ons, and pull-offs in one position.",
    },
    {
        "id": 7,
        "title": "Dust in the Wind",
        "search_title": "Dust in the Wind",
        "artist": "Kansas",
        "type": "fingerstyle",
        "skill_level": "intermediate",
        "genre": "rock",
        "description": "Fingerpicked arpeggios across a full chord progression — good next step after simpler travis patterns.",
    },
    {
        "id": 8,
        "title": "12-bar blues turnaround lick",
        "search_title": None,
        "artist": None,
        "type": "lick",
        "skill_level": "intermediate",
        "genre": "blues",
        "description": "The classic descending lick that signals the end of a 12-bar blues progression — used constantly in blues/rock.",
    },
    {
        "id": 9,
        "title": "Little Wing",
        "search_title": "Little Wing",
        "artist": "Jimi Hendrix",
        "type": "song",
        "skill_level": "intermediate",
        "genre": "rock",
        "description": "Chord-melody style with small fills between chords — introduces the idea of playing melody and harmony together.",
    },

    # --- ADVANCED ---
    {
        "id": 10,
        "title": "Classical Gas",
        "search_title": "Classical Gas",
        "artist": "Mason Williams",
        "type": "fingerstyle",
        "skill_level": "advanced",
        "genre": "instrumental",
        "description": "Fast, complex fingerstyle piece with rapid position shifts — a serious technical benchmark piece.",
    },
    {
        "id": 11,
        "title": "Sweep-picked arpeggios (3-string major/minor)",
        "search_title": None,
        "artist": None,
        "type": "technique",
        "skill_level": "advanced",
        "genre": None,
        "description": "Economy picking across arpeggio shapes — foundational for neoclassical/shred styles.",
    },
    {
        "id": 12,
        "title": "Cliffs of Dover",
        "search_title": "Cliffs of Dover",
        "artist": "Eric Johnson",
        "type": "lick",
        "skill_level": "advanced",
        "genre": "instrumental",
        "description": "Fast pentatonic runs with legato and picking hybrid technique — a well-known technical showcase lick.",
    },
    {
        "id": 13,
        "title": "Jazz ii-V-I comping voicings",
        "search_title": None,
        "artist": None,
        "type": "technique",
        "skill_level": "advanced",
        "genre": "jazz",
        "description": "Movable chord voicings over the most common jazz progression — essential for jazz rhythm playing.",
    },
]


def get_suggestions(skill_level=None, genre=None, session_type=None, search=None):
    """Filter the suggestion list by any combination of skill_level, genre, type, and a free-text search on title."""
    results = SUGGESTIONS

    if skill_level:
        results = [s for s in results if s["skill_level"] == skill_level]
    if genre:
        results = [s for s in results if s["genre"] == genre]
    if session_type:
        results = [s for s in results if s["type"] == session_type]
    if search:
        term = search.lower()
        results = [s for s in results if term in s["title"].lower()]

    return results
