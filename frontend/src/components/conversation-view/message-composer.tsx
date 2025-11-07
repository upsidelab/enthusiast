import { ChangeEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import './message-composer.css';
import { ApiClient } from "@/lib/api.ts";
import { cn } from '@/lib/utils';
import { authenticationProviderInstance } from "@/lib/authentication-provider";
import { Loader, Send } from "lucide-react";
import { Textarea } from "@/components/ui/textarea.tsx";
import { Button } from "@/components/ui/button.tsx";
import { FileUpload, UploadedFile } from "./file-upload";
import { FileList } from "./file-list";

import type { HandleFileRemove } from "./file-list";

export interface MessageFile {
  id: number;
  name: string;
  type: string;
}
export interface Message {
  text: string;
  files: MessageFile[];
}
export type OnSubmit = (message: Message, createdConversationId?: number) => void;

export interface MessageComposerProps {
  onSubmit: OnSubmit;
  isLoading: boolean;
  conversationLocked?: boolean;
  conversationId?: number;
  agentId?: number;
  fileUploadEnabled?: boolean;
}

const maxHeight = 300;
const api = new ApiClient(authenticationProviderInstance);

export function MessageComposer({ onSubmit, isLoading, conversationLocked = false, conversationId, agentId, fileUploadEnabled }: MessageComposerProps) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [showUploadArea, setShowUploadArea] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const createdConversationIdRef = useRef<number | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const inputLength = input.trim().length;

  useEffect(() => {
    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();

      if (!fileUploadEnabled || isLoading || conversationLocked || showUploadArea) {
        return;
      }

      setShowUploadArea(true);
    };

    const handleDragEnd = () => {
      setShowUploadArea(false);
    };

    const handleDragLeave = (e: DragEvent) => {
      e.preventDefault();

      if (e.relatedTarget && e.relatedTarget !== document.documentElement) {
        return;
      }

      handleDragEnd();
    };

    document.body.addEventListener("dragover", handleDragOver);
    document.body.addEventListener("dragleave", handleDragLeave);
    document.body.addEventListener("dragend", handleDragEnd);
    window.addEventListener("blur", handleDragEnd);

    return () => {
      document.body.removeEventListener("dragover", handleDragOver);
      document.body.removeEventListener("dragleave", handleDragLeave);
      document.body.removeEventListener("dragend", handleDragEnd);
      window.removeEventListener("blur", handleDragEnd);
    };
  }, [fileUploadEnabled, isLoading, conversationLocked, showUploadArea]);

  const resizeTextArea = (element: HTMLTextAreaElement) => {
    if (!element) {
      return;
    }

    element.style.height = '0px';
    element.style.height = `${Math.min(element.scrollHeight, maxHeight)}px`;
  }

  const uploadFile = async (file: File, conversationId: number): Promise<string> => {
    const uploadResponse = await api.conversations().uploadFile(conversationId, file);
    return uploadResponse.task_id;
  };

  const pollUploadStatus = async (taskId: string): Promise<number> => {
    const maxAttempts = 30;
    let attempts = 0;

    while (attempts < maxAttempts) {
      const statusData = await api.conversations().getFileUploadStatus(taskId);

      if (statusData.status === 'SUCCESS') {
        return statusData.result!.file_id!;
      } else if (statusData.status === 'FAILURE') {
        throw new Error(statusData.result?.error || 'Upload failed');
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }

    throw new Error('Upload timeout - please try again');
  };

  const resetComposer = () => {
    setInput("");
    setUploadedFiles([]);
    setShowUploadArea(false);
    setUploadError(null);
    createdConversationIdRef.current = null;
    
    setTimeout(() => {
      resizeTextArea(inputRef.current!);
    });
  };
  const submitMessage = async () => {
    if (inputLength === 0) return;

    const allFilesReady = uploadedFiles.every(f => f.uploaded && f.fileId);
    const hasUploadingFiles = uploadedFiles.some(f => f.uploading);
    const hasErrors = uploadedFiles.some(f => f.uploadError);

    if (uploadedFiles.length > 0 && !allFilesReady) {
      if (hasUploadingFiles) {
        setUploadError('Please wait for all files to finish uploading.');
      } else if (hasErrors) {
        setUploadError('Please fix upload errors before sending.');
      }
      return;
    }

    if (!uploadedFiles.length) {
      onSubmit({ text: input, files: [] }, createdConversationIdRef.current || undefined);
      resetComposer();
      return;
    }

    try {
      setUploadingFiles(true);
      
      const message = {
        text: input,
        files: uploadedFiles.filter(f => f.uploaded && f.fileId).map(f => ({
          id: f.fileId!,
          name: f.file.name,
          type: f.file.name.includes('.') ? f.file.name.split('.').pop() : '',
        }))
      } as Message;

      onSubmit(message, createdConversationIdRef.current || undefined);
      resetComposer();
    } catch {
      setUploadError('Failed to send message. Please try again.');
    } finally {
      setUploadingFiles(false);
    }
  }

  const handleTextAreaInput = (event: ChangeEvent<HTMLTextAreaElement>) => {
    setInput(event.target.value);
    resizeTextArea(event.target);
  }

  const handleTextAreaKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.shiftKey || event.key !== 'Enter')
      return;

    event.preventDefault();
    submitMessage();
  }

