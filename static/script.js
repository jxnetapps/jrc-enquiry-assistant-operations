let authToken = null;
let currentUserId = "user_" + Math.random().toString(36).substr(2, 9);
let chatMode = null;
let isAutoLoggedIn = false; // Track auto-login status

// Auto-login function
async function autoLogin() {
  try {
    const response = await fetch("/api/auto-login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      authToken = data.access_token;
      isAutoLoggedIn = true;
      
      // Show welcome message and first question together
      if (data.welcome_message && data.first_question) {
        const combinedMessage = `${data.welcome_message}\n\n${data.first_question}`;
        addMessage("bot", combinedMessage, {
          mode: data.chat_mode,
          state: "parent_type",
          options: ["New Parent", "Existing Parent"],
          requires_input: true
        });
      } else if (data.welcome_message) {
        addMessage("bot", data.welcome_message);
        // Start pre-trained conversation if no first question provided
        startPreTrainedConversation();
      }
      
      // Hide login button and show chat interface
      document.getElementById("login-btn").style.display = "none";
      document.getElementById("chat-container").style.display = "block";
      
      return true;
    } else {
      console.log("Auto-login failed, showing manual login");
      return false;
    }
  } catch (error) {
    console.error("Auto-login error:", error);
    return false;
  }
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
      body: JSON.stringify({ 
        message: message,
        user_id: currentUserId 
      }),
    });

    if (response.ok) {
      const data = await response.json();
      chatMode = data.mode;
      
      // Add bot response with enhanced data
      addMessage("bot", data.response, {
        mode: data.mode,
        state: data.state,
        options: data.options,
        collected_data: data.collected_data,
        requires_input: data.requires_input,
        conversation_complete: data.conversation_complete
      });
      
      // Handle conversation completion
      if (data.conversation_complete) {
        showConversationComplete(data.collected_data);
      }
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
    currentUserId = "user_" + Math.random().toString(36).substr(2, 9);
    chatMode = null;
    document.getElementById("chat-messages").innerHTML = "";
    
    // Reset chat session on server
    if (authToken) {
      fetch("/api/chat/reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ user_id: currentUserId }),
      });
    }
  }
}

// Initialize page on load
document.addEventListener("DOMContentLoaded", async function() {
  // Try auto-login first
  const autoLoginSuccess = await autoLogin();
  
  if (!autoLoginSuccess) {
    // Show manual login button if auto-login fails
    document.getElementById("login-btn").style.display = "block";
    document.getElementById("chat-container").style.display = "none";
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
