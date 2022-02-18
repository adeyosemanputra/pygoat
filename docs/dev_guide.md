# Developer's Guide

PyGoat is an intentionally vulnerable web application written using the Python-Django Framework.

## Project Structure

![image](https://user-images.githubusercontent.com/70275323/154626667-be93c711-47ca-45db-be8d-4ce62e7fbfbb.png)

`installer.sh` is the installer bash file. It downloads and installs requirements that are necessary for the project.

`uninstaller.sh` is the uninstaller bash file. It will uninstall the project and and requirements that were installed along with it.

`requirements.txt` is the python3  requirements file.

### Django Folder Structure

The `pygoat` folder is the main folder that contains the Django Project. The project has 2 apps - `introduction` and `pygoat`, and both of them have their own folders. Apart from them there's another folder - `Solutions` which contains solutions to all scenarios. 

* The Inroduction folder contains the main workings of the project and consists of HTML templates, CSS files, and Python code that forms the backend of the application
* The pygoat folder is the Django default folder and it contains all important settings/configurations essential to running the apps. 
* The Solutions folder has `solutions.md` and has solutions to all scenarios presented in application

### Contents of the `introdution` folder

The `introduction` folder has a few more folders and files

![image](https://user-images.githubusercontent.com/70275323/154636031-c5bd01de-82ac-4fff-836a-b44e01c0e415.png)

#### Folders

* `lab_code` - This contains test.py which can be used to test a piece of code before implementing it in the app.
* `static` - Contains CSS files that give the pages styling
* `templates` - Contains all HTML templates used by the we app. This has 3 folders
* * `introduction` - Contains the base html code that is used throughout the app. 
* * `lab` - contains HTML code for the 10 Scenarios that can be solved
* * `registration` - Contains HTML code for registration and login pages
* 
#### Files

* `models.py` - Has different models eg - FAANG, login, etc 
* `urls.py` - List of URLS and how to route them
* `views.py` - Main Backend Code that runs the Web App

## Adding/Changing backend working

Navigate to `views.py` located in the introduction folder of the Django Project. This file will be your main concern when it comes to backend development

How views.py works -

The python file is divided into sections depending on which purpose they're being used for.

For example lets take the function `cmd_lab`

The function is as follows

```python3
def cmd_lab(request):
    if request.user.is_authenticated: # checks if the user is authenticated
        if(request.method=="POST"):
            domain=request.POST.get('domain') # this is the input of the user
            domain=domain.replace("https://www.",'')
            os=request.POST.get('os')
            print(os)
            if(os=='win'):
                command="nslookup {}".format(domain)
            else:
                command = "dig {}".format(domain)
            
            try:
                # output=subprocess.check_output(command,shell=True,encoding="UTF-8")
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                data = stdout.decode('utf-8')
                stderr = stderr.decode('utf-8')
                # res = json.loads(data)
                # print("Stdout\n" + data)
                output = data + stderr
                print(data + stderr)
            except:
                output = "Something went wrong"
                return render(request,'Lab/CMD/cmd_lab.html',{"output":output}) # this renders the template - cmd_lab.html
            print(output)
            return render(request,'Lab/CMD/cmd_lab.html',{"output":output}) # this renders the template - cmd_lab.html
        else:
            return render(request, 'Lab/CMD/cmd_lab.html') # this renders the template - cmd_lab.html
    else:
        return redirect('login') # if user wasn't logged in the first if statement of the function then redirect to login
```

The first statement checks if the user is authenticated. If not, it directs to the login page.

The syntax to take input from user through a web page using POST request is 

```python3
value=request.POST.get('value_name')
```
This syntax is used twice in the above function

```python3
domain=request.POST.get('domain')
os=request.POST.get('os')
```

The function usually ends with rendering a particular template along with giving it a few values. Lets see how this works.




