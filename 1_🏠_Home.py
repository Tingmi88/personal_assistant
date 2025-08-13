import streamlit as st
import argparse
from streamlit_pills import pills

from st_utils import (
    add_builder_config,
    add_sidebar,
    get_current_state,
    get_weather,
    parse_args,
    get_nyt_stories
)

# Steps
# 1. parse command-line arguments
# 2. Retrieve the current state
# 3. Page configuration
# 4. Add additional channels
# 5. Add pills

# step-1: parse command-line arguments
args = parse_args()

# step-2: retrieve the current state
current_state = get_current_state()

####################
#### STREAMLIT #####
####################

# step-3: page configuration
st.set_page_config(
    page_title=f"{args.title}, what can I do for you today 😎?",
    page_icon="🦙",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None,
)

st.markdown(
    f'<h1 style="font-size: 2 em; color: black;">{args.title} 😎</h1>',
    unsafe_allow_html=True
)

if "metaphor_key" in st.secrets:
    st.info("**NOTE**: The ability to add web search is enabled.")

#add_builder_config()
add_sidebar()

#st.info(f"Currently building/editing agent: {current_state.cache.agent_id}", icon="ℹ️")

## step-4: add weather channel

st.write("")
st.write("")
if args.city:
    city_name = args.city
    weather_data = get_weather(city_name)

    if 'current' in weather_data:
        current = weather_data['current']
        temperature = current['temperature']
        weather_descriptions = current['weather_descriptions']
        humidity = current['humidity']
        wind_speed = current['wind_speed']

        st.subheader(f"🌤️ Current weather in {city_name}:")
        st.write(f"Temperature: {temperature}°C")
        st.write(f"Weather: {', '.join(weather_descriptions)}")
        st.write(f"Humidity: {humidity}%")
        st.write(f"Wind Speed: {wind_speed} km/h")
    else:
        st.error("City not found or API request failed.")

### step-4: add NYT top storeis
# Fetch top stories from the 'home' section
top_stories = get_nyt_stories()[:3]

# Display the top stories
st.subheader("🗞️ New York Times Top Stories:")

for story in top_stories:
    st.caption(story["title"])
    st.write(f"**By:** {story.get('byline', 'N/A')}")
    st.write(f"**Published on:** {story['published_date'].strftime('%B %d, %Y')}")
    st.write(story["abstract"])
    st.markdown(f"[Read more]({story['url']})")
    if story.get("multimedia") and story["multimedia"][0].get("url"):
        st.image(story["multimedia"][0]["url"], width=700)
    else:
        st.write("No image available.")
    st.write("---")

# step-5: add messages
if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "What can I do for you today?"}
    ]

def add_to_message_history(role: str, content: str) -> None:
    message = {"role": role, "content": str(content)}
    st.session_state.messages.append(message)  # Add response to message history

for message in st.session_state.messages:  # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# step-5: add pills
# we have to be careful not to add selected messages to the chat history multiple times
st.write("")
if 'show_pills' not in st.session_state:
    st.session_state.show_pills = True

if st.session_state.show_pills:
    selected = pills(
        "☕ Outline your task today!",
        [
            "I want you to recommend me some musics",
            "I want you to recommend me some books",
            "I want you to recommend me some recipes",
            "I want to analyze this PDF file (data/invoices.pdf)",
            "I want to search over my CSV documents",
        ],
        clearable=True,
        index=None,
    )
    if selected:
        st.session_state.show_pills = False
else:
    selected = None

if "selected_pill" not in st.session_state:
    st.session_state.selected_pill = None

if selected and selected != st.session_state.selected_pill:
    # Add the selected pill as a user message
    add_to_message_history("user", selected)
    with st.chat_message("user"):
        st.write(selected)

# Generate and display the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = current_state.builder_agent.chat(selected)
            st.write(str(response))
            add_to_message_history("assistant", str(response))
        # Reset the pill selection to prevent duplicate processing
        st.session_state.selected_pill = selected

# TODO: this is really hacky, only because st.rerun is jank
if prompt := st.chat_input(
    "Your question",
):  # Prompt for user input and save to chat history
    # TODO: hacky
    if "has_rerun" in st.session_state.keys() and st.session_state.has_rerun:
        # if this is true, skip the user input
        st.session_state.has_rerun = False
    else:
        add_to_message_history("user", prompt)
        with st.chat_message("user"):
            st.write(prompt)

        # If last message is not from assistant, generate a new response
        if st.session_state.messages[-1]["role"] != "assistant":
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = current_state.builder_agent.chat(prompt)
                    st.write(str(response))
                    add_to_message_history("assistant", str(response))

        else:
            pass
        # check agent_ids again
        # if it doesn't match, add to directory and refresh
        agent_ids = current_state.agent_registry.get_agent_ids()
        # check diff between agent_ids and cur agent ids
        diff_ids = list(set(agent_ids) - set(st.session_state.cur_agent_ids))
        if len(diff_ids) > 0:
            # # clear streamlit cache, to allow you to generate a new agent
            # st.cache_resource.clear()
            st.session_state.has_rerun = True
            st.rerun()

else:
    # TODO: set has_rerun to False
    st.session_state.has_rerun = False