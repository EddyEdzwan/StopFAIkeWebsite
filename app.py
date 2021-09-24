import json
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import base64
import os
from google.cloud import firestore


from load_css import local_css

# Setting page config
st.set_page_config(layout="wide", page_title="StopFAIke", page_icon="images/StopFAIke_logo1.jpg")

# Loading css
local_css("style.css")

# Custom function to load the page background
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

# Loading the page background
set_png_as_page_bg('images/Newspaper_background_cropped.jpg')

# Check if App is on Heroku
on_heroku = False
if 'private_key' in os.environ:
  on_heroku = True

# Get firestore credentials from HEROKU environment variables
if on_heroku:
    firestore_credentials = {
        "type": os.environ["type"],
        "project_id": os.environ["project_id"],
        "private_key_id": os.environ["private_key_id"],
        "private_key": os.environ["private_key"],
        "client_email": os.environ["client_email"],
        "client_id": os.environ["client_id"],
        "auth_uri": os.environ["auth_uri"],
        "token_uri": os.environ["token_uri"],
        "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
        "client_x509_cert_url": os.environ["client_x509_cert_url"]
    }
    json_dump = json.dumps(firestore_credentials)

    # Authenticate to Firestore with the JSON account key.
    db = firestore.Client.from_service_account_info(json.loads(json_dump))

# Or get firestore credentials from local file
else:
    try:
        db = firestore.Client.from_service_account_json('firestore-key.json')
    except:
        st.markdown('''<div class="highlight white" style='color:red;text-align: center;'>Connection to a firestore DB is not successful.
        Please check your Heroku environment variables or provide a firestore-key.json in the same directory.
        Information sent and received from this page will not be captured</div>''', unsafe_allow_html=True)
        db = None

# Create a reference to the Google post.
if db:
    doc_ref = db.collection("url_predictions").document("user_input_predictions")
    # Then get the data at that reference
    doc = doc_ref.get()

    # Let's see what we got!
    st.write("The id is: ", doc.id)
    st.write("The contents are: ", doc.to_dict())


st.markdown('''
<div style="color:black;font-size:20px; text-align: center;"> Welcome to the front-page of our modest application. This application aims to provide you, our users, with a probability on an article you are reading \
as to its likelihood of being untrue (a.k.a. credibility index). Our objective is to enable you to benefit from our model, built on fact-checked truths and widespread untruths, \
to allow you to determine for yourself if you can trust what you are reading</div>''', unsafe_allow_html= True)

st.text(f'''{"-"*228}''')

st.markdown('''<div style="color:black;font-size:30px; text-align: center;"> Join us in our battle against misinformation </div>''', unsafe_allow_html=True)

st.text('')
st.text(f'''{"-"*228}''')

#Dividing up page into columns to show image in center column
col1, col2, col3, col4, col5, col6, col7 = st.columns([1,1,1,1.5,1,1,1])

with col1:
    st.write("")

with col2:
    st.write("")

with col3:
    st.write("")

with col4:
    st.image("images/StopFAIke_logo1.jpg", width=300)

with col5:
    st.write("")

with col6:
    st.write("")

with col7:
    st.write("")

model_url = 'https://stop-faike-j7vxpv56fq-de.a.run.app/predict'

direction = st.radio('Select a type of data to pass', ('URL', 'Textual Content'))

disclaimer = f'''<div class="highlight white" style='color:black;font-size:20px; text-align: center;'>Disclaimer: The model has been trained on \
                    <div style='font-size:15px;'> 1. Fake and real news dataset - <a href=https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset> Kaggle </a> </div>
                    <div style='font-size:15px;'> 2. Dataset collected using FakeNewsNet - <a href=https://github.com/KaiDMML/FakeNewsNet> GitHub Repo </a> </div>
                    <div style='font-size:15px;'> 3. Scraped information from US Politics related fact-checks - <a href=https://www.politifact.com/factchecks/list/> Politifact </a> </div>
                    <div style='font-size:15px;'> 4. Scraped information from COVID-related fact-checks - <a href=https://www.poynter.org/ifcn-covid-19-misinformation/> Poynter </a> </div>
                    Results on new information may vary, especially on unrelated topics </div>
                    '''

if direction == 'URL':
    txt = st.text_area('', '''
    Please enter a URL - https://example.com
    ''')

    url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.match(url_regex, txt) is not None:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

        response = requests.get(txt, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        title = ''
        #Looping over the h1 tags and finding the first instance where it is most likely the title
        for item in soup.find_all('h1'):
            if item.string and len(set(str.split(item.string))) > 3:
                title += item.string
                break
        
        # para_list = ''
        # for item in soup.find_all('p'):
        #     if item.string:
        #         para_list += item.string

        # attrs={'class':re.compile(r'title')}
        # st.write(para_list)

        #TODO - Loading Bar/Expected waiting time

        pred_response = requests.get(model_url, params={'article': title})
        pred = pred_response.json()['prediction']

        col1, col2 = st.columns([2,1])

        with col1:
            #Show a preview pane of the url
            st.components.v1.html(response.content,  height = 500, scrolling=True)

        with col2:
            if pred >= 0.5:
                st.markdown(f'''<div class="highlight red" style='color:white;font-size:30px; text-align: center;'>FAKE
                <div> {pred*100:.1f} % </div> </div>''', unsafe_allow_html=True)

                st.markdown(disclaimer, unsafe_allow_html=True)
                
            else:
                st.markdown(f'''<div class="highlight green" style='color:white;font-size:30px; text-align: center;'>TRUE
                <div> {(1-pred)*100:.1f} % </div> </div>''', unsafe_allow_html=True)

                st.markdown(disclaimer, unsafe_allow_html=True)      

        #TODO - Highlight the words that are important to the model in terms of affecting the score
        
        # Store information in DB
        if db:
            db.collection("url_predictions").add({
                "pred"      : pred,
                "title"     : title,
                "url"       : txt,
                "timestamp" : firestore.SERVER_TIMESTAMP
                })

    else:
        st.markdown('''<div class="highlight white" style='color:red;text-align: center;'>You entered an invalid URL.
        Please enter it with the "https://" prefix if you missed it.</div>''', unsafe_allow_html=True)


elif direction == 'Textual Content':
    txt = st.text_area('Please enter the textual content below', '''
    Enter your text here
    ''')

    #TODO - Loading Bar/Expected waiting time
   
    if txt != '''
    Enter your text here
    ''':
        pred_response = requests.get(model_url, params={'article': txt})
        pred = pred_response.json()['prediction']

        col1, col2, col3 = st.columns([1,2,1])

        with col1:
            st.write("")

        with col2:
            if pred >= 0.5:
                st.markdown(f'''<div class="highlight red" style='color:white;font-size:30px; text-align: center;'>FAKE
                <div> {pred*100:.1f} % </div> </div>''', unsafe_allow_html=True)

                st.markdown(disclaimer, unsafe_allow_html=True)

            else:
                st.markdown(f'''<div class="highlight green" style='color:white;font-size:30px; text-align: center;'>TRUE
                <div> {(1-pred)*100:.1f} % </div> </div>''', unsafe_allow_html=True)

                st.markdown(disclaimer, unsafe_allow_html=True)            

        with col3:
            st.write("")

        #TODO - Highlight the words that are important to the model in terms of affecting the score

        # Store information in DB
        if db:
            db.collection("text_predictions").add({
                "pred"      : pred,
                "text"      : txt,
                "timestamp" : firestore.SERVER_TIMESTAMP
                })
