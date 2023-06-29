# README #

This client app written in Python3 demonstrates how Viper API can be used for submitting verification tasks to the ViperServer and receiving the resulting stream of Json objects. 

### What is this repository for? ###

We used to use Nailgun for launching a persistent JVM for Viper. With ViperServer, we don't need Nailgun anymore. 

Use cases (list not exhaustive): 

* Collecting statistics 
* Black box testing of ViperServer

### How do I get set up? ###

* Install [ViperServer](https://bitbucket.org/viperproject/viperserver).
* Install Python 3 (preferably with VirtualEnv: `python3 -m venv env`).
* Install pip for Python 3: `env/bin/python3 -m ensurepip --default-pip`.
* Run `env/bin/pip install -r requirements.txt`
* Start ViperServer by running `sbt run` (from the root directory of ViperServer). Alternatively, if you downloaded a [Viper Server release](https://github.com/viperproject/viperserver/releases), you can run `Z3_EXE=viper_tools/z3/bin/z3 java -Xss1024m -Xmx4024m -jar viper_tools/backends/viperserver.jar`.
* Usage: `env/bin/python3 ./client.py -p 50424 -f /Users/wi/eth/phd_proj/trclo/repo/trclo_mark.vpr -v silicon -x="--disableCaching"`

### Can I use this tool to benchmark Viper? ###

Yes:

```bash
python3 client.py -p 12345 \
    --warmup-file log/viper_program/<test-name>/<some-small-file.vpr> \
    --benchmark log/viper_program/<test-name>* \
    --benchmark-report report
```

### Who do I talk to? ###

* Requests are welcome! Please send them to [Arshavir](mailto:ter-gabrielyan@inf.ethz.ch)
