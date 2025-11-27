# Enterprise Portal

This project is a web application built with Python, Flask, and SQLite. It provides a login system with user roles (admin and user) and separate dashboards for each role.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3
* pip

### Installation

**1. Clone the repository:**

```bash
https://github.com/Raj-srivastav-org/A-Flask-Application-with-Login-and-Registration-Features.git
```

**2. Navigate to the project directory:**

```bash
cd <your-project-directory>
```

**3. Create and activate a virtual environment:**

**For Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**For Unix or MacOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**4. Install the required packages:**

```bash
pip install -r requirements.txt
```

**5. Run the application:**

```bash
python main.py
```

The application will be running at `http://127.0.0.1:8080`.

## Login Credentials

*   **Username:** admin
*   **Password:** admin

## How to create a new user

To create a new user, you can use the following curl command in your terminal. Make sure the application is running.

```bash
curl -X POST -H "Content-Type: application/json" -d '{"username": "newuser", "password": "newpassword", "email": "newuser@example.com", "full_name": "New User", "role": "user"}' http://127.0.0.1:8080/users
```

**Note:** You must be logged in as an admin to create new users. The above command is a simplified example and does not include authentication. In a real-world application, you would need to handle authentication to protect this endpoint.
