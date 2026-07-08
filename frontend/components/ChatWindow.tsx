"use client";
import ReactMarkdown from "react-markdown";
import { useState, useRef, useEffect } from "react";
import { useWebSocket } from "@/hooks/useWebSocket";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import ConfirmAction from "@/components/ConfirmAction";
import AttachmentCard from "@/components/AttachmentCard";
import Link from "next/link";

type PendingFile = {
  file: File;
  type: "document" | "image";
  preview?: string;
};

type ChatWindowProps = {
  conversationId: string;
};

export default function ChatWindow({ conversationId }: ChatWindowProps) {
  const {
    messages,
    isConnected,
    isThinking,
    sendMessage,
    sendContext,
    sendConfirmation,
  } = useWebSocket(conversationId);
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [pendingFile, setPendingFile] = useState<PendingFile | null>(null);
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowAttachMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = Math.min(textarea.scrollHeight, 128) + "px";
    }
  };

  const handleFileSelect = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "document" | "image",
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (type === "image") {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setPendingFile({ file, type, preview: ev.target?.result as string });
      };
      reader.readAsDataURL(file);
    } else {
      setPendingFile({ file, type });
    }

    setShowAttachMenu(false);
    e.target.value = "";
  };

  const handleSend = async () => {
    if ((!input.trim() && !pendingFile) || !isConnected) return;

    const textToSend = input.trim();
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }

    if (pendingFile) {
      setIsUploading(true);
      const formData = new FormData();
      formData.append("file", pendingFile.file);

      try {
        const endpoint =
          pendingFile.type === "document"
            ? "/upload/document"
            : "/upload/image";

        const res = await fetch(`http://localhost:8000${endpoint}`, {
          method: "POST",
          body: formData,
        });

        const data = await res.json();

        if (data.success) {
          if (pendingFile.type === "document") {
            const contextWithMsg = textToSend
              ? `${data.content}\n\nUser question: ${textToSend}`
              : data.content;
            sendContext(
              pendingFile.file.name,
              contextWithMsg,
              "document",
              undefined,
              textToSend,
            );
          } else {
            const description =
              data.description || "Image could not be analyzed.";
            const contextWithMsg = textToSend
              ? `The user uploaded an image called "${data.filename}". Description:\n\n${description}\n\nUser question: ${textToSend}`
              : `The user uploaded an image called "${data.filename}". Description:\n\n${description}`;
            sendContext(
              pendingFile.file.name,
              contextWithMsg,
              "image",
              data.base64,
              textToSend,
            );
          }
        }
      } catch (err) {
        console.error("Upload failed:", err);
      }

      setIsUploading(false);
      setPendingFile(null);
    } else if (textToSend) {
      sendMessage(textToSend);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleVoiceInput = () => {
    if (
      !("webkitSpeechRecognition" in window) &&
      !("SpeechRecognition" in window)
    ) {
      alert("Voice input not supported. Please use Chrome.");
      return;
    }

    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRecognition =
      (window as any).webkitSpeechRecognition ||
      (window as any).SpeechRecognition;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognitionRef.current = recognition;

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event: any) => {
      setInput(event.results[0][0].transcript);
      setIsRecording(false);
    };
    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognition.start();
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 pb-4 border-b">
        <div>
          <h1 className="text-xl font-semibold">Aria</h1>
          <p className="text-sm text-muted-foreground">AI Personal Secretary</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant={isConnected ? "default" : "destructive"}>
            {isConnected ? "Connected" : "Disconnected"}
          </Badge>
          <Link href="/settings">
            <Button variant="outline" size="sm">
              Settings
            </Button>
          </Link>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 pr-4">
        <div className="flex flex-col gap-4 pb-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.type === "attachment" && msg.attachmentData ? (
                <div className="flex flex-col items-end gap-1">
                  <AttachmentCard
                    filename={msg.attachmentData.filename}
                    file_type={msg.attachmentData.file_type}
                    preview={msg.attachmentData.preview}
                  />
                  {msg.attachmentData.userMessage && (
                    <div className="max-w-[75%] rounded-2xl rounded-br-sm px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap bg-primary text-primary-foreground">
                      {msg.attachmentData.userMessage}
                    </div>
                  )}
                </div>
              ) : msg.type === "confirm" && msg.confirmData ? (
                <ConfirmAction
                  action={msg.confirmData.action}
                  details={msg.confirmData.details}
                  onApprove={() =>
                    sendConfirmation(msg.confirmData!.confirm_id, true)
                  }
                  onReject={() =>
                    sendConfirmation(msg.confirmData!.confirm_id, false)
                  }
                />
              ) : msg.role === "system" ? (
                <div className="text-xs text-muted-foreground text-center w-full py-1">
                  {msg.content}
                </div>
              ) : (
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground rounded-br-sm"
                      : "bg-muted text-foreground rounded-bl-sm"
                  }`}
                >
                  {msg.role === "user" ? (
                    <span className="whitespace-pre-wrap">{msg.content}</span>
                  ) : (
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => (
                          <p className="mb-2 last:mb-0">{children}</p>
                        ),
                        strong: ({ children }) => (
                          <strong className="font-semibold">{children}</strong>
                        ),
                        ul: ({ children }) => (
                          <ul className="list-disc pl-4 mb-2 space-y-1">
                            {children}
                          </ul>
                        ),
                        ol: ({ children }) => (
                          <ol className="list-decimal pl-4 mb-2 space-y-1">
                            {children}
                          </ol>
                        ),
                        li: ({ children }) => <li>{children}</li>,
                        code: ({ children }) => (
                          <code className="bg-black/10 dark:bg-white/10 rounded px-1 py-0.5 text-xs font-mono">
                            {children}
                          </code>
                        ),
                        pre: ({ children }) => (
                          <pre className="bg-black/10 dark:bg-white/10 rounded p-3 text-xs font-mono overflow-x-auto mb-2">
                            {children}
                          </pre>
                        ),
                        h1: ({ children }) => (
                          <h1 className="text-base font-semibold mb-2">
                            {children}
                          </h1>
                        ),
                        h2: ({ children }) => (
                          <h2 className="text-sm font-semibold mb-2">
                            {children}
                          </h2>
                        ),
                        h3: ({ children }) => (
                          <h3 className="text-sm font-medium mb-1">
                            {children}
                          </h3>
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  )}
                </div>
              )}
            </div>
          ))}

          {isThinking && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-2xl rounded-bl-sm px-4 py-3">
                <div className="flex gap-1 items-center h-4">
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce [animation-delay:300ms]" />
                </div>
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.txt,.docx"
        className="hidden"
        onChange={(e) => handleFileSelect(e, "document")}
      />
      <input
        ref={imageInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => handleFileSelect(e, "image")}
      />

      {/* Pending file preview */}
      {pendingFile && (
        <div className="flex items-center gap-3 mb-2 p-3 bg-muted rounded-xl border">
          {pendingFile.type === "image" && pendingFile.preview ? (
            <img
              src={pendingFile.preview}
              alt="preview"
              className="w-10 h-10 rounded-lg object-cover shrink-0"
            />
          ) : (
            <span className="text-xl shrink-0">📄</span>
          )}
          <span className="text-sm truncate flex-1">
            {pendingFile.file.name}
          </span>
          <button
            onClick={() => setPendingFile(null)}
            className="text-muted-foreground hover:text-foreground text-lg shrink-0"
          >
            ✕
          </button>
        </div>
      )}

      {/* Input bar */}
      <div className="flex gap-2 mt-2 pt-4 border-t items-end">
        {/* + attach menu */}
        <div className="relative shrink-0" ref={menuRef}>
          <Button
            variant="outline"
            size="sm"
            className="w-8 h-8 rounded-full p-0 text-lg font-light"
            onClick={() => setShowAttachMenu((prev) => !prev)}
            disabled={!isConnected}
          >
            +
          </Button>

          {showAttachMenu && (
            <div className="absolute bottom-10 left-0 bg-background border rounded-xl shadow-lg py-1 w-52 z-50">
              <button
                className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted text-left"
                onClick={() => fileInputRef.current?.click()}
              >
                <span>📄</span> Add files
              </button>
              <button
                className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted text-left"
                onClick={() => imageInputRef.current?.click()}
              >
                <span>🖼️</span> Add photos
              </button>
              <div className="border-t my-1" />
              <button
                className="w-full flex items-center gap-3 px-4 py-2 text-sm hover:bg-muted text-left"
                onClick={() => {
                  handleVoiceInput();
                  setShowAttachMenu(false);
                }}
              >
                <span>{isRecording ? "🔴" : "🎤"}</span>
                {isRecording ? "Stop recording" : "Voice input"}
              </button>
            </div>
          )}
        </div>

        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            adjustTextareaHeight();
          }}
          onKeyDown={handleKeyDown}
          placeholder={isConnected ? "Message Aria..." : "Connecting..."}
          disabled={!isConnected}
          rows={1}
          className="flex-1 resize-none rounded-md border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 overflow-y-auto"
          style={{ maxHeight: "128px" }}
        />

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={
            !isConnected || (!input.trim() && !pendingFile) || isUploading
          }
          className="shrink-0"
        >
          {isUploading ? "Sending..." : "Send"}
        </Button>
      </div>
    </div>
  );
}