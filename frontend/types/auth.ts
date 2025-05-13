// Based on backend/src/adapters/inbound/api/routers/auth/schemas.py

/**
 * Represents the user data returned by the API after creation or for profile display.
 */
export interface UserResponse {
  id: string;
  email: string;
  // Add other fields if UserService.create_user or user retrieval returns more
}

/**
 * Data structure for creating a new user.
 */
export interface UserCreate {
  email: string;
  password: string;
}

/**
 * Represents the API response containing access and refresh tokens.
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string; // Typically "bearer"
}

/**
 * Request body for refreshing an access token.
 */
export interface RefreshTokenRequest {
  refresh_token: string;
}

/**
 * Response body containing a new access token.
 */
export interface NewAccessTokenResponse {
  access_token: string;
  token_type?: string; // Typically "bearer"
}

/**
 * Data structure for user login, matching the Pydantic model UserLogin.
 */
export interface UserLogin {
  email: string;
  password: string;
}

// --- Pinia Store User State ---
/**
 * Represents the authenticated user object stored in Pinia state.
 */
export interface AuthenticatedUser {
  id: string;
  email: string;
  // Add any other user-specific details needed in the frontend state
} 