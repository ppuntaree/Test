import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import os
import PIL
import pdf2image
from pdf2image import convert_from_path
from PIL import Image, ImageFilter, ImageEnhance
import time
import base64

import pytesseract
import re
import pandas as pd
from PIL import Image, ImageDraw
from IPython.display import HTML, IFrame
import math
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



# ---------------------------- image processing ----------------------------#
def image_processing(output_file):
    start = time.time()
    progress_text = "⏳Please wait to image processing..."
    progress_bar = st.progress(0)
    file_name = os.listdir(folder_path2.upper())
    for i,file in  enumerate(file_name):
        if file.endswith('.PNG'):
            img_path = os.path.join(folder_path2.upper(),file)
            img = Image.open(img_path)
            w1 , h1 = img.size
            right = w1 - (w1 * 0.01) 
            left = right - (w1//4) 
            lower = h1 - (h1 * 0.03)  
            upper = lower - (h1 * 0.14)
            area = (left, upper, right, lower)

            ############# Crop images#############
            crop_img = img.crop(area)

            ############# Resize image #############
            new_w1,new_h1 = crop_img.size
            scale = 0.85
            w2 = int(new_w1 * scale)
            h2 = int(new_h1 * scale)
            size = (w2, h2)
            crop_img = crop_img.resize(size)


            ############# Binarize images #############
            # Convert to grayscale
            crop_img = crop_img.convert('L')
            thresh=230
            w3 , h3 = crop_img.size
            for x in range(w3):
                for y in range(h3):
                    if crop_img.getpixel((x,y)) < thresh:
                        crop_img.putpixel((x,y),0) #white
                    else:
                        crop_img.putpixel((x,y),255) #black

        dilate_img = crop_img.filter(ImageFilter.MinFilter (size = 1))
        output_file = os.path.join(folder_path3.upper(),file)
        dilate_img.save(output_file, dpi=(300,300))
        progress_bar.progress((i + 1) / len(file_name), text=progress_text)
    
    end = time.time()
    st.write("Timelapse :",end-start)
    #st.write('!!Complete!!')

# ----------------------------------------------------------- OCR ---------------------------------------#
def text_ocr(folder_path):   
    img = Image.open(folder_path)
    #draw = ImageDraw.Draw(img)
    psm_dwg_name = '--psm 4'
    data = pytesseract.image_to_data(img,  lang='eng',config = psm_dwg_name, output_type='data.frame')
    data.dropna(inplace=True)
    #data = data.dropna(inplace=True).reset_index(drop=True)
    data['text'] = data['text'].astype(str).str.strip()
    data_df = pd.DataFrame(data)
    #print(i,'\n',data.to_string(),'\n')
    return data_df, img

##------------------------------------------ Drawing number --------------------------------------------##
def drawing_no(data, img):
    new_left, new_top, new_width, new_height = 0, 0, 0, 0    
    df_old = pd.DataFrame(data) 
    
    #------------------------- เลือกเฉพาะ text ที่มี - ----------------------#
    df = df_old[df_old['text'].str.contains("-", regex=False, na=False)]

    
    characters = ["K", "<","/","E","N","PID","«","PIO","°"]
    dwg_no = df[~df['text'].str.upper().str.contains('|'.join(characters))]
    
    substitutions = {
        '—': '-',
        '-—|—-':'-',
        '——':'-',
        '_':'-',
        '---':'-',
        '--':'-',
        '~': '-',
        '=': '-',
        'z|Z':'2',
        '^AA|^YA|^Y9|^0A|^9A|^A9|^19|^8|^1A|^A':'18',
        '^901':'1801',
        '^902':'1802',
        'i|I|T|L|^4': '1',
        'o|O|D|Q': '0',
        'S|s':'5',
        'B|e|E':'8',
        '^Y|R|r|{|}':'1',
        '“|”':'',
        'G':'9',
        'A1':'01'
    }
    dwg_no = df.copy()
    dwg_no['text'] = df['text'].replace(substitutions, regex=True)
    dwg_no = dwg_no[((dwg_no["text"].str.count("-") >= 4) & dwg_no['text'].str.contains("p|P"))]
    dwg_no = dwg_no[~dwg_no['text'].str.contains("^\d{5,}")]
    dwg_no['text'] = dwg_no['text'].replace(substitutions, regex=True)
    dwg_no['text'] = dwg_no['text'].apply(lambda x: re.sub(r'[^A-Za-z0-9-]', '', x))
    dwg_no['text'] = dwg_no['text'].str.upper()
    dwg_no = dwg_no[(dwg_no['height'] >= 10)]
    #print('\n',dwg_no.to_string())
 
    #----------------------------- dwg_no data = 1  -------------------------------#
    if(dwg_no.shape[0] == 1):
        for index, row2 in dwg_no.iterrows():
            dwg_no['text'] = dwg_no['text'].replace(substitutions, regex=True)
            
            left, top, width, height = row2['left'], row2['top'], row2['width'], row2['height']
            #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
            #display(img)
       
        
    #----------------------------- dwg_no data > 1 -------------------------------#
    elif (dwg_no.shape[0] > 1):  
        
        dwg_no['text'] = dwg_no['text'].replace(substitutions, regex=True)
        
        for index, row1 in dwg_no.iterrows():
            left, top, width, height = row1['left'], row1['top'], row1['width'], row1['height']
        
            # Calculate the distance (euclidean)
            distance = math.dist([0, 0], [left, top])
            dwg_no.loc[index, 'distance'] = distance
        
        #print(dwg_no.to_string())
        max_distance = dwg_no['distance'].max()

        if max_distance > 0:
            dwg_no['text'] = dwg_no['text'].replace(substitutions, regex=True)
            #print("----------------------------------------------------------------------------------------------------------------------------")  
            dwg_no = dwg_no[dwg_no['distance'] == dwg_no['distance'].max()]
            #print(dwg_no.to_string())
            #print( 'Drawing no.:', dwg_no['text'].iloc[0])
            left, top, width, height = dwg_no['left'], dwg_no['top'], dwg_no['width'], dwg_no['height']
            #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
            #print(left,top)
            
    return img, dwg_no


    ##------------------------------------------ Revision number --------------------------------------------##
##------------------------------------------ Revision number --------------------------------------------##
def revision_no(data, img):

    w , h = img.size
    df = pd.DataFrame(data)

    characters = ["-", "<", "/", "—", r"\)", r"\(", r"\*",r"[A-Ya-y]"] 
    #print(df.to_string())

    substitutions = {
        'o|O': '0',
        'S|s':'5',
        '{|}':'1',
        '[|]':'1',
        'ZZ|2Z':'Z'
        
    }

    pattern_rev_1 = r'SGeseac|Sesesc|SKE|GSE&C|[se]{1|&c|UHV|UHY|URV|EAE|EAC|GS|CONSORTIUM|wood|WOOG,|ROSTER|LIMITED|PROPERTY|CONSENT|HYDROTEK|PUBLIC|CAUSTIC|SPENT'
    pattern1 = df[df['text'].str.contains(pattern_rev_1, regex=True, na=False)]  
    #print(pattern1.to_string())
    
    pattern_rev_2 = r'IRPC|SINOPEC|ENGINEERING|CONFIDENTIAL'
    pattern2= df[df['text'].str.contains(pattern_rev_2, regex=True, na=False)]
    #print(pattern2.to_string())
    
    pattern_rev_3 = r'RDCC|ROCC|ELECTROSTATIC|PRECIPITATOR|India|Private|Research'
    pattern3 = df[df['text'].str.contains(pattern_rev_3, regex=True, na=False)]
    #print(pattern3.to_string())

    rev_no = df[~df['text'].str.contains('|'.join(characters))]
    rev_no = rev_no.copy()
    rev_no = rev_no[rev_no['text'].str.contains(r'[0-9]{1}|[0-90-9{1}|[Zz]{1,2}|[\S[^A-Ya-y]]', regex=True, na=False)]
    #rev_no['text'] = rev_no['text'].replace(substitutions, regex=True)
    rev_no['text'] = rev_no['text'].apply(lambda x: re.sub(r'[^A-Za-z0-9-]', '', x))
    rev_no['text'] = rev_no['text'].str.upper()
    rev_no['text'] = rev_no['text'].replace(substitutions, regex=True)
    #print(rev_no.to_string())

    if not pattern1.empty:
        #print('Pattern1')
        # Calculate the distances (Euclidean)
        if not rev_no.empty:
            rev_no['distance'] = rev_no.apply(lambda row: math.dist([0, 0], [row['left'], row['top']]), axis=1)
            max_distance = rev_no['distance'].max()

            if max_distance > 0:
                rev_no = rev_no[(rev_no['top'] >= h*0.6) ]
                rev_no = rev_no[rev_no['left'] >= w*0.6]
                rev_no = rev_no[(rev_no['top'] <= (h- (h*0.10)))]

                rev_no = rev_no[(rev_no["text"].str.count(r"[\d]|[Zz]") <= 2)]
                rev_no = rev_no[rev_no['distance'] == max_distance]
                if not rev_no.empty:
                    #print(i, 'Revision no.:', rev_no['text'].iloc[0])
                    left, top, width, height = rev_no['left'], rev_no['top'], rev_no['width'], rev_no['height']
                    #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
                    # print(left, top)
                    #display(img)
               

    elif not pattern2.empty:
        #print('Pattern2')
        # Calculate the distances (Euclidean)
        if not rev_no.empty:
            rev_no['distance'] = rev_no.apply(lambda row: math.dist([0, 0], [row['left'], row['top']]), axis=1)
            max_distance = rev_no['distance'].max()

            if max_distance > 0:
                rev_no = rev_no[(rev_no['top'] <= h * 0.75)]
                rev_no = rev_no[(rev_no['height'] == rev_no['height'].min())]

                #rev_no = rev_no[(rev_no['height'] == rev_no['height'].min())]
                rev_no = rev_no[rev_no['distance'] == max_distance]
                if not rev_no.empty:
                    #print(i, 'Revision no.:', rev_no['text'].iloc[0])
                    left, top, width, height = rev_no['left'], rev_no['top'], rev_no['width'], rev_no['height']
                    #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
                    # print(left, top)
                    #display(img)
                

    elif not pattern3.empty:

        #print('Pattern3')

        # Calculate the distances (Euclidean)
        if not rev_no.empty:
            rev_no['distance'] = rev_no.apply(lambda row: math.dist([0, 0], [row['left'], row['top']]), axis=1)
            max_distance = rev_no['distance'].max()

            if max_distance > 0:
                rev_no = rev_no[(rev_no['top'] > h*0.9) |((rev_no['left']+rev_no['width']) > w*0.85)]
                rev_no = rev_no[(rev_no["text"].str.count(r"[\d]|[Zz]") <= 2)]
                rev_no = rev_no[rev_no['distance'] == max_distance]
                if not rev_no.empty:
                    #print(i, 'Revision no.:', rev_no['text'].iloc[0])
                    left, top, width, height = rev_no['left'], rev_no['top'], rev_no['width'], rev_no['height']
                    #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
                    # print(left, top)
                    #display(img)

    else:
        #print('Pattern4')

        # Calculate the distances (Euclidean)
        if not rev_no.empty:
            rev_no['distance'] = rev_no.apply(lambda row: math.dist([0, 0], [row['left'], row['top']]), axis=1)
            max_distance = rev_no['distance'].max()

            if max_distance > 0:
                rev_no = rev_no[(rev_no['height'] == rev_no['height'].max())]
                rev_no = rev_no[(rev_no['top'] > h*0.9) |((rev_no['left']+rev_no['width']) > w*0.85)]
                #rev_no = rev_no[(rev_no['height'] >= 27) & (rev_no['height'] <= 29)]
                #rev_no = rev_no[(rev_no['height'] == rev_no['height'].max())]

                rev_no = rev_no[(rev_no["text"].str.count(r"[\d]|[Zz]") <= 2)]
                rev_no = rev_no[rev_no['distance'] == max_distance]
                if not rev_no.empty:
                    #print(i, 'Revision no.:', rev_no['text'].iloc[0])
                    left, top, width, height = rev_no['left'], rev_no['top'], rev_no['width'], rev_no['height']
                    #draw.rectangle([(left, top), (left + width, top + height)], outline="red", width=5)
                    # print(left, top)
                    #display(img)
                


    return img, rev_no

##------------------------------------------- Drawing name ----------------------------------------------##
def drawing_name(data, img):
    w,h = img.size
    df = pd.DataFrame(data)
    remove_words = ["UHV", "PROJECT", "E&C","SK", "NONE", "SKPeac", "Sesesc", "FOSTER",
                "WHEELER", "[INTERNATIONAL]{1}", "CORPORATION", "CONSORTIUM","[CONTRACT]{1}","UPWARO" ,"DIRECTION",
               "FELD","AID","&C","JOB","PUBLIC", "COMPANY", "LIMITED", "ENGINEERING","IRPC","CONSORT",
                "MY","CONFIDENTIAL","SEONG","INSTALL","UHY", "NAW","[WOR]{1}","AES","BUNDLE","[TIONAL]{1}","TOATE","EAC{1}",
                "PHONE{1}"
               ]

    replace_words = {
        '¥':'Y',
        'DIAGRAH' : 'DIAGRAM',
        'ROCC':'RDCC',
        'ATR':'AIR',
        r'[$]|§':'5',
        ';':'',
        '~|--|—':'-',
        'All':'AII',
        'Q1|O1|Ot|Of|G1|O01':'01',
        '’|}':')',
        '{':'(',
        '[.]':'',
        r'[(Olt.|(Oll,]{5}':'(OIL',
        r'ANO':'AND',
        r'CAUTIIC':'CAUSTIC'
        #'!':''

    }

    #------ Symbols -----#

    symbols = ["—o","®",'"', "°", "=", "£","€", r'”',r'“', '«','»', '!',"‘",  "*", "<", "@", r"[", r"]", ">", "%","|"]

    filter_data = df[~df['text'].str.contains(r'[A-Z]+[a-z]|[a-z]+[A-Z]', regex = True, na = False)]
    filter_data = df[~df['text'].str.contains('|'.join(map(re.escape, symbols)), regex=True, na=False)]


    filter_data = filter_data.copy()
    filter_data['text'] = filter_data['text'].replace(replace_words, regex=True)
    filter_data = filter_data[~filter_data['text'].str.contains(r'[a-z]{2}|\d{3,}-|\w{2,}-\d{2,}', regex=True, na=False)]
    filter_data = filter_data[~(filter_data["text"].str.count("-") > 1)]
    #filter_data['text'] = filter_data['text'].str.upper()

    #print(filter_data.to_string())

    filter_data = filter_data[~filter_data['text'].str.contains('[\d]{6}', regex=True, na=False)]
    filter_data = filter_data[~filter_data['text'].str.contains('[[A-Z]+[0-9]]{2,}|[\d]{6}|^[\d]{3}$', regex=True, na=False)]
    #filter_data = filter_data[~filter_data['text'].str.contains('^[[A-Z]+[0-9]{2,}$|^[\d]{6}$|^[\d]{3,}$|[-]^[A-Z]{2}$', regex=True, na=False)]
    filter_data = filter_data[filter_data['text'].str.contains(r'[A-Z]{2,}|&|[\d]{1}|[\(\)]|\/|OF{1}|[G+]{2}', regex=True, na=False)]
    filter_data['text'] = filter_data['text'].str.upper()

    #print(filter_data.to_string())


    pattern_dwg_1 = r'SGeseac|Sesesc|SKE|GSE&C|[se]{1}|&c|UHV|UHY|URV|EAE|EAC|GS|CONSORTIUM|wood|WOOG,|ROSTER|PROPERTY|CONSENT|CAUSTIC|SPENT|HYDROTEK|PUBLIC'
    pattern1 = filter_data[filter_data['text'].str.contains(pattern_dwg_1, regex=True, na=False)]
    pattern_dwg_2 = r'IRPC|SINOPEC|ENGINEERING|CONFIDENTIAL'
    pattern2= filter_data[filter_data['text'].str.contains(pattern_dwg_2, regex=True, na=False)]
    #print(pattern2.to_string())

    pattern_dwg_3 = r'RDCC|ROCC|ELECTROSTATIC|PRECIPITATOR|India|Private|Research'
    pattern3 = filter_data[filter_data['text'].str.contains(pattern_dwg_3, regex=True, na=False)]
    #print(pattern3.to_string())


    ##################################### dwg name pattern 1 ############################################################
    if not pattern1.empty:
        if not filter_data.empty:
            #print('pattern1')
            dwg_name_data = []
            #print(filter_data.to_string())

            filter_data = filter_data[~filter_data['text'].str.contains(r'^[0-9][A-Z]{1}$|90|REE{1}|TRY,{1}|RY,{1}|C7{1}|AY,{1}', regex=True, na=False)]  
            filter_data = filter_data[~filter_data['text'].str.contains('|'.join(map(re.escape, remove_words)), regex=True, case=False, na=False)]

            filter_data = filter_data[filter_data['top'] > ( h*0.25)]
            filter_data = filter_data[(filter_data['top'] < (h -( h*0.25)))]
            filter_data = filter_data[(filter_data['left'] > (w*0.3))]
            filter_data = filter_data[~(filter_data['conf'] < 20)]

            med1 = filter_data['height'].median()
            #print(med1)
            filter_data = filter_data[(filter_data['height'] >= med1 - 2)]

            #print(filter_data)

            for block_num, group_data in filter_data.groupby('block_num'):

                std = group_data['height'].std()
                dwg_name= " ".join(group_data['text'])
                dwg_name_data.append({'drawing name': dwg_name ,'std':std})

            dwg_name_df = pd.DataFrame(dwg_name_data)

            if not dwg_name_df.empty:
                dwg_name_df = dwg_name_df[~(dwg_name_df['drawing name'].str.count(r"#")>=1)]
                dwg_name_df = dwg_name_df.dropna(subset=['std'])
                dwg_name_df = dwg_name_df[~dwg_name_df['drawing name'].str.contains(r'\b(?:' + '|'.join(map(re.escape, remove_words)) + r')\b', regex=True, case=False)]
                combined_dwg_names = " ".join(dwg_name_df['drawing name'])
                combined_dwg_names = re.sub('^PLANT[ ]{1}','',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING AND','PIPING AND',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING &','PIPING &',combined_dwg_names)
                combined_dwg_names = re.sub('.*? UTILITY','UTILITY',combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERISATION', 'POLYNAPHTHA - OLIGOMERISATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERIZATION', 'POLYNAPHTHA - OLIGOMERIZATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]CONDITIONING', 'HYVAHL - CONDITIONING', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]REACTION', 'HYVAHL - REACTION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]PRETREATMENT', 'POLYNAPHTHA - PRETREATMENT', combined_dwg_names)
                combined_dwg_names = re.sub(r'UNIT[ ]UNIT', 'UNIT - UNIT', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(FLARE\)[ ]', '(FLARE) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(TANK FARM\)[ ]', '(TANK FARM) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'IAF[ ]PACKAGE', 'IAF PACKAGE - ', combined_dwg_names)
                combined_dwg_names = re.sub('\)[ ]\d',')',combined_dwg_names)
                combined_dwg_names = re.sub('\([ ]\(+$| \w{3}$|\(\d{3}.*?$| \({1}\d{1}$|\($|\s[ES|ER|TD|PT|FP]{2}$|É','',combined_dwg_names)

            else:
                combined_dwg_names = None


        dwg_name_df = pd.DataFrame({'drawing name': [combined_dwg_names]})

    ############################################### dwg name pattern 2 #######################################################
    elif not pattern2.empty:
        if not filter_data.empty:
            #print('pattern2')
            dwg_name_data = []
            #print(filter_data.to_string())

            filter_data = filter_data[~filter_data['text'].str.contains(r'^[0-9][A-Z]{1}$', regex=True, na=False)]
            filter_data = filter_data[~filter_data['text'].str.contains('|'.join(map(re.escape, remove_words)), regex=True, case=False, na=False)]

            filter_data = filter_data[filter_data['top'] > ( h*0.5)]
            filter_data = filter_data[(filter_data['top'] < (h -( h*0.05)))]
            filter_data = filter_data[(filter_data['left'] < w - (w*0.4))]
            #filter_data = filter_data[~(filter_data['conf'] < 20)]

            med2 = filter_data['height'].median()
            #print(med2)

            filter_data = filter_data[(filter_data['height'] >= med2 - 2)]
            #print(filter_data.to_string())

            for block_num, group_data in filter_data.groupby('block_num'):
                
                std = group_data['height'].std()
                dwg_name= " ".join(group_data['text'])
                dwg_name_data.append({'drawing name': dwg_name ,'std':std})    
                
    
            dwg_name_df = pd.DataFrame(dwg_name_data)  
    
           
            if not dwg_name_df.empty:
                dwg_name_df = dwg_name_df[~(dwg_name_df['drawing name'].str.count(r"#")>=1)]
                dwg_name_df = dwg_name_df.dropna(subset=['std'])
                dwg_name_df = dwg_name_df[~dwg_name_df['drawing name'].str.contains(r'\b(?:' + '|'.join(map(re.escape, remove_words)) + r')\b', regex=True, case=False)]
                combined_dwg_names = " ".join(dwg_name_df['drawing name'])
                combined_dwg_names = re.sub('^PLANT[ ]{1}','',combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERISATION', 'POLYNAPHTHA - OLIGOMERISATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERIZATION', 'POLYNAPHTHA - OLIGOMERIZATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]CONDITIONING', 'HYVAHL - CONDITIONING', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]REACTION', 'HYVAHL - REACTION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]PRETREATMENT', 'POLYNAPHTHA - PRETREATMENT', combined_dwg_names)
                combined_dwg_names = re.sub(r'UNIT[ ]UNIT', 'UNIT - UNIT', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(FLARE\)[ ]', '(FLARE) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(TANK FARM\)[ ]', '(TANK FARM) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'IAF[ ]PACKAGE', 'IAF PACKAGE - ', combined_dwg_names)
                combined_dwg_names = re.sub('\)[ ]\d',')',combined_dwg_names)
                #combined_dwg_names = re.sub('.*? PIPING &','PIPING &',combined_dwg_names)
                #combined_dwg_names = re.sub('.*? PIPING AND','PIPING AND',combined_dwg_names)
                combined_dwg_names = re.sub('\([ ]\(+$| \w{3}$|É','',combined_dwg_names)


            else:
                combined_dwg_names = None

        dwg_name_df = pd.DataFrame({'drawing name': [combined_dwg_names]})

    ############################################### dwg name pattern3 ####################################################
    elif not pattern3.empty:
        if not filter_data.empty:
            #print('pattern3')
            dwg_name_data = []

            filter_data = filter_data[~filter_data['text'].str.contains(r'^[0-9][A-Z]{1}$', regex=True, na=False)]
            filter_data = filter_data[~filter_data['text'].str.contains('|'.join(map(re.escape, remove_words)), regex=True, case=False, na=False)]

            filter_data = filter_data[filter_data['top'] > ( h*0.2)]
            filter_data = filter_data[(filter_data['top'] < (h -( h*0.15)))]
            filter_data = filter_data[(filter_data['left'] > (w*0.1))]
            filter_data = filter_data[~(filter_data['conf'] < 20)]

            med3 = filter_data['height'].median()
            #print(med3)
            filter_data = filter_data[(filter_data['height'] >= med3 - 2)]

            #print(filter_data.to_string())

            for block_num, group_data in filter_data.groupby('block_num'):

                std = group_data['height'].std()
                dwg_name= " ".join(group_data['text'])
                dwg_name_data.append({'drawing name': dwg_name ,'std':std})

            dwg_name_df = pd.DataFrame(dwg_name_data)
            if not dwg_name_df.empty:
                dwg_name_df = dwg_name_df[~(dwg_name_df['drawing name'].str.count(r"#")>=1)]
                dwg_name_df = dwg_name_df.dropna(subset=['std'])
                dwg_name_df = dwg_name_df[~dwg_name_df['drawing name'].str.contains(r'\b(?:' + '|'.join(map(re.escape, remove_words)) + r')\b', regex=True, case=False)]
                combined_dwg_names = " ".join(dwg_name_df['drawing name'])
                combined_dwg_names = re.sub('^PLANT[ ]{1}','',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING AND','PIPING AND',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING &','PIPING &',combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERISATION', 'POLYNAPHTHA - OLIGOMERISATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERIZATION', 'POLYNAPHTHA - OLIGOMERIZATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]CONDITIONING', 'HYVAHL - CONDITIONING', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]REACTION', 'HYVAHL - REACTION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]PRETREATMENT', 'POLYNAPHTHA - PRETREATMENT', combined_dwg_names)
                combined_dwg_names = re.sub(r'UNIT[ ]UNIT', 'UNIT - UNIT', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(FLARE\)[ ]', '(FLARE) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(TANK FARM\)[ ]', '(TANK FARM) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'IAF[ ]PACKAGE', 'IAF PACKAGE - ', combined_dwg_names)
                combined_dwg_names = re.sub('\)[ ]\d',')',combined_dwg_names)
                #combined_dwg_names = re.sub('.*? UTILITY','UTILITY',combined_dwg_names)
                combined_dwg_names = re.sub('\([ ]\(+$| \w{3}$|\(\d{3}.*?$| \({1}\d{1}$| \.*$|[ \d \d]{4}$|É','',combined_dwg_names)

            else:
                combined_dwg_names = None


        dwg_name_df = pd.DataFrame({'drawing name': [combined_dwg_names]})

    ############################################# dwg name pattern 4 ########################################################
    else:
        if not filter_data.empty:
            dwg_name_data = []
            combined_dwg_names = []

            filter_data = filter_data[~filter_data['text'].str.contains(r'^[0-9][A-Z]{1}$', regex=True, na=False)]
            filter_data = filter_data[(filter_data['left'] <= w - (w*0.1))]
            filter_data = filter_data[~(filter_data['conf'] < 20)]

            med4 = filter_data['height'].median()
            #print(med4)
            filter_data = filter_data[(filter_data['height'] >= med4 - 2)]
            filter_data = filter_data[~filter_data['text'].str.contains('|'.join(map(re.escape, remove_words)), regex=True, case=False, na=False)]

            for block_num, group_data in filter_data.groupby('block_num'):

                std = group_data['height'].std()
                dwg_name= " ".join(group_data['text'])
                dwg_name_data.append({'drawing name': dwg_name ,'std':std})    

            dwg_name_df = pd.DataFrame(dwg_name_data)  

            if not dwg_name_df.empty:
                dwg_name_df = dwg_name_df[~(dwg_name_df['drawing name'].str.count(r"#")>=1)]
                dwg_name_df = dwg_name_df.dropna(subset=['std'])
                dwg_name_df = dwg_name_df[~dwg_name_df['drawing name'].str.contains(r'\b(?:' + '|'.join(map(re.escape, remove_words)) + r')\b', regex=True, case=False)]

                combined_dwg_names = " ".join(dwg_name_df['drawing name'])
                combined_dwg_names = re.sub('^PLANT[ ]{1}','',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING AND','PIPING AND',combined_dwg_names)
                combined_dwg_names = re.sub('.*? PIPING &','PIPING &',combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERISATION', 'POLYNAPHTHA - OLIGOMERISATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]OLIGOMERIZATION', 'POLYNAPHTHA - OLIGOMERIZATION', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]CONDITIONING', 'HYVAHL - CONDITIONING', combined_dwg_names)
                combined_dwg_names = re.sub(r'HYVAHL[ ]REACTION', 'HYVAHL - REACTION', combined_dwg_names)
                combined_dwg_names = re.sub(r'POLYNAPHTHA[ ]PRETREATMENT', 'POLYNAPHTHA - PRETREATMENT', combined_dwg_names)
                combined_dwg_names = re.sub(r'UNIT[ ]UNIT', 'UNIT - UNIT', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(FLARE\)[ ]', '(FLARE) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'\(TANK FARM\)[ ]', '(TANK FARM) - ', combined_dwg_names)
                combined_dwg_names = re.sub(r'IAF[ ]PACKAGE', 'IAF PACKAGE - ', combined_dwg_names)
                combined_dwg_names = re.sub('\)[ ]\d',')',combined_dwg_names)
                #combined_dwg_names = re.sub('\([ ]\(+$| \w{3}$|','',combined_dwg_names)
                combined_dwg_names = re.sub('\([ ]\(+$| \w{3}$|\(\d{3}.*?$| \({1}\d{1}$| \/.*$|[ \d \d]{4}$|É','',combined_dwg_names)

        dwg_name_df = pd.DataFrame({'drawing name': [combined_dwg_names]})
        # Replace words
        #dwg_name_df['drawing name'] = dwg_name_df['drawing name'].replace(replace_words, regex=True)
    return img, dwg_name_df



