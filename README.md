# PyGoat
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-9-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

PyGoat is an intentionally vulnerable web application built with Django. It's designed to help security professionals and developers learn about common web vulnerabilities based on the OWASP Top Ten. Our roadmap focuses on implementing real-world vulnerability scenarios for educational purposes.

Table of Contents
=================

* [pygoat](#pygoat)
   * [Installation](#installation)
      * [From Sources](#from-sources)
      * [From Container Image](#docker-container)
      * [Installation Video](#installation-video)
   * [Uninstallation](#uninstallation)
   * [Solutions](/Solutions/solution.md)
   * [For Developers](/docs/dev_guide.md)

## Installation

### Build from Source Code

#### Windows Notes on PowerShell
 
- PyGoat is tested primarily on Linux/macOS. Windows users are recommended to use:
  - **Docker Desktop** (preferred), or
  - **WSL2 (Ubuntu)** for smoother setup.
- On some Windows environments, the `python3` command may not be available by default.
  - If `python3` is not recognized, try using `python` instead (ensure it points to Python 3.x).
- Ensure Python version is **3.10 or 3.11** for best compatibility.
- Some labs rely on Unix-style commands and may behave differently on native Windows shells.

Follow these steps to set up the project on your local machine:

1. Clone the GitHub repository

    ```shell
    git clone https://github.com/adeyosemanputra/pygoat.git
    
    # Clone on specific branch
    git clone -b <branch_name> https://github.com/adeyosemanputra/pygoat.git
    ```
2. Setup Python dependencies

    You can use several methods to set up the required dependencies.

    1. Shell Installer
        ```shell
        bash ./installer.sh
        ```
    2. Python Package Manager with `requirements.txt`
        ```shell
        pip install -r ./requirements.txt
        ```
    3. Python Package Manager with `setup.py`
        ```shell
        pip3 install .
        ```
3. Run migrations and start the server
    ```shell
    python3 manage.py migrate
    python3 manage.py runserver
    ```
    The server will be available at <http://127.0.0.1:8000>

### From Container Image

#### Directly on Container Engine (Docker or Podman)

1. Install [Docker](https://docs.docker.com/engine/install/) or [Podman](https://podman.io/docs/installation) on your machine. With Podman, you need change your command from `docker` with `podman`
2. Pull the container image
    ```shell
    docker pull docker.io/pygoat/pygoat:latest
    ```
3. Run the container image on your machine
    ```shell
    docker run --rm -p 8000:8000 \
    docker.io/pygoat/pygoat:latest
    ```
4. The server will be available at <http://127.0.0.1:8000> 

#### Run with Docker Compose (easier and more managable) 
1. Install [Docker](https://docs.docker.com/compose/install/)
2. Run the container on your machine
    ```shell
    # Foreground
    docker-compose up

    # Background
    docker-compose up -d
    ```
3. The server will be available at <http://127.0.0.1:8000> 

## Populate Challenge Data

PyGoat stores challenge definitions in `challenge/challenge.json`.
To populate the `Challenge` table in the database from this file, use the
built-in Django management command:

### Using Docker Compose

```bash
docker compose exec web python manage.py populate_challenges


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
