from flask import Flask, Response, request, session, abort, url_for, jsonify, send_file
from flask_cors import CORS
import os
import base64
from PIL import Image
from datetime import datetime
from datetime import date
import datetime
import random
from random import seed
from random import randint
import re
# import cv2  # unused — commented out to avoid opencv-python dependency
import PIL.Image
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import threading
import time
import shutil
import hashlib
import urllib.request
import requests
import urllib.parse
from urllib.request import urlopen
import webbrowser
import json
import mysql.connector
# gensim replaced with nltk (gensim incompatible with Python 3.14)
import nltk
from nltk.stem import PorterStemmer
# Note: gensim STOPWORDS/remove_stopwords not actually used —
# bot() overrides them with wordcloud STOPWORDS locally
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
# --- Heavy ML imports below are used only in model() which is never called ---
# import torch
# from transformers import (
#     BertTokenizer,
#     BertForSequenceClassification,
#     BertForTokenClassification
# )
# from sentence_transformers import SentenceTransformer
# --- Keep sklearn for potential future use ---
from sklearn.metrics.pairwise import cosine_similarity

# API Overrides
def render_template(template_name, **kwargs):
    return jsonify({"template": template_name, "data": kwargs})

def redirect(location, **kwargs):
    return jsonify({"redirect": location})

mydb = mysql.connector.connect(
  host=os.environ.get("DB_HOST", "localhost"),
  user=os.environ.get("DB_USER", "schemebot_user"),
  passwd=os.environ.get("DB_PASS", "schemebot123"),
  charset="utf8",
  database=os.environ.get("DB_NAME", "schemebot")
)

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = 'abcdef'
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####

@app.route('/',methods=['POST','GET'])
def index():
    msg=""
    mycursor = mydb.cursor()

    ff=open("static/det.txt","w")
    ff.write("1")
    ff.close()

                
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM cc_register where uname=%s && pass=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('bot')) 
        else:
            msg="You are logged in fail!!!"

    return render_template('index.html',msg=msg)

@app.route('/login',methods=['POST','GET'])
def login():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM cc_admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            msg="You are logged in fail!!!"
        

    return render_template('login.html',msg=msg,act=act)

@app.route('/login_user',methods=['POST','GET'])
def login_user():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM cc_register where uname=%s && pass=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('bot')) 
        else:
            msg="You are logged in fail!!!"
        

    return render_template('login_user.html',msg=msg,act=act)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""
    mycursor = mydb.cursor()
    if request.method=='POST':
        file = request.files['file']

        fn="datafile.csv"
        file.save(os.path.join("static/upload", fn))

        filename = 'static/upload/datafile.csv'
        data1 = pd.read_csv(filename, header=0, encoding='cp1252')

        inserted = 0
        skipped = 0
        for ss in data1.values:

            des=""
            if pd.isnull(ss[2]):
                des=""
            else:
                des=str(ss[2])
                
            eligi=""
            if pd.isnull(ss[3]):
                eligi=""
            else:
                eligi=str(ss[3])

            # Skip if scheme already exists
            mycursor.execute("SELECT count(*) FROM cc_data where scheme=%s", (str(ss[0]),))
            already = mycursor.fetchone()[0]
            if already > 0:
                skipped += 1
                continue

            mycursor.execute("SELECT max(id)+1 FROM cc_data")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid = 1

            sql = "INSERT INTO cc_data(id,scheme,department,description,eligibility) VALUES (%s,%s,%s,%s,%s)"
            val = (maxid, str(ss[0]), str(ss[1]), des, eligi)
            mycursor.execute(sql, val)
            mydb.commit()
            inserted += 1
        
        msg = f"success: {inserted} schemes inserted, {skipped} already existed"


    return render_template('admin.html',msg=msg)

@app.route('/process', methods=['GET', 'POST'])
def process():
    msg=""
    cnt=0
    

    filename = 'static/upload/datafile.csv'
    data1 = pd.read_csv(filename, header=0,encoding='cp1252')
    data2 = list(data1.values.flatten())

    
    data=[]
    i=0
    sd=len(data1)
    rows=len(data1.values)
    
    #print(str(sd)+" "+str(rows))
    for ss in data1.values:
        cnt=len(ss)
        data.append(ss)
    cols=cnt

    
    return render_template('process.html',data=data, msg=msg, rows=rows, cols=cols)

