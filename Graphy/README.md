# Graphy

This is the main project for the thesis.

## Architecture

The project architecture can be found in the [Architecture](/docs/architecture) directory.

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

## Run

Graphy can run in multiple modes - `graphy [MODE]`. They are the following:

```
graphy run              # Runs using the default implemented graph algorithm to perform the analysis
graphy zipkin           # Runs using the Zipkin API to perform the analysis
```

For more information about each mode, please run - `graphy [MODE] --help`
