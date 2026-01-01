# ============================================================
# Study Buddy Quest 🧠
# A fun, interactive quiz app for students!
# Built for the Presidential AI Challenge
# ============================================================

# Import the Streamlit library - this is what makes our web app work!
import streamlit as st

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
# GENERATE QUIZ BUTTON
# The main action button that creates the quiz
# ============================================================

# Add some space before the button
st.markdown("")
st.markdown("")

# Create the big "Generate Quiz!" button
# When clicked, this will show our sample quiz
if st.button("🎲 Generate Quiz! 🎲", use_container_width=True):
    
    # Check if the user entered a topic
    if not topic:
        # If no topic, show a friendly warning
        st.warning("⚠️ Oops! Please enter a topic first! What do you want to learn about?")
    else:
        # Topic was entered - let's show the quiz!
        
        # 🎈 BALLOONS! Because learning should be fun!
        st.balloons()
        
        # Show a success message
        st.success(f"🎉 Awesome! Here's your {difficulty} quiz about **{topic}**!")
        
        # ============================================================
        # SAMPLE QUIZ DISPLAY
        # This shows a placeholder quiz with 5 questions
        # Later, we can replace this with AI-generated questions!
        # ============================================================
        
        st.markdown("---")
        st.markdown("## 📝 Your Quiz")
        
        # Question 1
        st.markdown(f"""
### Question 1 🔢
**What is the main concept of {topic}?**

- A) The first option about {topic}
- B) The second option explaining {topic}
- C) The third possible answer ✅ **(Correct!)**
- D) The fourth choice

> 💡 **Explanation:** This is the correct answer because it best describes the fundamental concept of {topic}. Great job if you got it right!
        """)
        
        st.markdown("---")
        
        # Question 2
        st.markdown(f"""
### Question 2 🧮
**Which example best demonstrates {topic}?**

- A) Example one
- B) Example two ✅ **(Correct!)**
- C) Example three
- D) Example four

> 💡 **Explanation:** Option B is correct because it shows a real-world application of {topic}. Understanding examples helps you remember better!
        """)
        
        st.markdown("---")
        
        # Question 3
        st.markdown(f"""
### Question 3 🎯
**Why is {topic} important to learn?**

- A) It's not that important
- B) Only for tests
- C) It helps in daily life
- D) It builds foundation for advanced topics ✅ **(Correct!)**

> 💡 **Explanation:** Learning {topic} creates a strong foundation that helps you understand more complex ideas later. Keep building those skills!
        """)
        
        st.markdown("---")
        
        # Question 4
        st.markdown(f"""
### Question 4 🌟
**What's a common mistake when learning {topic}?**

- A) Practicing too much
- B) Rushing through without understanding ✅ **(Correct!)**
- C) Asking too many questions
- D) Taking notes

> 💡 **Explanation:** Taking your time to truly understand {topic} is key! It's better to go slow and learn well than to rush and forget.
        """)
        
        st.markdown("---")
        
        # Question 5
        st.markdown(f"""
### Question 5 🏆
**How can you master {topic}?**

- A) Just read about it once
- B) Practice regularly and ask questions ✅ **(Correct!)**
- C) Only study before tests
- D) Skip the hard parts

> 💡 **Explanation:** Regular practice and curiosity are the keys to mastering any topic! You're already on the right track by using Study Buddy Quest!
        """)
        
        # Final encouragement
        st.markdown("---")
        st.markdown("""
        ## 🎊 Quiz Complete! 🎊
        
        **You did amazing!** 🌟
        
        Remember: Every question you answer makes you smarter! 
        Keep questing, Study Buddy! 💪🧠
        """)

# ============================================================
# FOOTER
# A nice footer to end the page
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; padding: 20px;'>
    Made with 💜 for the Presidential AI Challenge<br>
    <small>Study Buddy Quest v1.0 | Day 1</small>
</div>
""", unsafe_allow_html=True)