@app.route('/process2', methods=['GET', 'POST'])
def process2():
    msg=""
    act=request.args.get("act")
    
    return render_template('process2.html',msg=msg, act=act)

@app.route('/add_query', methods=['GET', 'POST'])
def add_query():
    msg=""
    sid=""
    mycursor = mydb.cursor()

    cnt=0
    
    data=[]
    

    mycursor.execute("SELECT * FROM cc_data")
    data = mycursor.fetchall()
        
    
    if request.method=='POST':
        sid=request.form['sid']
        
        msg="success"

    return render_template('add_query.html',msg=msg,sid=sid,data=data)


@app.route('/add_query1', methods=['GET', 'POST'])
def add_query1():
    msg=""
    act=request.args.get("act")
    sid=request.args.get("sid")
    mycursor = mydb.cursor()
    
    cnt=0
    #filename = 'static/upload/datafile.csv'
    #data1 = pd.read_csv(filename, header=0,encoding='cp1252')
    #data2 = list(data1.values.flatten())

    
    data=[]
    #i=0
    #for ss in data1.values:
    #    cnt=len(ss)
    #    data.append(ss)
    #cols=cnt

    mycursor.execute("SELECT * FROM cc_data where id=%s",(sid,))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM cc_contact where scheme_id=%s",(sid,))
    data2 = mycursor.fetchall()
        
    
    if request.method=='POST':
        
        user_query=request.form['user_query']
        district=request.form['district']
        name=request.form['name']
        mobile=request.form['mobile']
        designation=request.form['designation']
        address=request.form['address']
        url_link=request.form['url_link']
        scheme_req=request.form['scheme_req']
        
        
        mycursor.execute("update cc_data set user_query=%s,district=%s,name=%s,mobile=%s,designation=%s,address=%s,url_link=%s,scheme_req=%s where id=%s",(user_query,district,name,mobile,designation,address,url_link,scheme_req,sid))
        mydb.commit()

        mycursor.execute("SELECT count(*) FROM cc_contact where id=%s && name=%s && mobile=%s",(sid,name,mobile))
        d1 = mycursor.fetchone()[0]
        if d1==0:
            mycursor.execute("SELECT max(id)+1 FROM cc_contact")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            

            sql = "INSERT INTO cc_contact(id,scheme_id,district,name,mobile,designation,address,url_link) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            val = (maxid,sid,district,name,mobile,designation,address,url_link)
            mycursor.execute(sql, val)
            mydb.commit()
        else:
            mycursor.execute("update cc_contact set district=%s,name=%s,mobile=%s,designation=%s,address=%s,url_link=%s where scheme_id=%s && name=%s",(district,name,mobile,designation,address,url_link,sid,name))
            mydb.commit()
        msg="success"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from cc_contact where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_query1',sid=sid)) 

    return render_template('add_query1.html',msg=msg,sid=sid,act=act,data=data,data2=data2)

##
def model():
    spacy.load("en_core_web_sm")

    # Load BERT Intent Model
    intent_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    intent_model = BertForSequenceClassification.from_pretrained(
        "bert-base-uncased",
        num_labels=5   # Example: eligibility, benefits, documents, amount, apply
    )

    # Load BERT NER Model
    ner_tokenizer = BertTokenizer.from_pretrained("dslim/bert-base-NER")
    ner_model = BertForTokenClassification.from_pretrained("dslim/bert-base-NER")

    # Load Sentence-BERT
    sbert_model = SentenceTransformer("all-MiniLM-L6-v2")

def preprocess_text(text):
    doc = nlp(text.lower())
    tokens = [
        token.text for token in doc
        if not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)

#Intent Detection (BERT)
def detect_intent(text):
    inputs = intent_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True
    )
    outputs = intent_model(**inputs)
    intent_id = torch.argmax(outputs.logits).item()
    
    intent_map = {
        0: "Eligibility Check",
        1: "Benefits",
        2: "Documents Required",
        3: "Amount",
        4: "Application Process"
    }
    return intent_map[intent_id]

