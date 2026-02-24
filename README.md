# PyGoat
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-9-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

intentionally vuln web Application Security in django.
our roadmap build intentionally vuln web Application in django. The Vulnerability can based on OWASP top ten
<br>

Table of Contents
=================

* [pygoat](#pygoat)
   * [Installation](#installation)
      * [From Sources](#from-sources)
      * [Docker Container](#docker-container)
      * [Installation Video](#installation-video)
   * [Uninstallation](#uninstallation)
   * [Solutions](/Solutions/solution.md)
   * [For Developers](/docs/dev_guide.md)

## Installation

### From Sources

To setup the project on your local machine:
<br>

First, Clone the repository using GitHub website or git in Terminal
```
  git clone https://github.com/adeyosemanputra/pygoat.git
  ### To Download a specific branch
  git clone -b <branch_name> https://github.com/adeyosemanputra/pygoat.git
```
Then, Download Traefik on your local machine (if not using docker compose) from [traefik releases](https://github.com/traefik/traefik/releases).
Open a separate terminal, navigate to the PyGoat main directory, and run:
```
tar -zxvf traefik_<traefik_version>_linux_<arch>.tar.gz
sudo ./traefik
```
If you face any issue while installation, kindly refer to the [documentation](https://doc.traefik.io/traefik/getting-started/install-traefik/)
#### Method 1

1. Install all app and python requirements using installer file - `bash installer.sh`
2. Apply the migrations `python3 manage.py migrate`.<br>
3. Finally, run the development server `python3 manage.py runserver`.<br>
4. The project will be available at <http://127.0.0.1:8000> 

#### Method 2

1. Install python3 requirements `pip install -r requirements.txt`.<br> 
2. Apply the migrations `python3 manage.py migrate`.<br>
3. Finally, run the development server `python3 manage.py runserver`.<br>
4. The project will be available at <http://127.0.0.1:8000> 

#### Method 3

1. Install all app and python requirements using `setup.py` file - `pip3 install .`
2. Apply the migrations `python3 manage.py migrate`.<br>
3. Finally, run the development server `python3 manage.py runserver`.<br>
4. The project will be available at <http://127.0.0.1:8000> 

### Docker Container
1. Install [Docker](https://www.docker.com)
2. Run `docker pull pygoat/pygoat` or `docker pull pygoat/pygoat:latest`
3. Run `docker run --rm -p 8000:8000 pygoat/pygoat:latest`
4. Browse to <http://127.0.0.1:8000> 
5. Remove existing image using `docker image rm pygoat/pygoat` and pull again incase of any error

### From Docker-Compose 
1. Install [Docker](https://www.docker.com)
2. Run `docker-compose up` or `docker-compose up -d`

### Build Docker Image and Run
1. Clone the repository  &ensp; `git clone https://github.com/adeyosemanputra/pygoat.git` 
2. Build the docker image from Dockerfile using &ensp; `docker build -f Dockerfile -t pygoat .`
3. Run the docker image &ensp;`docker run --rm -p 8000:8000 pygoat:latest`
4. Browse to <http://127.0.0.1:8000> or <http://0.0.0.0:8000> 

### Installation video 

1. From Source using `installer.sh`
 - [Installing PyGoat from Source](https://www.youtube.com/watch?v=7bYBJXG3FRQ)
2. Without using `installer.sh`
 - [![](http://img.youtube.com/vi/rfzQiMeiwso/0.jpg)](http://www.youtube.com/watch?v=rfzQiMeiwso "Installation Pygoat")
3. Install with Mac M1 (using Virtualenv)
 - [![](http://img.youtube.com/vi/rfzQiMeiwso/0.jpg)](https://youtu.be/a5UV7mUw580 "Install with Mac M1 - using Virtualenv")

## Adding new labs

This section guides you through creating and integrating new vulnerability labs into PyGoat.

### Step 1: Create Lab Directory Structure

1. Navigate to the `dockerized_labs` folder:
```bash
cd dockerized_labs
```

2. Create a new directory for your lab (use descriptive naming):
```bash
mkdir your_lab_name
cd your_lab_name
```

### Step 2: Create Required Files

Create the standard application structure with a Dockerfile, docker-compose.yml, requirements.txt (if using Python), a main application entry point (e.g., app.py, main.py, or equivalent), vulnerable endpoints or components relevant to the lab, and a README.md documenting the lab. The application does not necessarily have to be a Flask application—it can be any Python project (preferred, since this is part of Pygoat), or even another language if appropriate. Refer to existing labs in the dockerized_labs folder for examples and structure conventions.

**Important**: Add a `/health` endpoint in your app.py for container health check.

### Step 3: Register Lab in labs.json

1. Open [labs.json](labs.json) in the project root directory

2. Add a new entry to the `"labs"` array:
```json
{
  "name": "your_lab_name",
  "build_location": "dockerized_labs/your_lab_name",
  "port": <PORT_NUMBER>
}
```

**Important**: 
- Check [labs.json](labs.json) for all currently used ports before selecting a new one.
- Use the same port number in `Dockerfile`, `docker-compose.yml`, `app.py`, and `labs.json`


### Step 4: Test Your Lab

1. Navigate back to the project root:
```bash
cd /path/to/pygoat
```

2. Build and test your lab individually:
```bash
cd dockerized_labs/your_lab_name
docker compose up
```

3. Access your lab at `http://localhost:<PORT_NUMBER>`

4. Verify the vulnerability works as expected

### Step 5: Integrate with PyGoat

1. Stop the individual lab container

2. Add your lab details in [base.html](introduction/templates/introduction/base.html)

2. From the PyGoat root directory, rebuild the entire application:
```bash
docker compose down
docker compose up --build
```

## Uninstallation

### On Debian/Ubuntu Based Systems
- On Debian/Ubuntu based systems, you can use the `uninstaller.sh` script to uninstall `pygoat` along with all it's dependencies.
- To uninstall `pygoat`, simply run:
```bash
$ bash ./uninstaller.sh
```

### On Other Systems
- On other systems, you can use the `uninstaller.py` script to uninstall `pygoat` along with all it's dependencies
- To uninstall `pygoat`, simply run:
```bash
$ python3 uninstaller.py
```

## Solutions 
<a href="/Solutions/solution.md">Solutions to all challenges</a>

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/pwned-17"><img src="https://avatars.githubusercontent.com/u/61360833?v=4?s=100" width="100px;" alt=""/><br /><sub><b>pwned-17</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=pwned-17" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/prince-7"><img src="https://avatars.githubusercontent.com/u/53997924?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Aman Singh</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=prince-7" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/adeyosemanputra"><img src="https://avatars.githubusercontent.com/u/24958168?v=4?s=100" width="100px;" alt=""/><br /><sub><b>adeyosemanputra</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=adeyosemanputra" title="Code">💻</a> <a href="https://github.com/adeyosemanputra/pygoat/commits?author=adeyosemanputra" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/gaurav618618"><img src="https://avatars.githubusercontent.com/u/29380890?v=4?s=100" width="100px;" alt=""/><br /><sub><b>gaurav618618</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=gaurav618618" title="Code">💻</a> <a href="https://github.com/adeyosemanputra/pygoat/commits?author=gaurav618618" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/kUSHAL0601"><img src="https://avatars.githubusercontent.com/u/29600964?v=4?s=100" width="100px;" alt=""/><br /><sub><b>MajAK</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=kUSHAL0601" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/JustinDPerkins"><img src="https://avatars.githubusercontent.com/u/60413733?v=4?s=100" width="100px;" alt=""/><br /><sub><b>JustinPerkins</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=JustinDPerkins" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Hkakashi"><img src="https://avatars.githubusercontent.com/u/43193113?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Liu Peng</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=Hkakashi" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/RupakBiswas-2304"><img src="https://avatars.githubusercontent.com/u/75058161?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Metaphor</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=RupakBiswas-2304" title="Code">💻</a></td>
    <td align="center"><a href="https://whokilleddb.github.io"><img src="https://avatars.githubusercontent.com/u/56482137?v=4?s=100" width="100px;" alt=""/><br /><sub><b>whokilleddb</b></sub></a><br /><a href="https://github.com/adeyosemanputra/pygoat/commits?author=whokilleddb" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
