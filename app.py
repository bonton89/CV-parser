# Script for creating web form to take input and display the matched cv with the score
# pywebio lib is used for creating webform/UI and flask lib is used to deploy in local host
# -----------------------------------------------------------------------------------------

# import python libs
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH
from flask import Flask, send_from_directory
from pywebio.input import *
from pywebio.output import *
import argparse
from pywebio import start_server
import time
from resume_scoring import predict_resume_scoring
app = Flask(__name__)
import os
import shutil

# CV parser function will take input from the UI and display the matched results
def cv_parser():
    
    # Display welcome message
    put_code("-----<< Welcome to CV Parser Application >>-----")
    
    # count to track the history of search
    count=0
    # add_more us used to end the while loop
    add_more = True
    
    # loop to take values untill user press no button
    while add_more: 
        
        # Take input in the form of webform.
        info = input_group("Enter Details : ",[
          input("Enter Job Title you are looking for :", name='job_title'),
          input("Enter Skillset you are looking for :", name='skill'),
          input("Enter Education you are looking for :", name='education'),
          input("Enter years of experience you are looking for :", name='experience',type=FLOAT)
        ])
        # display all the input values
        print(info['job_title'], info['skill'],info['education'],info['experience'])
        
        # Value assignment
        job_title=info['job_title']
        skill=info['skill']
        education = info['education']
        experience = info['experience']
        
        # Displaying the value entered by the user    
        put_text('You have searched fors Job Tile : ',job_title)
        put_text('Selected Skillset :' ,skill)
        put_text('Required Degree :' ,education)
        put_text('Required experience :' ,experience)
        put_text('------------------------------------------------')
        
        # Creating loading effects in the UI
        with put_loading():
            put_code("Plz Wait..We are working on magic !! Fetching top CVs for you..")
            time.sleep(3)  # Some time-consuming operations
        put_text("Matched Results : ")
        
        # Calling resume_scoring.py function and get the selected resume list
        selected_resume = predict_resume_scoring(job_title,skill,education,experience)

        # Displaying the searched result in the UI
        put_table([
                    {"Job_Title":job_title,"SkillSet":skill,"TopCVFound":selected_resume}
                ], header=["Job_Title", "SkillSet","TopCVFound"]) 
        # Notify the folder location where selected CV in pdf format is saved
        put_code("**Note: All the matched CVs are stored in 04_Matched_CVs_pdf folder")   

        # Take input form user to end the loop
        add_more = actions(label="Would you like to search more ?", 
                        buttons=[{'label': 'Yes', 'value': True}, 
                                 {'label':'No', 'value': False}])
        
        # Displaying the count value which will tell us searched history
        count= count+1
        put_text("--------------------------")
        put_text(f"You have searched for {count} CVs | Search results shown above. ")
        
        put_text("--------------------------")
        
    # Exit Message  
    put_code("----- Thank You for using the CV Parser Application -----")


# Adding app rules
app.add_url_rule('/cv_parser', 'webio_view', webio_view(cv_parser),
            methods=['GET', 'POST', 'OPTIONS'])


# Add details to deploy in a local host
app.run(host='localhost', port=80)