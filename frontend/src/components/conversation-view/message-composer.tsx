import { Button } from "@/components/ui/button.tsx";
import { Loader, Send, Paperclip } from "lucide-react";
import { ChangeEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import './message-composer.css';
import { Textarea } from "@/components/ui/textarea.tsx";
import { FileUpload, UploadedFile } from "./file-upload";
import { ApiClient } from "@/lib/api.ts";
import { authenticationProviderInstance } from "@/lib/authentication-provider";

export interface MessageComposerProps {
  onSubmit: ((message: string, fileIds?: number[]) => void) | ((message: string, fileIds?: number[], createdConversationId?: number) => void);
  isLoading: boolean;
  conversationLocked?: boolean;
  conversationId?: number;
  agentId?: number;
}

const maxHeight = 300;
const api = new ApiClient(authenticationProviderInstance);

export function MessageComposer({ onSubmit, isLoading, conversationLocked = false, conversationId, agentId }: MessageComposerProps) {
  const [input, setInput] = useState("");
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [showUploadArea, setShowUploadArea] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [createdConversationId, setCreatedConversationId] = useState<number | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);
  const inputLength = input.trim().length;

  const resizeTextArea = (element: HTMLTextAreaElement) => {
    element.style.height = '0px';
    element.style.height = `${Math.min(element.scrollHeight, maxHeight)}px`;
  }

  const uploadFile = async (file: File): Promise<string> => {
    let currentConversationId = conversationId || createdConversationId;
    if (!currentConversationId && agentId) {
      currentConversationId = await api.conversations().createConversation(agentId);
      setCreatedConversationId(currentConversationId);
    }

    if (!currentConversationId) {
      throw new Error('No conversation ID available for file upload');
    }

    const uploadResponse = await api.conversations().uploadFile(currentConversationId, file);
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

    try {
      setUploadingFiles(true);
      
      const fileIds = uploadedFiles
        .filter(f => f.uploaded && f.fileId)
        .map(f => f.fileId!);

      if (createdConversationId) {
        onSubmit(input, fileIds, createdConversationId);
      } else {
        onSubmit(input, fileIds);
      }
      setInput("");
      setUploadedFiles([]);
      setShowUploadArea(false);
      setUploadError(null);
      setCreatedConversationId(null);
      
      setTimeout(() => {
        resizeTextArea(inputRef.current!);
      });
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
    setUploadedFiles(files);
    setUploadError(null);

    for (const file of files) {
      if (!file.uploading && !file.uploaded && !file.taskId) {
        try {
          setUploadedFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, uploading: true } : f
          ));

          const taskId = await uploadFile(file.file);
          
          setUploadedFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, taskId, uploading: false } : f
          ));

          const fileId = await pollUploadStatus(taskId);
          
          setUploadedFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, uploaded: true, fileId } : f
          ));
        } catch {
          setUploadedFiles(prev => prev.map(f => 
            f.id === file.id ? { 
              ...f, 
              uploading: false, 
              uploadError: 'Upload failed'
            } : f
          ));
        }
      }
    }
  };

  const handleFileRemove = (fileId: string) => {
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

      {(showUploadArea || uploadedFiles.length > 0) && (
        <div className="border rounded-lg p-4 bg-gray-50">
          <FileUpload
            onFilesChange={handleFilesChange}
            onFileRemove={handleFileRemove}
            uploadedFiles={uploadedFiles}
            disabled={isLoading || uploadingFiles || conversationLocked}
            onClose={() => setShowUploadArea(false)}
            showUploadArea={showUploadArea}
            onUploadError={setUploadError}
          />
        </div>
      )}

      {/* Message Input */}
      <form
        onSubmit={(event) => {
          event.preventDefault();
          submitMessage();
        }}
        className="flex w-full items-center space-x-2 relative"
      >
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={() => setShowUploadArea(!showUploadArea)}
          disabled={isLoading || conversationLocked}
          className="shrink-0"
        >
          <Paperclip className="h-4 w-4" />
          <span className="sr-only">Attach files</span>
        </Button>
        
        <div className="relative flex-1">
          <Textarea
            id="message"
            ref={inputRef}
            placeholder={conversationLocked ? "This agent is no longer available." : "Type your message..."}
            className="w-full resize-none"
            autoComplete="off"
            value={input}
            onChange={handleTextAreaInput}
            onKeyDown={handleTextAreaKeyDown}
            disabled={isLoading || uploadingFiles || conversationLocked}
          />
        </div>
        
        <Button 
          type="submit" 
          size="icon" 
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
      </form>
    </div>
  );
}
