# Solutions to all the Lab Exercise 


## A1: Injection 
 * ### Sql Injection
    The user on accesing the lab is given with a login page,which challenges the user to login as admin.
    The user now has to identify some mechanism to login as admin.
    To test for sql injection ,the user can begin with a ```'``` or ``` " ``` based on the error generated he can confirm that it is an sql injection.
    Search for common sql injections payloads in google and try using them to break the functionality of the backend code.
    
    Since the challenge requires yout to login as admin, the ```Username:admin``` . The user now can use a very common sql injection paylaod to bypass the login validation
    ```anything 1' OR '1' ='1```.
    Click login and now you will see that you have successfully logged into admins account.
    
  ##### Login :
   
   ![image](https://user-images.githubusercontent.com/61360833/118371215-27758800-b5c9-11eb-8591-212f448ddc13.png)
  
  ##### On Successful injection
  
   ![image](https://user-images.githubusercontent.com/61360833/118371252-5986ea00-b5c9-11eb-9efb-6beedd558f56.png)


    
    
 * ### Command Injection
    The user on accessing the lab is provided with a feature to perform a name server lookup on the given domain. The user has to give a domain name and the server would         perform a ns lookup and return back to the client. If the user is running the lab, based on the OS he can select Windows or Linux.
    
   The user can cause the server to execute commands ,because of the lack of input validation.
   The user can give a domain say ```google.com && [any cmd]```
   In This case lets give``` google.com && dir```and choose windows.
   This should give you the output for both```ns lookup``` as well as for the ```dir```.
   
   ![image](https://user-images.githubusercontent.com/61360833/118371341-cef2ba80-b5c9-11eb-9860-4f274ed22c8a.png)

    
    
## A2:Broken Authentication

The main aim of this lab is to login as admin, for that you are gonna exploit the ```lack of rate limiting ```feature in the otp verification flow. You can see that the otp is only of 3 digit(for demo purposes) and the application doesnt have any captcha or restricts number of tries for the otp.

Now to send the otp to admins mail you need to figure out the admins mail id. Luckily the admin has left his email id for the developers in the page source. Admins email id ```admin@pygoat.com``` Enter this email in the send otp input box and hit send,you can see that the page says that otp is sent to the email id of the admin. In order to exploit the lack of rate limiting , we can try to Brute-force the 3 digit otp.

##### Steps to Brute force: 

* Open Burpsuite and configure your browser to intercept the web trafic, but dont turn intercept on.
* Send the otp to the admins mail id with the help of send otp feature.
* In the enter the otp box enter a random 3 digit number.
* Before your press login , turn intercept on on Burp suite and then press log in
* Now you can see that the traffic is captured in Burpsuite.
* Now use the send to intruder feature and send this request to the intruder.
* Set the position of the payload to the otp= parameter.
* Go to the payloads session and choose the payload type to number list
* Fill the range to 100 to 999 with step 1.
* Now click attack and you can see that the burp suite tries different combinations of otp and collects it response.
* You can figure out if it has guessed the correct opt by seeing the difference in length of the response for each request.
* The correct otp will have a small response length .
* Using this otp you will be able to login into admins account.


## A3:Senstive Data Exposure
 
  The user has to find a way to trigger server error , so that the server throws some sensitive data in its error .
  Here the developer has forgoten to turn ```debug to false``` which resulted in showing the ```settings.py``` file whihc has some sensitive data.
  Try entering a ```random route``` to trigger the error and go through the settings.py file to find the sensitive data.
  
  ##### Triggering Error:
  
  ![image](https://user-images.githubusercontent.com/61360833/118371395-1da05480-b5ca-11eb-9d70-8a6d7708d039.png)

 ##### Finding the routes:
  
  ![image](https://user-images.githubusercontent.com/61360833/118371562-be8f0f80-b5ca-11eb-937f-b877ebfcc3a1.png)
  
#####  Finding the flag :
    
   ![image](https://user-images.githubusercontent.com/61360833/118371534-a919e580-b5ca-11eb-8f7d-02d0c9322a94.png)



## A4:XML External Entities
  
When the user clicks the button to save his comments, the data is sent to the server in th from of xml post request. This can be seen , by intercepting the request done to the server by that button using BurpSuite.
Sending data to the server in the form of XML is not actually vulnerable, the vulnerability lies in the way the xml is being parsed. An xml parsers which allows the DTD retrival is said to vulnerable to XXE injection if there arent any input validation done on the xml data.

##### Exploiting the XML Parser

* Open Burpsuite and make sure it is ready to capture the web traffic.
* Enter your comments in the input box provided.
* Before hiting the Let the world see button go to burpsuite and turn on intercept.
* Now you should be able to see a post request containing a xml data with your comment inside your the text tag.
* Now we need to introduce a DTD, which tries to fetch files from its server.
* This can be done by using the document tag and defining the Entity.

##### The Payload

                            ``` <?xml version='1.0'?>
                            <!DOCTYPE comm [
                            <!ELEMENT comm (#PCDATA)>
                            <!ENTITY xxe SYSTEM "C:\windows\system32\drivers\etc\hosts">
                            ]>
                            <comm>
                            <text>&xxe;</text>
                            </comm> ```

* Incase if the serve is a linux serve then use ``` SYSTEM "file:///etc/passwd" ``` instead.
* Forward the request and turn of intercept.
* Go to the see comments option and click view comments this should show you the requested files in your payload if the vulnerability exists.


## A5:Broken Access Control

On accessing the lab the user is provided with a simple login in page which requires a username and password.
The credentials for the user Jack is ```jack:jacktheripper.```
Use the above info to log in.
The main aim of this lab is to login with admin privileges to get the secret key.

##### Exploiting the Broken Access

Every time a valid user logs in,the user session is set with a cookie called ``` admin```
When you notice the cookie value when logged in as jack it is set to ```0```
Use BurpSuite to intercept the request change the value of the admin cookie from ```0 to 1```
This should log you in as a admin user and display the ```secret key```

###### The Scenario

![image](https://user-images.githubusercontent.com/61360833/118371737-9358f000-b5cb-11eb-900c-1b955f4d0078.png)


###### The cookies

![image](https://user-images.githubusercontent.com/61360833/118371826-f6e31d80-b5cb-11eb-808b-a76cc29d2947.png)


###### Changing the cookie value

![image](https://user-images.githubusercontent.com/61360833/118371851-0ebaa180-b5cc-11eb-9499-e1592cf30fc7.png)


###### Reloading the page

![image](https://user-images.githubusercontent.com/61360833/118371880-28f47f80-b5cc-11eb-99e8-5cbf34400be0.png)




## A6:Security Misconfiguration
 
The user is provided with a button which say secret key on clicking the button it provides us with some information.
With this information we can conclude that we need to have a header called ```X-Host:``` and its value should be ``` admin.localhost:8000```.
In order to add this header we can capture the requet of the button in ```BurpSuite``` and add the header to the request and forward it .
This should give you the secret key.
 
## A7:Cross Site Scripting

* Instead of giving a search term try giving a html tag, ``` <h4 >Hello </h4>.```
* Now you can see that the word Hello has been parsed as a Heading in the page.
* This shows that the page is able to render the user given html tags.
* In order to get an xss , the user needs to execute javascript code in the browser.
* This can be acheived by using a script tag and malicious javascript code.
* For now let's just use a basic javascript code to alert a text to prove that xss is possible .
                   ```<script >alert(“xss”) </script >```
* Now when a search query is performed with the above payload you can see that the browser is able to render the script tag and execute the javascript , thus alerting “xss” with a pop up.

## A8:Insecure Deserialization

This Lab consists of a Page that has some content only available to for the admin to see, How can we access that page as admin? How is our role defined?

If we check the cookie we see that it is base64 encoded, on decoding we realise it is pickle serialised and we can see some attributes, can you change the attributes to make the page readable?

Try to flip the bit of the admin from ```...admin\x94K\x00... to ...admin\x94K\x00...```

## A9:Using Components with Know Vulnerability
 
The user on accessing the lab is provided with a feature to convert yaml files into json objects. The user needs to choose an yaml file and click upload to get the json data. There is also a get version feature which tells the user the version of the library the app uses. 

##### Exploiting the vulnerability.

* The app uses```pyyaml 5.1 ``` Which is vulnerable to code execution.
* You can google the library with the version to get the poc and vulnerability details
* Create An yaml file with this payload:
                    ``` !!python/object/apply:subprocess.Popen ```
                     ```- ls ```

* On Uploading this file the user should be able to see the output of the command executed.

## A10:Insufficient Logging & Monitoring
   
The user on accessing the lab is given with a login page which says the log have been leaked. The user needs to find the leak and try to gain the credentials that have been leaked in the logs.

##### Finding the Log

* The log has been exposed in ```/debug route```
* This can be found out with subdomain brute-forcing or just by guess
* On seeing the Log try to get the required login details as there is a leak and the logging is improperly handled.
* On looking at the log we can see a get request ot the server that has a username and password to it 
 ``` INFO "GET /a10_lab?username=Hacker&password=Hacker HTTP/1.1" 301 0 ```
* Now use the credentials to log in .



