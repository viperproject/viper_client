# README #

This client app written in Python3 demonstrates how Viper REAT API can be used for submitting verification tasks to the ViperServer and receiving the resulting stream of Json objects. 

### What is this repository for? ###

We used to use Nailgun for launching a persistent JVM for Viper. With ViperServer, we don't need Nailgun anymore. 

Use cases (list not exhaustive): 

* Collecting statistics 
* Black box testing of ViperServer

### How do I get set up? ###

* Install [ViperServer](https://bitbucket.org/viperproject/viperserver)
* Install python3
* install pip for python3
* Run ```pip install -r requirements.txt```

    If not sure how to select pip for Python3, try ```python3 -m pip install -r requirements.txt```
    
* Run ```chmod +x client.py```
* Start ViperServer by running ```sbt run``` (from the root directory of ViperServer). 
* Usage: ```./client.py -p 50424 -f /Users/wi/eth/phd_proj/trclo/repo/trclo_mark.vpr -v silicon -x="--disableCaching"```

### Who do I talk to? ###

* Requests are welcome! Please send them to [Arshavir](mailto:ter-gabrielyan@inf.ethz.ch)