#Named Entity Recognition (NER)
def extract_entities(text):
    inputs = ner_tokenizer(text, return_tensors="pt", truncation=True)
    outputs = ner_model(**inputs)

    predictions = torch.argmax(outputs.logits, dim=2)
    tokens = ner_tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

    entities = []
    for token, pred in zip(tokens, predictions[0]):
        label = ner_model.config.id2label[pred.item()]
        if label != "O":
            entities.append((token, label))

    return entities

#Semantic Matching (Sentence-BERT + Cosine Similarity)
def semantic_search(query, schemes):
    query_embedding = sbert_model.encode([query])
    scheme_texts = [s["name"] + " " + s["description"] for s in schemes]
    scheme_embeddings = sbert_model.encode(scheme_texts)

    similarities = cosine_similarity(query_embedding, scheme_embeddings)
    best_match_idx = np.argmax(similarities)

    return schemes[best_match_idx]

#Dialogue Management (FSM – Rule-Based)
class DialogueManager:
    def __init__(self):
        self.current_scheme = None

    def update_context(self, scheme):
        self.current_scheme = scheme

    def respond(self, intent):
        if not self.current_scheme:
            return "Please specify the scheme name."

        if intent == "Eligibility Check":
            return self.current_scheme["eligibility"]

        if intent == "Benefits":
            return self.current_scheme["description"]

        if intent == "Documents Required":
            return self.current_scheme["documents"]

        if intent == "Amount":
            return self.current_scheme["amount"]

        if intent == "Application Process":
            return self.current_scheme["apply"]

        return "Sorry, I couldn't understand your request."

#Response Generation
def chatbot_response(user_input, dm):
    clean_text = preprocess_text(user_input)
    intent = detect_intent(clean_text)
    entities = extract_entities(user_input)

    scheme = semantic_search(clean_text, schemes)
    dm.update_context(scheme)

    response = dm.respond(intent)

    return {
        "Intent": intent,
        "Entities": entities,
        "Scheme": scheme["name"],
        "Response": response
    }
####

@app.route('/admin2', methods=['GET', 'POST'])
def admin2():
    msg=""
    mycursor = mydb.cursor()
    if request.method=='POST':
        input1=request.form['input']
        output=request.form['output']
        link=request.form['link']

        if link is None or link=="":
            url=""
        else:
            url=' <a href='+link+' target="_blank">Click Here</a>'

        output+=url
        
        mycursor.execute("SELECT max(id)+1 FROM cc_data")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        sql = "INSERT INTO cc_data(id,input,output) VALUES (%s,%s,%s)"
        val = (maxid,input1,output)
        mycursor.execute(sql, val)
        mydb.commit()

        
        print(mycursor.rowcount, "Added Success")
        
        return redirect(url_for('view_data',msg='success'))

    return render_template('admin2.html',msg=msg)

@app.route('/view_user', methods=['GET', 'POST'])
def view_user():
    value=[]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cc_register")
    data = mycursor.fetchall()

    
    return render_template('view_user.html', data=data)

@app.route('/page', methods=['GET', 'POST'])
def page():
    fn=request.args.get("fn")
   
    
    return render_template('page.html',fn=fn)



@app.route('/register',methods=['POST','GET'])
def register():
    msg=""
    act=""
    mycursor = mydb.cursor()
    name=""
    mobile=""
    mess=""
    uid=""
    if request.method=='POST':
        
        uname=request.form['uname']
        name=request.form['name']     
        mobile=request.form['mobile']
        email=request.form['email']
        location=request.form['location']
        pass1=request.form['pass']

        
        now = datetime.datetime.now()
        rdate = now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM cc_register where uname=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM cc_register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            
            uid=str(maxid)
            sql = "INSERT INTO cc_register(id, name, mobile, email, location, uname, pass, otp, status, create_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid, name, mobile, email, location, uname, pass1, '', '0', rdate)
            msg="success"
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
           
        else:
            msg="fail"
            
    return render_template('register.html',msg=msg,mobile=mobile,name=name,mess=mess,uid=uid)



