import { X, FileText, Image, File } from 'lucide-react';
import { Button } from '@/components/ui/button';

import type { UploadedFile } from './file-upload';

export type HandleFileRemove = (fileId: string) => void;

interface FileListProps {
  uploadedFiles: UploadedFile[];
  handleFileRemove: HandleFileRemove;
  disabled?: boolean;
}

const getFileIcon = (file: File) => {
  if (file.type.startsWith('image/')) {
    return <Image className="h-4 w-4" />;
  }
  if (file.type.includes('pdf') || file.type.includes('text')) {
    return <FileText className="h-4 w-4" />;
  }
  return <File className="h-4 w-4" />;
};

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const fileStatus = (file: UploadedFile) => {
  if (file.uploaded) {
    return 'Ready';
  }
  if (file.uploading) {
    return 'Uploading...';
  }
  if (file.uploadError) {
    return 'Upload failed';
  }

  return '';
};

export function FileList({
  uploadedFiles,
  handleFileRemove,
  disabled = false,
}: FileListProps) {
  return (
    <div className="flex w-full gap-2 flex-wrap">
      {uploadedFiles.length > 0 && uploadedFiles.map((uploadedFile) => (
        <div
          key={uploadedFile.id}
          className="flex items-center justify-between px-3 py-2 bg-gray-50 rounded-lg border w-[260px]"
        >
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            {uploadedFile.preview ? (
              <img
                src={uploadedFile.preview}
                alt={uploadedFile.file.name}
                className="h-8 w-8 object-cover rounded"
              />
            ) : (
              <div className="h-8 w-8 bg-gray-200 rounded flex items-center justify-center">
                {getFileIcon(uploadedFile.file)}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className={`text-sm font-medium truncate ${uploadedFile.uploadError ? 'text-red-600' : 'text-gray-900'}`}>
                {uploadedFile.file.name}
              </div>
              <div className="text-xs text-gray-500">
                {formatFileSize(uploadedFile.file.size)} • {fileStatus(uploadedFile)}
              </div>
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleFileRemove(uploadedFile.id)}
            disabled={disabled || uploadedFile.uploading}
            className="h-8 w-8 p-0 hover:bg-red-100 hover:text-red-600 ml-2"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}
