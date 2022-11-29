# <p style="text-align: center;"> <span style="color:orange"> Welcome to insta_splunk </span>  </p>

---




![Splunk_logo](img/Splunk_logo.jpg)

 ##### <p style="text-align: center;" color="red"> This program automates the installation of Splunk Enterprise and is developed for GNU/Linux distribution platforms compiled from RHEL such as CentOS Stream, Fedora, Oracle Linux, etc. The code was validated with the Community Edition of Splunk Enterprise on a CentOS Stream 9 box. In addition to Splunk downloading and installing, it also handles some miscellaneous underlying configurations such as file/directory rights, boot-start, firewall ports management, sweeping when exiting, etc. </p>
---


```Bash
$ git clone https://github.com/camarh/insta_splunk
```
---

|         | Name           | Creation date   | Author  | Programming language |
| ------- | -------------- | --------------- | ------- | -------------------- |
| Project | insta_splunk   | August 18, 2022 | Camar H.| Python               |


Pre-requisites

Also make sure to put functions directory in the same directory as main.py

Make sure you have Python3 at least and install/import the required librarie

Setup required packages

* pip
* beautifulsoup
* requests
* wget

> Run the following command to install those interesting package:

```Bash
$ pip install -r requirements.txt
```

Computation guide

> From a terminal, run the following command :

```Bash
$ python3 insta_splunk.py
```