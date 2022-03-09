# GoCart Sample Integration
Example cart and checkout which uses the GoCart API / SDK.

It's meant as a jumping off point and is likely already out of date.  Please consult the docs for current information:
https://docs.gocartpay.com/docs

Tools:
- Bootstrap
- Jinja
- Flask
- Python
- Caddy
- MongoDB
- Docker

## Usage
Clone into a directory, then run
```bash
docker volume create caddy
docker volume create mongodb
docker-compose up --build
```

If you want to run detached so it doesn't block the terminal, add `-d` as a flag to `docker-compose up`.

The site will be avilable on `http://localhost:5000`.