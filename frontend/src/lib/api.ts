import axios, { AxiosError } from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
});

export class ApiError extends Error {
  status: number;
  detail?: string;

  constructor(message: string, status: number, detail?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  subscription?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string | null;
  token_type: "bearer" | string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export interface UpdateProfilePayload {
  firstName: string;
  lastName: string;
  email: string;
}

export interface DurationOption {
  code: "weekly" | "monthly" | "annual";
  name: string;
  price: number;
  currency: string;
  duration_days: number;
}

export interface SubscriptionPlan {
  code: "free" | "premium";
  name: string;
  quota: number;
  features: string[];
  duration_options: DurationOption[];
}

function mapAxiosError(error: unknown): ApiError {
  if (!(error instanceof AxiosError)) {
    return new ApiError("Terjadi kesalahan yang tidak terduga.", 500);
  }

  const status = error.response?.status ?? 500;
  const detail =
    typeof error.response?.data?.detail === "string"
      ? error.response.data.detail
      : undefined;

  return new ApiError(detail ?? error.message, status, detail);
}

export const backendAuthApi = {
  async login(payload: LoginPayload): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>(
        "/auth/login",
        payload,
      );
      return response.data;
    } catch (error) {
      throw mapAxiosError(error);
    }
  },

  async register(payload: RegisterPayload): Promise<TokenResponse> {
    try {
      const response = await apiClient.post<TokenResponse>(
        "/auth/register",
        payload,
      );
      return response.data;
    } catch (error) {
      throw mapAxiosError(error);
    }
  },

  async me(accessToken: string): Promise<AuthUser> {
    try {
      const response = await apiClient.get<AuthUser>("/auth/me", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      return response.data;
    } catch (error) {
      throw mapAxiosError(error);
    }
  },

  async updateProfile(
    accessToken: string,
    payload: UpdateProfilePayload
  ): Promise<AuthUser> {
    try {
      const response = await apiClient.put<AuthUser>(
        "/auth/me",
        payload,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );
      return response.data;
    } catch (error) {
      throw mapAxiosError(error);
    }
  },

  async logout(accessToken: string): Promise<void> {
    try {
      await apiClient.post(
        "/auth/logout",
        {},
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        },
      );
    } catch (error) {
      throw mapAxiosError(error);
    }
  },
};

export const backendSubscriptionApi = {
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    try {
      const response = await apiClient.get<SubscriptionPlan[]>(
        "/subscription/plans",
      );
      return response.data;
    } catch (error) {
      throw mapAxiosError(error);
    }
  },
};
