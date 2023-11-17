# Sentiment-Analysis-Web-Application

Step 1: Download and Extract the .zip file.

Step 2: Open the folder and then open with your code editor (VS Code etc.).

Step 3: Install all the dependencies from the requirements.txt file by using the command- 
        pip install -r requirements.txt
        
Step 4: Open the values.py file in the SentimentApp folder.

Step 5: Put the sender email address in the 'useraddr' variable. 
        (NOTE:- Use a mail-id that has 2-Step Verification disabled and the Less Secure Apps Access option ENABLED. Otherwise the SMTP app will not be able to login succesfully)
        
Step 6: Put the password of the mail account in the 'pass' variable.

Step 7: Run the django server by using the command in the terminal of the code editor- 
        python manage.py runserver
        
Step 8: Click on the link that is shown in the terminal (http://127.0.0.1:8000/)

Step 9: Use the app as desired.
        (NOTE: Only the following brand names are available- Amazon, Google, Microsoft, Facebook, Nvidia, Xbox, PlayStation, Verizon, HomeDepot. Searching for any other brand name will result in an error message. Names of the brands are CASE-SENSITIVE)
        
Step 10: After searching for the brand name you can register with your mail-id to subscribe to messages when the brand rating changes. One mail-id can register for multiple brands.
         (NOTE:- One mail-id can register for a particular brand only once)
         
Step 11:- The Update Score button will allow for changes in the score for the brand and then notify the subscribers         
          simultaneously about the changes along with reasons for the change in the score.
