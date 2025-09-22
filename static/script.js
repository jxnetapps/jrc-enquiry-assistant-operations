let authToken = null;
let currentUserId = null;
let chatMode = null;

// Local storage keys
const TOKEN_KEY = 'chatbot_auth_token';
const USER_ID_KEY = 'chatbot_user_id';

// Local storage management functions
function saveAuthData(token, userId) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_ID_KEY, userId);
  authToken = token;
  currentUserId = userId;
}

function loadAuthData() {
  authToken = localStorage.getItem(TOKEN_KEY);
  currentUserId = localStorage.getItem(USER_ID_KEY);
  return authToken && currentUserId;
}

function clearAuthData() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  authToken = null;
  currentUserId = null;
}

function logout() {
  clearAuthData();
  // Clear chat messages
  document.getElementById("chat-messages").innerHTML = "";
  // Show login button and hide chat
  document.getElementById("login-btn").style.display = "block";
  document.getElementById("chat-container").style.display = "none";
  // Update login button text
  document.getElementById("login-btn").textContent = "Login";
  alert("Logged out successfully");
}

// Start pre-trained conversation
function startPreTrainedConversation() {
  // Send initial message to start the pre-trained flow
  sendMessage("Hello");
}

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
      
      // Check if login was successful using ApiResponse format
      if (data.success && data.access_token && data.user_id) {
        // Save auth data to local storage
        saveAuthData(data.access_token, data.user_id);
        
        // Update UI to show chat interface
        document.getElementById("login-btn").style.display = "none";
        document.getElementById("chat-container").style.display = "block";
        document.getElementById("login-btn").textContent = "Logout";
        document.getElementById("login-btn").onclick = logout;
        
        alert(`Login successful! Welcome ${username}`);
        return true;
      } else {
        alert(data.message || "Login failed");
        return false;
      }
    } else {
      const errorData = await response.json();
      alert(errorData.message || "Login failed");
      return false;
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Login error: " + error.message);
    return false;
  }
}

async function sendMessage() {
  // Load auth data from local storage first
  if (!loadAuthData()) {
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
      body: JSON.stringify({ 
        message: message,
        user_id: currentUserId  // Use stored user_id instead of temporary one
      }),
    });

    if (response.ok) {
      const data = await response.json();
      
      // Handle ApiResponse format
      if (data.success && data.data) {
        const chatData = data.data;
        chatMode = chatData.mode;
        
        // Add bot response with enhanced data
        addMessage("bot", chatData.response, {
          mode: chatData.mode,
          state: chatData.state,
          options: chatData.options,
          collected_data: chatData.collected_data,
          requires_input: chatData.requires_input,
          conversation_complete: chatData.conversation_complete
        });
        
        // Handle conversation completion
        if (chatData.conversation_complete) {
          showConversationComplete(chatData.collected_data);
        }
      } else {
        addMessage("bot", data.message || "Error: Could not get response");
      }
    } else {
      const errorData = await response.json();
      addMessage("bot", errorData.message || "Error: Could not get response");
    }
  } catch (error) {
    console.error("Chat error:", error);
    addMessage("bot", "Connection error");
  }
}

async function startCrawl() {
  if (!loadAuthData()) {
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
  if (!loadAuthData()) {
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

function addMessage(sender, text, data = null) {
  const messagesDiv = document.getElementById("chat-messages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}-message`;
  
  // Add enhanced data attributes
  if (data) {
    messageDiv.setAttribute('data-mode', data.mode || '');
    messageDiv.setAttribute('data-state', data.state || '');
    messageDiv.setAttribute('data-conversation-complete', data.conversation_complete || false);
  }

  // Auto-convert to Markdown
  const formatted = autoFormatAIResponse(text);
  messageDiv.innerHTML = marked.parse(formatted);
  
  // Add options if available
  if (data && data.options && data.options.length > 0) {
    const optionsDiv = document.createElement("div");
    optionsDiv.className = "chat-options";
    optionsDiv.innerHTML = "<strong>Options:</strong><br>";
    data.options.forEach(option => {
      const optionButton = document.createElement("button");
      optionButton.textContent = option;
      optionButton.className = "option-button";
      optionButton.onclick = () => selectOption(option);
      optionsDiv.appendChild(optionButton);
      optionsDiv.appendChild(document.createElement("br"));
    });
    messageDiv.appendChild(optionsDiv);
  }

  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function selectOption(option) {
  const input = document.getElementById("message-input");
  input.value = option;
  sendMessage();
}

function showConversationComplete(collectedData) {
  if (collectedData) {
    const summaryDiv = document.createElement("div");
    summaryDiv.className = "conversation-summary";
    summaryDiv.innerHTML = `
      <h3>Conversation Summary</h3>
      <p><strong>Parent Type:</strong> ${collectedData.parent_type || 'N/A'}</p>
      <p><strong>School Type:</strong> ${collectedData.school_type || 'N/A'}</p>
      <p><strong>Name:</strong> ${collectedData.name || 'N/A'}</p>
      <p><strong>Mobile:</strong> ${collectedData.mobile || 'N/A'}</p>
    `;
    document.getElementById("chat-messages").appendChild(summaryDiv);
  }
}

function resetChat() {
  if (confirm("Are you sure you want to reset the chat?")) {
    // Load auth data to get the stored user_id
    if (loadAuthData()) {
      chatMode = null;
      document.getElementById("chat-messages").innerHTML = "";
      
      // Reset chat session on server using stored user_id
      fetch("/api/chat/reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ user_id: currentUserId }),
      });
    } else {
      alert("Please login first");
    }
  }
}

// Initialize page on load
document.addEventListener("DOMContentLoaded", function() {
  // Try to load auth data from local storage
  if (loadAuthData()) {
    // User is already logged in, show chat interface
    document.getElementById("login-btn").style.display = "none";
    document.getElementById("chat-container").style.display = "block";
    document.getElementById("login-btn").textContent = "Logout";
    document.getElementById("login-btn").onclick = logout;
    console.log("User already logged in:", currentUserId);
  } else {
    // User needs to login, show login button
    document.getElementById("login-btn").style.display = "block";
    document.getElementById("chat-container").style.display = "none";
    document.getElementById("login-btn").textContent = "Login";
    document.getElementById("login-btn").onclick = login;
  }
});

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
