# Authentication Flow

- **User Registration**:
  - Client sends a POST request to `/auth/register` with a JSON payload containing an email and a password.
  - The server checks if the email is unique and creates a new user account.
  - On success, the server returns the user's id and email with a 201 Created status.
  - On failure (e.g., email already registered or invalid data), the server returns a 400 Bad Request error.

- **User Login**:
  - Client sends a POST request to `/auth/login` using the OAuth2PasswordRequestForm, providing the email (as username) and password.
  - The server authenticates the provided credentials.
  - If authentication fails, the server returns a 401 Unauthorized error.
  - On success, the server issues both an access token and a refresh token. The access token is used for authorization in subsequent requests, while the refresh token is used to obtain a new access token when the current one expires.

- **Token Refresh**:
  - When the access token expires, the client sends a POST request to `/auth/refresh` with a JSON payload containing the refresh token.
  - The server verifies the refresh token to ensure it is valid and of type 'refresh'.
  - If the verification fails (e.g., due to token expiration or invalid token), the server returns a 401 Unauthorized error.
  - On successful verification, the server issues a new access token for continued access to protected resources. 