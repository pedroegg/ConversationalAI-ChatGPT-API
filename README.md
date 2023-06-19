## Prerequisites:

1. `docker`
2. `docker-compose`

If you don't want to use docker to run the project, you will need to install `python3` and use `pip install -r app/requirements.txt` to install all dependencies.
<br>
<br>
Also, i think you will need to install `python3-flask` and `gunicorn` in your OS.

## Usage:

Go to the `docker/docker-compose.yml` file and add the api_keys you have/want to use before running the project.

## How to run:

First execution or when you add new dependencies: `make run-build`
</br>
After that you can just do: `make run`

If you don't want to use docker: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 --reload main:app`
