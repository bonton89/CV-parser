# Script to extract text from PDFs and creating database
# Used PDFminer lib 


# Import Libs
import re
import nltk
from nltk.corpus import stopwords
stop = stopwords.words('english')
from nltk.corpus import wordnet
import os
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import pandas as pd
from thefuzz import fuzz
from thefuzz import process
import numpy as np
import tqdm


# Function to extract text from pdf
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    #codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr,laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text
    
    
# Extract Phone Number   
def extract_phone_number(text):
    phone = re.findall(r"\d{10}",text)
    if phone:
        phone_number = phone[0]
        return phone_number
    else:
        phone_number = 'NA'
        return phone_number
        
        
# Extact emails     
def extract_email(email):
    email = re.findall("([^@|\s]+@[^@]+\.[^@|\s]+)", email)
    if email:
        email_id = email[0].split()[0].strip(';')
    else:
        email_id = 'NA'
    return email_id
    
# Extract Education details    
def education_degree_extraction(text):
    education = []
    education_title = ['education','qualification','educational qualification','educational credentials']
    word = '|'.join(education_title)
    if re.search(word,text):
        pos_start = re.search(word,text).start()
        pos_end =  re.search(word,text).end()
        degree = pd.read_csv(r'C:\Users\abhis\Downloads\Resume\01_Data\other_data\degree.csv')
        for deg in degree['Education Degree']:
            deg = deg.lower()
            deg = deg.strip()
            qualification = re.findall(r"\b" + re.escape(deg) + r"\b",text[pos_start:pos_end + 500])
            
            if len(qualification)>0:
                education.append(qualification[0])
                #print(qualification)
                
        return education
        
        
#Extract Skills        
def extract_skill(text):
    skills = []
    skills_df = pd.read_csv(r'C:\Users\abhis\Downloads\Resume\01_Data\other_data\skills.csv')
    for i in skills_df['Professional Skills']:
        i = i.strip()
        i = i.lower()
        skill = re.findall(r"\b" + re.escape(i) + r"\b",text)
        if len(skill) >0:
            skills.append(skill[0])
    return skills
    
    
# Extract Experience    
def extract_experience(text):
    word_1 = 'experience'
    if re.search(r"\b" + re.escape(word_1) + r"\b",text):
        exp_match = re.search(r"\b" + re.escape(word_1) + r"\b",text).start()
        exp_match = re.search(r"\b" + re.escape(word_1) + r"\b",text).end()
        #print(exp_match)
        years = re.findall(r"years",text[exp_match-50:exp_match +50])
        
        if len(years) >0:
            number = re.findall('(\d+(?:\.\d+)?)',text[exp_match-50:exp_match +50])
            
            return number[0]
            
    else:
        return 'NA'
        
# Function for preparing database        
def prepare_resume_database():
    df = pd.DataFrame()
    resume_list = os.listdir(r'C:\Users\abhis\Downloads\Resume\01_Data\Resume_data')
    for i in (resume_list):
        print(i)
        path = f"C:/Users/abhis/Downloads/Resume/01_Data/Resume_data/{i}"
        resume_text = convert_pdf_to_txt(path)
        resume_text = resume_text.lower()
        file_name = i
        education = education_degree_extraction(resume_text)
        professional_skill = extract_skill(resume_text)
        email_id = extract_email(resume_text)
        phone_number = extract_phone_number(resume_text)
        experience = extract_experience(resume_text)
        resume_df = pd.DataFrame([[file_name,education,professional_skill,email_id,phone_number,experience]],columns = ['file_name','education','professional_skill','email_id','phone_number','experience'])

        df = pd.concat([df,resume_df])



    df['qualification'] = 'NA'
    master_degree = ['master','master of science','m.sc','msc','mba','pg','post graduation','m.tech']
    bachelor_degree = ['b.tech','be','b.e','bachelor']


    master_pattern = '|'.join(master_degree)
    bachelor_pattern = '|'.join(bachelor_degree)
    for i in range(df.shape[0]):
        qualification = []
        element = []
        d = [re.findall(master_pattern,k) for k in df['education'].iloc[i] ]

        for e in d:
            element.append(len(e))
        if sum(element)>0:
            de = 'master'
            b ='bachelor'
            qualification.append(de)
            qualification.append(b)

        c = [re.findall(bachelor_pattern,k) for k in df['education'].iloc[i] ]
        b_element = []
        for e in c:
            b_element.append(len(e))
        if sum(b_element)>0:
            r = 'bachelor'
            qualification.append(r)

        df['qualification'].iloc[i] = qualification
        
    df['Qualification'] = df['education'] + df['qualification']
    df.drop(['education','qualification'],axis=1,inplace=True)
    
        
    return df
