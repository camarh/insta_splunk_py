#!/usr/bin/env python3

import os  # At this stage, this library is enough in order not to consume resources unnecessarily

# Getting sure of having sudo rights
if os.geteuid() == 0:

    # Importing all necessary modules/libraries
    import requests
    from bs4 import BeautifulSoup
    from functions_collection import get_pkg, get_prog_path
    import wget
    from getpass import getpass
    import shutil
    import subprocess
    import time
    import re

    # The website where we want to scrape the pages
    es_url = "https://www.splunk.com/en_us/download/splunk-enterprise.html"

    # let's make our soup
    soup = BeautifulSoup(requests.get(es_url).content, 'html.parser')
    result = soup.find("a", {"data-link": re.compile(r"^(.+?)\.rpm$")})
    package_url = (result["data-link"])

    # Spotting the interesting  package
    package_pattern = re.compile(r"splunk-.+rpm$")
    search_package_file = re.search(package_pattern, package_url)
    package_file = search_package_file.group(0)

    # Define found package version as last version
    pattern = re.compile(r"splunk-[\d.]+")
    search = re.search(pattern, package_url)
    latest_package_version = search.group(0)

    # Let's check if any Splunk flavour is already installed
    cmd_check_splunk = "rpm -q splunk"
    check_splunk = subprocess.Popen(cmd_check_splunk, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    check_splunk.wait()

    # Let's initialize some variable for further purpose
    choice = ""

    # When found, lets define as current
    if check_splunk.returncode == 0:
        check_splunk_output = check_splunk.stdout.read()
        check_splunk_search = re.search(pattern, check_splunk_output)
        current_package_version = check_splunk_search.group(0)

        # Nothing to do when latest already installed
        if latest_package_version == current_package_version:
            exit(f"\nNothing to do - You have Splunk latest version ({current_package_version})\n")

        # Otherwise let the user have the possibility to decline the upgrade
        else:
            choice = input("\nIt looks like there is an old version of Splunk installed on the system.\n"
                           f"\nCurrent version: {current_package_version}"
                           f"\nLatest version: {latest_package_version}"
                           "\n\nWould you like to upgrade it ? (y or n)\n")
            choice_pattern = re.compile(r"^[yn]$", re.I)
            choice_search = re.search(choice_pattern, choice)

            # Check the input filled by the user
            while not choice_search:
                choice = input("\nChoice not included. Would you like to upgrade it ? (y or n): \n")
                choice_pattern = re.compile(r"^[yn]$", re.I)
                choice_search = re.search(choice_pattern, choice)

            choice_pattern_y = re.compile(r"y", re.I)
            choice_search_y = re.search(choice_pattern_y, choice)

            # Process the Upgrade only when the user states it expressly
            if choice_search_y:
                print("\n\t... Splunk Enterprise upgrade in progress ...\n")

                # Download the package
                wget.download(package_url)

                # Process the Upgrade
                splunk_upgrade = subprocess.Popen(['rpm', '-U', get_pkg(), '--quiet'])
                splunk_upgrade.wait()

                # Start Splunk and accept the license
                start_splunk_u = subprocess.Popen([get_prog_path(), "start", "--accept-license", "--answer-yes"])
                start_splunk_u.wait()

            # Exit when upgrade refused
            else:
                exit()

    # When any, process brand new install
    else:

        # Ask to create the admin password to login platform
        admin_pass = getpass("\nTo login the Splunk platform, provide admin password :")
        print("\n\t... Splunk Enterprise install in progress ...\n")

        # Download the latest version of splunk
        wget.download(package_url)

        # Handle the ownership of the newly downloaded package
        shutil.chown(get_pkg(), "splunkuser", "splunkuser")

        # Install package and start the program
        splunk_install = subprocess.Popen(['rpm', '-i', get_pkg(), '--quiet'])
        splunk_install.wait()

        # Start the program, accept the license and provide the entered passwd as a parameter
        start_splunk = subprocess.Popen([get_prog_path(), "start", "--accept-license", "--answer-yes", "--no-prompt", "--seed-passwd", admin_pass])
        start_splunk.wait()

    # Then stop the programme in order to handle miscellaneous administrative setup
    splunk_stop = subprocess.Popen([get_prog_path(), "stop"])
    splunk_stop.wait()

    # [upgrade case] in order to guard against possible errors relating to pre-existing scripts for boot-start, lets found out if Splunk demon script exist
    cmd_boot_start = "find /etc/systemd/system -maxdepth 1 -name Splunkd.service"
    splunk_status = subprocess.Popen(cmd_boot_start, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    splunk_status.wait()
    splunk_status_output = splunk_status.stdout.read()

    # And disable the boot-start when the case
    if splunk_status_output:
        splunk_disable_boot = subprocess.Popen([get_prog_path(), "disable", "boot-start"])
        splunk_disable_boot.wait()

    # Now let systemd handle Splunk boot-start with user/group splunk
    enable_boot_start_u = subprocess.Popen([get_prog_path(), "enable", "boot-start", "-user", "splunk", "-group", "splunk", "-systemd-managed", "1"])
    enable_boot_start_u.wait()

    # Consider right/ownership for user splunk if we want to avoid ourselves some disaster when starting up the program
    os.system('chown -R splunk:splunk /opt/splunk')
    restart_splunk = subprocess.Popen([get_prog_path(), "start"])
    restart_splunk.wait()
    time.sleep(5)

    # Indicate the trash vortex for the anymore useful package
    os.system(f'rm {get_pkg()}')

    # Open/allow necessary ports/services
    os.system('firewall-cmd  --zone=public --permanent --add-service=http')
    os.system('firewall-cmd  --zone=public --permanent --add-service=https')
    os.system('firewall-cmd  --zone=public --permanent --add-port=8000/tcp')

    # Anticipate logs from various network devices by forwarding their logs to a port other than 514 which is intended for the local device
    os.system('firewall-cmd --permanent --add-forward-port=port=514:proto=udp:toport=5514')
    os.system('firewall-cmd --add-masquerade')
    os.system('firewall-cmd --reload')
    print("\n\n")

    # Print out the status to confirm that Splunk is up and running
    os.system(f'{get_prog_path()} status')

    # Notify user end of task
    if choice == "y" or choice == "Y":
        print('\n\nSplunk Enterprise has been upgraded\n\n')
    else:
        exit('\n\nSplunk Enterprise has been installed\n\n')

# Exit if no privileges and notify
else:
    exit("\nPrivileges needed to run this script.\n")
