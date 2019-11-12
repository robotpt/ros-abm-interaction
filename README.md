README
======

> WIP

The content for the human-robot interaction for the
ABM grant.

Setup 
-----

Clone the repository:

    git clone https://github.com/robotpt/abm-grant-interaction
    
An easy way to setup the repository with its dependencies and with your Python path
is to use `pip`.  

    pip install -e abm-grant-interaction

Before you can run the examples or tests, you will have to create a file called `fitbit_secrets.yaml` in `resources/`.  
This file should have the following format. See [here](https://github.com/robotpt/fitbit-reader) for instructions in 
generating these values.

    client_id: XXXXXX
    client_secret: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
Tests can be run with the following commands.
    
    cd abm-grant-interaction
    python3 -m unittest

