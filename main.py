# ============================================================
# Study Buddy Quest 🧠
# A fun, interactive quiz app for students!
# Built for the Presidential AI Challenge
# ============================================================

# Import the Streamlit library - this is what makes our web app work!
import streamlit as st

# Import os to access our secret API key
import os

# Import re for parsing the quiz answers
import re

# Import Google's Generative AI library for Gemini
# Blueprint: python_gemini - using direct API key integration
from google import genai

# ============================================================
# GEMINI CONFIGURATION
# Set up the Gemini AI client with our API key from Replit Secrets
# ============================================================
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# ============================================================
# PAGE CONFIGURATION
# This sets up how our page looks in the browser tab
# ============================================================
st.set_page_config(
    page_title="Study Buddy Quest 🧠",  # Shows in browser tab
    page_icon="🧠",                      # Favicon in browser tab
    layout="centered"                    # Centers our content nicely
)

# ============================================================
# SESSION STATE INITIALIZATION
# We use session state to remember the quiz between interactions
# ============================================================
if "quiz_content" not in st.session_state:
    st.session_state.quiz_content = None
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

# ============================================================
# GAMIFICATION: TOTAL SCORE AND LEVEL TRACKING
# Keep track of points across all quizzes!
# ============================================================
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "quizzes_completed" not in st.session_state:
    st.session_state.quizzes_completed = 0


