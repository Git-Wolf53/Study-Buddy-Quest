import streamlit as st

st.title("Hello World App")

word = st.text_input("Enter a word:")

if word:
    st.write(f"Hello {word}")
