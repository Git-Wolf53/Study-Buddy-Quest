# ============================================================
# Study Buddy Quest 🧠
# A fun, interactive quiz app for students!
# Built for the Presidential AI Challenge
# ============================================================

# Import the Streamlit library - this is what makes our web app work!
import streamlit as st

# Import os to access our secret API key
import os

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

Format your response EXACTLY like this in clean markdown:

## 📝 Your {clean_difficulty} Quiz on {topic}!

### Question 1 🔢
**[Question text here]**

- A) [Option A]
- B) [Option B]
- C) [Option C]
- D) [Option D]

✅ **Correct Answer: [Letter]**

> 💡 **Explanation:** [Short, friendly explanation that helps the student understand why this is correct. Keep it encouraging!]

---

### Question 2 🧮
[Continue same format...]

---

### Question 3 🎯
[Continue same format...]

---

### Question 4 🌟
[Continue same format...]

---

### Question 5 🏆
[Continue same format...]

---

## 🎊 Quiz Complete!

**Great job working through this quiz!** Keep learning and growing! 🌟

Remember: Every question you tackle makes you smarter! 💪🧠
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
        
        # Reset the answers submitted state for new quiz
        st.session_state.answers_submitted = False
        
        # Show a loading message while Gemini generates the quiz
        with st.spinner(f"🧠 Creating your {difficulty} quiz about {topic}... This is gonna be awesome!"):
            try:
                # Call our function to generate the quiz with Gemini
                quiz_content = generate_quiz_with_gemini(topic, difficulty)
                
                # Store the quiz in session state so it persists
                st.session_state.quiz_content = quiz_content
                st.session_state.quiz_generated = True
                
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
            # Set the flag that answers were submitted
            st.session_state.answers_submitted = True
            
            # Show balloons for fun!
            st.balloons()
            
            # Show success message
            st.success("🎉 Answers submitted! Great job completing the quiz!")

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
