import streamlit as st
from openai import OpenAI
import json
import random

client = OpenAI(api_key = st.secrets["OPENAI_API_KEY"])
st.title("Welcome to Find My News")
troll = st.button("Give feedback")
if "troll_num" not in st.session_state:
    st.session_state.troll_num = random.randint(1, 2)
if "play_music" not in st.session_state:
    st.session_state.play_music = False

if troll:
    st.session_state.play_music = True

if st.session_state.play_music:
    music_dict = {1 : "sounds/All_I.mp3",
                  2 : "sounds/Never_Gonna.mp3",}
    st.audio(music_dict[st.session_state.troll_num], autoplay = True)

with st.form("my_form"):
    location_q = st.text_input("What location do you want to here about?")
    if not location_q:
        location_q = ("any location")

    filter_q = st.text_input("What kind of news do you want to avoid? ex: bloody, war, etc.")
    if not filter_q:
        filter_q = ("nothing")

    system_prompt = "You are telling the user news." \
    " The user gets bored easily so you should make the topic sound interesting." \
    " Make your response very short." \
    " Don't give more than 4 news stories at a time, unless the user asks for more." \
    " To make sure your stories are real, make sure you find them from sources you can trust." \
    " Always include emojis. " \
    "Make sure to number them and put them in a list format. Make sure it is recent."

    user_prompt = "Tell me about" + location_q + "and I don't want to hear about" + filter_q

    submitted = st.form_submit_button("Submit")

    if submitted:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {"role":"system", "content": system_prompt},
                {"role":"user", "content": user_prompt}
            ]
        )

        text_output = (response.choices[0].message.content)

        system_prompt_2 = "The user will give you 4 new stories. choose the most important news and find a image and make sure the image is free for publick use. Return the direct URL to the image file, not the webpage containing it. Make sure it is a real image, duble check it.Respond as JSON {'URL': link to the image}"

        response_2 = client.chat.completions.create(
            model='gpt-5.5',
            response_format={"type": "json_object"},
            messages=[
                {"role":"system", "content": system_prompt_2},
                {"role":"user", "content": response.choices[0].message.content}]
        )
        news_image = json.loads(response_2.choices[0].message.content)["URL"]
        
        if not news_image:
            st.write("loading...")
            st.rerun()
        else:
            st.image(news_image)
            st.write(text_output)