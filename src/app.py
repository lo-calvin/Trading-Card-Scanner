import streamlit as st

st.title('Pokemon Trading Card Scanner')
scan_tab, collection_tab = st.tabs(['Scan', 'Collection'])

with scan_tab:
    st.header('Scan a new card')

with collection_tab:
    st.header('Collection')