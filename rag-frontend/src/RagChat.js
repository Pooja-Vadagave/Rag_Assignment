import React, { useState } from "react";

export default function RagChat() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer("");

    try {
      // Make sure your FastAPI server is running on port 8000
      const res = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error("Network error");
      }

      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "1rem" }}>
      <h2>RAG Q&A Bot</h2>

      <textarea
        rows="3"
        style={{ width: "100%", marginBottom: "0.5rem" }}
        placeholder="Ask a question about your PDFs..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <br />
      <button onClick={handleAsk} disabled={loading}>
        {loading ? "Asking..." : "Ask"}
      </button>

      {answer && (
        <div style={{ marginTop: "1rem", padding: "0.5rem", background: "#f7f7f7" }}>
          <strong>Answer:</strong>
          <div>{answer}</div>
        </div>
      )}
    </div>
  );
}
