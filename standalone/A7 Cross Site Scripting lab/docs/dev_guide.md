# Developer's Guide

PyGoat is an intentionally vulnerable web application written using the Python-Django Framework. We welcome Developers to contribute to the project. 

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

* `lab_code` - This contains `test.py` which can be used to test a piece of code before implementing it in the app.
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

## Understanding how the templates work

All templates are located in `pygoat/introduction/templates` and main CSS used for the project is located in `pygoat/introduction/static/introduction/style4.css`

There are 3 folders in templates 
- introduction - Contains `base.html` and `home.html`
- Lab - contains 12 folders. All folders except AUTH contain templates that will be displayed for the 10 labs
- registration - contains templates for registration, login and logout

`base.html` - Contains Base layout for the entire website. This is extended by most other templates and the base layout, CSS and formatting will be dictated by this template. CSS that is included for this template is automatically applied to the all other templates that extend this one.

The following image shows a few parts that `base.html` defines in the website.

![front_1](https://user-images.githubusercontent.com/70275323/154678332-ada4935f-a970-4ca3-a8be-f4babda8cb3b.png)

The different lab folders inside `Lab` contain templates related to labs

![image](https://user-images.githubusercontent.com/70275323/154682348-d51c521f-e885-4b81-958d-38c2f73ba9be.png)

## Understanding how `views.py` works (Working of Backend)

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

Lets take the snippet

```python3
output = "Something went wrong"
return render(request,'Lab/CMD/cmd_lab.html',{"output":output})
```

And lets take the snippet from `'Lab/CMD/cmd_lab.html'` that will display the `output` variable

```html
<div class="container">
    {% if output %}
    <h6><b>Output</b></h6><br>
    <b>
        <pre>{{output}}</pre>
    </b>
    {% endif %}
</div>
```

Lets see what these two snippets acheive

The python3 code from views.py renders this template and a variable 'output' with value of output ( which in this case is "Something went wrong") is made available in the HTML template

The `output` variable can be accessed from the HTML template by using tags provided in the the [Django Template Language](https://docs.djangoproject.com/en/4.0/ref/templates/language/) (the link contains vital info. It's recommended to check it out)

What this achieves in this case, is - 
- Checking if output variable exists
- If it exists, displays value of output variable in preformatted way

## Understanding request authentication

To ensure every page is rendered to an authenticated user, all functions in `views.py` begin with an authentication check that looks something like

```python3
if request.user.is_authenticated:
        # Logic of the program here!
    else:
        return redirect('login')
        # Rediects to login page if a request is not authenticated
```

To Add a new function to views.py, please make sure to include a check for authentication.

## Understanding routing with `urls.py`

There are 2 `urls.py` files in the project. 

These are located in `pygoat/pygoat` and `pygoat/introduction`

These files are responsibele for routing the website urls to the correct template and backend function. 

Let's take an example from a code snippet from `pygoat/introduction/urls.py`

```python3
    path('', views.home, name='homepage'),
    path('xss', views.xss,name="xss"),
    path('xssL',views.xss_lab,name='xss_lab'),
```

What this code does - 

- When user navigates to 127.0.0.1/ in web browser, function views.home is executed
- When user navigates to 127.0.0.1/xss in web browser, function views.xss is executed
- When user navigates to 127.0.0.1/xssL in web browser, function views.xss_lab is executed

Let's take an example from a code snippet from `pygoat/pygoat/urls.py`

```python3
    path('', views.home, name='homepage'),
    path('xss', views.xss,name="xss"),
    path('xssL',views.xss_lab,name='xss_lab'),
```

There are a few lines in urls.py that do not look like these. They're for special purposes like implementing django-allAuth and other features

If theres any doubt or issue feel free to raise an Issue, or correct an existing issue and send PR. Feel free to join the [PyGoat Devs channel](https://t.me/+WpqLBwviT00xZDI1) on telegram

Happy Coding!
