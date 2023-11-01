import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os

if 'review' not in st.session_state:
    st.session_state.review = None

if 'rename' not in st.session_state:
    st.session_state.rename = None
st.set_page_config(page_title = "Administration" ,initial_sidebar_state='collapsed', page_icon="🗃️", layout="wide")
st.markdown("# Administration")

def clear_png(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)
    os.rmdir(folder_path)

def clear_pre(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        os.remove(file_path)
    os.rmdir(folder_path)
        

if st.session_state.review and st.session_state.rename is not None:
    st.info('Step 4 : Rename files PDF & Clear ', icon="ℹ️")

    #st.write(f"{st.session_state.rename}")

    folder_path1 = st.session_state.folder_path1.upper()
    folder_path2 = st.session_state.folder_path2.upper()
    folder_path3 = st.session_state.folder_path3.upper()
    #st.write(f"{st.session_state.folder_path1}")

    rename = st.session_state.rename
    col1, col2,col3,col4,col5,col6,col7,col8 = st.columns (8)
    with col4:
        clear_file = st.button('Clear files', key='clear_file', help='Clear files in folder')
    with col5:
        rename_pdf = st.button('Rename PDF', key='rename_pdf',help='Rename PDF files')
        
    if 'rename_pdf' not in st.session_state:
        st.session_state.rename_pdf = False
        st.rerun()

    if 'clear_file' not in st.session_state:
        st.session_state.clear_file = False
        st.rerun()


    if rename_pdf:
        st.session_state.initialization = None
        st.session_state.extraction = True
        st.session_state.review = True
        st.session_state.administration = True
        pdf_files = [filename for filename in os.listdir(folder_path1) if filename.endswith('.PDF')]
        for i, filename in enumerate(pdf_files):
            old_path = os.path.join(folder_path1, filename)
            new_name = os.path.join(folder_path1, rename['drawing no.'][i]+".PDF")
            os.rename(old_path, new_name)

        st.success("PDFs have been renamed!")

    if clear_file:
        clear_png(folder_path2)
        clear_pre(folder_path3)
        st.session_state.folder_name = None
        st.session_state.folder_path1 = None
        st.session_state.folder_path2 = None
        st.session_state.folder_path3 = None
        st.session_state.folder_path4 = None
        st.session_state.initialization = None
        st.session_state.extraction = None
        st.session_state.review = None
        st.session_state.administration = True
        st.session_state.rename = None
        st.session_state.edited_df = None
        switch_page("Initialization")
        st.session_state.clear_file = True
        st.rerun()

else:
    st.error("Please click button 'Next step' on review page", icon="🚨")


