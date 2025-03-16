import streamlit as st
import pandas as pd
import sys
import os 
import asyncio
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Database methods
from backend.db_methods import get_card, populate_tables, retrieve_card_pricing_table, retrieve_pokemon_information_table, delete_card
# Model
from model import Model

model = Model()

st.title('Pokemon Trading Card Scanner')
scan_tab, collection_tab = st.tabs(['Scan', 'Collection'])

# Initial scan info
if 'scanned_image' not in st.session_state:
    st.session_state.scanned_image = None
if 'model_results' not in st.session_state:
    st.session_state.model_results = None
if 'scanned_name' not in st.session_state:
    st.session_state.scanned_name = []
if 'scanned_id' not in st.session_state:
    st.session_state.scanned_id = []

# Send card to scan
def scan_card(image):
    # Temp save image
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_image:
        temp_image.write(image.read())
        temp_image_path = temp_image.name

    # Call model and save results
    asyncio.run(model.process_image(temp_image_path))
    st.session_state.model_results = model.results
    
    # Save each card name and id
    names = []
    ids = []
    for card, data in model.results.items():
        names.append(data.name)
        ids.append(data.id)
    st.session_state.scanned_name = names
    st.session_state.scanned_id = ids

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
            with st.spinner('Scanning...'):
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

    # Display scanned image
    if st.session_state.scanned_image:
        st.subheader('Scanned image')
        st.image(st.session_state.scanned_image)

    # Display scanned data in table
    if st.session_state.model_results:
        st.subheader('Scanned data')
        selected_cards = []
        for i in range(1, len(st.session_state.model_results)+1):
            card_name = st.session_state.model_results[i].name
            col1, col2 = st.columns([10, 2.3])
            with col1: 
                st.markdown(f'##### Card: {card_name}')
            # Checkbox to select which cards to be added
            with col2:
                if st.checkbox('Select to Add', card_name, key=f'select_{i}'):
                    selected_cards.append(card_name)
            with st.expander('Card Information'):
                data_dict = {k: str(v) if not isinstance(v, str) else v for k, v in st.session_state.model_results[i].__dict__.items()}
                data_df = pd.DataFrame(data_dict.items(), columns=['Attribute', 'Value'])
                st.dataframe(
                    data_df, 
                    hide_index=True,
                    column_config={'Attribute': st.column_config.Column(width='medium')}
                    )

                # st.json(st.session_state.model_results[i].__dict__)

            st.divider()

    # Button to add to database
    if st.button('Add to collection', type='primary'):
        for name in selected_cards:
            index = st.session_state.scanned_name.index(name)
            card_id = st.session_state.scanned_id[index]
            populate_tables(card_id)
        st.success('Added to collection!')

# Collection tab
with collection_tab:
    st.header('Collection')
    
    # Get from database
    collection_prices_df = retrieve_card_pricing_table()
    collection_info_df = retrieve_pokemon_information_table()

    # Display Card Pricing Table
    st.subheader('Card Pricing Table')
    st.dataframe(
        collection_prices_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Image': st.column_config.ImageColumn(width='small'),
            'Price URL': st.column_config.LinkColumn()
        })
    
    st.divider()
    
    # Display Pokemon Information Table
    st.subheader('Pokemon Information Table')
    st.dataframe(
        collection_info_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            'Image': st.column_config.ImageColumn(width='small'),
            'Price URL': st.column_config.LinkColumn()
        })

