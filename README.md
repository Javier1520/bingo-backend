# bingo-backend
Here’s a sample `README.md` documenting your endpoints:

---

# Bingo API Documentation

This API allows users to register, play bingo games, claim wins, and interact with their bingo cards. Authentication is required for all endpoints except user registration and login.


### Prerequisites

1. **Python 3.10**: Ensure you have Python 3.10 installed.
   - Check your Python version:
     ```bash
     python --version
     ```
   - If not installed, download Python 3.10 from [python.org](https://www.python.org/downloads/).

2. **Pipenv**: The project uses `pipenv` to manage dependencies.
   - Install Pipenv:
     ```bash
     pip install pipenv
     ```
   - Install dependencies:
     ```bash
     pipenv install
     ```
   - Activate the virtual environment:
     ```bash
     pipenv shell
     ```
3. Set up the .env file based on the .env.example template.
4. Run migrations to set up the database:
   ```bash
     python manage.py migrate
     ```
5. Start the development server:
   ```bash
     python manage.py runserver
     ```
6. Access the application at ```http://127.0.0.1:8000/```


## Authentication

The API uses **token-based authentication**. Users must first register and log in using their **username** and **password**. Upon successful login, a token is returned, which must be included in the `Authorization` header (`Token <your_token>`) for all subsequent requests.

---

## Endpoints

### Authentication

#### Register a User
**URL:** `POST /api/auth/users/`  
**Description:** Registers a new user.  

**Request Body:**  
```json
{
  "username": "example_user",
  "password": "secure_password"
}
```

**Response:**  
```json
{
  "id": 1,
  "username": "example_user",
  "email": "",
  "first_name": "",
  "last_name": ""
}
```

---

#### Login
**URL:** `POST /api/auth/token/login/`  
**Description:** Logs in a user and returns a token.  

**Request Body:**  
```json
{
  "username": "example_user",
  "password": "secure_password"
}
```

**Response:**  
```json
{
  "auth_token": "your_token_here"
}
```

---

### Game Endpoints

#### Register to a Game
**URL:** `POST /api/register-to-game`  
**Description:** Registers the authenticated user to a new or ongoing inactive game.  

**Request Headers:**  
```http
Authorization: Token <your_token>
```

**Response (Success):**  
```json
{
  "player": "example_user",
  "card": {
    "B": [5, 14, 3, 12, 9],
    "I": [20, 26, 22, 18, 25],
    "N": [31, 36, null, 34, 33],
    "G": [50, 46, 48, 52, 55],
    "O": [61, 68, 65, 63, 66]
  }
}
```

**Response (Error - Game Full):**  
```json
{
  "error": "Game is full"
}
```

**Response (Error - Already Registered):**  
```json
{
  "error": "User is already registered for an active game"
}
```

---

#### Get Latest Ball
**URL:** `GET /api/latest-ball`  
**Description:** Retrieves the most recently drawn bingo ball for the current game.  

**Request Headers:**  
```http
Authorization: Token <your_token>
```

**Response (Success):**  
```json
{
  "latest_ball": 42
}
```

**Response (Error):**  
```json
{
  "message": "No balls drawn yet"
}
```

---

#### Claim a Win
**URL:** `POST /api/claim-win`  
**Description:** Allows the authenticated user to claim a win. Validates the user’s bingo card against drawn balls.  

**Request Headers:**  
```http
Authorization: Token <your_token>
```

**Response (Success):**  
```json
{
  "message": "example_user wins the game!"
}
```

**Response (Error - Invalid Card):**  
```json
{
  "error": "Invalid claim, you are disqualified"
}
```

**Response (Error - No Active Game):**  
```json
{
  "error": "No active game"
}
```

---

#### Get Bingo Card
**URL:** `GET /api/bingo-card`  
**Description:** Retrieves the authenticated user’s bingo card for the current active game.  

**Request Headers:**  
```http
Authorization: Token <your_token>
```

**Response (Success):**  
```json
{
  "card": {
    "B": [5, 14, 3, 12, 9],
    "I": [20, 26, 22, 18, 25],
    "N": [31, 36, null, 34, 33],
    "G": [50, 46, 48, 52, 55],
    "O": [61, 68, 65, 63, 66]
  }
}
```

**Response (Error):**  
```json
{
  "error": "User is not part of an active game"
}
```

---

## Notes

- Authentication is required for all endpoints except `/api/auth/users/` (registration) and `/api/auth/token/login/` (login).
- Token-based authentication must be provided via the `Authorization` header for all authenticated requests.
- A user can only participate in one active game at a time.
- Disqualified users and winners can register for new games once the previous game is completed.

### Environment Variables

The project uses environment variables to manage configuration. Create a `.env` file in the project root based on the `.env.example` template and fill in the required values.

Example:
```dotenv
DB_NAME=mydatabase
DB_USER=myuser
DB_PASSWORD=mypassword
SECRET_KEY=mysecretkey
