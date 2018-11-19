#!/bin/sh

# Run Zipkin on Docker in localhost:9411
docker run -d -p 9411:9411 openzipkin/zipkin

echo "Zipkin is running"

docker ps