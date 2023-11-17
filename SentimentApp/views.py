from django.shortcuts import render                                                 #for rendering the webpages in django

import pandas as pd                                                                 #pandas library for handling the csv files
from textblob import TextBlob                                                       #library for analysing the text and classify it

import os                                                                           #library to import os functions

from Sentiment_Analysis.settings import BASE_DIR                                    #import variables from another file

import requests
from bs4 import BeautifulSoup                                                       #library function used for youtube subscriber count functionality

from .models import *                                                               #import all the django models

import smtplib                                                                      #library function which enables mail functionality via Simple Mail Transfer Protocol (SMTP)
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from SentimentApp.values import *

file_path = os.path.join(BASE_DIR,'SentimentApp','static','db','facebook.csv')       #reads the csv file and store it in a pandas dataframe
df = pd.read_csv(file_path)
df = df.dropna()
brand_names = df["Brand"].unique()                                                  #stores all the unique brand names available in the database
name = ""                                                                           #global variable used to store the brand name    

init_score = 0                                                                      #global variable used to store the first score when the initial score calculation is done and henceforth is used to store the previous/last updated score of the brand
base_score = 10                                                                     #global variable used to store the base score of the brand before calculating the new score. Initially considered to be 10.
total_score = 0

fb_score = 0                                                                        #global variable used to calculate and store the facebook comment score
score_factor = 0.1                                                                  #global variable used to store the increment/decrement factor

yt_score = 0                                                                        #global variable used to calculate and store the youtube subscriber score
subscriber_count = 0                                                                #global variable used to store the live youtube subscriber count

result = None                                                                       #global variable used to store the message of the result
reason1 = None                                                                      #global variable used to store the facebook impact
reason2 = None                                                                      #global variable used to store the youtube impact

def mainpage(request):                                                              #function to render the mainpage of the application
    return render(request,'mainpage.html')

def register(request):                                                              #function to render the registration page of the application
    return render(request,'register.html')
    
def performSentimentAnalysis(text):                                                 #function to perform sentimental analysis on the given comment
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def initScoreCalc(request):                                                         #function to calculate the initial score of the brand from facebook and youtube data collected
    global init_score, base_score, fb_score, yt_score, name, brand_names, df, subscriber_count
    
    error = None                                                                    #re-initialisation of variables to initial values before calculating new values for other brands
    init_score = 0
    base_score = 10
    fb_score = base_score
    subscriber_count = 0
    
    name = request.GET['input-box']                                                 #get the brand name from the user
    
    if name not in brand_names:                                                     #return an error message if the user inputs a brand name which is unavailable in the database
        error = "Error: Brand not found!"
        return render(request,'mainpage.html',{'error':error})
    
    else:
        new_data = df[df["Brand"]==name]                                            #simulates the data available on Day 1 
        day1_data = new_data.sample(frac = 0.1, random_state = 1)
        fb_score = base_score
        
        calcFacebookScore(day1_data)                                                #function call to calculate the sentiment analysis score on the first day data available for facebook
        calcYoutubeScore()                                                          #function call to calculate the sentiment analysis score on the first day data available for youtube
        
        message = "Brand Rating for " + name + " is"                                #custom message and the calculated score sent to display on the main page
        init_score = round(fb_score + yt_score,1)
        return render(request,'mainpage.html',{'message':message,'score':init_score})
    
def calcFacebookScore(data):
    global fb_score, score_factor
    
    for i in data["comment"]:                                                       #all the comments are taken one by one for performing sentiment analysis and then the score is calculated accordingly
        facebook_comment = i
            
        #perform_sentiment_analysis
        facebook_sentiment = performSentimentAnalysis(facebook_comment)             #function call to perform sentiment analysis which returns the polarity of the comment and categorise it
            
        if(facebook_sentiment < 0):                                                 #check whether the comment yielded positive or negative scores and calculate the final facebook score accordingly
            #decrease_the_sentiment_score
            fb_score = fb_score - score_factor
        else:
            #increase_the_sentiment_score
            fb_score = fb_score + score_factor
    
    fb_score = round(fb_score,1)
        
def updateScore(request):                                                           #function to calculate and update the score of the brand from facebook and youtube data collected
    global init_score, base_score, fb_score, yt_score, total_score, name, df, result, reason1, reason2
    
    flag = 0
    result = None                                                                   #re-initialisation of variables to initial values before calculating new values for other brands
    reason1 = None
    reason2 = None
    base_score = init_score
    fb_score = base_score
        
    new_data = df[df["Brand"]==name]                                                #simulates the data available on the next day
    sample_data = new_data.sample(frac = 0.995, random_state = 1)
    next_day_data = new_data.drop(sample_data.index)
      
    calcFacebookScore(next_day_data)                                                #function call to calculate the sentiment analysis score on the next day data available for facebook
    calcYoutubeScore()                                                              #function call to calculate the sentiment analysis score on the next day data available for youtube
        
    total_score = round(fb_score + yt_score,1)
    init_score = total_score
    
    if(total_score > base_score):                                                   #set the messages according to positive or negative ratings as per calculations made for facebook
        reason1 = "Positive Comment on Facebook! " 
        result = "Sentiment Score Increased! - "  
        flag = 1
    elif(total_score < base_score):
        reason1 = "Negative Comment on Facebook! " 
        result = "Sentiment Score Decreased! - "  
        flag = 0
    else:
        reason1 = "Comments and Ratings did not change"
        result = "No Rating Change"
        flag = 2
    
    if(yt_score>0):                                                                #set the messages according to positive or negative ratings as per calculations made for youtube                       
        reason2 = "Subcriber Count Increased!"
    elif(yt_score<0):
        reason2 = "Subscriber Count Decreased!"
    else:
        reason2 = "No changes in subscriber count"
    
    sendEmail()                                                                     #function call for sending mail to registered email-ids
            
    return render(request,'mainpage.html',{'result':result,'score':total_score,'reason1':reason1,'reason2':reason2,'flag':flag})
        
