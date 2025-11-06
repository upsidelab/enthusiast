import { useCallback, useState } from 'react';
import { useDropzone, FileRejection } from 'react-dropzone';
import { Upload, Paperclip } from 'lucide-react';
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
  uploadedFiles: UploadedFile[];
  onClose: () => void;
  disabled?: boolean;
  showUploadArea?: boolean;
  onUploadError?: (error: string) => void;
}

export function FileUpload({
  onFilesChange,
  uploadedFiles,
  onClose,
  disabled = false,
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

    onClose();
    onFilesChange([...uploadedFiles, ...newFiles]);
  }, [uploadedFiles, onFilesChange, disabled, onUploadError, onClose]);

  const acceptObject = supportedExtensions.reduce((acc, ext) => {
    if (ext === '.txt') acc['text/plain'] = [];
    else if (ext === '.pdf') acc['application/pdf'] = [];
    else if (ext === '.jpg' || ext === '.jpeg') acc['image/jpeg'] = [];
    else if (ext === '.png') acc['image/png'] = [];
    return acc;
  }, {} as Record<string, string[]>);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    disabled: disabled || isLoadingExtensions,
    accept: isLoadingExtensions ? undefined : acceptObject,
  });

  return (<>
    <Button
      type="button"
      variant="ghost"
      size="icon"
      onClick={open}
      disabled={disabled}
      className="shrink-0 left-2 bottom-2 absolute"
    >
      <Paperclip className="h-4 w-4" />
      <span className="sr-only">Attach files</span>
    </Button>

    <input {...getInputProps()} />

    {showUploadArea && (
      <div className="space-y-3 absolute w-full h-full bg-white rounded-lg z-10">
        <div
          {...getRootProps()}
          className={cn(
            "relative h-full text-center flex flex-col justify-center transition-colors cursor-pointer",
            "hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
            isDragActive && "border-blue-500 bg-blue-50",
            disabled && "opacity-50 cursor-not-allowed",
            dragActive && "border-blue-500 bg-blue-50"
          )}
          onDragEnter={() => setDragActive(true)}
          onDragLeave={() => setDragActive(false)}
        >
        <Upload className="mx-auto h-6 w-6 text-gray-400 mb-2" />
        <div className="text-sm text-gray-600">Drag and drop files here</div>
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
  </>);
}
