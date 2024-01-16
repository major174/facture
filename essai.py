import streamlit as st

input = st.text_input("text", key="text")
nom=st.text_input("nom", key="nom")
def clear_text():
    st.session_state["text"] = ""
    st.session_state["nom"] = ""
selecter=[]  
selecter.append(input)
selecter.append
st.write(selecter)
st.button("clear text input", on_click=clear_text)

    
