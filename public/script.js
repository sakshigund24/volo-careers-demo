const log = document.getElementById("matchLog");
const input = document.getElementById("skillsInput");
const btn = document.getElementById("sendBtn");


// ============================================================
// RUN AI COMPATIBILITY SCAN
// ============================================================

async function runMatch() {

  const text = input.value.trim();

  if (!text) {
    return;
  }


  // ----------------------------------------------------------
  // USER MESSAGE
  // ----------------------------------------------------------

  const userMsg = document.createElement("div");

  userMsg.className = "msg user";

  userMsg.innerHTML =
    '<span class="label">You</span>' +
    '<div class="msg-text">' +
    escapeHtml(text) +
    "</div>";

  log.appendChild(userMsg);

  input.value = "";

  log.scrollTop = log.scrollHeight;


  // ----------------------------------------------------------
  // LOADING MESSAGE
  // ----------------------------------------------------------

  const loading = document.createElement("div");

  loading.className = "msg bot";

  loading.innerHTML =
    '<span class="label">Scan</span>' +
    '<div class="msg-text">' +
    "Reading your profile against the current roles…" +
    "</div>";

  log.appendChild(loading);

  log.scrollTop = log.scrollHeight;

  btn.disabled = true;


  try {

    // --------------------------------------------------------
    // API REQUEST
    // --------------------------------------------------------

    const res = await fetch("/api/match", {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        message: text
      })

    });


    // --------------------------------------------------------
    // HTTP ERROR
    // --------------------------------------------------------

    if (!res.ok) {

      let errorMessage = "";

      try {

        const errorData = await res.json();

        errorMessage =
          errorData.detail ||
          errorData.reply ||
          "";

      } catch (e) {

        errorMessage = "";

      }

      throw new Error(
        `API Error ${res.status} ${errorMessage}`
      );
    }


    // --------------------------------------------------------
    // READ RESPONSE
    // --------------------------------------------------------

    const data = await res.json();

    const reply =
      data.reply ||
      "Couldn't reach the model — try again in a moment.";


    // --------------------------------------------------------
    // DISPLAY ACTUAL AI RESPONSE
    // --------------------------------------------------------

    loading.innerHTML =
      '<span class="label">Scan</span>' +
      '<div class="msg-text">' +
      escapeHtml(reply).replace(/\n/g, "<br>") +
      "</div>";


  } catch (err) {

    console.error(
      "Compatibility Scan Error:",
      err
    );


    // --------------------------------------------------------
    // ERROR MESSAGE
    // --------------------------------------------------------

    loading.innerHTML =
      '<span class="label">Scan</span>' +
      '<div class="msg-text">' +
      "Something went wrong reaching the server. " +
      "Please try again in a moment." +
      "</div>";

  } finally {

    btn.disabled = false;

    log.scrollTop = log.scrollHeight;

  }
}


// ============================================================
// ESCAPE HTML
// ============================================================

function escapeHtml(str) {

  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");

}


// ============================================================
// BUTTON
// ============================================================

btn.addEventListener(
  "click",
  runMatch
);


// ============================================================
// ENTER KEY
// ============================================================

input.addEventListener(
  "keydown",
  function (e) {

    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {

      e.preventDefault();

      runMatch();

    }

  }
);