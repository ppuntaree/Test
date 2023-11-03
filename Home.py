import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages, hide_pages
import time
from PIL import Image

st.set_page_config(page_title = "Home",page_icon = "🏠", layout="wide")
st.markdown("# Home")


#with st.sidebar.container():
#    image = Image.open('D:\Project\image\IRPC.PNG')
#    st.image(image,use_column_width=True)


home = st.button('Go to Step 1',key='home',help=" Step 1 : Iniiatilization")
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






