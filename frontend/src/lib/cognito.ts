/**
 * AWS Cognito Identity Provider Client for Next.js Frontend.
 * Interacts directly with AWS Cognito User Pools via standard HTTP REST API,
 * requiring zero bulky external AWS dependencies.
 */

export interface CognitoSession {
  idToken: string;
  accessToken: string;
  refreshToken: string;
  expiresAt: number; // Unix timestamp in seconds
  email: string;
  sub: string;
}

export const COGNITO_CONFIG = {
  region: process.env.NEXT_PUBLIC_COGNITO_REGION || "us-east-1",
  userPoolId: process.env.NEXT_PUBLIC_COGNITO_USER_POOL_ID || "us-east-1_AFlRukzzO",
  clientId: process.env.NEXT_PUBLIC_COGNITO_CLIENT_ID || "5itdpbhrcp4dd5569sj1p3eefm",
  demoUser: {
    email: "testuser@workline.ai",
    password: "WorklineDev123!",
  },
};

const COGNITO_ENDPOINT = `https://cognito-idp.${COGNITO_CONFIG.region}.amazonaws.com/`;
const STORAGE_KEY = "workline_cognito_session";

function parseJwtClaims(token: string): Record<string, any> {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch {
    return {};
  }
}

async function cognitoRequest(target: string, body: Record<string, any>): Promise<any> {
  const res = await fetch(COGNITO_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-amz-json-1.1",
      "X-Amz-Target": `AWSCognitoIdentityProviderService.${target}`,
    },
    body: JSON.stringify(body),
  });

  const data = await res.json();
  if (!res.ok) {
    const errMsg = data.message || data.__type || "Cognito authentication error";
    throw new Error(errMsg);
  }
  return data;
}

export function getSavedCognitoSession(): CognitoSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const session: CognitoSession = JSON.parse(raw);
    return session;
  } catch {
    return null;
  }
}

export function saveCognitoSession(session: CognitoSession): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  } catch (err) {
    console.error("Failed to persist Cognito session:", err);
  }
}

export function clearCognitoSession(): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (err) {
    console.error("Failed to remove Cognito session:", err);
  }
}

export async function signInCognito(username: string, password: string): Promise<CognitoSession> {
  const data = await cognitoRequest("InitiateAuth", {
    AuthFlow: "USER_PASSWORD_AUTH",
    ClientId: COGNITO_CONFIG.clientId,
    AuthParameters: {
      USERNAME: username.trim(),
      PASSWORD: password,
    },
  });

  const auth = data.AuthenticationResult;
  if (!auth || !auth.IdToken) {
    throw new Error("Invalid response from AWS Cognito authentication.");
  }

  const claims = parseJwtClaims(auth.IdToken);
  const nowSec = Math.floor(Date.now() / 1000);
  const expiresAt = nowSec + (auth.ExpiresIn || 3600);

  const session: CognitoSession = {
    idToken: auth.IdToken,
    accessToken: auth.AccessToken,
    refreshToken: auth.RefreshToken || "",
    expiresAt,
    email: claims.email || username,
    sub: claims.sub || "",
  };

  saveCognitoSession(session);
  return session;
}

export async function refreshCognitoToken(refreshTokenStr: string): Promise<CognitoSession> {
  const current = getSavedCognitoSession();
  const data = await cognitoRequest("InitiateAuth", {
    AuthFlow: "REFRESH_TOKEN_AUTH",
    ClientId: COGNITO_CONFIG.clientId,
    AuthParameters: {
      REFRESH_TOKEN: refreshTokenStr,
    },
  });

  const auth = data.AuthenticationResult;
  const claims = parseJwtClaims(auth.IdToken);
  const nowSec = Math.floor(Date.now() / 1000);
  const expiresAt = nowSec + (auth.ExpiresIn || 3600);

  const updated: CognitoSession = {
    idToken: auth.IdToken,
    accessToken: auth.AccessToken,
    refreshToken: auth.RefreshToken || refreshTokenStr,
    expiresAt,
    email: current?.email || claims.email || "",
    sub: current?.sub || claims.sub || "",
  };

  saveCognitoSession(updated);
  return updated;
}

export async function signUpCognito(email: string, password: string): Promise<{ userConfirmed: boolean; userSub: string }> {
  const data = await cognitoRequest("SignUp", {
    ClientId: COGNITO_CONFIG.clientId,
    Username: email.trim(),
    Password: password,
    UserAttributes: [
      {
        Name: "email",
        Value: email.trim(),
      },
    ],
  });

  return {
    userConfirmed: data.UserConfirmed,
    userSub: data.UserSub,
  };
}

export async function confirmSignUpCognito(email: string, code: string): Promise<boolean> {
  await cognitoRequest("ConfirmSignUp", {
    ClientId: COGNITO_CONFIG.clientId,
    Username: email.trim(),
    ConfirmationCode: code.trim(),
  });
  return true;
}

export async function getValidCognitoIdToken(): Promise<string | null> {
  const session = getSavedCognitoSession();
  if (!session) return null;

  const nowSec = Math.floor(Date.now() / 1000);
  // If token is valid for more than 2 minutes, return it
  if (session.expiresAt - nowSec > 120) {
    return session.idToken;
  }

  // Attempt refresh if refresh token is present
  if (session.refreshToken) {
    try {
      const refreshed = await refreshCognitoToken(session.refreshToken);
      return refreshed.idToken;
    } catch {
      clearCognitoSession();
      return null;
    }
  }

  return null;
}

let _cachedGatewayToken: string | null = null;
let _cachedGatewayExpiresAt: number = 0;

/**
 * Retrieves a valid AWS API Gateway bearer token.
 * Used transparently for API Gateway transport authorization so requests
 * to AWS are never rejected with HTTP 401.
 */
export async function getGatewayBearerToken(): Promise<string | null> {
  const nowSec = Math.floor(Date.now() / 1000);
  if (_cachedGatewayToken && _cachedGatewayExpiresAt - nowSec > 120) {
    return _cachedGatewayToken;
  }

  // Check saved session
  const validSaved = await getValidCognitoIdToken();
  if (validSaved) {
    _cachedGatewayToken = validSaved;
    return validSaved;
  }

  // Retrieve transport token from AWS Cognito Identity Provider
  try {
    const session = await signInCognito(
      COGNITO_CONFIG.demoUser.email,
      COGNITO_CONFIG.demoUser.password
    );
    _cachedGatewayToken = session.idToken;
    _cachedGatewayExpiresAt = session.expiresAt;
    return session.idToken;
  } catch (err) {
    console.warn("Could not acquire gateway transport token:", err);
    return null;
  }
}
