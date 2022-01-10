echo -e "\e[34m\e[1m Please run this as sudo \e[0m"\

# uninstalling pip requirements 

echo -e "\e[105m\e[1m Uninstalling Python Requirements \e[0m"
python3 -m pip uninstall -yr requirements.txt
echo -e "\e[105m\e[1m Python Requirements Uninstalled \e[0m"

# uninstalling git

read -p "Would you like to remove git? (y/N) " user_choice
if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
  echo -e "\e[101m\e[1m git will be deleted \e[0m"
  apt-get -y purge git # purgeing git
else
  echo -e "\e[104m\e[1m git kept intact \e[0m"
fi

# uninstalling python pip

read -p "Would you like to remove python pip? (y/N) " user_choice
if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
  echo -e "\e[101m\e[1m Python and Pip will be deleted \e[0m"
  apt-get -y purge python3
  apt-get -y purge python3-pip # python3 and pip purgeed
  apt-get -y purge python3-setuptools
  add-apt-repository --remove ppa:deadsnakes/ppa
else
  echo -e "\e[104m\e[1m Python installation is kept intact \e[0m"
fi

# deleting pygoat files

read -p "Would you like to remove all pygoat directories and files? (y/N) " user_choice
if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
  echo -e "\e[101m\e[1m All pygoat Files and Directories will be deleted \e[0m"
  curr_folder=$(pwd)
  read -p "Remove $curr_folder? (y/N) " user_choice
  if [ "$user_choice" == 'y' ] || [ "$user_choice" == 'Y' ]; then
    rm -rfv "$curr_folder"
    echo -e "\e[101m\e[1m $curr_folder has been deleted \e[0m"
  else
    echo -e "\e[104m\e[1m $curr_folder kept intact \e[0m"
  fi

else
  echo -e "\e[104m\e[1m pygoat files and directories kept intact \e[0m"
fi