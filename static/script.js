let authToken = null;

async function login() {
  const username = prompt("Username:");
  const password = prompt("Password:");

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (response.ok) {
      const data = await response.json();
      authToken = data.access_token;
      alert("Login successful!");
      return true;
    } else {
      alert("Login failed");
      return false;
    }
  } catch (error) {
    console.error("Login error:", error);
    return false;
  }
}

async function sendMessage() {
  if (!authToken) {
    if (!(await login())) return;
  }

  const input = document.getElementById("message-input");
  const message = input.value.trim();

  if (!message) return;

  // Add user message to chat
  addMessage("user", message);
  input.value = "";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({ message }),
    });

    if (response.ok) {
      const data = await response.json();
      addMessage("bot", data.response);
    } else {
      addMessage("bot", "Error: Could not get response");
    }
  } catch (error) {
    console.error("Chat error:", error);
    addMessage("bot", "Connection error");
  }
}

async function startCrawl() {
  if (!authToken) {
    if (!(await login())) return;
  }

  const urlInput = document.getElementById("crawl-url");
  const url = urlInput.value.trim();

  if (!url) {
    alert("Please enter a URL");
    return;
  }

  const statusDiv = document.getElementById("crawl-status");
  statusDiv.textContent = "Starting crawl...";

  try {
    const response = await fetch("/api/crawl", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({ url }),
    });

    const data = await response.json();
    statusDiv.textContent = `Crawl completed: ${data.chunks_processed} chunks processed`;
  } catch (error) {
    console.error("Crawl error:", error);
    statusDiv.textContent = "Crawl failed";
  }
}

async function uploadDocs() {
  if (!authToken) {
    if (!(await login())) return;
  }

  const input = document.getElementById("upload-files");
  const files = input.files;
  if (!files || files.length === 0) {
    alert("Select one or more files");
    return;
  }

  const statusDiv = document.getElementById("upload-status");
  statusDiv.textContent = "Uploading...";

  const form = new FormData();
  for (const f of files) form.append("files", f);

  try {
    const response = await fetch("/api/upload-docs", {
      method: "POST",
      headers: { Authorization: `Bearer ${authToken}` },
      body: form,
    });
    const data = await response.json();
    if (response.ok) {
      statusDiv.textContent = `Uploaded. ${data.chunks_processed} chunks processed`;
    } else {
      statusDiv.textContent = `Upload failed: ${
        data.detail || "unknown error"
      }`;
    }
  } catch (e) {
    console.error("Upload error:", e);
    statusDiv.textContent = "Upload failed";
  }
}

function addMessage(sender, text) {
  const messagesDiv = document.getElementById("chat-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}-message`;
  //messageDiv.textContent = text;

  // Auto-convert to Markdown
  const formatted = autoFormatAIResponse(text);
  messageDiv.innerHTML = marked.parse(formatted);

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Enter key support
document
  .getElementById("message-input")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

document.getElementById("crawl-url").addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    startCrawl();
  }
});

function autoFormatAIResponse(text) {
  // Replace single line breaks with a space (keeps sentences intact)
  text = text.replace(/([^\n])\n([^\n])/g, "$1 $2");

  // Normalize extra spaces
  text = text.replace(/\s+/g, " ").trim();

  // Split into sentences
  let sentences = text.split(/(?<=[.!?])\s+/);

  // First sentence bolded
  let intro = sentences.shift();

  let bullets = [];
  let paragraphs = [];

  sentences.forEach((s) => {
    if (
      /^(He|She|They|It|Sampathraj|The|This|These|In addition|Also|Moreover|Additionally|Unfortunately|However|For example)/i.test(
        s
      )
    ) {
      bullets.push(s);
    } else {
      paragraphs.push(s);
    }
  });

  let markdown = `**${intro}**\n\n`;

  if (bullets.length) {
    markdown += bullets.map((s) => `- ${s}`).join("\n") + "\n\n";
  }

  if (paragraphs.length) {
    markdown += paragraphs.join("\n\n") + "\n";
  }

  return marked.parse(markdown);
}
