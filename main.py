# ============================================================
# Study Buddy Quest 🧠
# A fun, interactive quiz app for students!
# Built for the Presidential AI Challenge
# ============================================================

import streamlit as st
import os
import re
from google import genai

# ============================================================
# GEMINI CONFIGURATION
# ============================================================
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="Study Buddy Quest 🧠",
    page_icon="🧠",
    layout="centered"
)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
if "quiz_content" not in st.session_state:
    st.session_state.quiz_content = None
if "quiz_questions_only" not in st.session_state:
    st.session_state.quiz_questions_only = None
if "quiz_generated" not in st.session_state:
    st.session_state.quiz_generated = False
if "answers_submitted" not in st.session_state:
    st.session_state.answers_submitted = False
if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = []
if "explanations" not in st.session_state:
    st.session_state.explanations = []
if "user_answers" not in st.session_state:
    st.session_state.user_answers = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_topic" not in st.session_state:
    st.session_state.current_topic = ""
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "quizzes_completed" not in st.session_state:
    st.session_state.quizzes_completed = 0
if "perfect_scores" not in st.session_state:
    st.session_state.perfect_scores = 0
if "weak_topics" not in st.session_state:
    st.session_state.weak_topics = []
if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = []
if "badges" not in st.session_state:
    st.session_state.badges = set()

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

# Encouraging messages that rotate
ENCOURAGEMENTS = [
    "You're leveling up your brain! 🧠✨",
    "Every question makes you smarter! 💪",
    "Knowledge is your superpower! ⚡",
    "You've got this! 🚀",
    "Learning looks good on you! 😎",
    "Future genius in the making! 🌟",
]


def check_and_award_badges():
    new_badges = []
    
    if st.session_state.quizzes_completed >= 1 and "first_quiz" not in st.session_state.badges:
        st.session_state.badges.add("first_quiz")
        new_badges.append("first_quiz")
    
    if st.session_state.quizzes_completed >= 5 and "five_quizzes" not in st.session_state.badges:
        st.session_state.badges.add("five_quizzes")
        new_badges.append("five_quizzes")
    
    if st.session_state.quizzes_completed >= 10 and "ten_quizzes" not in st.session_state.badges:
        st.session_state.badges.add("ten_quizzes")
        new_badges.append("ten_quizzes")
    
    if st.session_state.total_score >= 50 and "points_50" not in st.session_state.badges:
        st.session_state.badges.add("points_50")
        new_badges.append("points_50")
    
    if st.session_state.total_score >= 100 and "points_100" not in st.session_state.badges:
        st.session_state.badges.add("points_100")
        new_badges.append("points_100")
    
    if st.session_state.total_score >= 200 and "points_200" not in st.session_state.badges:
        st.session_state.badges.add("points_200")
        new_badges.append("points_200")
    
    if st.session_state.total_score >= 500 and "points_500" not in st.session_state.badges:
        st.session_state.badges.add("points_500")
        new_badges.append("points_500")
    
    if st.session_state.perfect_scores >= 1 and "perfect_score" not in st.session_state.badges:
        st.session_state.badges.add("perfect_score")
        new_badges.append("perfect_score")
    
    if st.session_state.perfect_scores >= 3 and "three_perfects" not in st.session_state.badges:
        st.session_state.badges.add("three_perfects")
        new_badges.append("three_perfects")
    
    current_level = calculate_level(st.session_state.total_score)
    if current_level >= 5 and "level_5" not in st.session_state.badges:
        st.session_state.badges.add("level_5")
        new_badges.append("level_5")
    
    return new_badges


