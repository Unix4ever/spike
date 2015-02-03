Spike - distributed load testing utility
================


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


##### Run frontend

Assuming you have Rabbimq running locally

```bash
    env/bin/celeryd -A frontend
    env/bin/python manage.py runserver
```
You can customize configs in the conf.d folder, if you want to use
different queues or another rabbitmq.

##### Run worker

```bash
    env/bin/python spike.py -l logfile.log
```

##### Starting tasks from the frontend

If you started server as described above:
[http://localhost:8000/v1/tasks/](Starting tasks)
[http://localhost:8000/v1/scenarios/](Uploading scenarios)

##### Putting tasks directly to the queue

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

#### Proposed way of use

* deploy frontend to some server, set up rabbitmq there.
* deploy workers to various machines.
* upload scripts to frontend.

Then, when you start task you will be able to define scenario to use.
Every worker will download script file to local cache and will execute
it defined number of times.

#### Roadmap

Project is still in early beta.

My planned tasks, if I have some spare time, I will implement:
:clipboard: visual representation of load test in real time;
:clipboard: make the service set up EC2/Google VM instances on demand;
:clipboard: calling delete on task will cause load test interruption;
:clipboard: add data driven model for scenarios: e.g. use json for storing flow and UI for configuring steps;
:clipboard: add some startup scripts for the service.
