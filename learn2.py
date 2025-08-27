import streamlit as st
import time

st.header('Empty: st.empty')

placeholder = st.empty()

for i in range(1,11):
    placeholder.write('This message will disappear in {} seconds'.format(10-i))
    time.sleep(1)
    
placeholder.empty()