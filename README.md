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

# API Documentation

This documentation provides information about the various API endpoints and their functionalities.

## Serve Sphinx-generated Documentation

### Endpoint: `/docs/` and `/docs/<path:path>`

Serve the Sphinx-generated documentation files.

#### Example API Call

- Request: GET `/docs/`
- Response: HTML documentation file

---

## Get Data Records within a Specified Range

### Endpoint: `/api/rankings`

Retrieve data records within a specified range and return a formatted response.

#### Example API Call

- Request: GET `/api/rankings`
- Response: JSON formatted response containing data records

---

## Get Data Record for a Specified ID

### Endpoint: `/api/<int:id>`

Retrieve data records for a specified ID and return a formatted response.

#### Example API Call

- Request: GET `/api/123`
- Response: JSON formatted response containing data records for ID 123

---

## Add a New Data Record

### Endpoint: `/api/add-record`

Add a new data record and return a response message.

#### Example API Call

- Request: POST `/api/add-record`
  - Body: JSON data for the new record
    {
    "column1": "value1",
    "column2": "value2",
    ...
    }
- Response: JSON response indicating the success of the POST request

---

## Delete a Data Record by ID

### Endpoint: `/api/<int:id>/delete-record`

Delete a data record by ID and return a response message.

#### Example API Call

- Request: DELETE `/api/123/delete-record`
- Response: JSON response indicating the success of the DELETE request

---

## Update a Data Record by ID

### Endpoint: `/api/<int:id>/update-record`

Update a data record by ID and return a response message.

#### Example API Call

- Request: PUT `/api/123/update-record`
- Body: JSON data with updated values
    {
    "column1": "new_value1",
    "column2": "new_value2",
    ...
    }
- Response: JSON response indicating the success of the UPDATE request
