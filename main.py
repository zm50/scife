import streamlit as st

st.title("Translation")

word = st.text_input("Enter a word")

if st.button("Submit"):
    st.write("The word:" + word)
