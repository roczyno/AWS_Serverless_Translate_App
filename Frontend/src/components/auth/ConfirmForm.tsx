import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";

interface ConfirmFormProps {
  email: string;
  onSuccess: () => void;
  onBack: () => void;
}

const ConfirmForm: React.FC<ConfirmFormProps> = ({
  email,
  onSuccess,
  onBack,
}) => {
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const { confirmEmail, resendConfirmationCode } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await confirmEmail(email, code);
      onSuccess();
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to confirm email. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendCode = async () => {
    setError("");
    setIsLoading(true);

    try {
      await resendConfirmationCode(email);
      setError("Confirmation code resent! Check your email.");
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to resend code. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Confirm Your Email
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            We sent a confirmation code to{" "}
            <span className="font-medium text-indigo-600">{email}</span>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="code" className="sr-only">
              Confirmation Code
            </label>
            <input
              id="code"
              name="code"
              type="text"
              required
              className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Enter confirmation code"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Confirming..." : "Confirm Email"}
            </button>
          </div>

          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={onBack}
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              Back to Login
            </button>
            <button
              type="button"
              onClick={handleResendCode}
              disabled={isLoading}
              className="text-sm text-indigo-600 hover:text-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Resend Code
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ConfirmForm;
