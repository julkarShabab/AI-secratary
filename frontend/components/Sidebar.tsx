"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";

type Conversation = {
  id: string;
  title: string;
  is_starred: boolean;
  created_at: string;
  updated_at: string;
};

type SidebarProps = {
  activeId: string;
  onSelect: (id: string) => void;
  onNewChat: (id: string) => void;
  token: string;
  userName?: string;
  onLogout: () => void;
};

const API_URL = "http://localhost:8000";

export default function Sidebar({
  activeId,
  onSelect,
  onNewChat,
  token,
  userName,
  onLogout,
}: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const menuWrapperRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const editInputRef = useRef<HTMLInputElement>(null);

  const fetchConversations = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/conversations`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setConversations(data);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations, activeId]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (!openMenuId) return;
      const wrapper = menuWrapperRefs.current.get(openMenuId);
      if (wrapper && !wrapper.contains(e.target as Node)) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [openMenuId]);

  useEffect(() => {
    if (editingId) {
      editInputRef.current?.focus();
      editInputRef.current?.select();
    }
  }, [editingId]);

  const handleNewChat = async () => {
    try {
      const res = await fetch(`${API_URL}/api/conversations`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: "New conversation" }),
      });
      const data = await res.json();
      onNewChat(data.id);
    } catch (err) {
      console.error("Failed to create conversation:", err);
    }
  };

  const patchConversation = async (
    id: string,
    payload: Record<string, unknown>,
  ) => {
    try {
      const res = await fetch(`${API_URL}/api/conversations/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
      const updated = await res.json();
      setConversations((prev) => prev.map((c) => (c.id === id ? updated : c)));
    } catch (err) {
      console.error("Failed to update conversation:", err);
    }
  };

  const handleToggleStar = (conv: Conversation) => {
    patchConversation(conv.id, { is_starred: !conv.is_starred });
    setOpenMenuId(null);
  };

  const startRename = (conv: Conversation) => {
    setEditingId(conv.id);
    setEditValue(conv.title);
    setOpenMenuId(null);
  };

  const commitRename = (id: string) => {
    const trimmed = editValue.trim();
    setEditingId(null);
    if (trimmed) {
      patchConversation(id, { title: trimmed });
    }
  };

  const handleDelete = async (id: string) => {
    setOpenMenuId(null);
    if (!confirm("Delete this conversation? This can't be undone.")) return;

    try {
      await fetch(`${API_URL}/api/conversations/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (id === activeId) {
        handleNewChat();
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const starred = conversations.filter((c) => c.is_starred);
  const unstarred = conversations.filter((c) => !c.is_starred);

  const renderItem = (conv: Conversation) => (
    <div
      key={conv.id}
      className="relative group"
      ref={(el) => {
        if (el) menuWrapperRefs.current.set(conv.id, el);
        else menuWrapperRefs.current.delete(conv.id);
      }}
    >
      {editingId === conv.id ? (
        <input
          ref={editInputRef}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={() => commitRename(conv.id)}
          onKeyDown={(e) => {
            if (e.key === "Enter") commitRename(conv.id);
            if (e.key === "Escape") setEditingId(null);
          }}
          className="w-full text-sm px-3 py-2 rounded-lg border border-input bg-background"
        />
      ) : (
        <button
          onClick={() => onSelect(conv.id)}
          className={`w-full text-left text-sm pl-3 pr-8 py-2 rounded-lg truncate transition-colors ${
            conv.id === activeId
              ? "bubble-user text-primary-foreground"
              : "hover:bg-white/5 text-foreground"
          }`}
          title={conv.title}
        >
          {conv.is_starred && <span className="mr-1">⭐</span>}
          {conv.title}
        </button>
      )}

      {editingId !== conv.id && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            setOpenMenuId((prev) => (prev === conv.id ? null : conv.id));
          }}
          className={`absolute right-1 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded hover:bg-white/10 text-xs ${
            conv.id === activeId
              ? "text-primary-foreground"
              : "text-muted-foreground"
          } ${openMenuId === conv.id ? "opacity-100" : "opacity-0 group-hover:opacity-100"}`}
        >
          ⋮
        </button>
      )}

      {openMenuId === conv.id && (
        <div className="absolute right-0 top-9 glass-panel-strong rounded-lg shadow-lg py-1 w-36 z-50">
          <button
            className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-white/5 text-left"
            onClick={() => handleToggleStar(conv)}
          >
            <span>{conv.is_starred ? "☆" : "⭐"}</span>
            {conv.is_starred ? "Unstar" : "Star"}
          </button>
          <button
            className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-white/5 text-left"
            onClick={() => startRename(conv)}
          >
            <span>✏️</span> Rename
          </button>
          <button
            className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-white/5 text-left text-destructive"
            onClick={() => handleDelete(conv.id)}
          >
            <span>🗑️</span> Delete
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="w-64 h-full flex flex-col glass-panel-strong border-r-0">
      <div className="px-4 py-4 border-b border-white/10">
        <h2 className="font-heading font-semibold tracking-tight">Aria</h2>
      </div>

      <div className="p-3 border-b border-white/10">
        <Button
          onClick={handleNewChat}
          className="w-full glow-signal"
          size="sm"
        >
          + New chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-1">
        {isLoading && (
          <div className="text-xs text-muted-foreground text-center py-4">
            Loading...
          </div>
        )}

        {!isLoading && conversations.length === 0 && (
          <div className="text-xs text-muted-foreground text-center py-4">
            No conversations yet
          </div>
        )}

        {starred.length > 0 && (
          <>
            <div className="text-xs font-mono uppercase tracking-wider text-muted-foreground px-3 pt-2 pb-1">
              Starred
            </div>
            {starred.map(renderItem)}
            <div className="border-t border-white/10 my-2" />
          </>
        )}

        {unstarred.map(renderItem)}
      </div>

      <div className="p-3 border-t border-white/10 flex items-center justify-between gap-2">
        <span className="text-xs text-muted-foreground truncate">
          {userName}
        </span>
        <Button variant="ghost" size="sm" onClick={onLogout}>
          Log out
        </Button>
      </div>
    </div>
  );
}
