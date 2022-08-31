import glob


def get_prog_path():
    path = "/opt/splunk/bin/splunk"
    return path


def get_pkg():
    for pkg in glob.glob("splunk*"):
        return pkg