def calcYoutubeScore():                                                             #function to calculate the youtube score from the subscriber count of the brand channel
    global subscriber_count, yt_score, name
    
    last_count = subscriber_count
    subscriber_count = 0
    
    urls = {"Amazon":"UC2cZjd8SBxVvZFGC5FEXn2Q","Xbox":"UCjBp_7RuDBUYbd1LegWEJ8g","PlayStation":"UC-2Y8dQb0S6DtpxNgAKoJKA","Google":"UCK8sQmJBp8GCxrOtXWBpyEA","Microsoft":"UCFtEEv80fQVKkD4h1PF-Xqw","Verizon":"UCDF1rHyRH8LcxbHX5_mrZ0w","HomeDepot":"UCfB9yx0y0dUwQ0lpjH8R4gA","Facebook":"UCcr9tciZbuvJrEVAgIXCp8Q","Johnson & Johnson":"UCg0sL-UssDXE2Ohk3Dfpz7g","Nvidia":"UCHuiy8bXnmK5nisYHUd1J5g"}
    social_count_url = 'https://socialcounts.org/youtube-live-subscriber-count/' + urls[name] #store the channel ids of the brands in a dictionary and use them as per requirement to call the required URL

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' #browser_details
    }

    try:
        response = requests.get(social_count_url, headers=headers)                  #establish connection to the URL

        if response.status_code == 200:                                             #if connection is confirmed then we collect the subscriber count from the page
            soup = BeautifulSoup(response.text, 'html.parser')
            subscriber_count_element = soup.find('div', {'class': 'id_odometer__dDC1d mainOdometer'})
            
            if subscriber_count_element:
                subscriber_count = int(subscriber_count_element.text.strip())

    except Exception as e:
        print(f'An error occurred: {e}')
        
    if(subscriber_count>last_count and last_count != 0):                            #perform the sentiment analysis calculation from the subscriber count
        yt_score = 0.1 * ((subscriber_count-last_count)/10)
    elif (subscriber_count<last_count):
        yt_score = -0.1 * ((last_count-subscriber_count)/10)
    else:
        yt_score = 0
    
def registerEmail(request):                                                         #function to register all the email-ids that are interested to be notified about rating changes of a particular brand
    global name
    
    table = mailDataBase()                                                          #create an object of the django model and store the values that the user has given
    table.Name = request.GET['Name']
    table.Email = request.GET['Email']
    table.Brand = name
    
    if mailDataBase.objects.filter(Email=request.GET['Email'], Brand = name):       #check the validuty of the data and then store it in the database
        return render(request,'register.html',{'error':"Email id already used"})
    else:
        table.save()
        
    return render(request,'register.html',{'message':'Email id successfully registered'})

def sendEmail():                                                                    #function to send email notifications to all the registered email-ids
    global result, reason1, reason2, name, total_score
    
    fromaddr = values.get('useraddr')
    pscode = values.get('pass')
    port = values.get('port')
    url = values.get('url')
    listaddr = mailDataBase.objects.all().filter(Brand = name)                      #store all the email-ids in this object who are subscribed to recieve notifications about changes in the particular brand rating

    body = result + "\n" + str(total_score) + "\n" + reason1 +"\n"+ reason2         #string to store the body of the mail

    server = smtplib.SMTP_SSL(url, port)                                            #creates SMTP session 

    server.login(fromaddr, pscode)                                                  #login&authentication       

    for toaddr in listaddr:                                                         #iterate through all the email-ids and then send the details to each one of them one by one
        msg = MIMEMultipart()                                                       #instance of MIMEMultipart 
        msg['From'] = fromaddr                                                      #storing the senders email address 
        msg['To'] = toaddr.Email                                                    #storing the receivers email address 
        msg['Subject'] = "Change in Rating of " + name                              #storing the subject 
        
        msg.attach(MIMEText(body, 'plain'))                                         #attach the body with the msg instance 

        text = msg.as_string()                                                      #converts the Multipart msg into a string 

        server.sendmail(fromaddr, toaddr.Email, text)                               #sending the mail 

    server.quit()                                                                   #terminating the session 