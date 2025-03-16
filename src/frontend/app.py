import streamlit as st
import pandas as pd

import sys
import os 

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database methods
from backend.db_methods import get_card, populate_tables, retrieve_card_pricing_table, retrieve_pokemon_information_table

st.title('Pokemon Trading Card Scanner')
scan_tab, collection_tab = st.tabs(['Scan', 'Collection'])

# Initial scan info
if 'scanned_image' not in st.session_state:
    st.session_state.scanned_image = None
if 'scanned_data' not in st.session_state:
    st.session_state.scanned_data = None
if 'scanned_name' not in st.session_state:
    st.session_state.scanned_name = None
if 'scanned_id' not in st.session_state:
    st.session_state.scanned_id = None

# Send card to scan
def scan_card(image):
    # TODO: send to model
    
    card_id = "xy1-146"
    st.session_state.scanned_id = card_id
    card = get_card(card_id) # call database method to get card info from id
    st.session_state.scanned_data = card['data']
    st.session_state.scanned_name = card['data']['name']


# Dialog for camera
@st.dialog('Scan from Camera')
def scan_from_camera():
    st.write('Scanning from camera')
    img = st.camera_input('Take a picture')
    if img:
        st.image(img)
        if st.button('Scan'):
            scan_card(img)
            st.session_state.scanned_image = img
            st.rerun()

# Dialog for file upload
@st.dialog('Scan from File')
def scan_from_file():
    st.write('Scanning from file')
    img = st.file_uploader('Upload a picture')
    if img:
        st.image(img)
        if st.button('Scan'):
            scan_card(img)
            st.session_state.scanned_image = img
            st.rerun()

# Scan tab
with scan_tab:
    st.header('Scan a new card')

    # Buttons to scan image
    col1, col2, col3 = st.columns([5, 5, 10])
    with col1:
        st.button('Scan from camera', on_click=scan_from_camera)
    with col2:
        st.button('Scan from file', on_click=scan_from_file)

    # Display scanned card name
    if st.session_state.scanned_data:
        st.subheader(f'Scanned card: {st.session_state.scanned_name}')
    col1, col2 = st.columns(2)
    
    # Display scanned image
    with col1:
        if st.session_state.scanned_image:
            st.image(st.session_state.scanned_image)

    # Display scanned data
    with col2:
        if st.session_state.scanned_data:
            # TODO: filter what data we want to display here when scanning card
            scanned_data_df = pd.DataFrame([st.session_state.scanned_data])
            scanned_data_df = scanned_data_df.transpose()
            scanned_data_df_html = scanned_data_df.to_html(header=False)
            st.markdown(scanned_data_df_html, unsafe_allow_html=True)

            # Button to add to database
            if st.button('Add to collection', type='primary'):
                # Add to database
                populate_tables(st.session_state.scanned_id)
                st.success('Added to collection!')

# Collection tab
with collection_tab:
    st.header('Collection')
    
    collection_prices_df = retrieve_card_pricing_table()
    collection_info_df = retrieve_pokemon_information_table()

    # Card Pricing Table
    st.subheader('Card Pricing Table')
    st.dataframe(
        collection_prices_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Image': st.column_config.ImageColumn(width='small'),
            'Price URL': st.column_config.LinkColumn()
        })
    
    # Pokemon Information Table
    st.subheader('Pokemon Information Table')
    st.dataframe(
        collection_info_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Image': st.column_config.ImageColumn(width='small'),
            'Price URL': st.column_config.LinkColumn()
        })

