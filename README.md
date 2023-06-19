## Description:

This is an API application that is capable to interact with chatGPT to create a conversation with you in english and talk about desired topics.
<br>
<br>
The conversationalAI should correct you in every english mistake you do and also keep the conversation going asking you questions.

## Prerequisites:

1. `docker`
2. `docker-compose`

If you don't want to use docker to run the project, you will need to install `python3` and use `pip install -r app/requirements.txt` to install all dependencies. Also, i think you will need to install `python3-flask` and `gunicorn` in your OS.

## Usage:

Go to the `docker/docker-compose.yml` file and add the api_keys you have/want to use before running the project.
<br>
<br>
I will add more details on the routes and requests body later...

## How to run:

First execution or when you add new dependencies: `make run-build`
</br>
After that you can just do: `make run`

If you don't want to use docker: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload main:app`
