# ============================================================
# Study Buddy Quest 🧠
# A fun, interactive quiz app for students!
# Built for the Presidential AI Challenge
# ============================================================

import streamlit as st
import os
import re
import random
import time
from io import BytesIO
from gtts import gTTS

# ============================================================
# PAGE CONFIGURATION - Must be first Streamlit command
# ============================================================
st.set_page_config(
    page_title="Study Buddy Quest 🧠",
    page_icon="🧠",
    layout="centered"
)

# ============================================================
# API KEY VALIDATION
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("""
    ## 🔑 API Key Missing!
    
    This app needs a Google Gemini API key to generate quizzes.
    
    **To fix this:**
    1. Get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
    2. Add it to your Replit Secrets as `GEMINI_API_KEY`
    3. Refresh this page
    
    *Need help? Ask your teacher or check the Replit docs!*
    """)
    st.stop()

# Import and configure Gemini only after validating API key
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
defaults = {
    "quiz_content": None,
    "quiz_questions_only": None,
    "parsed_questions": [],
    "quiz_generated": False,
    "answers_submitted": False,
    "correct_answers": [],
    "explanations": [],
    "user_answers": [],
    "score": 0,
    "current_topic": "",
    "total_score": 0,
    "quizzes_completed": 0,
    "perfect_scores": 0,
    "weak_topics": [],
    "wrong_questions": [],
    "badges": set(),
    "generation_error": None,
    "dark_mode": True,
    "quiz_history": [],
    "quiz_length": 5,
    "font_size": "medium",
    "selected_category": None,
    "sound_enabled": True,
    "timed_mode": False,
    "quiz_start_time": None,
    "time_per_question": 30,
    "study_notes": None,
    "high_contrast": False,
    "reduce_animations": False,
    "default_timed_mode": False,
    "default_quiz_length": 5,
    "compact_mode": False,
}

# ============================================================
# SUBJECT CATEGORIES (Grade-dependent for school topics)
# ============================================================
DEFAULT_CATEGORIES = [
    "Any Topic",
    "Science",
    "History", 
    "Math",
    "Language Arts",
    "Geography",
    "Art & Music",
    "Technology",
    "Sports & Games",
    "Animals & Nature",
    "Fun Facts",
]

