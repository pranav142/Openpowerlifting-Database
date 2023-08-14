# Openpowerlifting Database
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/YourUsername/YourRepoName/blob/master/LICENSE)

Welcome to the Openpowerlifting Database project – a robust and comprehensive restful CRUD API designed for seamless access to powerlifting records. These records have been meticulously scraped from [Openpowerlifting.org](https://www.openpowerlifting.org/) and thoughtfully stored within a MySQL database. my goal is to provide users like you with a powerful tool to explore, retrieve, and interact with this valuable repository of powerlifting data.

## Documentation
For detailed information on how to use my API and dive into the source code, please visit my [API Documentation](https://openpowerlifting-server.orangebush-9d08bf9d.westus2.azurecontainerapps.io/docs/). This documentation serves as a comprehensive guide, helping you navigate the features and functionalities we offer.

## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

Make sure you have the following installed:

- Python (version 3.9.x)
- MySQL instance

### Installation

1. Clone the repository to your local machine.

```bash
https://github.com/pranav142/PowerLifting-Data-Analysis.git
```

2. navigate to the root directory of the project and install requirements
```bash
pip install -r requirements.txt
```

3. Build the project distribution and wheel packages.
```bash
python setup.py bdist_wheel sdist
```

4. Install the project package.
```bash
pip install .
```

5. Navigate to the `src/data` directory and run the data scraping and cleaning scripts.
```bash
cd src/data
python scrape.py
python clean.py
```

6. Setup MySQl Database Connection
Create a `.env` file in the `src/server` directory and define the following variables:
```.env
MY_SQL_HOST=your_host
MY_SQL_USER=your_user
MY_SQL_PASSWORD=your_password
MY_SQL_DATABASE=desired_schema_name
```

7. Create the Database Schema
```bash
python create_db.py
```

8. Start the application server
```bash
python app.py
```

9. Access the application.
Open your web browser and navigate to http://localhost:8080 to see the server up and running.

# API Usage Guide

This guide explains how to use the APIs provided by the project. The project offers several APIs for interacting with data records and documentation.

## API Endpoints

### Serve Documentation

To access the Sphinx-generated documentation, use the following routes:

- `/docs/`: Serves the default documentation index page.
- `/docs/<path:path>`: Serves other documentation files within the specified path.

### Get Data Records Within a Range

Retrieve data records within a specified range. Replace `<your-host>` with your host and `<your-port>` with your port number.

**Endpoint:** `/api/rankings`

**HTTP Method:** GET

**Example Request:**

```http
GET http://localhost:8080/api/rankings
```
