#!/usr/bin/env bash

# Graphy data directory
sudo mkdir ./data

# Graphy root directory
sudo mkdir /tmp/graphy

# TODO: Remove this if it's not necessary anymore.  -----
# ArangoDB Data directory
# sudo mkdir -p /tmp/graphy/arangodb
# sudo chown 472:472 /tmp/graphy/arangodb

# Grafana Data directory
# sudo mkdir -p /tmp/graphy/grafana/data;
# sudo chown 472:472 /tmp/graphy/grafana/data
# -------------------------------------------------------

# OpenTSDB Data directory
sudo mkdir -p /tmp/graphy/opentsdb/data
sudo chown 472:472 /tmp/graphy/opentsdb/data
