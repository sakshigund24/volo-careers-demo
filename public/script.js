const log = document.getElementById('matchLog');
const input = document.getElementById('skillsInput');
const btn = document.getElementById('sendBtn');

async function runMatch(){
  const text = input.value.trim();
  if(!text) return;

  const userMsg = document.createElement('div');
  userMsg.className = 'msg user';
  userMsg.innerHTML = '<span class="label">You</span>' + escapeHtml(text);
  log.appendChild(userMsg);
  input.value = '';
  log.scrollTop = log.scrollHeight;

  const loading = document.createElement('div');
  loading.className = 'msg bot';
  loading.innerHTML = '<span class="label">Scan</span>Reading against current roles…';
  log.appendChild(loading);
  log.scrollTop = log.scrollHeight;
  btn.disabled = true;

  try {
    const res = await fetch('/api/match', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await res.json();
    const reply = data.reply || "Couldn't reach the model — try again in a moment.";
    loading.innerHTML = '<span class="label">Scan</span>' + escapeHtml(reply).replace(/\n/g, '<br>');
  } catch (err) {
    loading.innerHTML = '<span class="label">Scan</span>Something went wrong reaching the server. Try again in a moment.';
  } finally {
    btn.disabled = false;
    log.scrollTop = log.scrollHeight;
  }
}

function escapeHtml(str){
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

btn.addEventListener('click', runMatch);
input.addEventListener('keydown', function(e){
  if(e.key === 'Enter' && !e.shiftKey){
    e.preventDefault();
    runMatch();
  }
});
