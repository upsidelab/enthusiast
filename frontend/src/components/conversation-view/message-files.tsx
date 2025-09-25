import { FileText, Image, File } from 'lucide-react';
import { MessageFile } from './conversation';

interface MessageFilesProps {
  files: MessageFile[];
  compact?: boolean;
}

const getFileIcon = (contentType: string) => {
  if (contentType.startsWith('image/')) {
    return <Image className="h-5 w-5" />;
  }
  if (contentType.includes('pdf') || contentType.includes('text')) {
    return <FileText className="h-5 w-5" />;
  }
  return <File className="h-5 w-5" />;
};


export function MessageFiles({ files, compact = false }: MessageFilesProps) {
  if (!files || files.length === 0) return null;

  return (
    <div className="w-full">
      {files.map((file) => (
        <div
          key={file.filename}
          className={`w-full flex items-center space-x-2 rounded-md border bg-blue-50 border-blue-200 text-blue-900 shadow-sm ${
            compact ? "px-2 py-1" : "px-3 py-2"
          }`}
        >
          <div className="flex-shrink-0">
            {getFileIcon(file.content_type)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">
              {file.filename}
            </div>
            <div className="text-xs opacity-60">
              {file.content_type}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
