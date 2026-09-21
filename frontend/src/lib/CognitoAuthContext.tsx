'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import {
  CognitoSession,
  getSavedCognitoSession,
  getValidCognitoIdToken,
  signInCognito,
  signUpCognito,
  confirmSignUpCognito,
  clearCognitoSession,
  COGNITO_CONFIG,
} from './cognito';

interface CognitoAuthContextType {
  isSignedIn: boolean;
  isLoaded: boolean;
  userId: string | null;
  userEmail: string | null;
  session: CognitoSession | null;
  getToken: () => Promise<string | null>;
  signIn: (email: string, pass: string) => Promise<void>;
  signUp: (email: string, pass: string) => Promise<{ userConfirmed: boolean }>;
  confirmSignUp: (email: string, code: string) => Promise<void>;
  signOut: () => void;
  signInDemo: () => Promise<void>;
  error: string | null;
  clearError: () => void;
}

const CognitoAuthContext = createContext<CognitoAuthContextType | undefined>(undefined);

export function CognitoAuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<CognitoSession | null>(null);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize session from localStorage on mount
  useEffect(() => {
    const saved = getSavedCognitoSession();
    if (saved) {
      // Purge any pre-existing hardcoded testuser session
      if (saved.email === 'testuser@workline.ai') {
        clearCognitoSession();
        setSession(null);
      } else {
        setSession(saved);
      }
    }
    setIsLoaded(true);
  }, []);

  const getToken = useCallback(async (): Promise<string | null> => {
    const token = await getValidCognitoIdToken();
    if (token) return token;
    return null;
  }, []);

  const signIn = useCallback(async (email: string, pass: string) => {
    setError(null);
    try {
      const newSession = await signInCognito(email, pass);
      setSession(newSession);
    } catch (err: any) {
      setError(err.message || 'Failed to sign in with AWS Cognito');
      throw err;
    }
  }, []);

  const signInDemo = useCallback(async () => {
    setError(null);
    try {
      const newSession = await signInCognito(
        COGNITO_CONFIG.demoUser.email,
        COGNITO_CONFIG.demoUser.password
      );
      setSession(newSession);
    } catch (err: any) {
      setError(err.message || 'Failed to sign in as demo user');
      throw err;
    }
  }, []);

  const signUp = useCallback(async (email: string, pass: string) => {
    setError(null);
    try {
      const res = await signUpCognito(email, pass);
      return res;
    } catch (err: any) {
      setError(err.message || 'Failed to create AWS Cognito account');
      throw err;
    }
  }, []);

  const confirmSignUp = useCallback(async (email: string, code: string) => {
    setError(null);
    try {
      await confirmSignUpCognito(email, code);
    } catch (err: any) {
      setError(err.message || 'Failed to verify confirmation code');
      throw err;
    }
  }, []);

  const signOut = useCallback(() => {
    clearCognitoSession();
    setSession(null);
    setError(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: CognitoAuthContextType = {
    isSignedIn: Boolean(session && session.idToken),
    isLoaded,
    userId: session?.sub || null,
    userEmail: session?.email || null,
    session,
    getToken,
    signIn,
    signUp,
    confirmSignUp,
    signOut,
    signInDemo,
    error,
    clearError,
  };

  return (
    <CognitoAuthContext.Provider value={value}>
      {children}
    </CognitoAuthContext.Provider>
  );
}

export function useCognitoAuth(): CognitoAuthContextType {
  const context = useContext(CognitoAuthContext);
  if (!context) {
    throw new Error('useCognitoAuth must be used within a CognitoAuthProvider');
  }
  return context;
}
