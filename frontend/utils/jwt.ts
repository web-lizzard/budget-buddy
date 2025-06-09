/**
 * JWT utilities for token decoding
 */

interface JWTPayload {
  sub: string; // user ID
  email?: string;
  exp: number;
  iat: number;
  type?: string;
}

/**
 * Decode JWT token payload without verification
 * Note: This is for client-side extraction only, server must verify
 */
export function decodeJWTPayload(token: string): JWTPayload | null {
  try {
    // JWT structure: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('Invalid JWT token format');
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];

    // Add padding if necessary
    let decoded = payload;
    switch (payload.length % 4) {
      case 2: decoded += '=='; break;
      case 3: decoded += '='; break;
    }

    const decodedPayload = JSON.parse(atob(decoded));
    return decodedPayload as JWTPayload;
  } catch (error) {
    console.error('Failed to decode JWT payload:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 */
export function isTokenExpired(token: string): boolean {
  const payload = decodeJWTPayload(token);
  if (!payload) return true;

  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
}

/**
 * Extract user ID from JWT token
 */
export function extractUserIdFromToken(token: string): string | null {
  const payload = decodeJWTPayload(token);
  return payload?.sub || null;
}
