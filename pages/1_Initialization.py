import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import time
import os
import pdf2image
import PyPDF2
from PIL import Image
from pdf2image import convert_from_path

drive_letter = "D:\Project"

# ------------------------- multi page to single page -------------------------#
def convert_pdf_to_single_page(pdf_file, output_folder):
    #start_1 = time.time()
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    for i, page in enumerate(pdf_reader.pages):
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(page)
        output_filename = os.path.join(output_folder, f"{folder_name.upper()}_PAGE_{i + 1:03}.PDF")

        with open(output_filename, "wb") as output:
            pdf_writer.write(output)

    #end_1 = time.time()
    #st.write("Time End:", end_1)
    #st.write("Timelapse:", end_1 - start_1)

# ------------------------- single page to png -------------------------#
def convert_pdf_to_png(output_file):
    start = time.time()
    pdf_files = [entry for entry in os.scandir(folder_path1.upper()) if entry.is_file() and entry.name.endswith('.PDF')]

    progress_text = "⏳Please wait..."
    progress_bar = st.progress(0)

    for i, pdf in enumerate(pdf_files):
        PDF = convert_from_path(pdf, thread_count=4, poppler_path=r"C:\path\to\poppler-23.08.0\Library\bin")
        pdf_filename = os.path.splitext(os.path.basename(pdf))[0]

        for j, image in enumerate(PDF):
            output_png = os.path.join(output_file, f"{pdf_filename}.PNG")
            image.save(output_png, "PNG", dpi=(300, 300))

        progress_bar.progress((i + 1) / len(pdf_files), text=progress_text)

    #progress_bar.empty()
    end = time.time()
    st.write("Timelapse:", end - start)
    #end =time.time()

if 'start' not in st.session_state:
    st.session_state.start = None


st.set_page_config(page_title="Initialization" ,initial_sidebar_state='collapsed',page_icon="🗂️", layout="wide")
st.markdown("# Initialization")


if st.session_state.start is not None:

    st.info('Step 1 : Upload file ', icon="ℹ️")
    #st.write(f"{st.session_state.start}")
    uploaded_file = st.file_uploader("Upload a PDF file", accept_multiple_files=False)

    if "visibility" not in st.session_state:
        st.session_state.visibility = "visible"
        st.session_state.disabled = False

    st.session_state.folder_name = st.text_input(
        "Create folder name :",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        key="placeholder",
    )

    folder_name = st.session_state.folder_name.upper()

    if  folder_name and uploaded_file is not None  :
        col1, col2,col3,col4,col5,col6,col7,col8 = st.columns (8)
        with col4:
            button_home = st.button('Home',key='button_home',help="Go to Home Page",)
        with col5:
            button1 = st.button(' Next step ', key='button1', help='Step 2 : Extraction')
    

        if 'button1' not in st.session_state:
            st.session_state.button1 = False
            st.rerun()

        if 'button_home' not in st.session_state:
            st.session_state.button_home = False

        if button1:
            folder_path1 = os.path.join(drive_letter, folder_name, "STEP1_" + folder_name + "_PDF")
            folder_path2 = os.path.join(drive_letter, folder_name, "STEP2_" + folder_name + "_PNG")
            folder_path3 = os.path.join(drive_letter, folder_name, "STEP3_" + folder_name + "_PREP")
            folder_path4 = os.path.join(drive_letter, folder_name, "STEP4_" + folder_name + "_OCR")

            st.session_state.folder_path1 = folder_path1
            st.session_state.folder_path2 = folder_path2
            st.session_state.folder_name = folder_name
            st.session_state.folder_path3 = folder_path3
            st.session_state.folder_path4 = folder_path4


            if not os.path.exists(folder_path1):
                os.makedirs(folder_path1.upper())

            if not os.path.exists(folder_path2):
                os.makedirs(folder_path2.upper())

            if not os.path.exists(folder_path3):
                os.makedirs(folder_path3.upper())

            if not os.path.exists(folder_path4):
                os.makedirs(folder_path4.upper())

            #st.toast(f" Folder '{folder_name.upper()}' created successfully on drive '{drive_letter}\{folder_name.upper()}'.",icon ="✔️")
            st.write(f"✔️Folder '{folder_name.upper()}' created successfully on drive '{drive_letter}\{folder_name.upper()}'.")
            st.session_state.uploaded_file = True
            st.session_state.initialization = True
            st.session_state.extraction = None
            st.session_state.review = None
            st.session_state.administration = None
            convert_pdf_to_single_page(uploaded_file, folder_path1)
            convert_pdf_to_png(folder_path2)
            time.sleep(.5)
            st.success ('!! Complete Step 1 !!')

            time.sleep(5)
            switch_page("Extraction")
            st.session_state.button1 = True
            st.rerun()

        elif button_home:
            st.session_state.folder_name = None
            st.session_state.folder_path2 = None
            st.session_state.folder_path3 = None
            st.session_state.folder_path4 = None
            #st.session_state.start = None
            st.session_state.initialization = None
            st.session_state.extraction = None
            st.session_state.review = None
            st.session_state.administration = None
            switch_page("Home")

            st.rerun()
    else:
        st.warning('Please create folder name and upload file', icon="⚠️")
        #st.session_state.initialization = None
        #st.session_state.extraction = None
        #st.session_state.review = None
        #st.session_state.administration = None
else:
    st.error("Please click button 'Next step' on the home page", icon="🚨")
