import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo
from st_pages import Page, show_pages, hide_pages
import time
from PIL import Image
import os




st.set_page_config(
    page_title="P&ID to e-DL Application", layout="wide", page_icon=":robot_face:"
)
st.markdown("# P&ID to e-DL Processsing Web Application")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Page header and sidebar setup
add_logo("D:\\Project\\image\\IRPC.png")

# Add objective section
with st.container():
    st.subheader("Objectives:")
    st.markdown(
    '<div style="text-align: justify;"><p>The objectives of this application are manifold and encompass a range of crucial improvements aimed at enhancing the productivity and accuracy of IRPC staffs. By harnessing the power of AI, specifically through the deployment of sophisticated machine learning models and state-of-the-art tools, we seek to achieve the following:</p></div>',
        unsafe_allow_html=True,
    )

    # Add column layout
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1:
        stream_url = (
            "D:\\Project\\image\\process_0.png"
        )
        with Image.open(stream_url) as stream:
            st.image(stream, width=64)
            st.markdown(
            '<div style="text-align: justify;"><p><b>1. Streamline Workflow:</b></p> Our foremost objective is to streamline and optimize the workflow of IRPC staffs, enabling them to accomplish tasks more efficiently and effectively.</div>',
                unsafe_allow_html=True,
            )
    with col2:
        clock_url = (
            "D:\\Project\\image\\clock_0.png"
        )
        with Image.open(clock_url) as clock:
            st.image(clock, width=64)
            st.markdown(
            '<div style="text-align: justify;"><p><b>2. Increase Time Efficiency:</b></p> By automating repetitive and time-consuming tasks, this application would significantly reduce the burden on staff, allowing them to focus their time and energy on more critical and value-added activities.</div>',
                unsafe_allow_html=True,
            )
    with col3:
        quality_url = (
            "D:\\Project\\image\\quality_0.png"
        )
        with Image.open(quality_url) as quality:
            st.image(quality, width=64)
            st.markdown(
            '<div style="text-align: justify;"><p><b>3. Improve Accuracy and Quality:</b></p> Our objective is to enhance the accuracy and quality of the information generated within the organization. By leveraging AI algorithms, the application will enable staff to produce precise and reliable outputs consistently.</div>',
                unsafe_allow_html=True,
            )
    with col4:
        inno_url = (
            "D:\\Project\\image\\innovation_0.png"
        )
        with Image.open(inno_url) as innovation:
            st.image(innovation, width=64)
            st.markdown(
            '<div style="text-align: justify;"><p><b>4. Foster Innovation:</b></p> By embracing AI technologies, we seek to foster a culture of innovation within IRPC culture, encouraging staff to explore novel ways of leveraging AI capabilities to drive continuous improvement and stay at the forefront of industry advancements.</div>',
                unsafe_allow_html=True,
            )

st.divider()

# Add image comparison section
with st.container():
    # Add column layout
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(":red[**As-is:**]")
        asis_url = (
            "D:\\Project\\image\\Asis_0.png"
        )
        with Image.open(asis_url) as asis:
            st.image(asis, width=450)
    with col2:
        st.subheader(":blue[**To-be:**]")
        tobe_url = (
            "D:\\Project\\image\\Tobe_0.png"
        )
        with Image.open(tobe_url) as tobe:
            st.image(tobe, width=450)

st.divider()


columns = st.columns(5)
home = columns[2].button('Go to Step 1',key='home',help=" Step 1 : Iniiatilization")
#restart = st.button('Restart',key='restart')

if 'home' not in st.session_state:
    st.session_state.home = False


if home:
    st.session_state.start = "hello1"
    st.success('!! Go to step 1 !! ')
    time.sleep(2.5)
    switch_page("initialization")
    st.session_state.home = True
    st.rerun()






