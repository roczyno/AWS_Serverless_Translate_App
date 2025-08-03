import React, { useState } from "react";
import { FileUpload } from "../upload/FileUpload";
import { TranslationList } from "../translations/TranslationList";

export const Dashboard: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadComplete = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Document Translation
          </h1>
          <p className="text-gray-600 mt-2">
            Upload your documents and translate them into multiple languages
            using AWS Translate
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <FileUpload onUploadComplete={handleUploadComplete} />
          <TranslationList refresh={refreshKey > 0} />
        </div>
      </main>
    </div>
  );
};
