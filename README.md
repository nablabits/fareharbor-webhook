
This is a simple Flask server that processes webhooks from [Fareharbor](https://fareharbor.com/) and, eventually, it will store the data on a Postgres database. For the moment just saves the data in json files.

## Run the local server
```shell
$> export FLASK_APP=fh_webhook
$> export FLASK_ENV=development
$> flask run
$> curl localhost:5000/  # test that it works
```

## Run the test suite
Assuming there's a virtual environment running:

```shell
(venv)$ python3 -m pytest -vv tests
```
This implies having a test database that matches that of `config.TestingConfig.SQLALCHEMY_DATABASE_URI`


## Spinning up the container
The webhook can run as well as a docker container
```shell
$> sudo docker-compose build flask
$> sudo docker-compose up -d flask
```