def run_process(folder_path, output_path):
    start = time.time()
    file_name = os.listdir(folder_path)
    result = pd.DataFrame([])
    progress_text = "⏳Please wait to extraction..."
    progress_bar = st.progress(0)

    for i, file in enumerate(file_name):
        img_path = os.path.join(folder_path, file)
        data_df, img = text_ocr(img_path)
        img, dwg_no = drawing_no(data_df, img)
        img, rev_no = revision_no(data_df, img)
        img, dwg_name_df = drawing_name(data_df, img)

        df = pd.DataFrame({
            'file_path': [file],
            'drawing no.': [dwg_no['text'].iloc[0] if not dwg_no.empty else None],
            'revision no.': [rev_no['text'].iloc[0] if not rev_no.empty else None],
            'drawing name': [dwg_name_df['drawing name'].iloc[0] if not dwg_name_df.empty else None]
        })

        result = pd.concat([result, df], ignore_index=True)

        progress_bar.progress((i + 1) / len(file_name), text=progress_text)

    output = os.path.join(folder_path4.upper(), f"{folder_name}_BEFORE_REVIEW.csv")
    st.session_state.result_csv_path = output
    result.to_csv(output, encoding='utf-8', index=False)
    end = time.time()
    st.write("Timelapse:", end - start)

