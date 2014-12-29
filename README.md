Spike - distributed load testing utility
================

#### Manual task schelduling:

##### Install python-dev package.

Ubuntu:
```
    sudo apt-get install python-dev python-pip
```
Mac os x:
```
    brew install python
```
##### Setup virtualenv.
```
    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt
```
##### Run command.

General syntax:
```
    python tools/manual_start.py [-h] [-amqp AMQP_SERVER] [-s SCENARIO] [-c COUNT]
```
Example:
```
    python tools/manual_start.py -s flow.py -c 100
```

```
    python tools/manual_start.py -amqp localhost -amqp-pass pwd123 -c 100 -s flow.py
```

Available scripts are under scripts folder.

