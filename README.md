<h1 align="center"> Welcome to insta_splunk </h1>

![Splunk_logo](img/illustration.jpg)

<p align="justify"> This program automates the installation of Splunk Enterprise and is developed for GNU/Linux distribution platforms compiled from RHEL such as CentOS Stream, Fedora, Oracle Linux, etc. The code was validated with the Community Edition of Splunk Enterprise on a CentOS Stream 9 box. In addition to Splunk downloading and installing, it also handles some miscellaneous underlying configurations such as file/directory rights, boot-start, firewall ports management, sweeping when exiting, etc. </p>

#
#

<br/>

### Pre-requisites
#

> Clone the repo with the following from a terminal :

```Bash
git clone https://github.com/camarh/insta_splunk_py
```

> Make sure :
* you have Python3 at least
* to make updates beforehand if applicable

<br/>

### Required packages
#

* pip

> Run the following command to install pip :

```Bash
sudo dnf -y install pip
```

* bs4
* wget

> Run the following command to install those interesting packages :

```Bash
sudo pip install -r requirements.txt
```

<br/>

### Computation guide
#

> From a terminal, run the following command :

```Bash
sudo python3 insta_splunk.py
```

<br/>

### Project Info

#

<div>Name &nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Creation date&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Author&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Programming language</div>

#

<div>insta_splunk&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;August 18, 2022&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Camar H.&nbsp;&nbsp;&nbsp;&nbsp; Python</div>

<br/>

### Contact

- Email - &nbsp;&nbsp;&nbsp;&nbsp; camar.houssein@outlook.com
- Linkedin - [https://www.linkedin.com/in/camarh/](https://www.linkedin.com/in/camarh/)

#

© 2022 Camar H.