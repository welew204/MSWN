#!/bin/bash

if [ $1 = "sim" ]
then
    export DB="mswnSim.sqlite"
    
else
    export DB="mswnapp.sqlite"
fi

echo "running DB from ... "$DB


export FLASK_RUN_PORT=8000 
flask --app runMswn.py --debug run