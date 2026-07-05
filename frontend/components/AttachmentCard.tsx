type AttachmentCardProps = {
  filename: string
  file_type: "document" | "image"
  preview?: string
}

export default function AttachmentCard({ filename, file_type, preview }: AttachmentCardProps) {
  return (
    <div className="flex items-center gap-3 bg-primary text-primary-foreground rounded-2xl rounded-br-sm px-4 py-3 max-w-[60%]">
      {file_type === "image" && preview ? (
        <img
          src={`data:image/jpeg;base64,${preview}`}
          alt={filename}
          className="w-12 h-12 rounded-lg object-cover flex-shrink-0"
        />
      ) : (
        <div className="w-10 h-10 rounded-lg bg-primary-foreground/20 flex items-center justify-center flex-shrink-0 text-xl">
          {file_type === "document" ? "📄" : "🖼️"}
        </div>
      )}
      <div className="min-w-0">
        <p className="text-sm font-medium truncate">{filename}</p>
        <p className="text-xs opacity-70">
          {file_type === "document" ? "Document" : "Image"} uploaded
        </p>
      </div>
    </div>
  )
}