def lg_translate(lg, output):
    """Translate output text using deep-translator (Python 3.14 compatible)."""
    result = output  # fallback: return original
    recognized_text = output

    available_languages = {
        'ta': 'Tamil', 'hi': 'Hindi', 'ml': 'Malayalam',
        'kn': 'Kannada', 'te': 'Telugu', 'mr': 'Marathi',
        'ur': 'Urdu', 'bn': 'Bengali', 'gu': 'Gujarati', 'fr': 'French'
    }

    try:
        selected_languages = lg.split(',')
        for lang_code in selected_languages:
            lang_code = lang_code.strip()
            if lang_code in available_languages:
                translated = GoogleTranslator(
                    source='auto', target=lang_code
                ).translate(recognized_text)
                print(f"Translation ({lang_code}): {translated}")
                result = translated
            else:
                print(f"Language code {lang_code} not available.")
    except Exception as e:
        print("Translation error:", e)

    return result

####
def translate_text(text, source_language, target_language):
    api_key = 'AIzaSyDW9tvaQUsywmaILt73Go8Fy5mU6ILOixU'  # Replace with your API key
    url = f'https://translation.googleapis.com/language/translate/v2?key={api_key}'
    payload = {
        'q': text,
        'source': source_language,
        'target': target_language,
        'format': 'text'
    }
    response = requests.post(url, json=payload)
    translation_data = response.json()
    translated_text = translation_data
    #translation_data['data']['translations'][0]['translatedText']
    return translated_text

