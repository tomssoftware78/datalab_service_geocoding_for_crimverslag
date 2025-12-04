# Prerequisite

The geocoding service needs to be up and running before this tool can start. Otherwise it will exit.
Add the endpoint config to the .env file

## Build

```
docker build -t docker-host.ccuvpndom.com:5000/crimverslag-geocodering:latest .
docker push docker-host.ccuvpndom.com:5000/crimverslag-geocodering:latest
```

## Start

Provide following folder structure on the server you want to run the project on:

```
- project/
  - app/
    - logging_config.yml
  - docker-compose.yml
  - .env
  ```

  .env contains the connection settings to the file share!

  Run the tool:

  ```
  docker compose up -d
  ```