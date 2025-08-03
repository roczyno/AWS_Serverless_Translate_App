import React, { useState } from "react";
import { Languages, Globe2 } from "lucide-react";
import { LoginForm } from "./LoginForm";
import { RegisterForm } from "./RegisterForm";
import ConfirmForm from "./ConfirmForm";

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);
  const [confirmEmail, setConfirmEmail] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full grid grid-cols-1 lg:grid-cols-2 gap-8 bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Left side - Hero/Branding */}
        <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-8 flex items-center justify-center">
          <div className="text-center text-white">
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-4">
                <Languages className="w-8 h-8" />
              </div>
              <h1 className="text-3xl font-bold mb-2">TranslateDoc</h1>
              <p className="text-blue-100">
                Professional document translation powered by AWS
              </p>
            </div>

            <div className="space-y-4">
              <div className="flex items-center text-blue-100">
                <Globe2 className="w-5 h-5 mr-3" />
                <span>Support for 50+ languages</span>
              </div>
              <div className="flex items-center text-blue-100">
                <Languages className="w-5 h-5 mr-3" />
                <span>AI-powered translation</span>
              </div>
              <div className="flex items-center text-blue-100">
                <Globe2 className="w-5 h-5 mr-3" />
                <span>Secure cloud storage</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right side - Auth Form */}
        <div className="p-8 flex items-center justify-center">
          {showConfirm ? (
            <ConfirmForm
              email={confirmEmail}
              onSuccess={() => {
                setShowConfirm(false);
                setIsLogin(true);
              }}
              onBack={() => {
                setShowConfirm(false);
                setIsLogin(true);
              }}
            />
          ) : isLogin ? (
            <LoginForm onToggleForm={() => setIsLogin(false)} />
          ) : (
            <RegisterForm
              onToggleForm={() => setIsLogin(true)}
              onRegistrationSuccess={(email: string) => {
                setConfirmEmail(email);
                setShowConfirm(true);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
