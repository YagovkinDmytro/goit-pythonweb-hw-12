# FastAPI and REST API construction. Application architecture.

## Docker / PostgreSQL

### Start the project

```bash
docker-compose up -d # runs in background
docker-compose logs -f # view logs after launch
docker-compose up # runs and shows logs
```

### Stop the project

```bash
docker-compose down
```

### Restart the project (preserving data)

```bash
docker-compose restart
```

# Alternative to create docker container

```bash
docker run --name db-contacts -p 5432:5432 -e POSTGRES_USER="POSTGRES_USER" -e POSTGRES_PASSWORD="POSTGRES_PASSWORD" -e POSTGRES_DB="POSTGRES_DB" -d postgres
```

# Alembic migrations

Before this, you need to make all the necessary settings for migrations.

```bash
alembic init migrations
alembic revision --autogenerate -m 'Init'
alembic upgrade head
```

# Starting development server

```bash
fastapi dev main.py
- starts the development server.
```

Server started at http://127.0.0.1:8000

Documentation at http://127.0.0.1:8000/docs

Documentation at http://127.0.0.1:8000/redoc

```bash
fastapi run main.py
- starts the production server.
```

# Architecture of the project

```bash
├── migrations
│   ├── versions
│   │   └──name_of_version.py
├── src
│   ├── api
│   │   ├── utils.py
│   │   └── contacts.py
│   ├── services
│   │   └── contacts.py
│   ├── repository
│   │   └── contacts.py
│   ├── database
│   │   ├── models.py
│   │   └── db.py
│   ├── conf
│   │   └── config.py
│   └── schemas.py
├── .env
├── .env.examlpe
├── .gitignore
├── alembic.ini
├── poetry.lock
├── pyproject.toml
├── README.md
└── main.py
```

# Test Coverage (pytest-cov)

If you want to know how much code is covered by tests:

- pytest-cov allows you to collect information about code coverage by tests

This will show the % coverage and the lines that were not tested.

```
poetry add pytest-cov
pytest --cov=src tests/
pytest --cov=src tests/ --cov-report=html
pytest --cov=src tests/ --cov-report=xml
pytest --cov=src --cov-report=term-missing

```

```
Coverage report: 78%

File	                     statements	missing	excluded	coverage
src\api\auth.py	                     54	     28	       0	     48%
src\api\contacts.py	                 53	     26	       0	     51%
src\api\users.py	                 22	      5	       0	     77%
src\api\utils.py	                 16	      0	       0	    100%
src\conf\config.py	                 23	      0	       0	    100%
src\database\db.py	                 23	     11	       0	     52%
src\database\models.py	             34	      2	       0	     94%
src\repository\contacts.py	         64	      1	       0	     98%
src\repository\users.py	             35	      0	       0	    100%
src\schemas.py	                     42	      0	       0	    100%
src\services\auth.py	             55	     19	       0	     65%
src\services\contacts.py	         38	      3	       0	     92%
src\services\email.py	             15	      7	       0	     53%
src\services\upload_file.py	         14	      8	       0	     43%
src\services\users.py	             25	      4	       0	     84%
Total	                            513	    114	       0	     78%

```