def calculate_level(total_points: int) -> int:
    return 1 + (total_points // 50)


def get_points_for_next_level(total_points: int) -> tuple:
    current_level = calculate_level(total_points)
    points_at_current_level_start = (current_level - 1) * 50
    points_into_level = total_points - points_at_current_level_start
    points_needed = 50
    return points_into_level, points_needed


def get_level_title(level: int) -> str:
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
    quiz_text = re.sub(r'✅\s*\*\*Correct Answer:.*?\*\*\s*\n?', '', quiz_text)
    quiz_text = re.sub(r'>\s*💡\s*\*\*Explanation:\*\*.*?(?=\n\n|---|\n###|$)', '', quiz_text, flags=re.DOTALL)
    quiz_text = re.sub(r'##\s*🎊\s*Quiz Complete!.*$', '', quiz_text, flags=re.DOTALL)
    quiz_text = re.sub(r'\n{3,}', '\n\n', quiz_text)
    return quiz_text.strip()


def get_random_encouragement():
    import random
    return random.choice(ENCOURAGEMENTS)


# ============================================================
# AWESOME CUSTOM STYLING - Teen-Friendly & Mobile-First! 🎨
# ============================================================
st.markdown("""
<style>
    /* Import fun Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');
    
    /* Apply font globally */
    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }
    
    /* Hide Streamlit branding for cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container padding for mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 800px;
    }
    
    /* Epic gradient title */
    .mega-title {
        font-size: 2.8rem;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #f5576c 75%, #4facfe 100%);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        margin-bottom: 0;
        animation: gradient-shift 5s ease infinite;
        text-shadow: 0 0 30px rgba(102, 126, 234, 0.3);
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        font-size: 1.4rem;
        color: #6c5ce7;
        margin-top: 10px;
        font-weight: 600;
    }
    
    /* Encouragement message - animated */
    .encourage-box {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 15px 25px;
        border-radius: 50px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        color: #2d3436;
        margin: 20px auto;
        max-width: 500px;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.4);
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* Level card - super cool gradient */
    .level-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .level-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: rotate(45deg);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
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
    
    /* Badge display - glowing effect */
    .badge-showcase {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 20px;
        border-radius: 20px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 8px 30px rgba(252, 182, 159, 0.3);
    }
    
    .badge-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #d63031;
        margin-bottom: 15px;
    }
    
    .badge-icons {
        font-size: 2.5rem;
        letter-spacing: 10px;
        filter: drop-shadow(0 2px 5px rgba(0,0,0,0.2));
    }
    
    /* New badge animation */
    .new-badge-alert {
        background: linear-gradient(135deg, #f5af19 0%, #f12711 100%);
        color: white;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin: 15px 0;
        animation: celebrate 0.5s ease-out;
        box-shadow: 0 10px 40px rgba(241, 39, 17, 0.4);
    }
    
    @keyframes celebrate {
        0% { transform: scale(0.8); opacity: 0; }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    .new-badge-emoji {
        font-size: 3rem;
        display: block;
        margin: 10px 0;
    }
    
    /* Weak topics - friendly warning style */
    .practice-areas {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        border-left: 5px solid #f39c12;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
    }
    
    .practice-title {
        font-weight: 700;
        color: #d35400;
        font-size: 1.2rem;
        margin-bottom: 10px;
    }
    
    .practice-item {
        color: #7f5539;
        padding: 5px 0;
        font-size: 1.1rem;
    }
    
    /* Big beautiful buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        padding: 20px 40px !important;
        border-radius: 50px !important;
        border: none !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Form submit button special styling */
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%) !important;
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4) !important;
    }
    
    .stFormSubmitButton > button:hover {
        box-shadow: 0 12px 35px rgba(0, 184, 148, 0.5) !important;
    }
    
    /* Input fields - modern look */
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
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 15px !important;
    }
    
    /* Result cards */
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
    
    /* Progress bar custom styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
        border-radius: 10px !important;
    }
    
    /* Radio buttons - bigger touch targets for mobile */
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
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        border-radius: 15px !important;
        font-size: 1.1rem !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 30px 0;
    }
    
    /* Footer styling */
    .cool-footer {
        text-align: center;
        padding: 30px;
        color: #636e72;
        font-size: 1rem;
    }
    
    .cool-footer a {
        color: #667eea;
        text-decoration: none;
    }
    
    /* Mobile responsiveness */
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
</style>
""", unsafe_allow_html=True)

# ============================================================
# MAIN TITLE AND WELCOME
# ============================================================

st.markdown('<h1 class="mega-title">🎮 Study Buddy Quest 🧠</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Level up your knowledge, one quiz at a time! 🚀</p>', unsafe_allow_html=True)

# ============================================================
# ETHICS DISCLAIMER - Prominent and clear
# ============================================================
st.markdown("""
<div style="background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); 
            color: white; 
            padding: 15px 25px; 
            border-radius: 15px; 
            text-align: center; 
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(9, 132, 227, 0.3);">
    <strong>🎓 Learning Pledge:</strong> This tool helps you learn and understand – always think for yourself and never use it to cheat! 
    <br><small>Real knowledge comes from real effort! 💪</small>
</div>
""", unsafe_allow_html=True)

# Encouraging message box
st.markdown(f'<div class="encourage-box">{get_random_encouragement()}</div>', unsafe_allow_html=True)

# ============================================================
# UNDERSTANDING INFO BOX
# ============================================================
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
# USER INPUT SECTION
# ============================================================
st.markdown("### 🎯 Choose Your Quest!")

col1, col2 = st.columns(2)

with col1:
    topic = st.text_input(
        "📚 What do you want to study?",
        placeholder="e.g., space, fractions, history...",
        help="Type any topic you want to learn about!"
    )

with col2:
    difficulty = st.selectbox(
        "🎮 Difficulty Level",
        options=["Easy 🌱", "Medium 🌿", "Hard 🌳"],
        help="Pick based on how confident you feel!"
    )

# Difficulty encouragement
if difficulty == "Easy 🌱":
    st.success("💪 Perfect for building your foundation! Let's go!")
elif difficulty == "Medium 🌿":
    st.info("🔥 Ready for a challenge! You've got this!")
else:
    st.warning("🏆 Brave choice! Time to show what you're made of!")


# ============================================================
# QUIZ PARSING FUNCTION
# ============================================================
def parse_quiz_answers(quiz_text: str) -> tuple:
    correct_answers = []
    explanations = []
    
    answer_pattern = r"✅\s*\*\*Correct Answer:\s*([A-Da-d])\s*\*\*"
    explanation_pattern = r">\s*💡\s*\*\*Explanation:\*\*\s*(.+?)(?=\n\n|---|\n###|$)"
    
    answer_matches = re.findall(answer_pattern, quiz_text, re.IGNORECASE)
    for match in answer_matches:
        correct_answers.append(match.upper())
    
    explanation_matches = re.findall(explanation_pattern, quiz_text, re.DOTALL)
    for match in explanation_matches:
        clean_explanation = match.strip()
        explanations.append(clean_explanation)
    
    return correct_answers, explanations


# ============================================================
# QUIZ GENERATION FUNCTION WITH ADAPTIVE LEARNING
# ============================================================
def generate_quiz_with_gemini(topic: str, difficulty: str, weak_topics: list = None) -> str:
    clean_difficulty = difficulty.split()[0]
    
    adaptive_section = ""
    if weak_topics and len(weak_topics) > 0:
        weak_topics_str = ", ".join(weak_topics[-5:])
        adaptive_section = f"""
ADAPTIVE LEARNING NOTE:
The student has struggled with these topics recently: {weak_topics_str}
If any of these topics relate to {topic}, please include 1-2 gentle review questions to help reinforce their understanding. Make these questions encouraging and supportive!
"""
    
    prompt = f"""You are a fun and encouraging teacher creating a quiz for a 14-year-old student.

Create a 5-question multiple-choice quiz about: {topic}
Difficulty level: {clean_difficulty}
{adaptive_section}
Guidelines:
- Make questions appropriate for a 14-year-old student
- For Easy: Basic concepts, straightforward questions
- For Medium: Requires some thinking, applies concepts
- For Hard: Challenging questions that require deeper understanding
- Use friendly, encouraging language with emojis
- Make it fun and engaging!

IMPORTANT: You MUST follow this EXACT format for each question. Do not deviate!

## 📝 Your {clean_difficulty} Quiz on {topic}!

### Question 1 🔢
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation that helps the student understand why this is correct. Keep it encouraging!]

---

### Question 2 🧮
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation]

---

### Question 3 🎯
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation]

---

### Question 4 🌟
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation]

---

### Question 5 🏆
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Single Letter A, B, C, or D]**

> 💡 **Explanation:** [Short, friendly explanation]

---

## 🎊 Quiz Complete!

**Great job working through this quiz!** Keep learning and growing! 🌟
"""
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text if response.text else "Sorry, couldn't generate a quiz. Please try again!"


# ============================================================
# GENERATE QUIZ BUTTON
# ============================================================
st.markdown("")
st.markdown("")

if st.button("🎲 START QUIZ! 🎲", use_container_width=True):
    
    if not topic:
        st.warning("⚠️ Oops! Enter a topic first! What do you want to learn about today? 🤔")
    else:
        st.balloons()
        
        st.session_state.answers_submitted = False
        st.session_state.correct_answers = []
        st.session_state.explanations = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        st.session_state.current_topic = topic
        st.session_state.wrong_questions = []
        
        with st.spinner(f"🧠 Creating your epic quiz about **{topic}**... Get ready to learn! ✨"):
            try:
                quiz_content = generate_quiz_with_gemini(topic, difficulty, st.session_state.weak_topics)
                correct_answers, explanations = parse_quiz_answers(quiz_content)
                quiz_questions_only = strip_answers_from_quiz(quiz_content)
                
                st.session_state.quiz_content = quiz_content
                st.session_state.quiz_questions_only = quiz_questions_only
                st.session_state.quiz_generated = True
                st.session_state.correct_answers = correct_answers
                st.session_state.explanations = explanations
                
                st.success(f"🎉 Your quiz is ready! Let's see what you know about **{topic}**! Good luck! 🍀")
                
            except Exception as e:
                st.error(f"😅 Oops! Something went wrong. Please try again!")
                st.error(f"Error: {str(e)}")

# ============================================================
# DISPLAY QUIZ AND ANSWER FORM
# ============================================================
if st.session_state.quiz_generated and st.session_state.quiz_questions_only:
    
    if not st.session_state.answers_submitted:
        st.markdown("---")
        st.markdown(st.session_state.quiz_questions_only)
        
        st.markdown("---")
        st.markdown("## ✏️ Lock In Your Answers!")
        st.markdown("*Choose wisely... or guess boldly! 😄*")
        
        with st.form(key="quiz_answers_form"):
            
            st.markdown("### Your Answers:")
            
            q1_answer = st.radio("Question 1 🔢", options=["A", "B", "C", "D"], horizontal=True, key="q1")
            q2_answer = st.radio("Question 2 🧮", options=["A", "B", "C", "D"], horizontal=True, key="q2")
            q3_answer = st.radio("Question 3 🎯", options=["A", "B", "C", "D"], horizontal=True, key="q3")
            q4_answer = st.radio("Question 4 🌟", options=["A", "B", "C", "D"], horizontal=True, key="q4")
            q5_answer = st.radio("Question 5 🏆", options=["A", "B", "C", "D"], horizontal=True, key="q5")
            
            st.markdown("")
            
            submitted = st.form_submit_button("📨 SUBMIT ANSWERS!", use_container_width=True)
            
            if submitted:
                user_answers = [q1_answer, q2_answer, q3_answer, q4_answer, q5_answer]
                st.session_state.user_answers = user_answers
                
                correct_count = 0
                wrong_questions = []
                correct_answers = st.session_state.correct_answers
                
                for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
                    if user_ans.upper() == correct_ans.upper():
                        correct_count += 1
                    else:
                        wrong_questions.append(i + 1)
                
                st.session_state.wrong_questions = wrong_questions
                
                quiz_score = correct_count * 10
                st.session_state.score = quiz_score
                
                if correct_count == 5:
                    st.session_state.perfect_scores += 1
                
                if correct_count < 3 and st.session_state.current_topic:
                    if st.session_state.current_topic not in st.session_state.weak_topics:
                        st.session_state.weak_topics.append(st.session_state.current_topic)
                
                st.session_state.total_score += quiz_score
                st.session_state.quizzes_completed += 1
                
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
        
        correct_count = sum(1 for u, c in zip(user_answers, correct_answers) if u.upper() == c.upper())
        
        if correct_count == 5:
            st.balloons()
            st.snow()
        elif correct_count >= 4:
            st.balloons()
        
        if correct_count == 5:
            st.success(f"""
            ## 🏆 PERFECT SCORE! 🏆
            ### You got **{correct_count}/5** correct!
            ### **+{score} XP** earned! 
            
            🌟 You're absolutely CRUSHING it! Your brain is on fire! 🔥
            """)
        elif correct_count >= 4:
            st.success(f"""
            ## 🎉 Amazing Job! 🎉
            ### You got **{correct_count}/5** correct!
            ### **+{score} XP** earned!
            
            💪 So close to perfect! You're a knowledge machine!
            """)
        elif correct_count >= 3:
            st.info(f"""
            ## 👍 Nice Work!
            ### You got **{correct_count}/5** correct!
            ### **+{score} XP** earned!
            
            📈 You're learning and growing! Keep going!
            """)
        else:
            st.warning(f"""
            ## 💪 Keep Practicing!
            ### You got **{correct_count}/5** correct.
            ### **+{score} XP** earned.
            
            🌱 Every quiz makes you smarter! Try again!
            """)
            if st.session_state.current_topic:
                st.info(f"📖 **{st.session_state.current_topic}** added to your practice list!")
        
        new_level = calculate_level(st.session_state.total_score)
        st.markdown(f"### 📈 Total: **{st.session_state.total_score} XP** | Level **{new_level}**")
        
        new_badges = check_and_award_badges()
        if new_badges:
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
        
        if wrong_questions:
            st.markdown("---")
            st.markdown("### 📝 Let's Learn From These!")
            st.markdown("*Here's what you missed and why:*")
            
            question_labels = ["Question 1 🔢", "Question 2 🧮", "Question 3 🎯", "Question 4 🌟", "Question 5 🏆"]
            
            for i in range(5):
                if (i + 1) in wrong_questions:
                    user_ans = user_answers[i] if i < len(user_answers) else "?"
                    correct_ans = correct_answers[i] if i < len(correct_answers) else "?"
                    explanation = explanations[i] if i < len(explanations) else "No explanation available."
                    
                    st.markdown(f"""
<div class="result-wrong">
<strong>{question_labels[i]}</strong><br><br>
❌ You answered: <strong>{user_ans}</strong><br>
✅ Correct answer: <strong>{correct_ans}</strong><br><br>
💡 <em>{explanation}</em>
</div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("---")
            st.markdown("### 🌟 FLAWLESS! You got everything right! 🌟")
            st.markdown("*No corrections needed - you're already a pro at this! 😎*")
        
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
            st.session_state.answers_submitted = False
            st.session_state.correct_answers = []
            st.session_state.explanations = []
            st.session_state.user_answers = []
            st.session_state.score = 0
            st.session_state.wrong_questions = []
            st.rerun()

# ============================================================
# FOOTER - Credits and Ethics Reminder
# ============================================================
st.markdown("---")

# Final ethics reminder
st.markdown("""
<div style="background: linear-gradient(135deg, #dfe6e9 0%, #b2bec3 100%); 
            padding: 20px; 
            border-radius: 15px; 
            text-align: center; 
            margin-bottom: 20px;">
    <strong>🌟 Remember:</strong> The best learning happens when you challenge yourself! 
    <br>Use this tool to <em>strengthen</em> your understanding, not replace it.
    <br><small>Think critically. Question everything. Stay curious! 🔍</small>
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