const handleFilesChange = async (files: UploadedFile[]) => {
  setUploadedFiles(files.map(f => ({ ...f, uploading: true, uploadError: undefined })));
  let currentConversationId = conversationId || createdConversationIdRef.current;

  if (!currentConversationId && agentId) {
    currentConversationId = await api.conversations().createConversation(agentId);
    createdConversationIdRef.current = currentConversationId;
  }

  if (!currentConversationId) {
    throw new Error('No conversation ID available for file upload');
  }
  const uploadPromises = files.map(async file => {
    try {
      const taskId = await uploadFile(file.file, currentConversationId);

      setUploadedFiles(prev => prev.map(f =>
        f.id === file.id ? { ...f, taskId, uploading: true } : f
      ));

      const fileId = await pollUploadStatus(taskId);

      setUploadedFiles(prev => prev.map(f =>
        f.id === file.id ? { ...f, uploaded: true, fileId, uploading: false } : f
      ));
    } catch {
      setUploadedFiles(prev => prev.map(f =>
        f.id === file.id ? { ...f, uploading: false, uploadError: 'Upload failed' } : f
      ));
    }
  });

  await Promise.all(uploadPromises);
};

  const handleFileRemove: HandleFileRemove = (fileId) => {
    setUploadedFiles(prev => {
      const newFiles = prev.filter(f => f.id !== fileId);
      if (newFiles.length === 0) {
        setShowUploadArea(false);
      }
      return newFiles;
    });
    setUploadError(null);
  };

  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  return (
    <div className="space-y-3">
      {uploadError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="text-sm text-red-600">{uploadError}</div>
        </div>
      )}

      <FileList
        uploadedFiles={uploadedFiles}
        handleFileRemove={handleFileRemove}
        disabled={isLoading || uploadingFiles || conversationLocked}
      />

      <form
        onSubmit={(event) => {
          event.preventDefault();
          submitMessage();
        }}
        className="flex w-full items-center space-x-2 relative"
      >
        <div className={cn("relative flex-1 rounded-md border bg-white", showUploadArea && 'border-dashed')}>
          {fileUploadEnabled && (
            <FileUpload
              onFilesChange={handleFilesChange}
              uploadedFiles={uploadedFiles}
              disabled={isLoading || uploadingFiles || conversationLocked}
              onClose={() => setShowUploadArea(false)}
              showUploadArea={showUploadArea}
              onUploadError={setUploadError}
            />
          )}
          <Textarea
            id="message"
            ref={inputRef}
            placeholder={conversationLocked ? "This agent is no longer available." : "Type your message..."}
            className="w-full resize-none border-0 focus-visible:ring-0 focus-visible:outline-none shadow-none pt-3"
            autoComplete="off"
            value={input}
            onChange={handleTextAreaInput}
            onKeyDown={handleTextAreaKeyDown}
            disabled={isLoading || uploadingFiles || conversationLocked}
          />
          <div className="flex">
            <Button
              type="submit"
              size="icon"
              className="ml-auto mr-2 mb-2"
              disabled={
                isLoading || 
                uploadingFiles || 
                inputLength === 0 || 
                conversationLocked ||
                uploadedFiles.some(f => f.uploading || f.uploadError)
              }
            >
              {isLoading || uploadingFiles ? (
                <Loader className="h-4 w-4 animate-spin text-gray-500" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              <span className="sr-only">Send</span>
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
