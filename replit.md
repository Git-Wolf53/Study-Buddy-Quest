# Study Buddy Quest

## Overview

Study Buddy Quest is an educational web application built for the Presidential AI Challenge. It's a quiz generation app that helps students learn any topic through engaging, AI-generated quizzes. Users can enter any subject they want to study, select a difficulty level (Easy, Medium, or Hard), and receive a 5-question multiple choice quiz with instant feedback and explanations.

The application uses Google's Gemini AI to dynamically generate quiz questions and includes features like text-to-speech support, celebratory animations, and a teen-friendly design with emojis and colorful UI elements.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Framework
- **Streamlit**: The entire application is built using Streamlit, a Python framework for creating web applications. This was chosen for its simplicity and rapid development capabilities, making it ideal for educational projects and prototyping.
- Single-file architecture (`main.py`) contains all application logic, which keeps the project simple and easy to understand.

### AI Integration
- **Google Gemini API**: Used for dynamically generating quiz questions based on user-provided topics and difficulty levels. The API key is loaded from environment variables (`GEMINI_API_KEY`).
- The `google-genai` client library is used to interact with the Gemini API.

### Text-to-Speech
- **gTTS (Google Text-to-Speech)**: Integrated for accessibility, allowing quiz content to be read aloud to users.

### State Management
- **Streamlit Session State**: Used to maintain quiz state, user answers, and application flow across interactions.

### Configuration
- Streamlit configuration is stored in `.streamlit/config.toml` for customizing server behavior and appearance.

## External Dependencies

### APIs
- **Google Gemini API**: Required for quiz generation. Users must provide their own API key via the `GEMINI_API_KEY` environment variable. Free keys can be obtained from Google AI Studio.

### Python Libraries
- `streamlit`: Web application framework
- `google-genai`: Google Gemini AI client library
- `gtts`: Google Text-to-Speech for audio generation

### Environment Variables
- `GEMINI_API_KEY`: Required. The Google Gemini API key for AI-powered quiz generation.