GRADE_CATEGORIES = {
    "Pre-K": ["Any Topic", "Colors & Shapes", "Animals", "Numbers 1-10", "ABCs", "Nature", "My Body", "Seasons"],
    "Kindergarten": ["Any Topic", "Phonics", "Counting", "Animals", "Weather", "Community Helpers", "Shapes", "Colors"],
    "1st Grade": ["Any Topic", "Reading", "Addition & Subtraction", "Plants", "Animals", "Maps", "Time & Calendar"],
    "2nd Grade": ["Any Topic", "Reading Comprehension", "Math Facts", "Life Cycles", "Geography", "Money", "Measurement"],
    "3rd Grade": ["Any Topic", "Multiplication", "Fractions", "Earth Science", "US States", "Grammar", "Solar System"],
    "4th Grade": ["Any Topic", "Division", "Decimals", "US History", "Ecosystems", "Writing", "Electricity"],
    "5th Grade": ["Any Topic", "Fractions & Decimals", "American Revolution", "Human Body", "Grammar", "Ancient Civilizations"],
    "6th Grade": ["Any Topic", "Pre-Algebra", "World History", "Earth Science", "Literature", "Geography"],
    "7th Grade": ["Any Topic", "Algebra Basics", "Life Science", "World Geography", "Writing Skills", "Civics"],
    "8th Grade": ["Any Topic", "Algebra", "Physical Science", "US History", "Literature Analysis", "Government"],
    "9th Grade": ["Any Topic", "Algebra I", "Biology", "World History", "English", "Physical Science"],
    "10th Grade": ["Any Topic", "Geometry", "Chemistry", "World Literature", "US History", "Health"],
    "11th Grade": ["Any Topic", "Algebra II", "Physics", "American Literature", "US Government", "Psychology"],
    "12th Grade": ["Any Topic", "Pre-Calculus", "AP Sciences", "British Literature", "Economics", "Philosophy"],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Ensure timed_mode respects default_timed_mode preference on fresh sessions
if 'timed_mode_initialized' not in st.session_state:
    st.session_state.timed_mode = st.session_state.get('default_timed_mode', False)
    st.session_state.timed_mode_initialized = True

# ============================================================
# BADGE SYSTEM
# ============================================================
BADGES = {
    "first_quiz": {"emoji": "🎯", "name": "First Quiz!", "desc": "Complete your first quiz"},
    "five_quizzes": {"emoji": "📚", "name": "Quiz Explorer", "desc": "Complete 5 quizzes"},
    "ten_quizzes": {"emoji": "🏅", "name": "Quiz Master", "desc": "Complete 10 quizzes"},
    "points_50": {"emoji": "⭐", "name": "50 Points!", "desc": "Earn 50 total points"},
    "points_100": {"emoji": "🌟", "name": "100 Points!", "desc": "Earn 100 total points"},
    "points_200": {"emoji": "💫", "name": "200 Points!", "desc": "Earn 200 total points"},
    "points_500": {"emoji": "🔥", "name": "500 Points!", "desc": "Earn 500 total points"},
    "perfect_score": {"emoji": "💯", "name": "Perfect Score!", "desc": "Get 5/5 on a quiz"},
    "three_perfects": {"emoji": "🏆", "name": "Perfectionist", "desc": "Get 3 perfect scores"},
    "level_5": {"emoji": "👑", "name": "Level 5 Hero", "desc": "Reach Level 5"},
}

ENCOURAGEMENTS = [
    "You're leveling up your brain! 🧠✨",
    "Every question makes you smarter! 💪",
    "Knowledge is your superpower! ⚡",
    "You've got this! 🚀",
    "Learning looks good on you! 😎",
    "Future genius in the making! 🌟",
]

LOADING_MESSAGES = [
    "🧠 Warming up the brain cells...",
    "📚 Gathering knowledge nuggets...",
    "✨ Sprinkling in some fun...",
    "🎯 Crafting perfect questions...",
    "🔥 Almost ready to challenge you...",
]


def check_and_award_badges():
    """Check and award any new badges based on current stats."""
    new_badges = []
    
    badge_conditions = [
        ("first_quiz", st.session_state.quizzes_completed >= 1),
        ("five_quizzes", st.session_state.quizzes_completed >= 5),
        ("ten_quizzes", st.session_state.quizzes_completed >= 10),
        ("points_50", st.session_state.total_score >= 50),
        ("points_100", st.session_state.total_score >= 100),
        ("points_200", st.session_state.total_score >= 200),
        ("points_500", st.session_state.total_score >= 500),
        ("perfect_score", st.session_state.perfect_scores >= 1),
        ("three_perfects", st.session_state.perfect_scores >= 3),
        ("level_5", calculate_level(st.session_state.total_score) >= 5),
    ]
    
    for badge_id, condition in badge_conditions:
        if condition and badge_id not in st.session_state.badges:
            st.session_state.badges.add(badge_id)
            new_badges.append(badge_id)
    
    return new_badges


def calculate_level(total_points: int) -> int:
    """Calculate player level based on total points."""
    return 1 + (total_points // 50)


def get_points_for_next_level(total_points: int) -> tuple:
    """Get progress toward next level."""
    current_level = calculate_level(total_points)
    points_at_current_level_start = (current_level - 1) * 50
    points_into_level = total_points - points_at_current_level_start
    return points_into_level, 50


def get_level_title(level: int) -> str:
    """Get fun title based on level."""
    titles = {
        1: "Curious Beginner 🌱",
        2: "Knowledge Seeker 📖",
        3: "Quiz Explorer 🗺️",
        4: "Brain Builder 🧱",
        5: "Study Champion 🏅",
        6: "Wisdom Warrior ⚔️",
        7: "Master Learner 🎓",
        8: "Knowledge Knight 🛡️",
        9: "Quiz Legend 🌟",
        10: "Ultimate Genius 👑"
    }
    if level >= 10:
        return titles[10]
    return titles.get(level, f"Level {level} Hero 🦸")


def strip_answers_from_quiz(quiz_text: str) -> str:
    """Remove answers and explanations from quiz text."""
    quiz_text = re.sub(r'✅\s*\*\*Correct Answer:.*?\*\*\s*\n?', '', quiz_text)
    quiz_text = re.sub(r'>\s*💡\s*\*\*Explanation:\*\*.*?(?=\n\n|---|\n###|$)', '', quiz_text, flags=re.DOTALL)
    quiz_text = re.sub(r'##\s*🎊\s*Quiz Complete!.*$', '', quiz_text, flags=re.DOTALL)
    quiz_text = re.sub(r'\n{3,}', '\n\n', quiz_text)
    return quiz_text.strip()


def get_random_encouragement():
    """Get a random encouraging message."""
    return random.choice(ENCOURAGEMENTS)


def get_emoji_for_answer(answer_text: str) -> str:
    """Get a descriptive emoji based on answer content."""
    text = answer_text.lower()
    
    emoji_keywords = {
        "🏛️": ["roman", "rome", "empire", "ancient", "greek", "greece", "egypt", "pyramid", "pharaoh", "temple", "civilization"],
        "🌍": ["earth", "world", "globe", "planet", "continent", "geography", "country", "nation"],
        "🌊": ["ocean", "sea", "water", "wave", "marine", "fish", "whale", "dolphin", "beach", "river", "lake"],
        "🌋": ["volcano", "lava", "eruption", "magma", "tectonic"],
        "🔬": ["science", "experiment", "laboratory", "research", "scientist", "microscope", "cell", "bacteria"],
        "⚗️": ["chemistry", "chemical", "element", "atom", "molecule", "compound", "reaction"],
        "🧬": ["dna", "gene", "genetic", "biology", "evolution", "species"],
        "🔭": ["space", "star", "planet", "galaxy", "universe", "astronaut", "nasa", "telescope", "moon", "sun", "solar", "astronomy"],
        "🚀": ["rocket", "spacecraft", "launch", "mission", "orbit"],
        "🧮": ["math", "number", "calculate", "equation", "formula", "algebra", "geometry", "fraction", "decimal", "percent"],
        "📐": ["angle", "triangle", "square", "rectangle", "circle", "shape", "polygon"],
        "💻": ["computer", "technology", "digital", "software", "internet", "code", "programming", "algorithm"],
        "📱": ["phone", "mobile", "app", "device", "smart"],
        "🎨": ["art", "paint", "draw", "color", "artist", "museum", "sculpture", "creative"],
        "🎵": ["music", "song", "melody", "instrument", "orchestra", "band", "rhythm", "note"],
        "📚": ["book", "read", "library", "literature", "author", "novel", "story", "write"],
        "🏰": ["castle", "medieval", "knight", "king", "queen", "royal", "kingdom", "palace"],
        "⚔️": ["war", "battle", "fight", "army", "soldier", "military", "weapon"],
        "🦖": ["dinosaur", "fossil", "prehistoric", "extinct", "jurassic"],
        "🐾": ["animal", "mammal", "wildlife", "zoo", "pet", "dog", "cat", "bird"],
        "🌱": ["plant", "tree", "forest", "flower", "garden", "grow", "seed", "leaf", "nature"],
        "☀️": ["sun", "sunny", "solar", "light", "bright", "heat", "warm", "summer"],
        "❄️": ["ice", "snow", "cold", "winter", "freeze", "arctic", "polar", "glacier"],
        "⚡": ["electric", "energy", "power", "lightning", "current", "voltage", "battery"],
        "🧲": ["magnet", "magnetic", "force", "field", "attract"],
        "🎭": ["theater", "drama", "play", "actor", "performance", "stage"],
        "🏆": ["win", "champion", "victory", "first", "best", "gold", "trophy"],
        "🎮": ["game", "video", "play", "player", "gaming"],
        "⚽": ["soccer", "football", "sport", "ball", "goal", "team"],
        "🏀": ["basketball", "nba", "court", "dunk"],
        "🍎": ["food", "fruit", "apple", "eat", "nutrition", "healthy", "diet"],
        "🧠": ["brain", "think", "mind", "memory", "intelligence", "smart", "learn"],
        "❤️": ["heart", "love", "blood", "pump", "cardiovascular"],
        "🦴": ["bone", "skeleton", "body", "muscle", "organ"],
        "💰": ["money", "economy", "bank", "finance", "dollar", "currency", "trade", "business"],
        "🗳️": ["vote", "election", "government", "president", "congress", "democracy", "political"],
        "📜": ["constitution", "law", "document", "declaration", "rights", "amendment"],
        "🗽": ["america", "american", "usa", "united states", "liberty", "freedom"],
        "🎪": ["circus", "carnival", "fun", "entertainment"],
        "🌈": ["rainbow", "color", "spectrum", "light", "prism"],
    }
    
    for emoji, keywords in emoji_keywords.items():
        for keyword in keywords:
            if keyword in text:
                return emoji
    
    fun_defaults = ["✨", "🎯", "💫", "🌟", "🔮", "💎", "🎲", "🧩"]
    return random.choice(fun_defaults)


def sanitize_topic(topic: str) -> str:
    """Clean and validate topic input."""
    topic = topic.strip()
    topic = re.sub(r'[<>{}|\[\]\\^`]', '', topic)
    return topic[:100] if len(topic) > 100 else topic


def parse_quiz_answers(quiz_text: str) -> tuple:
    """Parse correct answers and explanations from quiz text."""
    correct_answers = []
    explanations = []
    
    answer_pattern = r"✅\s*\*\*Correct Answer:\s*([A-Da-d])\s*\*\*"
    explanation_pattern = r">\s*💡\s*\*\*Explanation:\*\*\s*(.+?)(?=\n\n|---|\n###|$)"
    
    answer_matches = re.findall(answer_pattern, quiz_text, re.IGNORECASE)
    for match in answer_matches:
        correct_answers.append(match.upper())
    
    explanation_matches = re.findall(explanation_pattern, quiz_text, re.DOTALL)
    for match in explanation_matches:
        explanations.append(match.strip())
    
    return correct_answers, explanations


def validate_quiz_data(correct_answers: list, explanations: list, expected_count: int = 5) -> bool:
    """Validate that quiz data is complete."""
    if len(correct_answers) < expected_count:
        return False
    if len(explanations) < expected_count:
        while len(explanations) < expected_count:
            explanations.append("Great effort! Keep learning and you'll master this topic.")
    for ans in correct_answers[:expected_count]:
        if ans not in ['A', 'B', 'C', 'D']:
            return False
    return True


def parse_individual_questions(quiz_text: str) -> list:
    """Parse quiz into individual questions with their options."""
    questions = []
    
    question_blocks = re.split(r'###\s*Question\s*', quiz_text)
    
    for block in question_blocks[1:]:
        try:
            first_line_match = re.match(r'(\d+)\s*([^\n]*)', block)
            if not first_line_match:
                continue
            
            q_num = first_line_match.group(1)
            emoji = first_line_match.group(2).strip()
            
            q_text = ""
            skip_phrases = ['correct answer', 'explanation', 'great job', 'quiz complete', 
                           'good job', 'well done', 'keep learning', 'keep going', 
                           'congratulations', 'awesome work', 'nice work']
            bold_matches = re.findall(r'\*\*([^*]+)\*\*', block)
            for match in bold_matches:
                match_lower = match.lower().strip()
                if any(phrase in match_lower for phrase in skip_phrases):
                    continue
                if len(match) > 10 and '?' in match:
                    q_text = match.strip()
                    break
                elif len(match) > 15 and '?' in match:
                    q_text = match.strip()
                    break
            
            if not q_text:
                lines = block.split('\n')
                for line in lines[1:6]:
                    line = line.strip()
                    if line and not line.startswith('-') and not line.startswith('*') and '✅' not in line and '💡' not in line:
                        if len(line) > 10:
                            q_text = line.replace('**', '').strip()
                            break
            
            if not q_text:
                q_text = f"Question {q_num}"
            
            options = {}
            option_patterns = [
                r'-\s*([A-Da-d])\)\s*(.+?)(?=\n-\s*[A-Da-d]\)|\n\n|✅|$)',
                r'\*\s*([A-Da-d])\)\s*(.+?)(?=\n\*\s*[A-Da-d]\)|\n\n|✅|$)',
                r'([A-Da-d])\)\s*(.+?)(?=\n[A-Da-d]\)|\n\n|✅|$)',
            ]
            
            for pattern in option_patterns:
                option_matches = re.findall(pattern, block, re.DOTALL)
                if len(option_matches) >= 4:
                    for opt_match in option_matches[:4]:
                        letter = opt_match[0].upper()
                        text = opt_match[1].strip().rstrip('\n').strip()
                        options[letter] = text
                    break
            
            if len(options) == 4:
                questions.append({
                    'number': int(q_num),
                    'emoji': emoji,
                    'text': q_text,
                    'options': options
                })
        except Exception:
            continue
    
    return questions


def generate_quiz_with_gemini(topic: str, difficulty: str, weak_topics: list = None, grade_level: str = None, num_questions: int = 5) -> str:
    """Generate a quiz using Gemini AI."""
    clean_difficulty = difficulty.split()[0]
    
    adaptive_section = ""
    if weak_topics and len(weak_topics) > 0:
        weak_topics_str = ", ".join(weak_topics[-5:])
        adaptive_section = f"""
ADAPTIVE LEARNING NOTE:
The student has struggled with these topics recently: {weak_topics_str}
If any of these topics relate to {topic}, please include 1-2 gentle review questions to help reinforce their understanding. Make these questions encouraging and supportive!
"""
    
    grade_section = ""
    age_description = "a 14-year-old student"
    if grade_level and grade_level != "None (Skip)":
        grade_section = f"\nGrade Level: {grade_level}"
        if grade_level == "Pre-K":
            age_description = "a Pre-K student (ages 3-5)"
        elif grade_level == "Kindergarten":
            age_description = "a Kindergarten student (ages 5-6)"
        elif "1st" in grade_level:
            age_description = "a 1st grade student (ages 6-7)"
        elif "2nd" in grade_level:
            age_description = "a 2nd grade student (ages 7-8)"
        elif "3rd" in grade_level:
            age_description = "a 3rd grade student (ages 8-9)"
        elif "4th" in grade_level:
            age_description = "a 4th grade student (ages 9-10)"
        elif "5th" in grade_level:
            age_description = "a 5th grade student (ages 10-11)"
        elif "6th" in grade_level:
            age_description = "a 6th grade student (ages 11-12)"
        elif "7th" in grade_level:
            age_description = "a 7th grade student (ages 12-13)"
        elif "8th" in grade_level:
            age_description = "an 8th grade student (ages 13-14)"
        elif "9th" in grade_level:
            age_description = "a 9th grade student (ages 14-15)"
        elif "10th" in grade_level:
            age_description = "a 10th grade student (ages 15-16)"
        elif "11th" in grade_level:
            age_description = "an 11th grade student (ages 16-17)"
        elif "12th" in grade_level:
            age_description = "a 12th grade student (ages 17-18)"
    
    question_emojis = ["🔢", "🧮", "🎯", "🌟", "🏆", "📚", "💡", "🔬", "🌍", "🎨", "🚀", "⭐", "🎓", "🧠", "✨"]
    
    questions_template = ""
    for i in range(1, num_questions + 1):
        emoji = question_emojis[(i - 1) % len(question_emojis)]
        questions_template += f"""
### Question {i} {emoji}
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation]

---
"""
    
    prompt = f"""You are a fun and encouraging teacher creating a quiz for {age_description}.

Create a {num_questions}-question multiple-choice quiz about: {topic}
Difficulty level: {clean_difficulty}{grade_section}
{adaptive_section}
Guidelines:
- Make questions appropriate for {age_description}
- For Easy: Basic concepts, straightforward questions
- For Medium: Requires some thinking, applies concepts
- For Hard: Challenging questions that require deeper understanding
- Use friendly, encouraging language with emojis
- Make it fun and engaging!

CRITICAL QUESTION FORMAT RULES:
- Each question MUST be a real question that ends with a question mark (?)
- Questions should start with words like: What, Which, Who, When, Where, Why, How, Is, Are, Do, Does, Can, etc.
- DO NOT write definitions, statements, or descriptions as questions
- BAD example: "The Libertarian Party believes in limited government" (this is a statement, NOT a question)
- GOOD example: "What is a core belief of the Libertarian Party?" (this IS a proper question)

IMPORTANT: You MUST follow this EXACT format for each question. Do not deviate!

## 📝 Your {clean_difficulty} Quiz on {topic}!
{questions_template}
## 🎊 Quiz Complete!

**Great job working through this quiz!** Keep learning and growing! 🌟
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    if not response.text:
        raise ValueError("No response received from AI. Please try again!")
    
    return response.text


def generate_quiz_summary(topic: str, correct_count: int, total_questions: int, 
                          parsed_questions: list, user_answers: list, correct_answers: list) -> str:
    """Generate an AI-powered summary of quiz performance."""
    
    wrong_details = []
    correct_details = []
    
    for i in range(min(len(user_answers), len(correct_answers), len(parsed_questions))):
        q = parsed_questions[i]
        user_ans = user_answers[i].upper()
        correct_ans = correct_answers[i].upper()
        question_text = q.get('text', f'Question {i+1}')
        options = q.get('options', {})
        
        if user_ans == correct_ans:
            correct_details.append(f"- Q{i+1}: {question_text}")
        else:
            user_choice = options.get(user_ans, "Unknown")
            correct_choice = options.get(correct_ans, "Unknown")
            wrong_details.append(f"- Q{i+1}: {question_text}\n  Student answered: {user_ans}) {user_choice}\n  Correct answer: {correct_ans}) {correct_choice}")
    
    wrong_section = "\n".join(wrong_details) if wrong_details else "None - Perfect score!"
    correct_section = "\n".join(correct_details) if correct_details else "None"
    
    prompt = f"""You are an encouraging study buddy for a student who just completed a quiz.

Topic: {topic}
Score: {correct_count}/{total_questions}

Questions answered correctly:
{correct_section}

Questions answered incorrectly:
{wrong_section}

Write a SHORT, personalized summary (3-5 sentences max) that:
1. Congratulates them on what they got right (be specific about topics they understood)
2. If they got any wrong, gently explain what concepts they should review (without being discouraging)
3. End with an encouraging tip or next step for studying this topic

Keep it friendly, supportive, and age-appropriate for a student. Use 1-2 emojis max. Be concise!"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            return response.text
        return "Great effort on this quiz! Keep practicing and you'll keep improving! 🌟"
    except Exception:
        return "Great effort on this quiz! Keep practicing and you'll keep improving! 🌟"


def generate_study_notes(topic: str, correct_count: int, total_questions: int,
                         parsed_questions: list, correct_answers: list, explanations: list) -> str:
    """Generate AI-powered study notes based on quiz content."""
    
    # Build summary of all questions and their key concepts
    questions_summary = []
    for i in range(min(len(parsed_questions), len(correct_answers), len(explanations))):
        q = parsed_questions[i]
        correct_ans = correct_answers[i].upper()
        correct_option = q.get('options', {}).get(correct_ans, '')
        explanation = explanations[i] if i < len(explanations) else ''
        questions_summary.append(f"Q{i+1}: {q.get('text', '')} → Answer: {correct_ans}) {correct_option}")
    
    questions_text = "\n".join(questions_summary)
    
    prompt = f"""You are a helpful study assistant. Based on this quiz about "{topic}", create concise study notes.

Quiz Questions and Answers:
{questions_text}

Create STUDY NOTES that:
1. List 3-5 KEY CONCEPTS covered in this quiz (use bullet points)
2. Provide 2-3 IMPORTANT FACTS to remember
3. Suggest 2 RELATED TOPICS the student might want to explore next

Format the notes clearly with headers. Keep it concise (under 200 words). 
Make it engaging for a student. Use simple language."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        if response.text:
            return response.text
        return "Study notes could not be generated. Review the explanations above for key concepts!"
    except Exception:
        return "Study notes could not be generated. Review the explanations above for key concepts!"


# ============================================================
# SOUND EFFECTS HELPER
# ============================================================
def play_sound(sound_type: str) -> str:
    """Generate JavaScript to play a sound effect using Web Audio API."""
    if not st.session_state.get('sound_enabled', True):
        return ""
    
    sounds = {
        'correct': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.setValueAtTime(523.25, ctx.currentTime);
            osc.frequency.setValueAtTime(659.25, ctx.currentTime + 0.1);
            osc.frequency.setValueAtTime(783.99, ctx.currentTime + 0.2);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.4);
        """,
        'wrong': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'square';
            osc.frequency.setValueAtTime(200, ctx.currentTime);
            osc.frequency.setValueAtTime(150, ctx.currentTime + 0.15);
            gain.gain.setValueAtTime(0.2, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.3);
        """,
        'complete': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [523.25, 659.25, 783.99, 1046.50];
            notes.forEach((freq, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.15);
                gain.gain.setValueAtTime(0.25, ctx.currentTime + i * 0.15);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.15 + 0.3);
                osc.start(ctx.currentTime + i * 0.15);
                osc.stop(ctx.currentTime + i * 0.15 + 0.3);
            });
        """,
        'levelup': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [392, 523.25, 659.25, 783.99, 1046.50];
            notes.forEach((freq, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.12);
                gain.gain.setValueAtTime(0.3, ctx.currentTime + i * 0.12);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.12 + 0.25);
                osc.start(ctx.currentTime + i * 0.12);
                osc.stop(ctx.currentTime + i * 0.12 + 0.25);
            });
        """,
        'badge': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [440, 554.37, 659.25, 880];
            notes.forEach((freq, i) => {
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.1);
                gain.gain.setValueAtTime(0.25, ctx.currentTime + i * 0.1);
                gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + i * 0.1 + 0.3);
                osc.start(ctx.currentTime + i * 0.1);
                osc.stop(ctx.currentTime + i * 0.1 + 0.3);
            });
        """,
        'click': """
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.setValueAtTime(800, ctx.currentTime);
            gain.gain.setValueAtTime(0.15, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.05);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.05);
        """
    }
    
    js_code = sounds.get(sound_type, '')
    if js_code:
        return f'<script>try {{ {js_code} }} catch(e) {{}}</script>'
    return ""


