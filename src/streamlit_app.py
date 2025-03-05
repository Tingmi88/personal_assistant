import streamlit as st
from rag_chatbot import generate_book_recommendation

st.title("Book Recommendation Agent with LlamaIndex")

user_input = st.text_input("Enter a book genre or author: ", "")

# Add a button to apply the input
if st.button("Get Recommendations"):
    if user_input:
        recommendation = generate_book_recommendation(user_input)
        st.write(f"Recommended Books: {recommendation}")
    else:
        st.write("Please enter a genre or author to get recommendations.") 