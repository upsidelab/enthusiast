import { useCallback, useState } from 'react';
import { useDropzone, FileRejection } from 'react-dropzone';
import { Upload, X, FileText, Image, File } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { useSupportedFileExtensions } from '@/lib/use-supported-file-extensions';

export interface UploadedFile {
  id: string;
  file: File;
  preview?: string;
  uploading?: boolean;
  uploaded?: boolean;
  fileId?: number;
  taskId?: string;
  uploadError?: string;
}

interface FileUploadProps {
  onFilesChange: (files: UploadedFile[]) => void;
  onFileRemove: (fileId: string) => void;
  uploadedFiles: UploadedFile[];
  disabled?: boolean;
  onClose?: () => void;
  showUploadArea?: boolean;
  onUploadError?: (error: string) => void;
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

export function FileUpload({
  onFilesChange,
  onFileRemove,
  uploadedFiles,
  disabled = false,
  onClose,
  showUploadArea = true,
  onUploadError,
}: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const { supportedExtensions, isLoading: isLoadingExtensions } = useSupportedFileExtensions();

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
    if (disabled) return;

        if (rejectedFiles.length > 0) {
          const errors = rejectedFiles.map(({ file, errors }) => ({
            file: file.name,
            errors: errors.map((e: { message: string }) => e.message),
          }));
      
      if (onUploadError) {
        const errorMessages = errors.map(({ file, errors }) => 
          `${file}: ${errors.join(', ')}`
        ).join('; ');
        onUploadError(errorMessages);
      }
    }

    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
    }));

    onFilesChange([...uploadedFiles, ...newFiles]);
  }, [uploadedFiles, onFilesChange, disabled, onUploadError]);

  const acceptObject = supportedExtensions.reduce((acc, ext) => {
    if (ext === '.txt') acc['text/plain'] = [];
    else if (ext === '.pdf') acc['application/pdf'] = [];
    else if (ext === '.jpg' || ext === '.jpeg') acc['image/jpeg'] = [];
    else if (ext === '.png') acc['image/png'] = [];
    return acc;
  }, {} as Record<string, string[]>);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: disabled || isLoadingExtensions,
    accept: isLoadingExtensions ? undefined : acceptObject,
  });


  return (
    <div className="space-y-3">
      {showUploadArea && (
        <div className="relative">
          {onClose && (
            <button
              onClick={onClose}
              className="absolute top-2 right-2 z-10 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              type="button"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          
          <div
            {...getRootProps()}
            className={cn(
              "relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer",
              "hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
              isDragActive && "border-blue-500 bg-blue-50",
              disabled && "opacity-50 cursor-not-allowed",
              dragActive && "border-blue-500 bg-blue-50"
            )}
            onDragEnter={() => setDragActive(true)}
            onDragLeave={() => setDragActive(false)}
          >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
          <div className="text-sm text-gray-600">
            <span className="font-medium text-blue-600 hover:text-blue-500">
              Click to upload
            </span>{' '}
            or drag and drop
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {isLoadingExtensions ? (
              'Loading supported file types...'
            ) : (
              `Supported types: ${supportedExtensions.join(', ')}`
            )}
          </div>
          </div>
        </div>
      )}

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">Selected Files:</div>
          {uploadedFiles.map((uploadedFile) => (
            <div
              key={uploadedFile.id}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border"
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
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {uploadedFile.file.name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatFileSize(uploadedFile.file.size)}
                    {uploadedFile.uploading && ' • Uploading...'}
                    {uploadedFile.uploaded && ' • Ready'}
                    {uploadedFile.uploadError && ' • Error'}
                  </div>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onFileRemove(uploadedFile.id)}
                disabled={disabled || uploadedFile.uploading}
                className="h-8 w-8 p-0 hover:bg-red-100 hover:text-red-600"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
