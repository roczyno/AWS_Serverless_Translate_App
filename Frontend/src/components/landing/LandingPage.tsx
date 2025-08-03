import React from "react";
import { Link } from "react-router-dom";

const features = [
  "Translate documents instantly",
  "Supports multiple languages",
  "Secure and private",
  "Easy file uploads",
  "Track translation progress",
];

export const LandingPage: React.FC = () => (
  <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 to-white">
    <header className="py-6 shadow-sm bg-white">
      <div className="max-w-7xl mx-auto px-4 flex items-center">
        <span className="text-2xl font-bold text-blue-700 flex items-center">
          <svg
            className="h-8 w-8 mr-2 text-blue-600"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 20l9 2-7-7 7-7-9 2-2 9z"
            />
          </svg>
          TranslateDoc
        </span>
      </div>
    </header>
    <main className="flex-1 flex flex-col items-center justify-center text-center px-4">
      <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-4 mt-8">
        Effortless Document Translation
      </h1>
      <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
        Instantly translate your documents to multiple languages with just a few
        clicks. Fast, secure, and easy to use.
      </p>
      <Link
        to="/auth"
        className="inline-block px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 transition mb-10 text-lg"
      >
        Get Started
      </Link>
      <div className="max-w-3xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-6 mb-16">
        {features.map((feature, idx) => (
          <div key={idx} className="flex items-center space-x-3">
            <span className="inline-block h-6 w-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
              <svg
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </span>
            <span className="text-gray-700 text-base">{feature}</span>
          </div>
        ))}
      </div>
    </main>
    <footer className="py-6 bg-white border-t text-gray-500 text-sm text-center">
      &copy; {new Date().getFullYear()} TranslateDoc. All rights reserved.
    </footer>
  </div>
);

export default LandingPage;
