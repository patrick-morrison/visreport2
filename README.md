# Vis.Report
[_Visibility reports for divers to share conditions. Configured by default for Perth, Western Australia_](https://vis.report)

This is version 2 of Vis.Report. Written from the ground up to support prediction. 

Written in Django. Original started in January 2020 by Patrick Morrison, rewritten in March 2022.

## Features

- Map interface to display reports, colour coded by the most recent visibility
- Detail pages for each site, with a full list of reports and an interface to add new ones.
- User accounts system with email authentication, and an admin page to add/edit dive sites. 
- A json api for using the data in other systems.
- New: weather for sites, depending on their specific geography

## Installation

Clone this repository, ,ake virtual environment, install requirements.txt and run with Django.

```bash
git clone https://github.com/PatrickMorrison1498/visreport.git
python -m venv ENV
source ENV/bin/activate
pip install -r requirements.txt
cd visreport2
python manage.py runserver
```

## Usage

Go to 127.0.0.1:8000. It will be running there.

## Deploying

I have it deployed on Digital Ocean App Platform, with a Postgres database and a static site. It needs the following environment variables
- EMAIL_HOST_USER = email account
- EMAIL_HOST_PASSWORD = email password
- WEATHER_API = willyweather api key
- RECAPTCHA_PUBLIC_KEY - google recaptcha
- RECAPTCHA_PRIVATE_KEY - google recaptcha
- TZ = Australia/Perth
- DEBUG = False
- DEVELOPMENT_MODE = False

The app platform should also include these at the app level:
DATABASE_URL  = ${db.DATABASE_URL}
DJANGO_ALLOWED_HOSTS = ${APP_DOMAIN}
DJANGO_SECRET_KEY = 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)

