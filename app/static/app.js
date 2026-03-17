let currentLinks = [];

const form = document.getElementById('scrape-form');
const urlInput = document.getElementById('url-input');
const proxyInput = document.getElementById('proxy-input');
const scrapeBtn = document.getElementById('scrape-btn');
const statusBar = document.getElementById('status-bar');
const resultsSection = document.getElementById('results-section');
const resultCount = document.getElementById('result-count');
const linksTbody = document.getElementById('links-tbody');
const exportBtn = document.getElementById('export-btn');

function showStatus(type, html) {
  statusBar.className = `status ${type}`;
  statusBar.innerHTML = html;
  statusBar.classList.remove('hidden');
}

function hideStatus() {
  statusBar.classList.add('hidden');
}

function renderTable(links) {
  linksTbody.innerHTML = '';
  for (const link of links) {
    const tr = document.createElement('tr');
    const tdTitle = document.createElement('td');
    tdTitle.textContent = link.title;
    const tdUrl = document.createElement('td');
    const a = document.createElement('a');
    a.href = link.url;
    a.textContent = link.url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    tdUrl.appendChild(a);
    tr.appendChild(tdTitle);
    tr.appendChild(tdUrl);
    linksTbody.appendChild(tr);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();

  const url = urlInput.value.trim();
  const proxy = proxyInput.value.trim() || null;

  scrapeBtn.disabled = true;
  resultsSection.classList.add('hidden');
  currentLinks = [];
  showStatus('loading', '<span class="spinner"></span> Scraping, please wait…');

  try {
    const resp = await fetch('/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, proxy }),
    });

    const data = await resp.json();

    if (data.status === 'error') {
      showStatus('error', `Error: ${data.message}`);
    } else {
      currentLinks = data.links;
      const count = data.count;

      if (count === 0) {
        showStatus('success', 'No links found on that page.');
        resultsSection.classList.add('hidden');
      } else {
        showStatus('success', `Found ${count} link${count !== 1 ? 's' : ''}.`);
        resultCount.textContent = `${count} link${count !== 1 ? 's' : ''}`;
        renderTable(currentLinks);
        resultsSection.classList.remove('hidden');
      }
    }
  } catch (err) {
    showStatus('error', `Network error: ${err.message}`);
  } finally {
    scrapeBtn.disabled = false;
  }
});

exportBtn.addEventListener('click', () => {
  if (!currentLinks.length) return;

  const header = 'Title,URL\n';
  const rows = currentLinks.map((link) => {
    const title = `"${link.title.replace(/"/g, '""')}"`;
    const url = `"${link.url.replace(/"/g, '""')}"`;
    return `${title},${url}`;
  });
  const csvContent = header + rows.join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const objUrl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = objUrl;
  a.download = 'links.csv';
  a.click();
  URL.revokeObjectURL(objUrl);
});
