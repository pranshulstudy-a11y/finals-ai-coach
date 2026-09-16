import streamlit as st
from google import genai
from google.genai import types

# --- Page Setup ---
st.set_page_config(page_title="The Finals GPT", page_icon="🪙")
st.title("🪙 The Finals GPT")
st.caption("Ask me anything about THE FINALS: loadouts, lore, Season 11 meta, or map strategies.")

# --- API Key Setup ---
api_key = st.sidebar.text_input("Gemini API Key", type="password")
st.sidebar.markdown("[Get a free API key here](https://aistudio.google.com/)")

# --- System Prompt ---
# This tells the AI who it is and sets the boundaries for its knowledge.
SYSTEM_INSTRUCTION = """
You are a highly knowledgeable ChatGPT-style assistant dedicated entirely to the video game 'THE FINALS' by Embark Studios.
You can answer absolutely anything about the game:
- Lore and sponsors (like ALFA ACTA, ISEUL-T, CNS, VAIIYA).
- Weapons and the current Season 11 Meta (e.g., M11 for Light, FCAR/CB-01 for Medium, ShAK-50/KS-23 for Heavy).
- Strategies for World Tour, Cashout, Terminal Attack, and Power Shift.
- Class mechanics, gadgets, and destruction physics.

Be conversational, helpful, and format your answers beautifully using markdown, bullet points, and bold text. 
If the user asks about something unrelated to THE FINALS, gently steer the conversation back to the game.
"""

# --- Chat History Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome to the Arena! I'm your dedicated *THE FINALS* AI. Ask me anything about weapons, lore, or how to counter that annoying Light sniper."}
    ]

# --- Display Chat History ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input & Streaming Response ---
if prompt := st.chat_input("Ask anything about the game..."):
    if not api_key:
        st.warning("Please enter your Gemini API Key in the sidebar first.")
    else:
        # 1. Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Prepare conversation history for the Gemini API
        contents = []
        for m in st.session_state.messages:
            # Gemini expects 'user' or 'model' roles
            role = "user" if m["role"] == "user" else "model"
            contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=m["content"])])
            )

        # 3. Stream the response from the AI
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                client = genai.Client(api_key=api_key)
                
                # We use generate_content_stream to get the typing effect
                response_stream = client.models.generate_content_stream(
                   model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7,
                    )
                )
                
                for chunk in response_stream:
                    full_response += chunk.text
                    # The "▌" adds a blinking cursor effect while typing
                    message_placeholder.markdown(full_response + "▌")
                
                # Remove the cursor when finished
                message_placeholder.markdown(full_response)
                
                # Save the assistant's response to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                message_placeholder.error(f"Something went wrong: {e}")
