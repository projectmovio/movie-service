#!/usr/bin/env bash

DIR=$(cd `dirname $0` && pwd)

if [[ -z "${MOVIE_SERVICE_API_KEY}" ]]
then
    echo "Please set the MOVIE_SERVICE_API_KEY env variable"
    exit 1
else
    envsubst '${MOVIE_SERVICE_API_KEY}' < ${DIR}/manifest/deployment.yml > deployment_injected.yml
    kubectl apply -f deployment_injected.yml
    rm deployment_injected.yml
fi