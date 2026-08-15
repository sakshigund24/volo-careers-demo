document.addEventListener("DOMContentLoaded", () => {

  const log = document.getElementById("matchLog");
  const input = document.getElementById("skillsInput");
  const btn = document.getElementById("sendBtn");

  // Check that HTML elements exist
  if (!log || !input || !btn) {
    console.error("Compatibility Scan elements not found.");
    return;
  }

  async function runMatch() {

    const text = input.value.trim();

    if (!text) {
      input.focus();
      return;
    }

    // -----------------------------
    // USER MESSAGE
    // -----------------------------

    const userMsg = document.createElement("div");

    userMsg.className = "msg user";

    userMsg.innerHTML =
      '<span class="label">You</span>' +
      '<div class="msg-text">' +
      escapeHtml(text) +
      "</div>";

    log.appendChild(userMsg);

    input.value = "";

    scrollChat();


    // -----------------------------
    // LOADING MESSAGE
    // -----------------------------

    const loading = document.createElement("div");

    loading.className = "msg bot";

    loading.innerHTML =
      '<span class="label">Scan</span>' +
      '<div class="msg-text">Reading your profile against the current roles…</div>';

    log.appendChild(loading);

    scrollChat();

    btn.disabled = true;
    btn.textContent = "Scanning…";


    try {

      console.log("Sending request to /api/match");


      // -----------------------------
      // CALL BACKEND
      // -----------------------------

      const response = await fetch("/api/match", {

        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({
          message: text
        })

      });


      console.log("API status:", response.status);


      // -----------------------------
      // HANDLE HTTP ERROR
      // -----------------------------

      if (!response.ok) {

        let errorText = `Server returned ${response.status}`;

        try {

          const errorData = await response.json();

          if (errorData.detail) {
            errorText = errorData.detail;
          }

          if (errorData.reply) {
            errorText = errorData.reply;
          }

        } catch (e) {
          console.log("Could not parse error response.");
        }

        throw new Error(errorText);
      }


      // -----------------------------
      // READ RESPONSE
      // -----------------------------

      const data = await response.json();

      console.log("API response:", data);


      const reply =
        data.reply ||
        "The AI did not return a response.";


      // -----------------------------
      // DISPLAY AI RESPONSE
      // -----------------------------

      loading.innerHTML =
        '<span class="label">Scan</span>' +
        '<div class="msg-text">' +
        escapeHtml(reply).replace(/\n/g, "<br>") +
        "</div>";

      scrollChat();


    } catch (error) {

      console.error("Compatibility Scan Error:", error);


      loading.innerHTML =
        '<span class="label">Scan</span>' +
        '<div class="msg-text">' +
        "Something went wrong: " +
        escapeHtml(error.message) +
        "</div>";

      scrollChat();

    } finally {

      btn.disabled = false;
      btn.textContent = "Scan";

    }

  }


  // -----------------------------
  // ESCAPE HTML
  // -----------------------------

  function escapeHtml(value) {

    return String(value)

      .replace(/&/g, "&amp;")

      .replace(/</g, "&lt;")

      .replace(/>/g, "&gt;")

      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#039;");

  }


  // -----------------------------
  // SCROLL CHAT
  // -----------------------------

  function scrollChat() {

    setTimeout(() => {

      log.scrollTop = log.scrollHeight;

    }, 50);

  }


  // -----------------------------
  // BUTTON CLICK
  // -----------------------------

  btn.addEventListener("click", runMatch);


  // -----------------------------
  // ENTER = SEND
  // SHIFT + ENTER = NEW LINE
  // -----------------------------

  input.addEventListener("keydown", (event) => {

    if (event.key === "Enter" && !event.shiftKey) {

      event.preventDefault();

      runMatch();

    }

  });


  console.log("Compatibility Scan initialized successfully.");

});