# ============================================================
# CUSTOM STYLING - Teen-Friendly & Mobile-First! 🎨
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .stDeployButton {display: none;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    .mega-title {
        font-size: 2.8rem;
        text-align: center;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        color: #7c7c7c;
        margin-top: 10px;
        font-weight: 600;
    }
    
    .encourage-box {
        background: #f0f4f8;
        border-left: 4px solid #6366f1;
        padding: 15px 25px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        color: #4a5568;
        margin: 20px auto;
        max-width: 500px;
    }
    
    .level-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
    }
    
    .level-number {
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .level-title {
        font-size: 1.3rem;
        opacity: 0.95;
        margin: 5px 0;
        font-weight: 600;
    }
    
    .stats-row {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
        margin-top: 15px;
        font-size: 1.1rem;
    }
    
    .stat-item {
        background: rgba(255,255,255,0.2);
        padding: 8px 16px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }
    
    .badge-showcase {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 20px;
        border-radius: 16px;
        margin: 20px 0;
        text-align: center;
    }
    
    .badge-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 15px;
    }
    
    .badge-icons {
        font-size: 2.2rem;
        letter-spacing: 8px;
    }
    
    .new-badge-alert {
        background: #6366f1;
        color: white;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        margin: 15px 0;
    }
    
    .new-badge-emoji {
        font-size: 2.5rem;
        display: block;
        margin: 10px 0;
    }
    
    .practice-areas {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        padding: 20px;
        border-radius: 12px;
        margin: 20px 0;
    }
    
    .practice-title {
        font-weight: 700;
        color: #b45309;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    
    .practice-item {
        color: #78716c;
        padding: 5px 0;
        font-size: 1rem;
    }
    
    .stButton > button {
        background: #6366f1 !important;
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        padding: 16px 32px !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25) !important;
    }
    
    .stButton > button:hover {
        background: #4f46e5 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stFormSubmitButton > button {
        background: #10b981 !important;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25) !important;
    }
    
    .stFormSubmitButton > button:hover {
        background: #059669 !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 2px solid #dfe6e9 !important;
        padding: 15px 20px !important;
        font-size: 1.1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 15px !important;
    }
    
    .result-correct {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
        padding: 20px;
        margin: 15px 0;
        border-radius: 15px;
        font-size: 1.1rem;
    }
    
    .result-wrong {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 5px solid #dc3545;
        padding: 20px;
        margin: 15px 0;
        border-radius: 15px;
        font-size: 1.1rem;
    }
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    .stRadio > div {
        gap: 10px !important;
    }
    
    .stRadio > div > label {
        padding: 12px 20px !important;
        border-radius: 12px !important;
        border: 2px solid #dfe6e9 !important;
        transition: all 0.2s ease !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.1) !important;
    }
    
    .stSuccess, .stInfo, .stWarning, .stError {
        border-radius: 15px !important;
        font-size: 1.1rem !important;
    }
    
    hr {
        border: none;
        height: 1px;
        background: #e2e8f0;
        margin: 30px 0;
    }
    
    .cool-footer {
        text-align: center;
        padding: 30px;
        color: #64748b;
        font-size: 0.95rem;
    }
    
    .loading-box {
        background: #6366f1;
        color: white;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin: 20px 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    @media (max-width: 768px) {
        .mega-title {
            font-size: 2rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
        }
        
        .level-number {
            font-size: 2.5rem;
        }
        
        .stats-row {
            flex-direction: column;
            gap: 10px;
        }
        
        .stat-item {
            display: block;
        }
        
        .stButton > button {
            font-size: 1.2rem !important;
            padding: 18px 30px !important;
        }
        
        .badge-icons {
            font-size: 2rem;
            letter-spacing: 5px;
        }
    }
    
    .bottom-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 12px 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 15px;
        z-index: 9999;
        box-shadow: 0 -4px 20px rgba(102, 126, 234, 0.3);
    }
    
    .bottom-bar-dark {
        background: linear-gradient(135deg, #2d3436 0%, #636e72 100%);
    }
    
    .bottom-bar-label {
        color: white;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .page-padding {
        padding-bottom: 80px !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# TOP RIGHT BUTTONS - HELP, SOUND & THEME TOGGLE
# ============================================================
theme_icon = "☀️" if st.session_state.dark_mode else "🌙"
theme_text = "Light" if st.session_state.dark_mode else "Dark"
sound_icon = "🔊" if st.session_state.sound_enabled else "🔇"
sound_text = "Off" if st.session_state.sound_enabled else "On"

col_spacer, col_help, col_sound, col_theme = st.columns([10, 1, 1, 1])
with col_help:
    if st.button("❓", key="help_btn", help="How to use Study Buddy"):
        st.session_state.show_tutorial = not st.session_state.get('show_tutorial', False)
        st.rerun()
with col_sound:
    if st.button(f"{sound_icon}", key="sound_btn", help=f"Turn Sound {sound_text}"):
        st.session_state.sound_enabled = not st.session_state.sound_enabled
        st.rerun()
with col_theme:
    if st.button(f"{theme_icon}", key="theme_btn", help=f"Switch to {theme_text} Mode"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# ============================================================
# INTERACTIVE TUTORIAL
# ============================================================
if st.session_state.get('show_tutorial', False):
    st.markdown("""
    <div style="background: #eff6ff; border: 2px solid #6366f1; border-radius: 16px; padding: 25px; margin-bottom: 20px;">
        <h3 style="color: #6366f1; margin-top: 0;">Welcome to Study Buddy Quest!</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tutorial_step = st.session_state.get('tutorial_step', 1)
    
    if tutorial_step == 1:
        st.markdown("### Step 1: Choose Your Topic")
        st.info("Type any subject you want to learn about in the **'What do you want to study?'** box below. It can be anything - dinosaurs, math, history, space, coding, and more!")
        col1, col2 = st.columns(2)
        with col2:
            if st.button("Next →", key="tut_next_1"):
                st.session_state.tutorial_step = 2
                st.rerun()
    
    elif tutorial_step == 2:
        st.markdown("### Step 2: Pick Your Difficulty")
        st.info("Select how challenging you want your quiz to be:\n- **Easy** - Great for beginners\n- **Medium** - A balanced challenge\n- **Hard** - Test your expertise!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="tut_back_2"):
                st.session_state.tutorial_step = 1
                st.rerun()
        with col2:
            if st.button("Next →", key="tut_next_2"):
                st.session_state.tutorial_step = 3
                st.rerun()
    
    elif tutorial_step == 3:
        st.markdown("### Step 3: Optional Grade Level")
        st.info("You can optionally select your grade level to get questions written at the right level for you. Skip it if you prefer!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="tut_back_3"):
                st.session_state.tutorial_step = 2
                st.rerun()
        with col2:
            if st.button("Next →", key="tut_next_3"):
                st.session_state.tutorial_step = 4
                st.rerun()
    
    elif tutorial_step == 4:
        st.markdown("### Step 4: Take the Quiz!")
        st.info("Click **'Start My Quest!'** to generate your quiz. Answer all 5 questions, then submit to see your score and earn XP points!")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="tut_back_4"):
                st.session_state.tutorial_step = 3
                st.rerun()
        with col2:
            if st.button("Next →", key="tut_next_4"):
                st.session_state.tutorial_step = 5
                st.rerun()
    
    elif tutorial_step == 5:
        st.markdown("### Step 5: Level Up & Earn Badges!")
        st.markdown("""
        **How Leveling Works:**
        - Every correct answer earns you **XP points** (10 XP each, plus bonuses!)
        - Every **50 XP** you earn moves you up to the next level
        - Each level has a special title showing your progress:
        
        | Level | Title | XP Needed |
        |-------|-------|-----------|
        | 1 | Curious Beginner 🌱 | 0 XP |
        | 2 | Knowledge Seeker 📖 | 50 XP |
        | 3 | Quiz Explorer 🗺️ | 100 XP |
        | 4 | Brain Builder 🧱 | 150 XP |
        | 5 | Study Champion 🏅 | 200 XP |
        | 6 | Wisdom Warrior ⚔️ | 250 XP |
        | 7 | Master Learner 🎓 | 300 XP |
        | 8 | Knowledge Knight 🛡️ | 350 XP |
        | 9 | Quiz Legend 🌟 | 400 XP |
        | 10 | Ultimate Genius 👑 | 450 XP |
        
        **Bonus XP:** Get extra points for perfect scores and fast answers in timed mode!
        """)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", key="tut_back_5"):
                st.session_state.tutorial_step = 4
                st.rerun()
        with col2:
            if st.button("Got it! ✓", key="tut_done", type="primary"):
                st.session_state.show_tutorial = False
                st.session_state.tutorial_step = 1
                st.rerun()
    
    st.markdown("---")

# ============================================================
# MAIN TITLE AND WELCOME
# ============================================================
st.markdown('<h1 class="mega-title">🎮 Study Buddy Quest 🧠</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Level up your knowledge, one quiz at a time! 🚀</p>', unsafe_allow_html=True)

with st.expander("💡 Why Use Study Buddy Quest?"):
    st.markdown("""
    **Study Buddy Quest makes learning fun and effective!**
    
    🎮 **Gamified Learning** - Earn XP, level up, and collect badges as you learn. It's like playing a game while studying!
    
    🧠 **AI-Powered Quizzes** - Get personalized questions on ANY topic you want to learn about, at your difficulty level.
    
    📊 **Track Your Progress** - See your weak areas and focus on what needs more practice. The app remembers what you struggle with!
    
    ⏱️ **Timed Challenges** - Test yourself under pressure and earn bonus points for quick thinking.
    
    📝 **Study Notes** - Get AI-generated study notes after each quiz to reinforce what you learned.
    
    🎓 **Grade-Appropriate** - Questions are tailored to your grade level, from Pre-K to 12th grade.
    
    🔊 **Accessibility** - Listen to questions read aloud, adjust font sizes, and customize your experience.
    
    *Start your learning quest today and watch your knowledge grow!*
    """)

# ============================================================
# BADGE DISPLAY
# ============================================================
if st.session_state.badges:
    badge_emojis = " ".join([BADGES[b]["emoji"] for b in st.session_state.badges if b in BADGES])
    st.markdown(f"""
    <div class="badge-showcase">
        <div class="badge-title">🏅 Your Trophy Case ({len(st.session_state.badges)}/{len(BADGES)})</div>
        <div class="badge-icons">{badge_emojis}</div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 View All Your Badges"):
        for badge_id in st.session_state.badges:
            if badge_id in BADGES:
                badge = BADGES[badge_id]
                st.markdown(f"### {badge['emoji']} {badge['name']}")
                st.markdown(f"*{badge['desc']}*")

# ============================================================
# LEVEL & STATS DISPLAY
# ============================================================
current_level = calculate_level(st.session_state.total_score)
level_title = get_level_title(current_level)
points_into_level, points_needed = get_points_for_next_level(st.session_state.total_score)
progress_percentage = points_into_level / points_needed

st.markdown(f"""
<div class="level-card">
    <p class="level-number">⭐ Level {current_level} ⭐</p>
    <p class="level-title">{level_title}</p>
    <div class="stats-row">
        <span class="stat-item">🏆 {st.session_state.total_score} pts</span>
        <span class="stat-item">📚 {st.session_state.quizzes_completed} quizzes</span>
        <span class="stat-item">💯 {st.session_state.perfect_scores} perfect</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"##### ⬆️ Progress to Level {current_level + 1}")
st.progress(progress_percentage)
st.markdown(f"<center><small>{points_into_level}/{points_needed} XP</small></center>", unsafe_allow_html=True)

# ============================================================
# WEAK TOPICS DISPLAY
# ============================================================
if st.session_state.weak_topics:
    unique_weak_topics = list(dict.fromkeys(st.session_state.weak_topics))
    topics_list = "".join([f'<div class="practice-item">📌 {topic}</div>' for topic in unique_weak_topics[-5:]])
    st.markdown(f"""
    <div class="practice-areas">
        <div class="practice-title">📖 Areas to Level Up</div>
        {topics_list}
        <small style="color: #7f5539;">Pro tip: Try these topics again! 💪</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# ACCESSIBILITY CONTROLS - Font Size
# ============================================================
font_sizes = {"small": "0.85rem", "medium": "1rem", "large": "1.25rem"}
current_font = font_sizes.get(st.session_state.font_size, "1rem")

st.markdown(f"""
<style>
    /* Apply font size to all main text elements */
    html, body, .main, .block-container {{
        font-size: {current_font} !important;
    }}
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{
        font-size: {current_font} !important;
    }}
    .stRadio label, .stSelectbox label, .stTextInput label {{
        font-size: {current_font} !important;
    }}
    .stRadio div[role="radiogroup"] label {{
        font-size: {current_font} !important;
    }}
    .quiz-question, .quiz-option, .explanation {{
        font-size: {current_font} !important;
    }}
    .stExpander summary, .stExpander p {{
        font-size: {current_font} !important;
    }}
    button, .stButton button {{
        font-size: {current_font} !important;
    }}
</style>
""", unsafe_allow_html=True)

# High Contrast Mode CSS
if st.session_state.get('high_contrast', False):
    st.markdown("""
    <style>
        /* High Contrast Mode */
        .stApp {
            background-color: #000000 !important;
        }
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
        .stTextInput label, .stSelectbox label, h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
        }
        .stRadio label, .stCheckbox label {
            color: #FFFFFF !important;
        }
        .stButton button {
            background-color: #FFFF00 !important;
            color: #000000 !important;
            border: 3px solid #FFFFFF !important;
            font-weight: bold !important;
        }
        .stButton button:hover {
            background-color: #00FF00 !important;
        }
        a, .stMarkdown a {
            color: #00FFFF !important;
            text-decoration: underline !important;
        }
        .stProgress > div > div {
            background-color: #00FF00 !important;
        }
        .stExpander {
            border: 2px solid #FFFFFF !important;
        }
        .quiz-question, .explanation {
            color: #FFFFFF !important;
            border: 2px solid #FFFF00 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Compact Mode CSS
if st.session_state.get('compact_mode', False):
    st.markdown("""
    <style>
        /* Compact Mode */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        .stMarkdown {
            margin-bottom: 0.25rem !important;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.25rem !important;
        }
        .stButton {
            margin-top: 0.25rem !important;
            margin-bottom: 0.25rem !important;
        }
        .stRadio > div {
            gap: 0.25rem !important;
        }
        .stExpander {
            margin-bottom: 0.5rem !important;
        }
        hr {
            margin: 0.5rem 0 !important;
        }
        .element-container {
            margin-bottom: 0.25rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# QUIZ HISTORY
# ============================================================
if st.session_state.quiz_history:
    with st.expander(f"📜 Quiz History ({len(st.session_state.quiz_history)} quizzes)"):
        for i, quiz in enumerate(reversed(st.session_state.quiz_history[-10:])):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{quiz['topic']}** - {quiz['score']}/{quiz['total']} ({quiz['difficulty']})")
            with col2:
                if st.button("Retake", key=f"retake_{i}"):
                    st.session_state.retake_topic = quiz['topic']
                    st.session_state.retake_difficulty = quiz['difficulty']
                    st.session_state.retake_grade = quiz.get('grade_level', 'None (Skip)')
                    st.session_state.retake_length = quiz.get('num_questions', 5)
                    st.rerun()

# ============================================================
# USER INPUT SECTION
# ============================================================
st.markdown("### 🎯 Choose Your Quest!")

example_topics = [
    "e.g., dinosaurs, volcanoes, the moon...",
    "e.g., ancient Egypt, the ocean, math...",
    "e.g., space exploration, animals, weather...",
    "e.g., the human body, planets, geography...",
    "e.g., world history, chemistry, coding...",
    "e.g., famous scientists, ecosystems, music...",
    "e.g., inventions, mythology, sports...",
    "e.g., rainforests, electricity, art history...",
]

if 'topic_placeholder' not in st.session_state:
    st.session_state.topic_placeholder = random.choice(example_topics)

retake_topic = st.session_state.get('retake_topic', '')
if retake_topic:
    del st.session_state['retake_topic']

col1, col2 = st.columns(2)

with col1:
    topic = st.text_input(
        "📚 What do you want to study?",
        value=retake_topic,
        placeholder=st.session_state.topic_placeholder,
        help="Type any topic you want to learn about!",
        max_chars=100
    )

with col2:
    difficulty_options = ["Easy 🌱", "Medium 🌿", "Hard 🌳"]
    retake_diff = st.session_state.get('retake_difficulty', None)
    diff_index = 0
    if retake_diff:
        for i, d in enumerate(difficulty_options):
            if retake_diff in d:
                diff_index = i
                break
        del st.session_state['retake_difficulty']
    
    difficulty = st.selectbox(
        "🎮 Difficulty Level",
        options=difficulty_options,
        index=diff_index,
        help="Pick based on how confident you feel!"
    )

col3, col4 = st.columns(2)

with col3:
    default_length = st.session_state.get('default_quiz_length', 5)
    retake_len = st.session_state.get('retake_length', default_length)
    quiz_length = st.selectbox(
        "📝 Number of Questions",
        options=[5, 10, 15],
        index=[5, 10, 15].index(retake_len) if retake_len in [5, 10, 15] else 0,
        help="Choose how many questions you want!"
    )
    if 'retake_length' in st.session_state:
        del st.session_state['retake_length']

with col4:
    grade_levels = ["None (Skip)", "Pre-K", "Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", 
                    "4th Grade", "5th Grade", "6th Grade", "7th Grade", "8th Grade", 
                    "9th Grade", "10th Grade", "11th Grade", "12th Grade"]
    
    retake_grade = st.session_state.get('retake_grade', 'None (Skip)')
    grade_index = 0
    if retake_grade in grade_levels:
        grade_index = grade_levels.index(retake_grade)
    if 'retake_grade' in st.session_state:
        del st.session_state['retake_grade']
    
    grade_level = st.selectbox(
        "🎓 Grade Level (Optional)",
        options=grade_levels,
        index=grade_index,
        help="Select your grade to get age-appropriate questions. Skip if not for school!"
    )

# Subject Category (Optional, grade-dependent)
if grade_level and grade_level != "None (Skip)":
    categories = GRADE_CATEGORIES.get(grade_level, DEFAULT_CATEGORIES)
else:
    categories = DEFAULT_CATEGORIES

selected_category = st.selectbox(
    "📂 Subject Category (Optional)",
    options=categories,
    index=0,
    help="Pick a category or choose 'Any Topic' to enter your own!"
)

if difficulty == "Easy 🌱":
    st.success("💪 Perfect for building your foundation! Let's go!")
elif difficulty == "Medium 🌿":
    st.info("🔥 Ready for a challenge! You've got this!")
else:
    st.warning("🏆 Brave choice! Time to show what you're made of!")

# Timed Mode Toggle
st.markdown("")
timed_col1, timed_col2 = st.columns([3, 1])
with timed_col1:
    st.markdown("**⏱️ Timed Challenge Mode**")
    st.caption("Race against the clock for bonus XP! 30 seconds per question.")
with timed_col2:
    default_timed = st.session_state.get('default_timed_mode', False)
    timed_mode = st.toggle("Enable Timer", value=st.session_state.get('timed_mode', default_timed), key="timed_toggle")

if timed_mode:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); 
                color: white; padding: 12px 20px; border-radius: 10px; text-align: center;">
        <strong>⚡ TIMED MODE ACTIVE!</strong> Answer quickly for bonus points!
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# GENERATE QUIZ BUTTON
# ============================================================
st.markdown("")

if st.button("🎲 START QUIZ! 🎲", use_container_width=True):
    
    # Combine category with topic if a category is selected
    if selected_category and selected_category != "Any Topic":
        if topic:
            full_topic = f"{selected_category}: {topic}"
        else:
            full_topic = selected_category
    else:
        full_topic = topic
    
    clean_topic = sanitize_topic(full_topic) if full_topic else ""
    
    if not clean_topic:
        st.warning("⚠️ Oops! Enter a topic first! What do you want to learn about today? 🤔")
    elif len(clean_topic) < 2:
        st.warning("⚠️ That topic is too short! Try something like 'volcanoes' or 'ancient Egypt' 🤔")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <div style="font-size: 3rem; animation: spin 2s linear infinite;">⚙️</div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.answers_submitted = False
        st.session_state.correct_answers = []
        st.session_state.explanations = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        st.session_state.current_topic = clean_topic
        st.session_state.wrong_questions = []
        st.session_state.generation_error = None
        st.session_state.quiz_length = quiz_length
        st.session_state.current_grade_level = grade_level
        st.session_state.current_difficulty = difficulty
        st.session_state.timed_mode = timed_mode
        st.session_state.quiz_start_time = time.time() if timed_mode else None
        st.session_state.study_notes = None
        st.session_state.time_bonus = 0
        st.session_state.base_score = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            for i, msg in enumerate(LOADING_MESSAGES):
                status_text.markdown(f'<div class="loading-box">{msg}</div>', unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 20)
                time.sleep(0.3)
            
            quiz_content = generate_quiz_with_gemini(clean_topic, difficulty, st.session_state.weak_topics, grade_level, quiz_length)
            correct_answers, explanations = parse_quiz_answers(quiz_content)
            
            if not validate_quiz_data(correct_answers, explanations, quiz_length):
                raise ValueError("Quiz generation incomplete. Please try again!")
            
            quiz_questions_only = strip_answers_from_quiz(quiz_content)
            parsed_questions = parse_individual_questions(quiz_content)
            
            st.session_state.quiz_content = quiz_content
            st.session_state.quiz_questions_only = quiz_questions_only
            st.session_state.parsed_questions = parsed_questions
            st.session_state.quiz_generated = True
            st.session_state.correct_answers = correct_answers
            st.session_state.explanations = explanations
            
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            st.success(f"🎉 Your quiz is ready! Let's see what you know about **{clean_topic}**! Good luck! 🍀")
            st.rerun()
            
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            error_msg = str(e)
            if "API" in error_msg or "key" in error_msg.lower():
                st.error("🔑 There's an issue with the API connection. Please check your API key and try again!")
            elif "timeout" in error_msg.lower():
                st.error("⏱️ The request took too long. Please try again!")
            else:
                st.error(f"😅 Oops! Something went wrong: {error_msg}")
            st.info("💡 **Tip:** Try a different topic or refresh the page!")

# ============================================================
# DISPLAY QUIZ WITH INLINE RADIO BUTTONS
# ============================================================
if st.session_state.quiz_generated and st.session_state.quiz_questions_only:
    
    if not st.session_state.answers_submitted:
        st.markdown("---")
        
        parsed_questions = st.session_state.parsed_questions
        num_questions = st.session_state.get('quiz_length', 5)
        question_emojis = ["🔢", "🧮", "🎯", "🌟", "🏆", "📚", "💡", "🔬", "🌍", "🎨", "🚀", "⭐", "🎓", "🧠", "✨"]
        
        if parsed_questions and len(parsed_questions) >= num_questions:
            st.markdown(f"## 📝 Quiz Time!")
            st.markdown("*Select your answer for each question below, then click Submit!*")
            
            # Timer display for timed mode (uses JavaScript for live updates)
            if st.session_state.get('timed_mode') and st.session_state.get('quiz_start_time'):
                total_time = num_questions * st.session_state.get('time_per_question', 30)
                start_time = st.session_state.quiz_start_time
                
                # JavaScript-based live countdown timer
                st.markdown(f"""
                <div id="timer-container" style="background: #d1fae5; border: 3px solid #10b981; 
                            border-radius: 15px; padding: 15px; text-align: center; margin: 15px 0;">
                    <div style="font-size: 0.9rem; font-weight: 600;">⏱️ TIME REMAINING</div>
                    <div id="timer-display" style="font-size: 2.5rem; font-weight: 800;">--:--</div>
                    <div style="font-size: 0.8rem; color: #666;">Bonus XP for fast completion!</div>
                </div>
                <script>
                    (function() {{
                        const startTime = {start_time};
                        const totalTime = {total_time};
                        const container = document.getElementById('timer-container');
                        const display = document.getElementById('timer-display');
                        
                        function updateTimer() {{
                            const now = Date.now() / 1000;
                            const elapsed = now - startTime;
                            const remaining = Math.max(0, totalTime - elapsed);
                            const minutes = Math.floor(remaining / 60);
                            const seconds = Math.floor(remaining % 60);
                            
                            display.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');
                            
                            // Update colors based on time
                            if (remaining > totalTime * 0.5) {{
                                container.style.background = '#d1fae5';
                                container.style.borderColor = '#10b981';
                                display.style.color = '#10b981';
                            }} else if (remaining > totalTime * 0.25) {{
                                container.style.background = '#fef3c7';
                                container.style.borderColor = '#f59e0b';
                                display.style.color = '#f59e0b';
                            }} else {{
                                container.style.background = '#fee2e2';
                                container.style.borderColor = '#ef4444';
                                display.style.color = '#ef4444';
                            }}
                            
                            if (remaining > 0) {{
                                requestAnimationFrame(updateTimer);
                            }} else {{
                                display.textContent = '00:00';
                                display.style.color = '#ef4444';
                            }}
                        }}
                        
                        updateTimer();
                        setInterval(updateTimer, 1000);
                    }})();
                </script>
                """, unsafe_allow_html=True)
            
            st.markdown("")
            
            if 'quiz_error' not in st.session_state:
                st.session_state.quiz_error = None
            
            if st.session_state.quiz_error:
                st.error(st.session_state.quiz_error)
            
            for idx, q in enumerate(parsed_questions[:num_questions]):
                emoji = question_emojis[idx] if idx < len(question_emojis) else "❓"
                
                st.markdown(f"""
<div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
            padding: 20px; 
            border-radius: 15px; 
            margin: 15px 0;
            border-left: 5px solid #667eea;">
    <h4 style="color: #667eea; margin-bottom: 10px;">Question {q['number']} {emoji}</h4>
    <p style="font-size: 1.15rem; font-weight: 600; color: #2d3436;">{q['text']}</p>
</div>
                """, unsafe_allow_html=True)
                
                # Text-to-Speech button for this question
                tts_col1, tts_col2 = st.columns([1, 8])
                with tts_col1:
                    if st.button("🔊", key=f"tts_{idx}", help="Read question aloud"):
                        try:
                            # Build full text to read
                            options_text = ". ".join([f"{letter}: {q['options'][letter]}" for letter in ['A', 'B', 'C', 'D']])
                            full_text = f"Question {q['number']}. {q['text']}. The options are: {options_text}"
                            
                            tts = gTTS(text=full_text, lang='en')
                            audio_bytes = BytesIO()
                            tts.write_to_fp(audio_bytes)
                            audio_bytes.seek(0)
                            st.audio(audio_bytes, format='audio/mp3')
                        except Exception as e:
                            st.warning("Could not generate audio. Please try again.")
                with tts_col2:
                    st.markdown("**👆 Pick your answer:**")
                
                option_emojis = {letter: get_emoji_for_answer(q['options'][letter]) for letter in ['A', 'B', 'C', 'D']}
                
                radio_key = f"q{idx+1}"
                current_val = st.session_state.get(radio_key)
                if current_val in ["A", "B", "C", "D"]:
                    current_idx = ["A", "B", "C", "D"].index(current_val)
                else:
                    current_idx = None
                
                st.radio(
                    f"Your answer for Q{q['number']}:",
                    options=["A", "B", "C", "D"],
                    format_func=lambda x, opts=q['options'], emojis=option_emojis: f"{emojis[x]} {x}) {opts[x]}",
                    horizontal=True,
                    key=radio_key,
                    index=current_idx,
                    label_visibility="collapsed"
                )
                
                if idx < num_questions - 1:
                    st.markdown("---")
            
            st.markdown("")
            if st.button("📨 SUBMIT ALL ANSWERS!", use_container_width=True):
                user_answers = [st.session_state.get(f"q{i+1}") for i in range(num_questions)]
                unanswered = [i+1 for i, ans in enumerate(user_answers) if ans is None]
                
                if unanswered:
                    st.session_state.quiz_error = f"⚠️ Please answer all questions! You haven't picked an answer for: Question {', '.join(map(str, unanswered))}"
                    st.rerun()
                else:
                    st.session_state.quiz_error = None
                    st.session_state.user_answers = user_answers
                    
                    correct_count = 0
                    wrong_questions = []
                    correct_answers = st.session_state.correct_answers
                    
                    num_questions = min(len(user_answers), len(correct_answers))
                    
                    for i in range(num_questions):
                        if user_answers[i].upper() == correct_answers[i].upper():
                            correct_count += 1
                        else:
                            wrong_questions.append(i + 1)
                    
                    st.session_state.wrong_questions = wrong_questions
                    
                    quiz_score = correct_count * 10
                    
                    # Calculate time bonus for timed mode
                    time_bonus = 0
                    if st.session_state.get('timed_mode') and st.session_state.get('quiz_start_time'):
                        total_time = num_questions * st.session_state.get('time_per_question', 30)
                        elapsed = time.time() - st.session_state.quiz_start_time
                        remaining = max(0, total_time - elapsed)
                        
                        if remaining > 0:
                            # Bonus based on time remaining (up to 50% extra)
                            time_bonus = int((remaining / total_time) * quiz_score * 0.5)
                            st.session_state.time_bonus = time_bonus
                    
                    total_quiz_score = quiz_score + time_bonus
                    st.session_state.score = total_quiz_score
                    st.session_state.base_score = quiz_score
                    
                    if correct_count == num_questions:
                        st.session_state.perfect_scores += 1
                    
                    if correct_count < (num_questions // 2) and st.session_state.current_topic:
                        if st.session_state.current_topic not in st.session_state.weak_topics:
                            st.session_state.weak_topics.append(st.session_state.current_topic)
                    
                    st.session_state.total_score += total_quiz_score
                    st.session_state.quizzes_completed += 1
                    
                    # Save to quiz history
                    st.session_state.quiz_history.append({
                        'topic': st.session_state.current_topic,
                        'score': correct_count,
                        'total': num_questions,
                        'difficulty': st.session_state.get('current_difficulty', 'Medium'),
                        'grade_level': st.session_state.get('current_grade_level', 'None (Skip)'),
                        'num_questions': num_questions,
                    })
                    
                    check_and_award_badges()
                    
                    st.session_state.answers_submitted = True
                    
                    st.rerun()
        else:
            st.markdown(st.session_state.quiz_questions_only)
            
            st.markdown("---")
            st.markdown("## ✏️ Lock In Your Answers!")
            
            with st.form(key="quiz_answers_form_fallback"):
                q1 = st.radio("Question 1 🔢", options=["A", "B", "C", "D"], horizontal=True, key="q1_fb")
                q2 = st.radio("Question 2 🧮", options=["A", "B", "C", "D"], horizontal=True, key="q2_fb")
                q3 = st.radio("Question 3 🎯", options=["A", "B", "C", "D"], horizontal=True, key="q3_fb")
                q4 = st.radio("Question 4 🌟", options=["A", "B", "C", "D"], horizontal=True, key="q4_fb")
                q5 = st.radio("Question 5 🏆", options=["A", "B", "C", "D"], horizontal=True, key="q5_fb")
                
                submitted = st.form_submit_button("📨 SUBMIT ANSWERS!", use_container_width=True)
                
                if submitted:
                    user_answers = [q1, q2, q3, q4, q5]
                    st.session_state.user_answers = user_answers
                    
                    correct_count = 0
                    wrong_questions = []
                    correct_answers = st.session_state.correct_answers
                    
                    for i in range(min(len(user_answers), len(correct_answers))):
                        if user_answers[i].upper() == correct_answers[i].upper():
                            correct_count += 1
                        else:
                            wrong_questions.append(i + 1)
                    
                    st.session_state.wrong_questions = wrong_questions
                    st.session_state.score = correct_count * 10
                    
                    fallback_total = min(len(user_answers), len(correct_answers))
                    if correct_count == fallback_total:
                        st.session_state.perfect_scores += 1
                    
                    if correct_count < (fallback_total // 2) and st.session_state.current_topic:
                        if st.session_state.current_topic not in st.session_state.weak_topics:
                            st.session_state.weak_topics.append(st.session_state.current_topic)
                    
                    st.session_state.total_score += st.session_state.score
                    st.session_state.quizzes_completed += 1
                    
                    # Save to quiz history (fallback form)
                    st.session_state.quiz_history.append({
                        'topic': st.session_state.current_topic,
                        'score': correct_count,
                        'total': fallback_total,
                        'difficulty': st.session_state.get('current_difficulty', 'Medium'),
                        'grade_level': st.session_state.get('current_grade_level', 'None (Skip)'),
                        'num_questions': fallback_total,
                    })
                    
                    check_and_award_badges()
                    st.session_state.answers_submitted = True
                    st.rerun()
    
    # ============================================================
    # SHOW RESULTS AFTER SUBMISSION
    # ============================================================
    if st.session_state.answers_submitted:
        st.markdown("---")
        st.markdown("## 📊 Your Results Are In!")
        
        user_answers = st.session_state.user_answers
        correct_answers = st.session_state.correct_answers
        explanations = st.session_state.explanations
        score = st.session_state.score
        wrong_questions = st.session_state.wrong_questions
        
        num_questions = min(len(user_answers), len(correct_answers))
        correct_count = sum(1 for i in range(num_questions) if user_answers[i].upper() == correct_answers[i].upper())
        
        if not st.session_state.get('reduce_animations', False):
            st.balloons()
        
        # Play quiz complete sound
        complete_sound = play_sound('complete')
        if complete_sound:
            st.markdown(complete_sound, unsafe_allow_html=True)
        
        total_questions = st.session_state.get('quiz_length', 5)
        base_score = st.session_state.get('base_score', score)
        time_bonus = st.session_state.get('time_bonus', 0)
        
        # Show time bonus if earned
        if time_bonus > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); 
                        color: white; padding: 15px; border-radius: 12px; text-align: center; margin: 10px 0;">
                <div style="font-size: 1.2rem;">⚡ SPEED BONUS! ⚡</div>
                <div style="font-size: 1.5rem; font-weight: bold;">+{time_bonus} XP</div>
                <div style="font-size: 0.9rem;">You finished with time to spare!</div>
            </div>
            """, unsafe_allow_html=True)
        
        if correct_count == total_questions:
            st.success(f"""
            ## 🏆 PERFECT SCORE! 🏆
            ### You got **{correct_count}/{total_questions}** correct!
            ### **+{score} XP** earned! 
            
            🌟 You're absolutely CRUSHING it! Your brain is on fire! 🔥
            """)
        elif correct_count >= total_questions * 0.8:
            st.success(f"""
            ## 🎉 Amazing Job! 🎉
            ### You got **{correct_count}/{total_questions}** correct!
            ### **+{score} XP** earned!
            
            💪 So close to perfect! You're a knowledge machine!
            """)
        elif correct_count >= total_questions * 0.6:
            st.info(f"""
            ## 👍 Nice Work!
            ### You got **{correct_count}/{total_questions}** correct!
            ### **+{score} XP** earned!
            
            📈 You're learning and growing! Keep going!
            """)
        else:
            st.warning(f"""
            ## 💪 Keep Practicing!
            ### You got **{correct_count}/{total_questions}** correct.
            ### **+{score} XP** earned.
            
            🌱 Every quiz makes you smarter! Try again!
            """)
            if st.session_state.current_topic:
                st.info(f"📖 **{st.session_state.current_topic}** added to your practice list!")
        
        new_level = calculate_level(st.session_state.total_score)
        old_level = calculate_level(st.session_state.total_score - score)
        
        # Check for level up
        if new_level > old_level:
            levelup_sound = play_sound('levelup')
            if levelup_sound:
                st.markdown(levelup_sound, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); 
                        color: white; padding: 20px; border-radius: 12px; text-align: center; margin: 15px 0;">
                <div style="font-size: 2rem;">🎉 LEVEL UP! 🎉</div>
                <div style="font-size: 1.5rem; font-weight: bold;">Level {old_level} → Level {new_level}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"### 📈 Total: **{st.session_state.total_score} XP** | Level **{new_level}**")
        
        new_badges = check_and_award_badges()
        if new_badges:
            # Play badge unlocked sound
            badge_sound = play_sound('badge')
            if badge_sound:
                st.markdown(badge_sound, unsafe_allow_html=True)
            for badge_id in new_badges:
                if badge_id in BADGES:
                    badge = BADGES[badge_id]
                    st.markdown(f"""
                    <div class="new-badge-alert">
                        <strong>🎊 NEW BADGE UNLOCKED! 🎊</strong>
                        <span class="new-badge-emoji">{badge['emoji']}</span>
                        <strong style="font-size: 1.3rem;">{badge['name']}</strong><br>
                        {badge['desc']}
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📚 Answer Review & Explanations")
        st.markdown("*Here's the breakdown for each question:*")
        
        question_emojis = ["🔢", "🧮", "🎯", "🌟", "🏆", "📚", "💡", "🔬", "🌍", "🎨", "🚀", "⭐", "🎓", "🧠", "✨"]
        parsed_questions = st.session_state.parsed_questions
        
        for i in range(min(total_questions, len(correct_answers))):
            user_ans = user_answers[i] if i < len(user_answers) else "?"
            correct_ans = correct_answers[i] if i < len(correct_answers) else "?"
            explanation = explanations[i] if i < len(explanations) else "Great job learning!"
            is_correct = user_ans.upper() == correct_ans.upper()
            
            question_text = ""
            user_ans_text = ""
            correct_ans_text = ""
            if parsed_questions and i < len(parsed_questions):
                question_text = parsed_questions[i].get('text', '')
                options = parsed_questions[i].get('options', {})
                user_ans_text = options.get(user_ans.upper(), "")
                correct_ans_text = options.get(correct_ans.upper(), "")
            
            q_emoji = question_emojis[i % len(question_emojis)]
            question_label = f"Question {i+1} {q_emoji}"
            
            if is_correct:
                st.markdown(f"""
<div class="result-correct">
<strong>{question_label}</strong><br>
<em style="color: #555;">{question_text}</em><br><br>
✅ You answered: <strong>{user_ans}) {user_ans_text}</strong> - Correct!<br><br>
💡 <em>{explanation}</em>
</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="result-wrong">
<strong>{question_label}</strong><br>
<em style="color: #555;">{question_text}</em><br><br>
❌ You answered: <strong>{user_ans}) {user_ans_text}</strong><br>
✅ Correct answer: <strong>{correct_ans}) {correct_ans_text}</strong><br><br>
💡 <em>{explanation}</em>
</div>
                """, unsafe_allow_html=True)
        
        if not wrong_questions:
            st.markdown("### 🌟 FLAWLESS! You got everything right! 🌟")
        
        st.markdown("---")
        st.markdown("### 🤖 AI Study Summary")
        with st.spinner("Generating your personalized summary..."):
            summary = generate_quiz_summary(
                st.session_state.current_topic,
                correct_count,
                5,
                parsed_questions,
                user_answers,
                correct_answers
            )
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 15px; 
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(108, 92, 231, 0.3);">
    {summary}
</div>
        """, unsafe_allow_html=True)
        
        # Study Notes Section
        st.markdown("---")
        st.markdown("### 📝 Study Notes")
        st.markdown("*Get AI-generated notes to help you remember key concepts!*")
        
        if st.session_state.get('study_notes'):
            st.markdown(f"""
<div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
            color: white; 
            padding: 20px; 
            border-radius: 15px; 
            margin: 10px 0;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);">
    {st.session_state.study_notes}
</div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📚 Generate Study Notes", use_container_width=True):
                with st.spinner("Creating your personalized study notes..."):
                    study_notes = generate_study_notes(
                        st.session_state.current_topic,
                        correct_count,
                        total_questions,
                        parsed_questions,
                        correct_answers,
                        explanations
                    )
                    st.session_state.study_notes = study_notes
                    st.rerun()
        
        st.markdown("---")
        if correct_count >= 4:
            st.markdown("## 🌟 You're a Study Buddy Superstar! 🌟")
            st.markdown("*Keep crushing it! Your brain is getting stronger every day!* 💪🧠")
        else:
            st.markdown("## 💪 Champions Never Give Up!")
            st.markdown("*Every quiz is a step forward! Ready for another round?* 🚀")
        
        st.markdown("")
        if st.button("🔄 TAKE ANOTHER QUIZ!", use_container_width=True):
            st.session_state.quiz_generated = False
            st.session_state.quiz_content = None
            st.session_state.quiz_questions_only = None
            st.session_state.parsed_questions = []
            st.session_state.answers_submitted = False
            st.session_state.correct_answers = []
            st.session_state.explanations = []
            st.session_state.user_answers = []
            st.session_state.score = 0
            st.session_state.wrong_questions = []
            st.session_state.quiz_error = None
            for i in range(1, 16):  # Support up to 15 questions
                if f"q{i}" in st.session_state:
                    del st.session_state[f"q{i}"]
            example_topics = [
                "e.g., dinosaurs, volcanoes, the moon...",
                "e.g., ancient Egypt, the ocean, math...",
                "e.g., space exploration, animals, weather...",
                "e.g., the human body, planets, geography...",
                "e.g., world history, chemistry, coding...",
                "e.g., famous scientists, ecosystems, music...",
                "e.g., inventions, mythology, sports...",
                "e.g., rainforests, electricity, art history...",
            ]
            st.session_state.topic_placeholder = random.choice(example_topics)
            st.rerun()

# ============================================================
# ETHICS SECTION (Near Bottom)
# ============================================================
st.markdown("---")
st.markdown("""
<div style="background: #eff6ff; 
            border-left: 4px solid #6366f1;
            color: #475569; 
            padding: 15px 25px; 
            border-radius: 8px; 
            text-align: center; 
            margin: 15px 0;">
    <strong>Learning Pledge:</strong> This tool helps you learn and understand – always think for yourself and never use it to cheat! 
    <br><small>Real knowledge comes from real effort!</small>
</div>
""", unsafe_allow_html=True)

with st.expander("💡 Why Real Understanding Matters"):
    st.info("""
    **🧠 Your Brain is Amazing!**
    
    This quiz app is designed to help you truly *understand* topics, not just memorize answers. Here's why that matters:
    
    ✨ **Deep learning lasts forever** - When you understand WHY something works, you'll remember it for life!
    
    🔗 **Connections make you smarter** - Real understanding helps you connect ideas across different subjects.
    
    🎯 **Problem-solving power** - Understanding concepts means you can solve NEW problems, not just repeat old ones.
    
    💪 **Build confidence** - Knowing you truly understand something feels way better than just guessing!
    
    *Use AI as a study buddy to LEARN, not a shortcut to skip learning. Your future self will thank you!* 🚀
    """)

# ============================================================
# ACCESSIBILITY SETTINGS (at bottom of page)
# ============================================================
with st.expander("⚙️ Settings"):
    st.markdown("### Display Settings")
    
    # Font Size
    st.markdown("**Font Size**")
    font_col1, font_col2, font_col3 = st.columns(3)
    with font_col1:
        if st.button("A", key="font_small", help="Small text", type="primary" if st.session_state.font_size == "small" else "secondary"):
            st.session_state.font_size = "small"
            st.rerun()
    with font_col2:
        if st.button("A", key="font_medium", help="Medium text", type="primary" if st.session_state.font_size == "medium" else "secondary"):
            st.session_state.font_size = "medium"
            st.rerun()
    with font_col3:
        if st.button("A", key="font_large", help="Large text", type="primary" if st.session_state.font_size == "large" else "secondary"):
            st.session_state.font_size = "large"
            st.rerun()
    st.caption(f"Current: {st.session_state.font_size.title()}")
    
    st.markdown("---")
    
    # High Contrast Mode
    high_contrast = st.toggle(
        "🔲 High Contrast Mode",
        value=st.session_state.get('high_contrast', False),
        help="Stronger colors for better visibility"
    )
    if high_contrast != st.session_state.high_contrast:
        st.session_state.high_contrast = high_contrast
        st.rerun()
    
    # Compact Mode
    compact_mode = st.toggle(
        "📐 Compact Mode",
        value=st.session_state.get('compact_mode', False),
        help="Reduce spacing for more content on screen"
    )
    if compact_mode != st.session_state.compact_mode:
        st.session_state.compact_mode = compact_mode
        st.rerun()
    
    # Reduce Animations
    reduce_animations = st.toggle(
        "🎯 Reduce Animations",
        value=st.session_state.get('reduce_animations', False),
        help="Turn off balloons and celebration effects"
    )
    if reduce_animations != st.session_state.reduce_animations:
        st.session_state.reduce_animations = reduce_animations
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Quiz Preferences")
    
    # Default Quiz Length
    default_quiz_length = st.selectbox(
        "📝 Default Quiz Length",
        options=[5, 10, 15],
        index=[5, 10, 15].index(st.session_state.get('default_quiz_length', 5)),
        help="This will be your default when starting new quizzes"
    )
    if default_quiz_length != st.session_state.default_quiz_length:
        st.session_state.default_quiz_length = default_quiz_length
    
    # Default Timer Setting
    default_timed_mode = st.toggle(
        "⏱️ Enable Timer by Default",
        value=st.session_state.get('default_timed_mode', False),
        help="Automatically enable timed mode for new quizzes"
    )
    if default_timed_mode != st.session_state.default_timed_mode:
        st.session_state.default_timed_mode = default_timed_mode
        st.session_state.timed_mode = default_timed_mode

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")

st.markdown("""
<div style="background: #f1f5f9; 
            padding: 20px; 
            border-radius: 12px; 
            text-align: center; 
            margin-bottom: 20px;
            color: #475569;">
    <strong>Remember:</strong> The best learning happens when you challenge yourself! 
    <br>Use this tool to <em>strengthen</em> your understanding, not replace it.
    <br><small>Think critically. Question everything. Stay curious!</small>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="cool-footer">
    <strong>🏛️ Built for the Presidential AI Challenge 🇺🇸</strong><br><br>
    <small>This educational app was created to demonstrate responsible AI use in learning.</small><br>
    <small>Quiz content is generated by <strong>Google Gemini AI</strong> 🤖✨</small><br><br>
    <small style="color: #636e72;">Study Buddy Quest v2.0 | Made with 💜 by a student, for students</small><br>
    <small>🧠 Learn. Level Up. Repeat! 🚀</small>
</div>
""", unsafe_allow_html=True)


if not st.session_state.dark_mode:
    st.markdown("""
    <style>
        .stApp {
            background-color: #ffffff !important;
        }
        
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
        .stTextInput label, .stSelectbox label {
            color: #333333 !important;
        }
        
        /* Light mode: Quest boxes and form elements */
        .stSelectbox > div > div,
        .stRadio > div,
        [data-baseweb="select"] > div,
        [data-baseweb="popover"] > div,
        .stSelectbox [data-baseweb="select"],
        div[data-baseweb="select"] > div:first-child {
            background-color: #f8f9fa !important;
            border-color: #e9ecef !important;
        }
        
        /* Dropdown menu items */
        [data-baseweb="menu"],
        [data-baseweb="popover"],
        ul[role="listbox"] {
            background-color: #f8f9fa !important;
        }
        
        [data-baseweb="menu"] li,
        ul[role="listbox"] li {
            background-color: #f8f9fa !important;
        }
        
        [data-baseweb="menu"] li:hover,
        ul[role="listbox"] li:hover {
            background-color: #e9ecef !important;
        }
        
        /* Radio buttons */
        .stRadio > div > label > div:first-child {
            background-color: #f8f9fa !important;
        }
        
        /* Text input boxes */
        .stTextInput > div > div > input {
            background-color: #f8f9fa !important;
            border-color: #e9ecef !important;
            color: #333333 !important;
        }
        
        .stTextInput > div > div {
            background-color: #f8f9fa !important;
        }
    </style>
    """, unsafe_allow_html=True)
