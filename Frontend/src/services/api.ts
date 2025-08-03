import { TranslationJob, Language } from "../types";
import { fetchAuthSession } from "aws-amplify/auth";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// Helper function to get auth headers
const getAuthHeaders = async () => {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    return {
      Authorization: token ? `Bearer ${token}` : "",
      "Content-Type": "application/json",
    };
  } catch (error) {
    console.error("Error getting auth token:", error);
    return {
      Authorization: "",
      "Content-Type": "application/json",
    };
  }
};

export const apiService = {
  getLanguages: async (): Promise<Language[]> => {
    const res = await fetch(`${API_BASE_URL}/languages`);
    if (!res.ok) throw new Error("Failed to fetch languages");
    return res.json();
  },

  uploadDocument: async (
    file: File,
    sourceLanguage: string,
    targetLanguage: string
  ): Promise<TranslationJob> => {
    console.log("=== UPLOAD DOCUMENT START ===");
    console.log("File details:", {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
    });
    console.log("Languages:", { sourceLanguage, targetLanguage });

    // Read file content based on file type
    let fileContent: string;
    if (
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")
    ) {
      console.log("PDF file detected, converting to base64...");
      // For PDF files, convert to base64
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      fileContent = btoa(String.fromCharCode(...uint8Array));
      console.log("PDF converted to base64, length:", fileContent.length);
    } else {
      // For text files, read as text
      fileContent = await file.text();
      console.log("Text file content length:", fileContent.length);
      console.log(
        "File content preview:",
        fileContent.substring(0, 200) + "..."
      );
    }

    const authHeaders = await getAuthHeaders();
    console.log("Auth headers:", authHeaders);

    const requestBody = {
      fileName: file.name,
      sourceLanguage,
      targetLanguage,
      fileContent,
      fileType: file.type,
    };
    console.log("Request body keys:", Object.keys(requestBody));
    console.log("Request body size:", JSON.stringify(requestBody).length);

    const res = await fetch(`${API_BASE_URL}/translations`, {
      method: "POST",
      headers: {
        ...authHeaders,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });

    console.log("Response status:", res.status);
    console.log("Response headers:", Object.fromEntries(res.headers.entries()));

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Response error body:", errorText);
      throw new Error(
        `Failed to upload document: ${res.status} - ${errorText}`
      );
    }

    const responseData = await res.json();
    console.log("Response data:", responseData);
    console.log("=== UPLOAD DOCUMENT SUCCESS ===");
    return responseData;
  },

  getTranslations: async (): Promise<TranslationJob[]> => {
    const authHeaders = await getAuthHeaders();

    const res = await fetch(`${API_BASE_URL}/translations`, {
      headers: authHeaders,
    });
    if (!res.ok) throw new Error("Failed to fetch translations");
    return res.json();
  },

  getTranslation: async (jobId: string): Promise<TranslationJob | null> => {
    const authHeaders = await getAuthHeaders();

    const res = await fetch(`${API_BASE_URL}/translations/${jobId}`, {
      headers: authHeaders,
    });
    if (!res.ok) throw new Error("Failed to fetch translation");
    return res.json();
  },

  downloadTranslation: async (jobId: string): Promise<Blob> => {
    const authHeaders = await getAuthHeaders();

    const res = await fetch(`${API_BASE_URL}/translations/${jobId}/download`, {
      headers: authHeaders,
    });
    if (!res.ok) throw new Error("Failed to download translation");
    return res.blob();
  },
};
