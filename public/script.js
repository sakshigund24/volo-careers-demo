document.addEventListener("DOMContentLoaded", function () {

  const log = document.getElementById("matchLog");
  const input = document.getElementById("skillsInput");
  const btn = document.getElementById("sendBtn");

  if (!log || !input || !btn) {
    console.error("Compatibility Scan elements not found.");
    return;
  }


  // ==========================================================
  // RUN COMPATIBILITY SCAN
  // ==========================================================

  async function runMatch() {

    const text = input.value.trim();

    if (!text) {
      input.focus();
      return;
    }


    // --------------------------------------------------------
    // USER MESSAGE
    // --------------------------------------------------------

    const userMsg = document.createElement("div");

    userMsg.className = "msg user";

    userMsg.innerHTML = `
      <span class="label">You</span>
      <div class="msg-text">${escapeHtml(text)}</div>
    `;

    log.appendChild(userMsg);

    input.value = "";

    scrollChat();


    // --------------------------------------------------------
    // LOADING MESSAGE
    // --------------------------------------------------------

    const loading = document.createElement("div");

    loading.className = "msg bot";

    loading.innerHTML = `
      <span class="label">Scan</span>
      <div class="msg-text">
        Reading your profile against the current roles…
      </div>
    `;

    log.appendChild(loading);

    scrollChat();


    // Disable button while request is running

    btn.disabled = true;
    btn.textContent = "Scanning…";


    try {

      console.log("Sending compatibility request...");


      // ======================================================
      // DO NOT CHANGE THIS BACKEND ENDPOINT
      // ======================================================

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


      // ------------------------------------------------------
      // HANDLE HTTP ERROR
      // ------------------------------------------------------

      if (!response.ok) {

        let errorMessage = `Server returned ${response.status}`;

        try {

          const errorData = await response.json();

          if (errorData.detail) {
            errorMessage = errorData.detail;
          }

          if (errorData.reply) {
            errorMessage = errorData.reply;
          }

        } catch (error) {

          console.log("Could not parse API error.");

        }

        throw new Error(errorMessage);
      }


      // ------------------------------------------------------
      // READ BACKEND RESPONSE
      // ------------------------------------------------------

      const data = await response.json();

      console.log("API response:", data);


      const reply =
        typeof data.reply === "string"
          ? data.reply
          : "The AI did not return a response.";


      // ------------------------------------------------------
      // DISPLAY AI RESPONSE
      // ------------------------------------------------------

      loading.innerHTML = `
        <span class="label">Scan</span>
        <div class="msg-text">${escapeHtml(reply)}</div>
      `;

      scrollChat();


    } catch (error) {

      console.error(
        "Compatibility Scan Error:",
        error
      );


      loading.innerHTML = `
        <span class="label">Scan</span>
        <div class="msg-text">
          Something went wrong reaching the server.
          Please try again in a moment.
        </div>
      `;

      scrollChat();


    } finally {

      btn.disabled = false;
      btn.textContent = "Scan";

    }

  }


  // ==========================================================
  // ESCAPE HTML
  // ==========================================================

  function escapeHtml(value) {

    return String(value)

      .replace(/&/g, "&amp;")

      .replace(/</g, "&lt;")

      .replace(/>/g, "&gt;")

      .replace(/"/g, "&quot;")

      .replace(/'/g, "&#039;");

  }


  // ==========================================================
  // SCROLL TO BOTTOM
  // ==========================================================

  function scrollChat() {

    requestAnimationFrame(() => {

      log.scrollTop = log.scrollHeight;

    });

  }


  // ==========================================================
  // BUTTON
  // ==========================================================

  btn.addEventListener("click", function () {

    runMatch();

  });


  // ==========================================================
  // ENTER = SEND
  // SHIFT + ENTER = NEW LINE
  // ==========================================================

  input.addEventListener("keydown", function (event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      runMatch();

    }

  });


  console.log(
    "Volo Compatibility Scan initialized."
  );

});