# Graphy

Graphy is the main project for the thesis.

## Requirements

Python 3.6

## Setup

After cloned this project, you have two ways to run Graphy. You can either install it on your local machine, or open it 
with the [Pycharm IDE](https://www.jetbrains.com/pycharm/) and run it in the IDE.

If the selected option is install it, you need to run the following commands:

```
sudo ./install.sh       # Install the Graphy tool
graphy --help           # Get the commands documentation
```

If you want to run `graphy` with `zipkin` integration, you can find some scripts to run Zipkin in a `docker` container.
Be sure to have [Docker](https://www.docker.com/) installed in your system.

```
scripts/docker-zipkin-start.sh          # Starts Zipkin in a docker container
scripts/docker-zipkin-stop-rm-all.sh    # Stops and removes all docker containers [BE CAREFULL IF YOU HAVE IMPORTANT CONTAINERS RUNNING]
```

## Run

Graphy can run in multiple modes - `graphy [MODE]`. They are the following:

```
graphy run              # Runs using the default implemented graph algorithm to perform the analysis
graphy zipkin           # Runs using the Zipkin API to perform the analysis
```

For more information about each mode and the possible options, please run - `graphy [MODE] --help`
