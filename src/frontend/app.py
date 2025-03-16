import streamlit as st
import pandas as pd

st.title('Pokemon Trading Card Scanner')
scan_tab, collection_tab = st.tabs(['Scan', 'Collection'])

# Initial scan info
if 'scanned_image' not in st.session_state:
    st.session_state.scanned_image = None
if 'scanned_data' not in st.session_state:
    st.session_state.scanned_data = None
if 'scanned_name' not in st.session_state:
    st.session_state.scanned_name = None

# Send card to scan
def scan_card(image):
    # TODO: send to model
    # example data
    st.session_state.scanned_data = {
        'Name': 'Pikachu',
        'Price': '$1'
    }
    st.session_state.scanned_name = st.session_state.scanned_data['Name']

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
            scanned_data_df = pd.DataFrame([st.session_state.scanned_data])
            scanned_data_df = scanned_data_df.transpose()
            scanned_data_df_html = scanned_data_df.to_html(header=False)
            st.markdown(scanned_data_df_html, unsafe_allow_html=True)

            # Button to add to database
            if st.button('Add to collection', type='primary'):
                # TODO: add to database
                st.success('Added to collection!')

# Collection tab
with collection_tab:
    st.header('Collection')

