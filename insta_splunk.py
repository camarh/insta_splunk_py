#!/usr/bin/env python3

# Required packages
import os
import requests
from bs4 import BeautifulSoup
import glob
import wget
from getpass import getpass
import subprocess
import time
import re

# ---------------------------------------------------------------------------------------------

# Splunk Enterprise main download page
splunk_releases = "https://www.splunk.com/en_us/download/splunk-enterprise.html"


def get_pkg_path():
    """
    This generic function will help to perform further computation
    in this program in order to handle Splunk application
    @return: A string that contains the path of Splunk application
    """
    path = "/opt/splunk/bin/splunk"
    return path


def get_pkg():
    """
    This generic function will help to perform further computation
    in this program in order to handle Splunk package
    @return: A string that contains the whole name of Splunk package
    """
    for pkg in glob.glob("splunk*"):
        return pkg


def harvest_splunk(url):
    """
    This function will help to extract the download link of the latest Linux RPM Splunk release
    @param url: Splunk main download page where the download link of the interesting package is located
    @return: Download link, name ond version  of the interesting package,
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find("a", {"data-link": re.compile(r"^(.+?)\.rpm$")})
    package_url = (content["data-link"])
    package_name = (re.search(re.compile(r"splunk-.+rpm$"), package_url)).group(0)
    package_version = (re.search(re.compile(r"splunk-[\d.]+"), package_url)).group(0)
    return package_url, package_name, package_version


def check_splunk():
    """
    This function check if Splunk is installed in the current environment
    @return: The exit code of the command and when applicable, the version of the Splunk detected
    """
    process_check = subprocess.Popen("rpm -q splunk", shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    process_check.wait()
    output = process_check.stdout.read()
    fetch_splunk_v = ""
    exit_code = process_check.returncode
    if not exit_code:
        fetch_splunk_v = re.search(re.compile(r"splunk-[\d.]+"), output).group(0)
    return output, fetch_splunk_v


def install_new(link):
    """
    This function handle the installing of Splunk (download, install and start)
    @param link: Download link of the interesting package (Linux RPM release)
    @return: Default (NoneType)
    """
    admin_passwd = getpass("\nTo login the Splunk platform, provide Admin password :")
    print("\n\t... Splunk Enterprise install in progress ...\n")
    wget.download(link)
    process_install = subprocess.Popen(['rpm', '-i', get_pkg(), '--quiet'])
    process_install.wait()
    process_start = subprocess.Popen([get_pkg_path(), "start", "--accept-license", "--answer-yes", "--no-prompt", "--seed-passwd", admin_passwd])
    process_start.wait()


def install_upgrade(link):
    """
    This function handle the upgrading of previous/outdated Splunk version
    @param link: Download link of the interesting package (Linux RPM release)
    @return: Default (NoneType)
    """
    print("\n\t... Splunk Enterprise upgrade in progress ...\n")
    wget.download(link)
    process_upgrade = subprocess.Popen(['rpm', '-U', get_pkg(), '--quiet'])
    process_upgrade.wait()
    start_upgrade = subprocess.Popen([get_pkg_path(), "start", "--accept-license", "--answer-yes"])
    start_upgrade.wait()


def pre_reading_user_opt(current, latest):
    """
    This function proposes and manages the option to upgrade when applicable
    @param current: Splunk version  detected in the current environment
    @param latest: Latest Splunk release that was harvested with harvest_splunk(url)
    @return: string that contains the user option - e.g => [Y, y] -> GO
                                                           [N,n] -> NO GO
    """
    primary_user_opt = input("\nIt looks like there is an old version of Splunk installed on the system.\n"
                             f"\n Current version: {current}"
                             f"\n Latest version: {latest}"
                             "\n\nWould you like to upgrade it ? (y or n)\n")
    while primary_user_opt not in ('Y', 'y', "N", "n"):
        secondary_user_opt = input("\nChoice not included. Would you like to upgrade it ? (y or n): \n")
        primary_user_opt = secondary_user_opt
    return primary_user_opt


def perform_initial_tasks():
    """
    This function handle miscellaneous administrative setup such as assigning to systemd the control of
    Splunk start at boot time with splunkd, considering right/ownership for splunk stuff to splunk user.
    It also indicates the trash vortex for the anymore useful package
    @return: Default (NoneType)
    """
    splunk_stop = subprocess.Popen([get_pkg_path(), "stop"])
    splunk_stop.wait()

    start_at_boot = "find /etc/systemd/system -maxdepth 1 -name Splunkd.service"
    splunkd_service = subprocess.Popen(start_at_boot, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    splunkd_service.wait()
    splunkd_service_output = splunkd_service.stdout.read()

    if splunkd_service_output:
        disable_splunk_boot_start = subprocess.Popen([get_pkg_path(), "disable", "boot-start"])
        disable_splunk_boot_start.wait()

    enable_splunk_boot_start = subprocess.Popen([get_pkg_path(), "enable", "boot-start", "-user", "splunk", "-group", "splunk", "-systemd-managed", "1"])
    enable_splunk_boot_start.wait()

    os.system('chown -R splunk:splunk /opt/splunk')
    restart_splunk = subprocess.Popen([get_pkg_path(), "start"])
    restart_splunk.wait()
    time.sleep(5)

    os.system(f'rm {get_pkg()}')


def open_required_ports(actions, ports, add_options, forward_options, mapped_ports, masquerade_options, reload_options):
    """
    This function will help to open/allow required ports/services and enable the program to anticipate logs from
    various network devices by forwarding their logs to a port other than 514 which is intended for the local device
    @param actions: Takes a list of action to be carried out ['add', 'forward', 'masquerade', 'reload']
    @param ports: Takes a list of pairs (port, 'Layer 4 protocol'), e.g => [(80, 'tcp')]
    @param add_options: Takes 'firewall-cmd' options in dictionary form to trigger the action of adding a port
    @param forward_options: Takes 'firewall-cmd' options in dictionary form to trigger the action of forwarding a port
    @param mapped_ports: Takes a list of a pair of ports to map/masquerade , e.g => [(514, 5514)]
    @param masquerade_options: Takes 'firewall-cmd' options in dictionary form to trigger the masquerading action
    @param reload_options: Takes 'firewall-cmd' status options in dictionary form to reload the firewall
    @return: Default (NoneType)
    """
    for a in actions:
        if a == 'add':
            for port, proto in ports:
                os.system(f"firewall-cmd {add_options[0]} {add_options[1]} {add_options[2]}={port}/{proto}")
        elif a == 'forward':
            for port_from, port_to in mapped_ports:
                os.system(f"firewall-cmd {forward_options[0]} {forward_options[1]}={port_from}:{forward_options[2]}={port_to}")
        elif a == 'masquerade':
            os.system(f"firewall-cmd {masquerade_options[0]}")
        else:
            os.system(f"firewall-cmd {reload_options[0]}")


def main():

    if os.geteuid() == 0:

        user_opt = ""

        harvest_splunk(splunk_releases)
        download_link = harvest_splunk(splunk_releases)[0]
        splunk_release_latest = harvest_splunk(splunk_releases)[2]

        check_splunk()
        splunk_installed = check_splunk()[1]

        if not splunk_installed:
            install_new(download_link)
        else:
            if splunk_installed != splunk_release_latest:
                user_opt = pre_reading_user_opt(splunk_installed, splunk_release_latest)
                if user_opt in ('Y', 'y'):
                    install_upgrade(download_link)
                else:
                    exit()
            else:
                exit(f"\nNothing to do - You have Splunk latest version ({splunk_release_latest})")

        perform_initial_tasks()

        action = ['add', 'forward', 'masquerade', 'reload']
        port_proto = [(80, 'tcp'), (443, 'tcp'), (8000, 'tcp')]
        add = {0: '--permanent', 1: '--zone=public', 2: '--add-port'}
        forward = {0: '--permanent', 1: '--add-forward-port=port', 2: 'proto=udp:toport'}
        port_to_map = [(514, 5514)]
        masquerade = {0: '--add-masquerade'}
        reload = {0: '--reload'}

        open_required_ports(action, port_proto, add, forward, port_to_map, masquerade, reload)

        os.system(f'{get_pkg_path()} status')

        if user_opt in ('Y', 'y'):
            exit('\nSplunk Enterprise has been upgraded !\n')
        else:
            exit('\nSplunk Enterprise has been installed !\n')

    else:
        exit("\nPrivileges are required to run this script.\n")


if __name__ == "__main__":
    main()
