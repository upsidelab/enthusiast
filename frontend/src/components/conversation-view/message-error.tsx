export interface MessageErrorProps {
  text: string;
}

export function MessageError({ text }: MessageErrorProps) {
  return (
    <div className="text-red-600 text-center">{text}</div>
  );
}
