import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
import os
import pandas as pd
import datetime


st.set_page_config(page_title = "Review" ,initial_sidebar_state='collapsed', page_icon="📝", layout="wide")
st.markdown("# Review")

today = str(datetime.date.today())


if 'extraction' not in st.session_state:
    st.session_state.extraction = None


if st.session_state.extraction and st.session_state.folder_path4 is not None:

    st.info('Step 3 : Review & Edit result', icon="ℹ️")
    #st.write(f"{st.session_state.folder_path4.upper()}")
    if 'Review' not in st.session_state.df.columns:
        st.session_state.df['Review'] = False
    
    if 'df'  != None   :
        df = st.session_state.df
        edited_df = st.data_editor(
            st.session_state.df,width=2000,height=600,
            column_config={
                "Images": st.column_config.ImageColumn(help="Images" ),
                "file_path": st.column_config.TextColumn(help = "file path"),
                "drawing no.": st.column_config.TextColumn(help = "drawing no."),
                "revision no.": st.column_config.TextColumn(width=15,help = "revision no."),
                "drawing name": st.column_config.TextColumn(help = "drawing name"),
                "Review": st.column_config.CheckboxColumn(
                    width=10,
                    help="Check to review",
                    default=False
                )
            },
            hide_index=True
        )

        if edited_df['Review'].all() == True:
            columns = st.columns (8)
            clear_button = columns[3].button('Clear Step 3',key='clear_button',help="Clear Review")
            button3 = columns[4].button('Next step',key='button3',help="Step 4 : Administration")


            if 'button3' not in st.session_state:
                st.session_state.button3 = False
                st.rerun()

            if 'clear_button' not in st.session_state:
                st.session_state.clear_button = False

            if button3:
                st.session_state.initialization = None
                st.session_state.extraction = True
                st.session_state.review = True
                st.session_state.administration = True
                folder_name = st.session_state.folder_name
                folder_path4 = st.session_state.folder_path4

                output = os.path.join(folder_path4.upper(), f"{today}_{folder_name}_AFTER_REVIEW.csv")
                edited_df.to_csv(output, columns=['file_path','drawing no.','revision no.','drawing name'], encoding='utf-8', index=False)
                rename = edited_df[['file_path','drawing no.']]
                st.session_state.rename = rename
                switch_page("Administration")
                st.session_state.button3 = True
                st.rerun()

            elif clear_button:
                st.session_state.drive_letter = None
                st.session_state.folder_name = None
                st.session_state.start = True
                st.session_state.initialization = None
                st.session_state.extraction = None
                st.session_state.review = None
                st.session_state.administration = None
                switch_page("Initialization")
                st.rerun()
        else:
            #st.session_state.extraction = True
            st.session_state.administration = None

else:
    st.error("Please click button 'Next step' on the extraction page", icon="🚨")
    #st.session_state.drive_letter = None