@app.route('/bot', methods=['GET', 'POST'])
def bot():
    msg=""
    output=""
    uname=""
    mm=""
    s=""
    xn=0
    val=""
    qry_st=""
    if 'username' in session:
        uname = session['username']
    mydb = mysql.connector.connect(
      host=os.environ.get("DB_HOST", "localhost"),
      user=os.environ.get("DB_USER", "schemebot_user"),
      passwd=os.environ.get("DB_PASS", "schemebot123"),
      charset="utf8",
      database=os.environ.get("DB_NAME", "schemebot")
    )

    
    
    cnt=0
   
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM cc_register where uname=%s",(uname, ))
    value = mycursor.fetchone()
    
    mycursor.execute("SELECT * FROM cc_data order by rand() limit 0,10")
    data=mycursor.fetchall()
            
    if request.method=='POST':
        msg_input=request.form['msg_input']
        lg=request.form['language']
        text=msg_input

        ff=open("static/det.txt","r")
        qry_st=ff.read()
        ff.close()
        ##
        #NLP
        #nlp=STOPWORDS
        #def remove_stopwords(text):
        #    clean_text=' '.join([word for word in text.split() if word not in nlp])
        #    return clean_text
        ##
        #txt=remove_stopwords(msg_input)
        ##
        stemmer = PorterStemmer()
    
        from wordcloud import STOPWORDS
        STOPWORDS.update(['rt', 'mkr', 'didn', 'bc', 'n', 'm', 
                          'im', 'll', 'y', 've', 'u', 'ur', 'don', 
                          'p', 't', 's', 'aren', 'kp', 'o', 'kat', 
                          'de', 're', 'amp', 'will'])

        def lower(text):
            return text.lower()

        def remove_specChar(text):
            return re.sub("#[A-Za-z0-9_]+", ' ', text)

        def remove_link(text):
            return re.sub(r'@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+', ' ', text)

        def remove_stopwords(text):
            return " ".join([word for word in 
                             str(text).split() if word not in STOPWORDS])

        def stemming(text):
            return " ".join([stemmer.stem(word) for word in text.split()])

        #def lemmatizer_words(text):
        #    return " ".join([lematizer.lemmatize(word) for word in text.split()])

        def cleanTxt(text):
            text = lower(text)
            text = remove_specChar(text)
            text = remove_link(text)
            text = remove_stopwords(text)
            text = stemming(text)
            
            return text

        

        #show the clean text
        #dat=df.head()
        #data=[]
        #for ss in dat.values:
        #    data.append(ss)
        #msg_input=data
        mm=""
        mm1=""
        ######################
        if msg_input=="" or msg_input=="hi":
            s=1
            output="How can i help you?"
            if lg=="":
                val=json.dumps(output)
            else:
                val=lg_translate(lg,output)                
            return val
            #return json.dumps(output)
        else:
            if qry_st=="1":
                clean_msg=cleanTxt(msg_input)
                print(clean_msg)
                cleaned='%'+clean_msg+'%'
                
                mycursor.execute("SELECT count(*) FROM cc_data where user_query like %s",(cleaned,))
                cnt1=mycursor.fetchone()[0]
                if cnt1>0:
                    mm='%'+clean_msg+'%'
                else:
                    mm='%'+msg_input+'%'

                ###
                mycursor.execute("SELECT count(*) FROM cc_data where scheme like %s",(cleaned,))
                cnt12=mycursor.fetchone()[0]
                if cnt12>0:
                    mm1='%'+clean_msg+'%'
                else:
                    mm1='%'+msg_input+'%'
                ###
                
                mycursor.execute("SELECT count(*) FROM cc_data where user_query like %s",(mm,))
                cnt=mycursor.fetchone()[0]



                
                if cnt>0:
                    dd3=""
                    sid=0
                    mycursor.execute("SELECT * FROM cc_data where user_query like %s",(mm,))# limit 0,1
                    dd=mycursor.fetchall()
                    for dd1 in dd:
                        sid=dd1[0]
                        
                        dd3+="<br>"+dd1[1]+"<br><br>Department:<br>"+dd1[2]

                        if dd1[3]=="":
                            s=1
                        else:
                            
                            dd3+="<br><br>Relevant Component:<br>"+dd1[3]


                        if dd1[4]=="":
                            s=1
                        else:
                            dd3+="<br><br>Eligibility:<br>"+dd1[4]
                            
                        if dd1[12]=="":
                            s=1
                        else:
                            dd3+="<br><br>Document Required: "+dd1[12]

                    dff=[]
                    dff2=""
                    
                    mycursor.execute("SELECT count(*) FROM cc_contact where scheme_id=%s && district!=''",(sid,))
                    cnt4=mycursor.fetchone()[0]
                    if cnt4>0:
                        mycursor.execute("SELECT * FROM cc_contact where scheme_id=%s",(sid,))
                        dd4=mycursor.fetchall()
                        for dd41 in dd4:
                            dff.append(dd41[2])
                        dff2=",".join(dff)
                        dd3+="<br><br>Which location contacts you want this scheme?<br>"
                        dd3+="("+dff2+")"
                        ff=open("static/det.txt","w")
                        ff.write("2")
                        ff.close()

                        ff=open("static/scheme.txt","w")
                        ff.write(str(sid))
                        ff.close()

                    
                    output=dd3
                    
                

                else:
                    ####mm1
                    print("aa")
                    print(mm1)
                    dd3=""
                    sid=0
                    mycursor.execute("SELECT count(*) FROM cc_data where scheme like %s",(mm1,))
                    cnt11=mycursor.fetchone()[0]
                    if cnt11>0:
                                        
                        mycursor.execute("SELECT * FROM cc_data where scheme like %s",(mm1,))# limit 0,1
                        ddx=mycursor.fetchall()
                        for dd1 in ddx:
                            sid=dd1[0]
                            print(dd1[1])
                            dd3+="<br>"+dd1[1]+"<br><br>Department:<br>"+dd1[2]

                            if dd1[3]=="":
                                s=1
                            else:
                                
                                dd3+="<br><br>Relevant Component:<br>"+dd1[3]


                            if dd1[4]=="":
                                s=1
                            else:
                                dd3+="<br><br>Eligibility:<br>"+dd1[4]

                            if dd1[12]=="":
                                s=1
                            else:
                                dd3+="<br>Document Required: "+dd1[12]

                        dff=[]
                        dff2=""
                        
                        mycursor.execute("SELECT count(*) FROM cc_contact where scheme_id=%s && district!=''",(sid,))
                        cnt4=mycursor.fetchone()[0]
                        if cnt4>0:
                            mycursor.execute("SELECT * FROM cc_contact where scheme_id=%s",(sid,))
                            dd4=mycursor.fetchall()
                            for dd41 in dd4:
                                dff.append(dd41[2])
                            dff2=",".join(dff)
                            dd3+="<br><br>Which location contacts you want this scheme?<br>"
                            dd3+="("+dff2+")"
                            ff=open("static/det.txt","w")
                            ff.write("2")
                            ff.close()

                            ff=open("static/scheme.txt","w")
                            ff.write(str(sid))
                            ff.close()

                                        
                        output=dd3
                    
                    else:                    
                        if msg_input=="":
                            output="How can i help you?"
                        else:
                            output="Sorry, No Results Found!"

                if lg=="":
                    val=json.dumps(output)
                else:
                    val=lg_translate(lg,output)                
                return val
                ####################

            

            elif qry_st=="2":
                clean_msg=cleanTxt(msg_input)
                print(clean_msg)
                cleaned='%'+clean_msg+'%'
                
                mycursor.execute("SELECT count(*) FROM cc_contact where district like %s",(cleaned,))
                cnt1=mycursor.fetchone()[0]
                if cnt1>0:
                    mm='%'+clean_msg+'%'
                else:
                    mm='%'+msg_input+'%'
                
                
                mycursor.execute("SELECT count(*) FROM cc_contact where district like %s",(mm,))
                cnt=mycursor.fetchone()[0]



                
                if cnt>0:
                    dd3=""
                    ff=open("static/scheme.txt","r")
                    sidd=ff.read()
                    ff.close()
                    mycursor.execute("SELECT * FROM cc_contact where district like %s && scheme_id=%s limit 0,1",(mm,sidd))
                    dd=mycursor.fetchall()
                    for dd1 in dd:
                        dd3+="<br>District: "+dd1[2]+"<br>Name: "+dd1[3]+"<br>Designation: "+dd1[5]
                        dd3+="<br>Address: "+dd1[6]+"<br>Mobile No.: "+str(dd1[4])
                        
                        if dd1[7]=="":
                            s=1
                        else:
                            dd3+="<br><a href='"+dd1[7]+"' target='_blank'>Click Here</a>"
                       
                        
                    output=dd3
                    ff=open("static/det.txt","w")
                    ff.write("1")
                    ff.close()
                

                else:
                    if msg_input=="":
                        output="How can i help you?"
                    else:
                        output="Sorry, No Results Found!"


            
                        
                if lg=="":
                    val=json.dumps(output)
                else:
                    val=lg_translate(lg,output)                
                return val
                #return json.dumps(output)
                ##################################


    return render_template('bot.html', msg=msg,output=output,uname=uname,data=data,value=value)   

    
