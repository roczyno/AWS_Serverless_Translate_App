export interface User {
  id: string;
  email: string;
  name: string;
}

export interface TranslationJob {
  id: string;
  user_id: string;
  file_name: string;
  original_text: string;
  translated_text?: string;
  source_language: string;
  target_language: string;
  status: "pending" | "processing" | "completed" | "failed";
  created_at: string;
  completed_at?: string;
  s3_input_key: string;
  s3_output_key?: string;
  download_url?: string;
}

export interface Language {
  code: string;
  name: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
