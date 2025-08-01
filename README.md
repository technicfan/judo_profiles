# Description

This is a project that tries to make it easier for trainers of judo clubs to manage their fighter profiles.<br>
It is intended to be hosted by the club and used by all the trainers and features management functions that should satisfy all needs for that purpose.<br>
This is my first django project so expect not everything to work perfectly fine.

# Features

- Djangos secure user system
- Django-Guardian for managing user permissions
- editing of the imprint/contact information at runtime
- an admin that can create users and staff members to help them
    - a registration token is used for registration instead of the admin setting a password
    - such a token can also be created to reset the password for a user
- Trainers that can create and manage fighter profiles
- Fighters can see and manage their profiles themselves
- Dark and light theme

# Installation

The project can be run either manually (linux only) or with docker (recommended)

## Manually

1. Clone/Download this repository (with git or the download zip button)
2. Create and activate (in your shell) a python venv:

```bash
python -m venv <location>
source <location>/bin/activate
```

3. Navigate to the project folder in your shell
4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

5. Set required environment variables
6. Create the "data" folder
7. Prepare the files

```bash
python manage.py collectstatic
django-admin compilemessages
python manage.py migrate
```

8. Create the admin account with a username and password

```bash
python manage.py createsuperuser
```

9. Run the server

```bash
./entrypoint.sh
```

## Docker (recommended)

1. Create a "docker-compose.yml" file
2. Paste the contents of the file from this repository
3. Replace "context: ." with "context: https://github.com/technicfan/judo_profiles.git"
4. Adjust and add required environment variables
    - If you want to use sqlite remove the database container and mount the data volume at "/app/data"
5. Run `docker compose up`

## Environment Variables

| Name                | Required                         | Description                                                                                                 |
| :------------------ | :------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| `SECRET_KEY`        | Yes                              | Generate a random key needed for encryption stuff (e.g. with `openssl rand -base64 48` on linux)            |
| `ALLOWED_URLS`      | Yes                              | List seperated by spaces with full the urls (e.g. "http://127.0.0.1:8000") you want to access the site with |
| `APP_PORT`          | No - default: `8000`             | The port the server runs on                                                                                 |
| `DEBUG`             | No                               | Turn on djangos debug mode with "True"                                                                      |
| `DATABASE_ENGINE`   | No                               | The database to use (sqlite is used by default - postgresql, mysql, oracle are available)                   |
| `DATABASE_NAME`     | Only when database is not sqlite | The database name                                                                                           |
| `DATABASE_USER`     | Only when database is not sqlite | The database user                                                                                           |
| `DATABASE_PASSWORD` | Only when database is not sqlite | The database password                                                                                       |
| `DATABASE_HOST`     | Only when database is not sqlite | The database host                                                                                           |
| `DATABASE_PORT`     | Only when database is not sqlite | The database port                                                                                           |

# Contributing

If you find any bugs/missing features feel free to create an issue here.<br>
If you want/can fix it yourself, I'd be happy to also see pull reqests.<br>
Unless you know how to properly handle django migrations, the database probably won't change after the first release which means no major features.<br>
I would especially be happy if someone with knowledge would look if the privacy page is sufficient.<br>
I will look at everything and try to answer all open questions.

# License

This project is distributed under the GPL-3.0 which means derived works have to be published under the same license.
