import React, { createContext, useContext, useReducer, useEffect } from "react";
import { AuthState, User } from "../types";
import { Amplify } from "aws-amplify";
import {
  signIn,
  signUp,
  signOut,
  getCurrentUser,
  confirmSignUp,
  resendSignUpCode,
} from "aws-amplify/auth";

// Debug environment variables
console.log("Environment variables:");
console.log(
  "VITE_COGNITO_USER_POOL_ID:",
  import.meta.env.VITE_COGNITO_USER_POOL_ID
);
console.log("VITE_COGNITO_CLIENT_ID:", import.meta.env.VITE_COGNITO_CLIENT_ID);
console.log("VITE_COGNITO_DOMAIN:", import.meta.env.VITE_COGNITO_DOMAIN);

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
      loginWith: {
        oauth: {
          domain: import.meta.env.VITE_COGNITO_DOMAIN,
          scopes: ["email", "openid", "profile"],
          redirectSignIn: [window.location.origin + "/dashboard"],
          redirectSignOut: [window.location.origin + "/auth"],
          responseType: "code",
        },
      },
    },
  },
});

interface AuthContextType extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  confirmEmail: (email: string, code: string) => Promise<void>;
  resendConfirmationCode: (email: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

type AuthAction =
  | { type: "LOGIN_START" }
  | { type: "LOGIN_SUCCESS"; user: User }
  | { type: "LOGIN_FAILURE" }
  | { type: "LOGOUT" }
  | { type: "SET_LOADING"; isLoading: boolean };

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case "LOGIN_START":
      return { ...state, isLoading: true };
    case "LOGIN_SUCCESS":
      return { user: action.user, isAuthenticated: true, isLoading: false };
    case "LOGIN_FAILURE":
      return { user: null, isAuthenticated: false, isLoading: false };
    case "LOGOUT":
      return { user: null, isAuthenticated: false, isLoading: false };
    case "SET_LOADING":
      return { ...state, isLoading: action.isLoading };
    default:
      return state;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
    isLoading: false,
  });

  useEffect(() => {
    // Check for existing session
    const checkUser = async () => {
      try {
        const cognitoUser = await getCurrentUser();
        const user: User = {
          id: cognitoUser.username,
          email: cognitoUser.userId,
          name: cognitoUser.username,
        };
        dispatch({ type: "LOGIN_SUCCESS", user });
      } catch {
        // Not signed in
      }
    };
    checkUser();
  }, []);

  const login = async (email: string, password: string) => {
    dispatch({ type: "LOGIN_START" });
    try {
      console.log("Attempting to sign in user:", email);
      // Use email as username since it's configured as alias
      await signIn({ username: email, password });
      const currentUser = await getCurrentUser();
      console.log("Sign in successful, current user:", currentUser);
      const user: User = {
        id: currentUser.userId,
        email: email,
        name: email,
      };
      localStorage.setItem("user", JSON.stringify(user));
      dispatch({ type: "LOGIN_SUCCESS", user });
    } catch (error) {
      console.error("Login error details:", error);
      if (error instanceof Error) {
        console.error("Error name:", error.name);
        console.error("Error message:", error.message);
        console.error("Error code:", (error as { code?: string }).code);

        // Provide more specific error messages
        if (error.name === "NotAuthorizedException") {
          throw new Error(
            "Invalid email or password. Please check your credentials."
          );
        } else if (error.name === "UserNotConfirmedException") {
          throw new Error(
            "Please check your email and confirm your account before logging in."
          );
        } else if (error.name === "UserNotFoundException") {
          throw new Error("User not found. Please check your email address.");
        }
      }
      dispatch({ type: "LOGIN_FAILURE" });
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    dispatch({ type: "SET_LOADING", isLoading: true });
    try {
      console.log("Attempting to register user:", { email, name });
      // Use email as username since it's configured as username attribute
      const result = await signUp({
        username: email,
        password,
        options: {
          userAttributes: { name },
        },
      });
      console.log("Registration successful:", result);
      console.log("You can login with your email:", email);
      dispatch({ type: "SET_LOADING", isLoading: false });
    } catch (error) {
      console.error("Registration error details:", error);
      if (error instanceof Error) {
        console.error("Error name:", error.name);
        console.error("Error message:", error.message);
        console.error("Error code:", (error as { code?: string }).code);
      }
      dispatch({ type: "LOGIN_FAILURE" });
      throw error;
    }
  };

  const confirmEmail = async (email: string, code: string) => {
    dispatch({ type: "SET_LOADING", isLoading: true });
    try {
      console.log("Confirming email for:", email);
      await confirmSignUp({ username: email, confirmationCode: code });
      console.log("Email confirmation successful");
      dispatch({ type: "SET_LOADING", isLoading: false });
    } catch (error) {
      console.error("Email confirmation error:", error);
      if (error instanceof Error) {
        console.error("Error name:", error.name);
        console.error("Error message:", error.message);
      }
      dispatch({ type: "SET_LOADING", isLoading: false });
      throw error;
    }
  };

  const resendConfirmationCode = async (email: string) => {
    dispatch({ type: "SET_LOADING", isLoading: true });
    try {
      console.log("Resending confirmation code for:", email);
      await resendSignUpCode({ username: email });
      console.log("Confirmation code resent successfully");
      dispatch({ type: "SET_LOADING", isLoading: false });
    } catch (error) {
      console.error("Resend confirmation code error:", error);
      if (error instanceof Error) {
        console.error("Error name:", error.name);
        console.error("Error message:", error.message);
      }
      dispatch({ type: "SET_LOADING", isLoading: false });
      throw error;
    }
  };

  const logout = async () => {
    await signOut();
    localStorage.removeItem("user");
    dispatch({ type: "LOGOUT" });
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        confirmEmail,
        resendConfirmationCode,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
