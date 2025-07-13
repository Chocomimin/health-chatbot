import { useState, useEffect } from "react";
import API from "../api";
import "./Chat.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import MapView from "./MapView"; // ✅ Map component

export default function Chat() {
  const [sessionId, setSessionId] = useState("");
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [editingIndex, setEditingIndex] = useState(null);
  const [editedText, setEditedText] = useState("");
  const [loading, setLoading] = useState(false);
  const [initialLoadComplete, setInitialLoadComplete] = useState(false);
  const [showMap, setShowMap] = useState(false); // ✅ Show/hide map modal

  useEffect(() => {
    let isMounted = true;
    const init = async () => {
      await fetchSessions();
      const storedId = localStorage.getItem("sessionId");
      if (storedId) {
        try {
          await loadChatSession(storedId);
        } catch (error) {
          console.error("Failed to load stored session:", storedId, error);
          localStorage.removeItem("sessionId");
          setSessionId("");
          setMessages([]);
        }
      }
      if (!sessionId) {
        const latest = await API.get("/chat/sessions");
        if (latest.data.length > 0) {
          const lastSession = latest.data[latest.data.length - 1];
          if (isMounted) {
            await loadChatSession(lastSession.chat_id);
            localStorage.setItem("sessionId", lastSession.chat_id);
          }
        }
      }
      if (isMounted) {
        setInitialLoadComplete(true);
      }
    };
    init();
    return () => {
      isMounted = false;
    };
  }, []);

  const fetchSessions = async () => {
    const res = await API.get("/chat/sessions");
    setSessions(res.data);
  };
  const handleLogout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("sessionId");
  window.location.href = "/"; // Redirect to Login page
};

  const startNewChat = async () => {
    setLoading(true);
    try {
      const res = await API.post("/chat/create", { name: "New Session" });
      setSessionId(res.data.chat_id);
      setMessages([]);
      await fetchSessions();
      localStorage.setItem("sessionId", res.data.chat_id);
    } catch (error) {
      console.error("Error starting new chat:", error);
      alert("Failed to start a new chat.");
    } finally {
      setLoading(false);
    }
  };

  const loadChatSession = async (id) => {
    setLoading(true);
    try {
      const res = await API.get(`/chat/${id}`);
      setSessionId(res.data.chat_id);
      setMessages(res.data.messages || []);
      localStorage.setItem("sessionId", res.data.chat_id);
    } catch (error) {
      console.error("Error loading chat session:", error);
      localStorage.removeItem("sessionId");
      setSessionId("");
      setMessages([]);
      alert("Failed to load chat session.");
      await fetchSessions();
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (chatId) => {
    if (window.confirm("Are you sure you want to delete this chat?")) {
      setLoading(true);
      try {
        await API.delete(`/chat/${chatId}`);
        if (chatId === sessionId) {
          setSessionId("");
          setMessages([]);
          localStorage.removeItem("sessionId");
        }
        await fetchSessions();
      } catch (error) {
        console.error("Error deleting chat:", error);
        alert("Failed to delete chat.");
      } finally {
        setLoading(false);
      }
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return;

    const userMsg = { role: "USER", message: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await API.post("/chat", {
        message: userMsg.message,
        session_id: sessionId,
      });
      const botMsg = { role: "BOT", message: res.data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "BOT", message: "⚠️ Unable to respond. Try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (index) => {
    setEditingIndex(index);
    setEditedText(messages[index].message);
  };

  const saveEditedMessage = async () => {
    if (!editedText.trim()) return;

    try {
      setLoading(true);
      await API.put("/chat/edit-message", {
        chat_id: sessionId,
        index: editingIndex,
        new_message: editedText,
      });

      const updated = [...messages];
      updated[editingIndex].message = editedText;
      const rebuilt = updated.slice(0, editingIndex + 1);
      const userMsgs = updated.slice(editingIndex + 1).filter((m) => m.role === "USER");

      const botReplies = await Promise.all(
        userMsgs.map((msg) =>
          API.post("/chat", {
            message: msg.message,
            session_id: sessionId,
          })
        )
      );

      userMsgs.forEach((msg, i) => {
        rebuilt.push(msg);
        rebuilt.push({ role: "BOT", message: botReplies[i].data.reply });
      });

      setMessages(rebuilt);
      setEditingIndex(null);
      setEditedText("");
    } catch (err) {
      console.error("Edit error:", err);
      alert("Editing failed.");
    } finally {
      setLoading(false);
    }
  };

  if (!initialLoadComplete) {
    return (
      <div className="layout loading-screen">
        <div className="loading-indicator large-loading">
          <div className="loading-dot"></div>
          <div className="loading-dot"></div>
          <div className="loading-dot"></div>
          <p>Loading sessions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="layout">
      {/* Sidebar */}
      <div className="sidebar">
        <h3>Chats</h3>
        
        <button onClick={startNewChat} className="new-chat-button" disabled={loading}>
          {loading ? "Creating..." : "+ New Chat"}
        </button>
        <button onClick={handleLogout} className="logout-button">
  🔒 Logout
</button>

        {sessions.length > 0 && (
          <ul className="session-list">
            {sessions.map((s) => (
              <li
                key={s.chat_id}
                className={`session-item ${sessionId === s.chat_id ? "active" : ""}`}
              >
                <span onClick={() => loadChatSession(s.chat_id)} className="session-name">
                  {s.name}
                </span>
                <button
                  onClick={() => handleDeleteChat(s.chat_id)}
                  className="delete-button"
                  disabled={loading}
                >
                  🗑️
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Chat Area */}
      {sessionId ? (
        <div className="chat-area">
          <h2>Healthcare Chatbot</h2>
          <div className="chat-box">
            {messages.map((m, i) => (
              <div key={i} className="message-container">
                <strong>{m.role === "USER" ? "You" : "Bot"}:</strong>
                {editingIndex === i ? (
                  <>
                    <input
                      value={editedText}
                      onChange={(e) => setEditedText(e.target.value)}
                      className="edit-input"
                    />
                    <button onClick={saveEditedMessage} className="save-button" disabled={loading}>
                      💾 Save
                    </button>
                  </>
                ) : (
                  <>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.message}</ReactMarkdown>
                    {m.role === "USER" && (
                      <button onClick={() => handleEdit(i)} className="edit-button" disabled={loading}>
                        ✏️ Edit
                      </button>
                    )}
                  </>
                )}
              </div>
            ))}
            {loading && (
              <div className="loading-indicator">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            )}
          </div>

          {/* 🏥 Find Nearby Hospitals Button */}
          <button
            className="send-button"
            style={{ marginBottom: "1rem", alignSelf: "center" }}
            onClick={() => setShowMap(true)}
          >
            🏥 Find Nearby Hospitals
          </button>

          {/* 🌍 Map Modal */}
          {showMap && (
            <div className="modal-overlay">
              <div className="modal-content">
                <button className="close-button" onClick={() => setShowMap(false)}>❌ Close</button>
                <MapView />
              </div>
            </div>
          )}

          <div className="input-container">
            <input
              className="input-field"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={loading ? "Waiting for response..." : "Type your message..."}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !loading) {
                  sendMessage();
                }
              }}
              disabled={loading}
            />
            <button className="send-button" onClick={sendMessage} disabled={loading}>
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      ) : (
        <div className="no-chat-selected">
          <p>Welcome! Start a new conversation to begin.</p>
          <button onClick={startNewChat} className="new-chat-button large-button" disabled={loading}>
            {loading ? "Creating..." : "+ Start New Chat"}
          </button>
        </div>
      )}
    </div>
  );
}