@app.route('/sign')
def sign():
    return render_template('sign.html')

@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username'];
    password = request.form['password'];

    print(password)
    return json.dumps({'status':'OK','user':user,'pass':password});


@app.route('/view_data', methods=['GET', 'POST'])
def view_data():
    data=[]
    msg=request.args.get("msg")
    act=request.args.get("act")
    url=""
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM cc_data")
    data1 = mycursor.fetchall()

    for dat in data1:
        dt=[]
        txt=dat[2]
        t=txt.replace("\t\r\n","<br>")
        #if "\t\r\n" in dat[2]:

        dt.append(dat[0])
        dt.append(dat[1])
        dt.append(t)
        data.append(dt)
            
            
    

    if request.method=='POST':
        input1=request.form['input']
        output=request.form['output']
        link=request.form['link']

        if link is None:
            url=""
        else:
            url=' <a href='+link+' target="_blank">Click Here</a>'

        output+=url
        
        mycursor.execute("SELECT max(id)+1 FROM cc_data")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        sql = "INSERT INTO cc_data(id,input,output) VALUES (%s,%s,%s)"
        val = (maxid,input1,output)
        mycursor.execute(sql, val)
        mydb.commit()

        
        print(mycursor.rowcount, "Added Success")
        
        return redirect(url_for('view_data',msg='success'))
        #if cursor.rowcount==1:
        #    return redirect(url_for('index',act='1'))

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from cc_data where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('view_data'))
    
    
    return render_template('view_data.html',msg=msg,act=act,data=data)

@app.route('/down', methods=['GET', 'POST'])
def down():
    fn = request.args.get('fname')
    path="static/upload/"+fn
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=3000)