# -----------------------------------------------------convert image to 64 bit ---------------------------------------#
def filepath_to_data_url(folder_path):
    data = pd.DataFrame(columns=['Images'])
    file_name = os.listdir(folder_path)
    for i, file in enumerate(file_name):
        file_path = os.path.join(folder_path, file)
        with open(file_path, 'rb') as file:
            image_bytes = file.read()
            base64_encode = base64.b64encode(image_bytes)
            data_url = 'data:image/PNG;base64,{}'.format(base64_encode.decode())
            data = pd.concat([data, pd.DataFrame({'Images': [data_url]})], ignore_index=True)
    return data

if 'initialization' not in st.session_state:
    st.session_state.initialization = None


st.set_page_config(page_title = "Extraction" ,initial_sidebar_state='collapsed', page_icon="📑", layout="wide")
st.markdown("# Extraction")

if st.session_state.initialization is not None:
    st.info('Step 2 : Pre-processing & Extraction information', icon="ℹ️")
    #st.write(f"{st.session_state.folder_path3.upper()}")

    st.session_state.option = st.selectbox(
        "Please select item :",
        ("UHV",),
        index=None,
        placeholder="Select item ...",
        )
    option = st.session_state.option
    folder_name = st.session_state.folder_name

    if  option is not None and folder_name != '' :
        columns= st.columns (8)
        clear_button = columns[3].button('Clear Step 2',key='clear_button',help='Clear Extraction')
        button2 = columns[4].button('Next step', key='button2', help = "Step 3 : Review")
            

        if 'button2' not in st.session_state:
            st.session_state.button2 = False
            st.rerun()

        if 'clear_button' not in st.session_state:
            st.session_state.clear_button = False

        if button2:
            st.session_state.initialization = True
            st.session_state.extraction = True
            st.session_state.review = True
            st.session_state.administration = None
            st.session_state.drive_letter = None

            folder_name = st.session_state.folder_name
            folder_path2 = st.session_state.folder_path2
            folder_path3 = st.session_state.folder_path3
            folder_path4 = st.session_state.folder_path4

            image_processing(folder_path3.upper())
            run_process(folder_path3.upper(), folder_path4.upper())
            result_df = pd.read_csv(st.session_state.result_csv_path)
            #filepath_to_data_url(folder_path3.upper())
            data = filepath_to_data_url(st.session_state.folder_path3)
            df = pd.concat([data, result_df], axis=1)
            st.session_state.df = df
            time.sleep(0.5)
            st.success("!! Complete Step 2 !!")
            time.sleep(4)
            switch_page("Review")
            st.session_state.button2 = True
            st.rerun()


        elif clear_button:
            st.session_state.drive_letter = None
            st.session_state.folder_name = None
            st.session_state.folder_path1 = None
            st.session_state.folder_path2 = None
            st.session_state.folder_path3 = None
            st.session_state.folder_path4 = None
            st.session_state.start = True
            st.session_state.initialization = None
            st.session_state.extraction = None
            st.session_state.review = None
            st.session_state.administration = None
            switch_page("Initialization")
            st.rerun()
    else:
        st.warning('Please select item', icon="⚠️")
        #st.session_state.initialization = None
        #st.session_state.extraction = None
        #st.session_state.review = None
        st.session_state.administration = None
else:
    st.error("Please click button 'Next step' on initialization page", icon="🚨")