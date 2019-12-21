#!/bin/bash
app="sentryo_backend_test"
docker build -t ${app} .
docker run -d -p 5000:5000 --name=${app} -v $PWD:/app ${app}