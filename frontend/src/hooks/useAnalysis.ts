"use client";

import { useState } from "react";
import { ParsedFileData } from "@/lib/file-parser";

export interface AnalysisState {
  mode: "upload" | "text";
  file: File | null;
  parsedData: ParsedFileData | null;
  textInput: string;
  loading: boolean;
  error: string | null;
}

export function useAnalysis() {
  const [state, setState] = useState<AnalysisState>({
    mode: "upload",
    file: null,
    parsedData: null,
    textInput: "",
    loading: false,
    error: null,
  });

  const setFile = (file: File | null) => {
    setState((prev) => ({
      ...prev,
      file,
      error: null,
    }));
  };

  const setParsedData = (data: ParsedFileData | null) => {
    setState((prev) => ({
      ...prev,
      parsedData: data,
    }));
  };

  const setTextInput = (text: string) => {
    setState((prev) => ({
      ...prev,
      textInput: text,
    }));
  };

  const setMode = (mode: "upload" | "text") => {
    setState((prev) => ({
      ...prev,
      mode,
      error: null,
    }));
  };

  const setLoading = (loading: boolean) => {
    setState((prev) => ({
      ...prev,
      loading,
    }));
  };

  const setError = (error: string | null) => {
    setState((prev) => ({
      ...prev,
      error,
    }));
  };

  const reset = () => {
    setState({
      mode: "upload",
      file: null,
      parsedData: null,
      textInput: "",
      loading: false,
      error: null,
    });
  };

  return {
    state,
    setFile,
    setParsedData,
    setTextInput,
    setMode,
    setLoading,
    setError,
    reset,
  };
}
