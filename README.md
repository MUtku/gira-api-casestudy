## GIRA API

An issue management system API created using Flask Python Framework. It takes [Flask API Boilerplate](https://appseed.us/boilerplate-code/flask-api-boilerplate) as base structure as it is enhanced with JWT authentication, SqlAlchemy, **SQLite** persistence and deployment scripts via Docker.

<br />

## Quick Start in `Docker`

> Get the code

```bash
$ git clone https://github.com/MUtku/gira-api-casestudy.git
$ cd gira-api-casestudy
```

> Start the app in Docker

```bash
$ docker-compose up --build  
```

The API server will start on `localhost:5005`.

<br />

## API

For a fast set up, a postman file will be shared with you. Please note that most of the operations neeed authorization. So **you must send the token returned upon login operation in the headers section of the request under the name "authorization" while trying call methods**. Otherwise you won't be able to operate the API.

Also a Swagger page containing OpenAPI Specification can be accessed at `localhost:5005`.

## Testing

Tests can be run using `pytest tests.py` command