def calculate_level(total_points: int) -> int:
    """
    Calculate the player's level based on total points.
    Level 1 starts at 0 points, +1 level every 50 points.
    """
    return 1 + (total_points // 50)


def get_points_for_next_level(total_points: int) -> tuple:
    """
    Calculate progress toward the next level.
    Returns (points_into_current_level, points_needed_for_next_level)
    """
    current_level = calculate_level(total_points)
    points_at_current_level_start = (current_level - 1) * 50
    points_into_level = total_points - points_at_current_level_start
    points_needed = 50  # Always 50 points per level
    return points_into_level, points_needed


def get_level_title(level: int) -> str:
    """
    Get a fun title based on the player's level!
    """
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


# ============================================================
# CUSTOM STYLING
# Adding some colorful CSS to make our app look awesome!
# ============================================================
st.markdown("""
<style>
    /* Make the main title colorful and fun */
    .big-title {
        font-size: 3rem;
        text-align: center;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        margin-bottom: 0;
    }
    
    /* Style for the encouraging message */
    .encourage-msg {
        text-align: center;
        font-size: 1.3rem;
        color: #666;
        margin-top: 10px;
    }
    
    /* Make buttons look cooler */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.2rem;
        padding: 15px 30px;
        border-radius: 25px;
        border: none;
        width: 100%;
        transition: transform 0.3s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    /* Style for correct answers */
    .correct-answer {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    /* Style for wrong answers */
    .wrong-answer {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    /* Level display styling */
    .level-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .level-number {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    
    .level-title {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 5px 0;
    }
    
    .points-display {
        font-size: 1.1rem;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# MAIN TITLE AND WELCOME MESSAGE
# Let's greet our users with enthusiasm!
# ============================================================

# Display the big colorful title using our custom CSS class
st.markdown('<h1 class="big-title">🎮 Study Buddy Quest 🧠</h1>', unsafe_allow_html=True)

# Show an encouraging message to motivate students
st.markdown('<p class="encourage-msg">Level up your knowledge, one quiz at a time! 🚀✨</p>', unsafe_allow_html=True)

# ============================================================
# GAMIFICATION DISPLAY
# Show current level, total points, and progress to next level
# ============================================================

# Calculate current level and progress
current_level = calculate_level(st.session_state.total_score)
level_title = get_level_title(current_level)
points_into_level, points_needed = get_points_for_next_level(st.session_state.total_score)
progress_percentage = points_into_level / points_needed

# Display the level card
st.markdown(f"""
<div class="level-display">
    <p class="level-number">⭐ Level {current_level} ⭐</p>
    <p class="level-title">{level_title}</p>
    <p class="points-display">🏆 Total Points: {st.session_state.total_score} | 📚 Quizzes: {st.session_state.quizzes_completed}</p>
</div>
""", unsafe_allow_html=True)

# Progress bar toward next level
st.markdown(f"**Progress to Level {current_level + 1}:** {points_into_level}/{points_needed} points")
st.progress(progress_percentage)

# Add some space
st.markdown("---")

# ============================================================
# USER INPUT SECTION
# This is where students enter what they want to learn about
# ============================================================

# Create two columns for a nicer layout
col1, col2 = st.columns(2)

# Column 1: Topic input
with col1:
    # Text input where students type their study topic
    # The placeholder shows an example to help them understand
    topic = st.text_input(
        "📚 What do you want to study?",
        placeholder="e.g., fractions",
        help="Type any topic you want to learn about!"
    )

# Column 2: Difficulty selector
with col2:
    # Selectbox lets students pick how hard they want the quiz
    difficulty = st.selectbox(
        "🎯 Choose your difficulty level:",
        options=["Easy 🌱", "Medium 🌿", "Hard 🌳"],
        help="Pick based on how confident you feel!"
    )

# Add some encouraging text based on difficulty
if difficulty == "Easy 🌱":
    st.info("💪 Great choice! Perfect for learning the basics!")
elif difficulty == "Medium 🌿":
    st.info("🔥 Nice! You're ready for a challenge!")
else:
    st.info("🏆 Wow! You're going for the tough stuff! Respect!")


# ============================================================
# QUIZ PARSING FUNCTION
# Extract correct answers and explanations from Gemini's response
# ============================================================
def parse_quiz_answers(quiz_text: str) -> tuple:
    """
    Parses the quiz text to extract correct answers and explanations.
    
    Args:
        quiz_text: The markdown quiz generated by Gemini
        
    Returns:
        A tuple of (correct_answers_list, explanations_list)
    """
    correct_answers = []
    explanations = []
    
    # Regex pattern to find correct answers
    # Matches: ✅ **Correct Answer: A** (with variations in spacing/formatting)
    answer_pattern = r"✅\s*\*\*Correct Answer:\s*([A-Da-d])\s*\*\*"
    
    # Regex pattern to find explanations
    # Matches: > 💡 **Explanation:** [text until end of line or next section]
    explanation_pattern = r">\s*💡\s*\*\*Explanation:\*\*\s*(.+?)(?=\n\n|---|\n###|$)"
    
    # Find all correct answers
    answer_matches = re.findall(answer_pattern, quiz_text, re.IGNORECASE)
    for match in answer_matches:
        correct_answers.append(match.upper())
    
    # Find all explanations
    explanation_matches = re.findall(explanation_pattern, quiz_text, re.DOTALL)
    for match in explanation_matches:
        # Clean up the explanation text
        clean_explanation = match.strip()
        explanations.append(clean_explanation)
    
    return correct_answers, explanations


# ============================================================
# QUIZ GENERATION FUNCTION
# This function calls Gemini AI to create a fun quiz!
# ============================================================
def generate_quiz_with_gemini(topic: str, difficulty: str) -> str:
    """
    Uses Google Gemini AI to generate a fun, educational quiz.
    
    Args:
        topic: The subject the student wants to learn about
        difficulty: Easy, Medium, or Hard
        
    Returns:
        A string containing the quiz in markdown format
    """
    
    # Clean the difficulty level (remove emoji)
    clean_difficulty = difficulty.split()[0]  # Gets just "Easy", "Medium", or "Hard"
    
    # Create a detailed prompt for Gemini
    # This tells the AI exactly what kind of quiz we want!
    prompt = f"""You are a fun and encouraging teacher creating a quiz for a 14-year-old student.

Create a 5-question multiple-choice quiz about: {topic}
Difficulty level: {clean_difficulty}

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
    
    # Call the Gemini API to generate the quiz
    response = client.models.generate_content(
        model="gemini-2.5-flash",  # Using the fast, efficient model
        contents=prompt
    )
    
    # Return the generated quiz text
    return response.text if response.text else "Sorry, couldn't generate a quiz. Please try again!"


# ============================================================
# GENERATE QUIZ BUTTON
# The main action button that creates the quiz
# ============================================================

# Add some space before the button
st.markdown("")
st.markdown("")

# Create the big "Generate Quiz!" button
# When clicked, this will call Gemini to generate a real quiz!
if st.button("🎲 Generate Quiz! 🎲", use_container_width=True):
    
    # Check if the user entered a topic
    if not topic:
        # If no topic, show a friendly warning
        st.warning("⚠️ Oops! Please enter a topic first! What do you want to learn about?")
    else:
        # Topic was entered - let's generate the quiz!
        
        # 🎈 BALLOONS! Because learning should be fun!
        st.balloons()
        
        # Reset quiz-specific state for new quiz (but keep total score!)
        st.session_state.answers_submitted = False
        st.session_state.correct_answers = []
        st.session_state.explanations = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        
        # Show a loading message while Gemini generates the quiz
        with st.spinner(f"🧠 Creating your {difficulty} quiz about {topic}... This is gonna be awesome!"):
            try:
                # Call our function to generate the quiz with Gemini
                quiz_content = generate_quiz_with_gemini(topic, difficulty)
                
                # Parse the correct answers and explanations
                correct_answers, explanations = parse_quiz_answers(quiz_content)
                
                # Store everything in session state
                st.session_state.quiz_content = quiz_content
                st.session_state.quiz_generated = True
                st.session_state.correct_answers = correct_answers
                st.session_state.explanations = explanations
                
                # Show a success message
                st.success(f"🎉 Your quiz is ready! Let's see how much you know about **{topic}**!")
                
            except Exception as e:
                # If something goes wrong, show a friendly error message
                st.error(f"😅 Oops! Something went wrong while creating your quiz. Please try again!")
                st.error(f"Error details: {str(e)}")

# ============================================================
# DISPLAY QUIZ AND ANSWER FORM
# Show the quiz and let students submit their answers
# ============================================================

# Check if we have a quiz to display
if st.session_state.quiz_generated and st.session_state.quiz_content:
    
    # Display the quiz content
    st.markdown("---")
    st.markdown(st.session_state.quiz_content)
    
    # Only show the answer form if answers haven't been submitted yet
    if not st.session_state.answers_submitted:
        # ============================================================
        # ANSWER SUBMISSION FORM
        # Let students select their answers and submit!
        # ============================================================
        
        st.markdown("---")
        st.markdown("## ✏️ Submit Your Answers!")
        st.markdown("Select your answer for each question below:")
        
        # Create a form for submitting answers
        # Using a form prevents the page from reloading on each selection
        with st.form(key="quiz_answers_form"):
            
            # Create 5 radio button groups, one for each question
            # Each group has options A, B, C, D
            
            st.markdown("### Your Answers:")
            
            # Question 1
            q1_answer = st.radio(
                "Question 1 🔢",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key="q1"
            )
            
            # Question 2
            q2_answer = st.radio(
                "Question 2 🧮",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key="q2"
            )
            
            # Question 3
            q3_answer = st.radio(
                "Question 3 🎯",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key="q3"
            )
            
            # Question 4
            q4_answer = st.radio(
                "Question 4 🌟",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key="q4"
            )
            
            # Question 5
            q5_answer = st.radio(
                "Question 5 🏆",
                options=["A", "B", "C", "D"],
                horizontal=True,
                key="q5"
            )
            
            # Add some space
            st.markdown("")
            
            # Submit button for the form
            submitted = st.form_submit_button(
                "📨 Submit Answers!",
                use_container_width=True
            )
            
            # Handle form submission
            if submitted:
                # Collect all user answers
                user_answers = [q1_answer, q2_answer, q3_answer, q4_answer, q5_answer]
                st.session_state.user_answers = user_answers
                
                # Grade the quiz
                correct_count = 0
                correct_answers = st.session_state.correct_answers
                
                # Compare each answer
                for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
                    if user_ans.upper() == correct_ans.upper():
                        correct_count += 1
                
                # Calculate score (10 points per correct answer)
                quiz_score = correct_count * 10
                st.session_state.score = quiz_score
                
                # Add to total score and increment quiz count
                st.session_state.total_score += quiz_score
                st.session_state.quizzes_completed += 1
                
                # Set the flag that answers were submitted
                st.session_state.answers_submitted = True
                
                # Trigger rerun to show results
                st.rerun()
    
    # ============================================================
    # SHOW RESULTS AFTER SUBMISSION
    # Display which answers were right/wrong with explanations
    # ============================================================
    
    if st.session_state.answers_submitted:
        st.markdown("---")
        st.markdown("## 📊 Your Results!")
        
        # Get the stored data
        user_answers = st.session_state.user_answers
        correct_answers = st.session_state.correct_answers
        explanations = st.session_state.explanations
        score = st.session_state.score
        
        # Count correct answers
        correct_count = sum(1 for u, c in zip(user_answers, correct_answers) if u.upper() == c.upper())
        
        # Celebrate with balloons if 4+ correct!
        if correct_count >= 4:
            st.balloons()
        
        # Display score prominently
        if correct_count == 5:
            st.success(f"## 🏆 PERFECT SCORE! 🏆\n### You got **{correct_count}/5** correct!\n### **+{score} points** earned! 🌟")
        elif correct_count >= 4:
            st.success(f"## 🎉 Amazing Job! 🎉\n### You got **{correct_count}/5** correct!\n### **+{score} points** earned! 🌟")
        elif correct_count >= 3:
            st.info(f"## 👍 Good Work!\n### You got **{correct_count}/5** correct!\n### **+{score} points** earned!")
        else:
            st.warning(f"## 💪 Keep Practicing!\n### You got **{correct_count}/5** correct.\n### **+{score} points** earned.\n### You'll do better next time!")
        
        # Show updated total
        new_level = calculate_level(st.session_state.total_score)
        st.markdown(f"### 📈 New Total: **{st.session_state.total_score} points** | Level **{new_level}**")
        
        st.markdown("---")
        st.markdown("### 📝 Detailed Results:")
        
        # Question labels
        question_labels = ["Question 1 🔢", "Question 2 🧮", "Question 3 🎯", "Question 4 🌟", "Question 5 🏆"]
        
        # Show each question's result
        for i in range(5):
            user_ans = user_answers[i] if i < len(user_answers) else "?"
            correct_ans = correct_answers[i] if i < len(correct_answers) else "?"
            explanation = explanations[i] if i < len(explanations) else "No explanation available."
            
            is_correct = user_ans.upper() == correct_ans.upper()
            
            if is_correct:
                st.markdown(f"""
<div class="correct-answer">
<strong>{question_labels[i]}</strong><br>
✅ <strong>Correct!</strong> You answered: <strong>{user_ans}</strong><br>
<em>💡 {explanation}</em>
</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="wrong-answer">
<strong>{question_labels[i]}</strong><br>
❌ You answered: <strong>{user_ans}</strong> | Correct answer: <strong>{correct_ans}</strong><br>
<em>💡 {explanation}</em>
</div>
                """, unsafe_allow_html=True)
        
        # Final encouragement
        st.markdown("---")
        if correct_count >= 4:
            st.markdown("## 🌟 You're a Study Buddy Superstar! 🌟")
            st.markdown("Keep up the amazing work! You're crushing it! 💪🧠")
        else:
            st.markdown("## 💪 Don't Give Up!")
            st.markdown("Every quiz makes you smarter! Try another topic or difficulty level! 🚀")
        
        # Button to try again
        st.markdown("")
        if st.button("🔄 Try Another Quiz!", use_container_width=True):
            # Reset for new quiz (keep total score!)
            st.session_state.quiz_generated = False
            st.session_state.quiz_content = None
            st.session_state.answers_submitted = False
            st.session_state.correct_answers = []
            st.session_state.explanations = []
            st.session_state.user_answers = []
            st.session_state.score = 0
            st.rerun()

# ============================================================
# FOOTER
# A nice footer to end the page
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    Made with 💜 for the Presidential AI Challenge<br>
    <small>Study Buddy Quest v1.0 | Day 1 | Powered by Google Gemini AI ✨</small>
</div>
""", unsafe_allow_html=True)
