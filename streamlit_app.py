
import streamlit as st
from openai import OpenAI
import json
import random

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Welcome to Find My News")

# Initialize session state
if "troll_num" not in st.session_state:
    st.session_state.troll_num = random.randint(1, 2)

if "play_music" not in st.session_state:
    st.session_state.play_music = False

if "news_text" not in st.session_state:
    st.session_state.news_text = None

if "news_image" not in st.session_state:
    st.session_state.news_image = None

music_dict = {
    1: "sounds/All_I.mp3",
    2: "sounds/Never_Gonna.mp3"
}

# Audio button
if st.button("Give feedback"):
    st.session_state.play_music = True

# Keep audio player visible after reruns
if st.session_state.play_music:
    st.audio(
        music_dict[st.session_state.troll_num],
        format="audio/mpeg",
        autoplay=True
    )

# News form
with st.form("my_form"):
    location_q = st.text_input(
        "What location do you want to hear about?"
    )

    filter_q = st.text_input(
        "What kind of news do you want to avoid?"
    )

    submitted = st.form_submit_button("Submit")

# Process form outside the form block
if submitted:
    location_q = location_q or "any location"
    filter_q = filter_q or "nothing"

    system_prompt = (
        "You are telling the user news. "
        "Make the topic interesting and the response very short. "
        "Give no more than 4 news stories. "
        "Use trustworthy sources. "
        "Always include emojis and number the stories. "
        "Make sure the news is recent."
    )

    user_prompt = (
        f"Tell me about {location_q} "
        f"and I don't want to hear about {filter_q}."
    )

    with st.spinner("Finding news..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        text_output = response.choices[0].message.content

        system_prompt_2 = (
            "Choose the most important news story. "
            "Find a publicly usable image related to it. "
            "Return a direct image URL as JSON with the key 'URL'. "
            "If you cannot find one, return an empty string."
        )

        response_2 = client.chat.completions.create(
            model="gpt-5.5",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt_2},
                {"role": "user", "content": text_output}
            ]
        )

        image_data = json.loads(
            response_2.choices[0].message.content
        )

        st.session_state.news_text = text_output
        st.session_state.news_image = image_data.get("URL")

# Display saved results
if st.session_state.news_text:
    if st.session_state.news_image:
        st.image(st.session_state.news_image)

    st.write(st.session_state.news_text)
