import streamlit as st
from rag_chatbot import generate_book_recommendation

# Set page title
st.title("Book Recommendation Agent with LlamaIndex")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Add a sidebar with options
with st.sidebar:
    st.header("Options")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This chatbot recommends books based on your interests. Ask about genres, authors, or topics!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask about book recommendations...")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Finding great books for you..."):
            # Get only the last 5 exchanges to keep context relevant but not overwhelming
            recent_conversation = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
            conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in recent_conversation])
            
            # Generate recommendation with context
            recommendation = generate_book_recommendation(
                user_input, 
                conversation_history=conversation_history
            )
            
            # Display the response
            st.markdown(recommendation)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": recommendation})