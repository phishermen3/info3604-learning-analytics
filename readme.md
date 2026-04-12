<a name="top"></a>


<!-- PROJECT SHIELDS -->
![Tests](https://github.com/phishermen3/info3604-learning-analytics/actions/workflows/dev.yml/badge.svg)
![Contributors](https://img.shields.io/github/contributors/phishermen3/info3604-learning-analytics)
![GitHub last commit](https://img.shields.io/github/last-commit/phishermen3/info3604-learning-analytics)
![Issues](https://img.shields.io/github/issues/phishermen3/info3604-learning-analytics)


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center"><strong>LogStack</strong></h3>

  <p align="center">
    An xAPI Learning Analytics Research Project
    <br />
    <br />
    <a href="https://www.youtube.com/watch?v=5U3usO6rMPk">View Demo Video</a>
    &middot;
    <a href="https://logstack.azurewebsites.net/">View Deployed Site</a>
    &middot;
    <a href="https://github.com/phishermen3/info3604-learning-analytics/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#database-setup">Database Setup</a></li>
        <li><a href="#running-the-project">Running the Project</a></li>
      </ul>
    </li>
    <li>
      <a href="#configuration-management">Configuration Management</a>
      <ul>
        <li><a href="#in-development">In Development</a></li>
        <li><a href="#in-production">In Production</a></li>
      </ul>
    </li>
    <li><a href="#deployment">Deployment</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#troubleshooting">Troubleshooting</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

This project was motivated by the rise of generative AI. Traditional assessment methods that rely on a student’s final submissions are becoming less reliable, as code, essays, and reports can now be produced with significant AI assistance, making it difficult to verify authentic learning. So, instead of focusing on final outputs, we shifted our attention to the learning process itself, exploring how student activity can be tracked and analysed over time in alignment with curriculum goals.

To address this, the project introduces this data collection instrument based on xAPI that captures detailed learner interactions and maps them to defined pedagogical stages. By recording key elements such as user actions, timestamps and learning artifacts, the system enables the reconstruction of learning pathways and supports process mining techniques to analyse how students progress from initial exposure to deeper understanding. This approach allows educators to observe patterns of engagement, identify transitions between stages such as planning, exploration, construction, testing, and reflection, and gain more reliable insights into the authenticity and development of student learning over time.


<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Login
- **Frontend:** HTML, CSS, Jinja2
- **Database:** PostgreSQL, psycopg2
- **Learning Analytics:** xAPI (Experience API), Yet Analytics SQL LRS (Learning Record Store)
- **Deployment & Tools:** Azure App Service, Azure Database for PostgreSQL flexible server, Gunicorn, python-dotenv
- **Testing & Utilities:** pytest, Werkzeug, click, rich

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- Python3/pip3
- Packages listed in requirements.txt
- Access to an xAPI-compatible LRS (e.g., Yet Analytics SQL LRS)
- Access to a database compatible with the LRS chosen (e.g., PostgreSQL)

### Installation

### Windows (PowerShell):

1. Navigate to the project
```bash
cd path\to\your\project
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Linux:

1. Navigate to the project
```bash
cd path/to/your/project
```

2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

### Database Setup

Since the project includes a migrations folder, you do not need to initialise the migration repository. Simply ensure your database connection string is set in your .env file and run:

```bash
flask db upgrade
```

If changes to the models are made, the database must be 'migrated' so that it can be synced with the new models.
Do so by executing the following commands:

```bash
flask db migrate -m "Describe your changes here"
flask db upgrade
flask db --help
```

### Running the Project

Once the environment is configured and the database is ready, start the development server:
```bash
flask run
```

The application will be available at http://127.0.0.1:8080

Once the application is running, you must seed the database with the default user credentials and initial courses, teams and project.

Navigate to the following URL in your browser:\
http://127.0.0.1:8080/init

After the page confirms success, you can log in using one of the following pre-configured accounts:

| Username | Password  |
| -------- | --------- |
| bob      | bobpass   |
| steve    | stevepass |

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONFIGURATION MANAGEMENT -->
## Configuration Management

Configuration information such as the database url/port, credentials, API keys etc are to be supplied to the application. However, it is bad practice to stage production information in publicly visible repositories.
Instead, all config is provided via [environment variables](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/).

### In Development

.env
```env
ENV="DEVELOPMENT"
LRS_ENDPOINT="https://LRS_URL.COM/xapi"
LRS_USERNAME="LRS_API_KEY"
LRS_PASSWORD="LRS_API_KEY_SECRET"
SQLALCHEMY_DATABASE_URI="sqlite:///temp-database.db"
JWT_SECRET_KEY="secret key"
```

### In Production

When deploying your application to production/staging you must pass in configuration information via the Environment variables tab of Azure's dashboard. If deploying to other platforms (e.g., Heroku, AWS, or Docker), use the equivalent "Environment variables" interface.

#### Required Environment Variables:

| Key                     | Description                                  |
| ----------------------- | -------------------------------------------- |
| ENV                     | Set to **PRODUCTION**                        |
| JWT_SECRET_KEY          | A long, random string for session encryption |
| LRS_ENDPOINT            | The production URL for your LRS              |
| LRS_PASSWORD            | Your LRS API Key                             |
| LRS_USERNAME            | Your LRS API Key Secret                      |
| SQLALCHEMY_DATABASE_URI | Your Database connection string              |

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- DEPLOYMENT -->
## Deployment

### Startup Command

```bash
gunicorn wsgi:app
```

### Initialising the Database
When connecting the project to a new, empty database, ensure your environment variables are configured correctly. Then, execute the following command to initialise the schema. For Azure deployments, this can be performed via the SSH console for the App Service.

```bash
flask db upgrade
```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- TESTING -->
## Testing

### Unit & Integration
Unit and Integration tests are created in the App/test. You can then create commands to run them. Look at the unit test command in wsgi.py for example:

```python
@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))
```

You can then execute all user tests as follows:

```bash
$ flask test user
```

You can also supply "unit" or "int" at the end of the command to execute only unit or integration tests.

You can run all application tests with the following command:

```bash
$ pytest
```

### Test Coverage

You can generate a report on your test coverage via the following command:

```bash
$ coverage report
```

You can also generate a detailed html report in a directory named htmlcov with the following command:

```bash
$ coverage html
```

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Troubleshooting -->
## Troubleshooting

### Views 404ing

If your newly created views are returning 404 ensure that they are added to the list in main.py.

```python
from App.views import (
    user_views,
    index_views
)

# New views must be imported and added to this list
views = [
    user_views,
    index_views
]
```

### Database Issues

If you are adding models you may need to migrate the database with the commands given in the [Database Setup](#database-setup) section.

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are welcome! Feel free to fork the repo, open issues, or submit pull requests.

Please use the [issue tracker](https://github.com/phishermen3/info3604-learning-analytics/issues/new?labels=bug&template=bug-report---.md) to report any bugs.

### Steps to Contribute

1. Fork the project to your account.
2. Clone your fork and create your feature branch:
```bash
# Clone fork
git clone https://github.com/your_username/info3604-learning-analytics.git
cd info3604-learning-analytics

# Create new branch
git checkout -b feature/AmazingFeature
```
3. Make changes and test.
4. Commit your changes and push to the branch:
```bash
# Commit changes
git commit -m 'Add some AmazingFeature'

# Push to branch
git push origin feature/AmazingFeature
```
5. Open a Pull Request with comprehensive description of changes.

### Top contributors:

<a href="https://github.com/phishermen3/info3604-learning-analytics/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=phishermen3/info3604-learning-analytics" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- Acknowledgments -->
## Acknowledgments

- [Yet Analytics SQL LRS](https://www.yetanalytics.com/sql-lrs) (Learning Record Store implementation)
- [xAPI](https://xapi.com/) (Experience API / Tin Can API specification)

<p align="right">(<a href="#top">back to top</a>)</p>
