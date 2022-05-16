#!/usr/bin/env python3
import os
import sys
import ctypes
import platform
import colorama
import subprocess
from shutil import rmtree, which


# Platform indepent way to check if user is admin
def is_user_admin():
    """
    Check if the script is being run as root/admin

    Return False if privileges cannot be determined
    """
    if platform.system() == 'Windows':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except WindowsError:
            return False

    else:
        try:
            return os.getuid() == 0
        except os.Error:
            return False


# Uninstall Pip packages in a platform independent way
def uninstall_pip_packages():
    """Remove pip packages installed by pygoat"""
    print(colorama.Back.CYAN + colorama.Style.BRIGHT + "[+] Uninstalling Pip packages!" + colorama.Style.RESET_ALL)

    try:
        # It is important to upgrade pip first to avoid environment errors
        if (platform.system != 'Windows'):
            pip_v = "pip3" if (which('pip3') is not None) else "pip"
            subprocess.run([pip_v,
                            "install",
                            "--upgrade",
                            "pip"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        subprocess.check_call([sys.executable,
                               "-m",
                               "pip",
                               "uninstall",
                               "-yr",
                               "requirements.txt"])
    except subprocess.CalledProcessError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "[!] Failed to uninstall pip packages" + colorama.Style.RESET_ALL)


# Uninstall PIP
def uninstall_pip():
    """Remove Pip"""
    print(colorama.Back.RED + colorama.Style.BRIGHT + "[+] Uninstalling Pip!" + colorama.Style.RESET_ALL)
    try:
        subprocess.check_call([sys.executable,
                               "-m",
                               "pip",
                               "uninstall",
                               "-y",
                               "pip"])
    except subprocess.CalledProcessError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "[!] Failed to uninstall pip" + colorama.Style.RESET_ALL)


# Remove pygoat
def remove_pygoat():
    """Remove pygoat files"""
    cwd = os.getcwd()
    print(colorama.Back.RED + colorama.Style.BRIGHT + f"All files in {cwd} will be deleted!" + colorama.Style.RESET_ALL)

    for item in os.listdir(cwd):
        if platform.system() == 'Windows':
            filename = cwd + '\\' + item
        else:
            filename = cwd + '/' + item

        if(os.path.isfile(filename)):
            try:
                print("[!] Deleted: " + colorama.Fore.RED + colorama.Style.BRIGHT + filename + colorama.Style.RESET_ALL)
                os.remove(filename)
            except os.Error:
                print(colorama.Fore.RED + colorama.Style.BRIGHT + f"[!] Failed To remove: {filename}" + colorama.Style.RESET_ALL)
                pass

        if(os.path.isdir(filename)):
            print("[!] Deleted: " + colorama.Fore.RED + colorama.Style.BRIGHT + filename + colorama.Style.RESET_ALL)
            rmtree(filename, ignore_errors=True)


def main():
    colorama.init()

    # Check if program is being run as admin
    # However, you need admin privileges only if you are not in a venv
    if(not is_user_admin() and sys.prefix == sys.base_prefix):
        print(colorama.Fore.RED + colorama.Style.BRIGHT + "[!] This script must be run as root!" + colorama.Style.RESET_ALL)
        sys.exit(-1)

    # Remove pip packages
    uninstall_pip_packages()

    # Remove pip
    choice = input("Uninstall pip? (y/N) ")
    if (choice.upper() == 'Y' or choice.upper() == 'YES'):
        uninstall_pip()
    else:
        print(colorama.Back.CYAN + colorama.Style.BRIGHT + "[+] Pip has been kept intact" + colorama.Style.RESET_ALL)

    # Remove pygoat files
    choice = input(
        "Would you like to remove all pygoat directories and files? (y/N) "
    )

    if (choice.upper() == 'Y' or choice.upper() == 'YES'):
        remove_pygoat()
        choice2 = input(f"Remove {os.getcwd()}? (y/N) ")
        if (choice2.upper() == 'Y' or choice2.upper() == 'YES'):
            try:
                rmtree(os.getcwd(), ignore_errors=True)
                print(colorama.Back.RED + colorama.Style.BRIGHT + f"[+] {os.getcwd()} has been removed" + colorama.Style.RESET_ALL)
            except FileNotFoundError:
                pass
    else:
        print(colorama.Back.CYAN + colorama.Style.BRIGHT + f"[+] {os.getcwd()} has been kept intact" + colorama.Style.RESET_ALL)

    print(colorama.Back.RED + colorama.Style.BRIGHT + "Uninstallations Done!" + colorama.Style.RESET_ALL)

    # Restore output streams to their original values
    colorama.deinit()


if __name__ == '__main__':
    main()
