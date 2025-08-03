import React, { useState, useEffect, useRef } from "react";
import {
  FileText,
  Download,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { TranslationJob } from "../../types";
import { apiService } from "../../services/api";
import { useAuth } from "../../contexts/AuthContext";

interface TranslationListProps {
  refresh: boolean;
}

export const TranslationList: React.FC<TranslationListProps> = ({
  refresh,
}) => {
  const [translations, setTranslations] = useState<TranslationJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const { user } = useAuth();
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const loadTranslations = async (showLoading = true) => {
    if (!user) return;

    try {
      if (showLoading) {
        setLoading(true);
      } else {
        setRefreshing(true);
      }
      const data = await apiService.getTranslations();
      console.log("Translation data received:", data);
      if (data.length > 0) {
        console.log("First translation job:", data[0]);
        console.log("Available fields:", Object.keys(data[0]));
      }
      setTranslations(data);
    } catch (error) {
      console.error("Failed to load translations:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleManualRefresh = () => {
    loadTranslations(false);
  };

  // Check if there are any jobs that need polling (pending or processing)
  const hasActiveJobs = translations.some(
    (job) => job.status === "pending" || job.status === "processing"
  );

  // Set up polling for active jobs
  useEffect(() => {
    if (hasActiveJobs && user) {
      // Poll every 3 seconds for active jobs
      pollingIntervalRef.current = setInterval(() => {
        console.log("Polling for translation updates...");
        loadTranslations();
      }, 3000);

      return () => {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current);
          pollingIntervalRef.current = null;
        }
      };
    } else {
      // Clear polling if no active jobs
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
        pollingIntervalRef.current = null;
      }
    }
  }, [hasActiveJobs, user]);

  useEffect(() => {
    loadTranslations();
  }, [user, refresh]);

  const handleDownload = async (jobId: string, fileName: string) => {
    try {
      // Find the job to get the download URL
      const job = translations.find((t) => t.id === jobId);

      if (job?.download_url) {
        // Use the pre-signed URL directly
        const link = document.createElement("a");
        link.href = job.download_url;
        link.download = `translated-${fileName}`;
        link.target = "_blank";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        // Fallback to API call
        const blob = await apiService.downloadTranslation(jobId);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `translated-${fileName}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error("Download failed:", error);
    }
  };

  const getStatusIcon = (status: TranslationJob["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "processing":
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <Clock className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: TranslationJob["status"]) => {
    switch (status) {
      case "completed":
        return "bg-green-100 text-green-800";
      case "failed":
        return "bg-red-100 text-red-800";
      case "processing":
        return "bg-blue-100 text-blue-800";
      default:
        return "bg-yellow-100 text-yellow-800";
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Translation History
        </h2>
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Translation History
        </h2>
        <div className="flex items-center space-x-3">
          {hasActiveJobs && (
            <div className="flex items-center space-x-2 text-sm text-blue-600">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Live updates active</span>
            </div>
          )}
          <button
            onClick={handleManualRefresh}
            disabled={refreshing}
            className="flex items-center space-x-1 px-3 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50"
          >
            <RefreshCw
              className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`}
            />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {translations.length === 0 ? (
        <div className="text-center py-8">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No translations yet</p>
          <p className="text-sm text-gray-400 mt-2">
            Upload a document to get started
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {translations.map((job) => (
            <div
              key={job.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-600" />
                  <div>
                    <h3 className="font-medium text-gray-900">
                      {job.file_name}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {job.source_language?.toUpperCase() || "Unknown"} →{" "}
                      {job.target_language?.toUpperCase() || "Unknown"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2">
                    {getStatusIcon(job.status)}
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        job.status
                      )}`}
                    >
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </div>

                  {job.status === "completed" && (
                    <button
                      onClick={() => handleDownload(job.id, job.file_name)}
                      className="flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md transition-colors"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-3 text-xs text-gray-500">
                Created: {new Date(job.created_at).toLocaleDateString()}
                {job.completed_at && (
                  <span className="ml-4">
                    Completed: {new Date(job.completed_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
