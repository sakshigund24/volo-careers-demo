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
  // Add user's message
  // ----------------------------------------------------------

  const userMsg = document.createElement("div");

  userMsg.className = "msg user";

  userMsg.innerHTML =
    '<span class="label">You</span>' +
    escapeHtml(text);

  log.appendChild(userMsg);

  input.value = "";

  log.scrollTop = log.scrollHeight;


  // ----------------------------------------------------------
  // Loading message
  // ----------------------------------------------------------

  const loading = document.createElement("div");

  loading.className = "msg bot";

  loading.innerHTML =
    '<span class="label">Scan</span>' +
    "Reading against current roles…";

  log.appendChild(loading);

  log.scrollTop = log.scrollHeight;

  btn.disabled = true;


  try {

    // --------------------------------------------------------
    // Call FastAPI backend
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
    // Check HTTP status
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
    // Read JSON response
    // --------------------------------------------------------

    const data = await res.json();

    const reply =
      data.reply ||
      "Couldn't reach the model — try again in a moment.";


    // --------------------------------------------------------
    // Display Gemini response
    // --------------------------------------------------------

    loading.innerHTML =
      '<span class="label">Scan</span>' +
      escapeHtml(reply).replace(/\n/g, "<br>");


  } catch (err) {

    console.error("Compatibility Scan Error:", err);

    loading.innerHTML =
      '<span class="label">Scan</span>' +
      "Something went wrong reaching the server. " +
      "Please try again in a moment.";

  } finally {

    btn.disabled = false;

    log.scrollTop = log.scrollHeight;

  }
}


// ============================================================
// ESCAPE HTML
// Prevents user input / AI output from injecting HTML
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

btn.addEventListener("click", runMatch);


// ============================================================
// ENTER KEY
// Enter = send
// Shift + Enter = new line
// ============================================================

input.addEventListener("keydown", function (e) {

  if (e.key === "Enter" && !e.shiftKey) {

    e.preventDefault();

    runMatch();

  }

});