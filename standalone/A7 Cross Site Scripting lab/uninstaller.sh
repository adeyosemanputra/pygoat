#!/bin/bash


# Color Schemas
PURPLE='\033[01;35m'
RED='\033[01;31m'
NONE='\033[00m'
HIGHLIGHT_PURPLE='\e[105m\e[1m'
HIGHLIGHT_PINK='\e[101m\e[1m'
HIGHLIGHT_CYAN='\e[104m\e[1m'
HIGHLIGHT_END='\e[0m'


# Check if the script is being run as root!
init(){
  if [[ $EUID -ne 0 ]]; then
    echo "$RED[!] This script must be run as root!" 1>&2
    exit -1
  fi  
}


# Uninstall pip packages
uninstall_pip_pkgs(){
  echo -e "$HIGHLIGHT Uninstalling Python Requirements $HIGHLIGHT_END"
  python3 -m pip uninstall -yr requirements.txt
  echo -e "$HIGHLIGHT Python Requirements Uninstalled $HIGHLIGHT_END" 
}


# uninstalling git
uninstall_git(){
  read -p "Would you like to remove git? (y/N) " user_choice
  if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
    echo -e "$HIGHLIGHT_PINK git will be deleted $HIGHLIGHT_END"
    apt-get -y purge git # purgeing git
  else
    echo -e "$HIGHLIGHT_CYAN git kept intact $HIGHLIGHT_END"
  fi
}


# uninstalling python pip
uninstall_python_pip(){
  read -p "Would you like to remove python pip? (y/N) " user_choice
  if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
    echo -e "$HIGHLIGHT_PINK Python and Pip will be deleted $HIGHLIGHT_END"
    apt-get -y purge python3
    apt-get -y purge python3-pip # python3 and pip purgeed
    apt-get -y purge python3-setuptools
  else
    echo -e "$HIGHLIGHT_CYAN Python installation is kept intact $HIGHLIGHT_END"
  fi
}


# deleting pygoat files
uninstall_pygoat(){
  read -p "Would you like to remove all pygoat directories and files? (y/N) " user_choice
  if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
    echo -e "$HIGHLIGHT_PINK All pygoat Files and Directories will be deleted $HIGHLIGHT_END"
    curr_folder=$(pwd)
    read -p "Remove $curr_folder? (y/N) " user_choice
    if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
      rm -rfv "$curr_folder"
      echo -e "$HIGHLIGHT_PINK $curr_folder has been deleted $HIGHLIGHT_END"
    else
      echo -e "$HIGHLIGHT_CYAN $curr_folder kept intact $HIGHLIGHT_END"
    fi

  else
    echo -e "$HIGHLIGHT_CYAN pygoat files and directories kept intact $HIGHLIGHT_END"
  fi
}


main(){
  init
  uninstall_pip_pkgs
  uninstall_git
  uninstall_python_pip
  uninstall_pygoat
}

main
