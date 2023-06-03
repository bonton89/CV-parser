# Script for scoring the matched CVs using different input values using fuzz algo and rule return Top Cvs with Score.
# The Fuzz algo used for finding out near match words.


# Import Libs

import re
import nltk
import os
from io import StringIO
import pandas as pd
from thefuzz import fuzz
from thefuzz import process
import numpy as np
import os
import shutil

# Scoring function

def predict_resume_scoring(job_title,skill,education,experience):
    
    # Read the database
    database = pd.read_csv(r'02_Database\full_database.csv')

    # Lowercase and type change for columns
    job_title = job_title.lower()
    skill = skill.lower()
    education = education.lower()
    experience = float(experience)
    database = database.set_index('file_name')

    # Selecting database for the Job Title entered
    database = database[database['Job Role']== job_title]

    # Setting Limit which will give us socre for all the docs
    limit = len(database)
    
    # Match results for education
    education_match = process.extract(str(education),database['Qualification'], limit= limit  , scorer=fuzz.token_set_ratio)
    edu_result_df = pd.DataFrame()
    for i in range(limit):

        education_score = education_match[i][1]
        file = education_match[i][2]
        match_df = pd.DataFrame([[file,education_score]],columns = ['file_name','education_score'])
        edu_result_df = pd.concat([edu_result_df,match_df])
    
    # Match results for Skills
    skill_match = process.extract(str(skill),database['professional_skill'], limit= limit  , scorer=fuzz.token_set_ratio)
    skill_result_df = pd.DataFrame()
    for i in range(limit):
        skill_score = skill_match[i][1]
        file = skill_match[i][2]
        match_df = pd.DataFrame([[file,skill_score]],columns = ['file_name','skill_score'])
        skill_result_df = pd.concat([skill_result_df,match_df])

    
    database = database.reset_index()
    # Joining the tables
    database = pd.merge(database,edu_result_df,how = 'left',on = 'file_name')
    database = pd.merge(database,skill_result_df,how = 'left',on = 'file_name')
    
    # Rule for Work Experience
    database['Work Experience'] = database['Work Experience'].astype('float')
    database['experience_score']=np.where(database['Work Experience']>=experience,100,np.where(np.logical_and(database['Work Experience']>=experience-1,database['Work Experience']<experience),50,0))
    
    # Setting up Total Score value with average for the three columns
    database['Total_Score'] = (database['education_score'] + database['skill_score'] + database['experience_score'])/3
    # Rounding Up
    database['Total_Score'] = np.round(database['Total_Score'])
    
    # Deciding the Threshold 
    selected_resume = database[database['Total_Score']>= 60]
    selected_resume = selected_resume[['file_name','Total_Score']]
    # Renaming the Coloumn Name
    selected_resume.columns = ['Matched_CV','Score']
    # Sorting the Values based on Score
    selected_resume = selected_resume.sort_values(by = ['Score'],ascending=False)
    # Remove Index
    selected_resume = selected_resume.reset_index(drop=True)
    # Incrementing the Index value
    selected_resume.index =  selected_resume.index + 1 

    # Writing the selected resume file  
    selected_resume.to_csv("03_Selected_CVs_File\selected_resume.csv")
    # Writing the database
    #database.to_csv("03_Selected_CVs_File\resulted_resume.csv")
    
    # Origin folder where raw CVs are stored
    origin = r'01_Raw_CVs/'
    # Target folder to place the matched CV
    target = r'04_Matched_CVs_pdf/'

    # Movement of Cvs from Origin folder to Target Folder
    files = selected_resume['Matched_CV'].to_list()
    # Copy the selected CVs
    for file in files:
        shutil.copy(origin + file ,target + file)

    print(selected_resume)
    # Return selected resume value
    return selected_resume