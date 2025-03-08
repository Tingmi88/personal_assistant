import streamlit as st
from rag_chatbot import generate_book_recommendation

# Set page title and configuration
st.set_page_config(page_title="Book Recommendation & Information Assistant", layout="wide")
st.title("📚 Book Recommendation Assistant")

# Add description
st.markdown("""
This intelligent assistant helps with:
- Book recommendations based on your interests
- Information about current bestsellers and popular books
- General questions about books and authors
- Basic information and facts when you need them
""")

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
    st.markdown("### How to use")
    st.markdown("""
    - Ask for book recommendations by genre, author, or theme
    - Ask about current bestsellers or popular books
    - Get information about new releases
    - Ask general questions when you need quick information
    - Follow up on recommendations for more details
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Ask about books or anything else...")

# Process user input
if user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get only the recent conversation to keep context relevant
            recent_conversation = st.session_state.messages[-10:] if len(st.session_state.messages) > 10 else st.session_state.messages
            conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in recent_conversation])
            
            # Generate recommendation with context
            response = generate_book_recommendation(
                user_input, 
                conversation_history=conversation_history
            )
            
            # Display the response
            st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})