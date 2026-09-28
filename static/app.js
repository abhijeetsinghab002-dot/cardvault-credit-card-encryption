const statusBox = document.querySelector('#status');

function status(message, bad = false) {
  statusBox.textContent = message;
  statusBox.className = bad ? 'bad' : 'good';
}

async function post(url, data) {
  const response = await fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || 'Request failed.');
  return body;
}

async function refresh() {
  const response = await fetch('/api/cards');
  const {cards} = await response.json();
  document.querySelector('#cards').innerHTML = cards.length ? cards.map(card =>
    `<div class="row"><strong>${card.masked_pan}</strong><code>${card.token}</code><small>${card.created_at} UTC</small></div>`
  ).join('') : '<p class="hint">No tokens created yet.</p>';
}

document.querySelector('#pan').addEventListener('input', event => {
  const digits = event.target.value.replace(/\D/g, '').slice(0, 19);
  event.target.value = digits.replace(/(.{4})/g, '$1 ').trim();
});

document.querySelector('#tokenize').addEventListener('click', async () => {
  try {
    const result = await post('/api/tokenize', {pan: document.querySelector('#pan').value});
    document.querySelector('#masked').textContent = result.masked_pan;
    document.querySelector('#token').textContent = result.token;
    document.querySelector('#lookup').value = result.token;
    document.querySelector('#token-result').hidden = false;
    document.querySelector('#pan').value = '';
    status('Test card encrypted and tokenized.');
    refresh();
  } catch (error) { status(error.message, true); }
});

document.querySelector('#reveal').addEventListener('click', async () => {
  try {
    const result = await post('/api/reveal', {token: document.querySelector('#lookup').value});
    document.querySelector('#revealed').textContent = result.pan;
    document.querySelector('#reveal-result').hidden = false;
    status('Authenticated decryption completed.');
  } catch (error) { status(error.message, true); }
});

refresh();
