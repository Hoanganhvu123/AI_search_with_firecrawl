// ═══════════════════════════════════════════════════════════
// FireStation — Fireplexity-style SSE Chat (Vanilla JS)
// ═══════════════════════════════════════════════════════════

const $ = id => document.getElementById(id);
const form = $('searchForm'), input = $('searchInput'), submitBtn = $('submitBtn');
const chatContainer = $('chatContainer'), emptyHero = $('emptyHero');
const chatScrollArea = $('chatScrollArea'), plusMenu = $('plusMenu');
const crawlBar = $('crawlBar'), crawlInput = $('crawlInput');
const modeLabel = $('modeLabel');

let currentMode = 'quick', crawlActive = false, isStreaming = false;

// ─── Helpers ────────────────────────────────────────────────
function esc(t) { var d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
function scrollBottom() { chatScrollArea.scrollTop = chatScrollArea.scrollHeight; }
function favicon(url) { return 'https://www.google.com/s2/favicons?sz=64&domain_url=' + encodeURIComponent(url); }
function domain(url) { try { return new URL(url).hostname.replace('www.',''); } catch(e) { return url; } }

// ─── Auto-resize ────────────────────────────────────────────
input.addEventListener('input', function() { this.style.height = 'auto'; this.style.height = Math.min(this.scrollHeight, 150) + 'px'; });
input.addEventListener('keydown', function(e) { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); if (input.value.trim() && !isStreaming) form.dispatchEvent(new Event('submit')); } });

// ─── Mode toggle ────────────────────────────────────────────
window.toggleSearchMode = function() { currentMode = currentMode === 'quick' ? 'deep' : 'quick'; modeLabel.textContent = currentMode === 'quick' ? 'Quick' : 'Deep'; };
window.togglePlusMenu = function() { plusMenu.classList.toggle('open'); };
document.addEventListener('click', e => { if (!e.target.closest('#plusBtn') && !e.target.closest('#plusMenu')) plusMenu.classList.remove('open'); });
window.toggleCrawl = function(on) { crawlActive = on; crawlBar.classList.toggle('visible', on); if (on) crawlInput.focus(); else crawlInput.value = ''; document.querySelectorAll('.menu-item')[0].classList.toggle('active', on); plusMenu.classList.remove('open'); };
window.startNewChat = function() { chatContainer.innerHTML = ''; chatContainer.appendChild(emptyHero); emptyHero.style.display = 'flex'; toggleCrawl(false); };

// ─── Build source card (Fireplexity-style) ──────────────────
function buildSourceCard(item, idx) {
    var title = item.title || item.metadata?.title || domain(item.url);
    var chars = (item.markdown || item.content || '').length;
    return '<a href="' + item.url + '" target="_blank" class="source-card" style="animation-delay:' + (idx * 60) + 'ms">' +
        '<div class="source-card-top"><img src="' + favicon(item.url) + '" class="source-favicon" alt="" onerror="this.style.display=\'none\'">' +
        '<span class="source-domain">' + esc(domain(item.url)) + '</span></div>' +
        '<div class="source-title">' + esc(title) + '</div>' +
        '<div class="char-counter">' + (chars > 0 ? chars.toLocaleString() + ' chars' : '') + '</div></a>';
}

// ─── Build response container (Fireplexity layout) ──────────
function buildAssistantResponse() {
    var wrap = document.createElement('div');
    wrap.className = 'message assistant';

    // Mode badge
    var badge = document.createElement('div');
    badge.className = 'mode-badge ' + currentMode;
    badge.innerHTML = (currentMode === 'quick' ? '<i class="fa-solid fa-bolt"></i> Quick Search' : '<i class="fa-solid fa-flask"></i> Deep Research');
    wrap.appendChild(badge);

    // Status
    var status = document.createElement('div');
    status.className = 'loading-indicator';
    status.innerHTML = '<div class="spinner"></div><span class="status-text">Searching the web...</span>';
    wrap.appendChild(status);

    // Sources section (hidden initially)
    var srcSection = document.createElement('div');
    srcSection.className = 'sources-section';
    srcSection.style.display = 'none';
    srcSection.innerHTML = '<div class="section-header"><div class="section-header-left"><i class="fa-solid fa-file-lines"></i><h3>Sources</h3></div><div class="section-header-right"></div></div><div class="sources-grid"></div>';
    wrap.appendChild(srcSection);

    // Answer section (hidden initially)
    var ansSection = document.createElement('div');
    ansSection.className = 'answer-section';
    ansSection.style.display = 'none';
    ansSection.innerHTML = '<div class="section-header"><div class="section-header-left"><i class="fa-solid fa-sparkles"></i><h3>Answer</h3></div>' +
        '<div class="section-header-right"><button class="action-btn" onclick="copyAnswer(this)" title="Copy"><i class="fa-regular fa-copy"></i></button>' +
        '<button class="action-btn" onclick="rewriteAnswer()" title="Rewrite"><i class="fa-solid fa-rotate"></i></button></div></div>' +
        '<div class="markdown-body streaming-cursor"></div>';
    wrap.appendChild(ansSection);

    // Related section
    var relSection = document.createElement('div');
    relSection.className = 'related-section';
    relSection.style.display = 'none';
    relSection.innerHTML = '<div class="section-header"><div class="section-header-left"><i class="fa-solid fa-lightbulb"></i><h3>Related</h3></div></div><div class="follow-ups-list"></div>';
    wrap.appendChild(relSection);

    return {
        wrap: wrap,
        status: status,
        srcSection: srcSection,
        srcGrid: srcSection.querySelector('.sources-grid'),
        srcRight: srcSection.querySelector('.section-header-right'),
        ansSection: ansSection,
        mdBody: ansSection.querySelector('.markdown-body'),
        relSection: relSection,
        relList: relSection.querySelector('.follow-ups-list')
    };
}

// ─── Copy / Rewrite helpers ─────────────────────────────────
var lastFullAnswer = '';
window.copyAnswer = function(btn) {
    navigator.clipboard.writeText(lastFullAnswer);
    btn.classList.add('copied');
    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
    setTimeout(function() { btn.classList.remove('copied'); btn.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 2000);
};
window.rewriteAnswer = function() {
    // Grab last user query from history and resubmit
    if (historyItems.length > 0) { input.value = historyItems[0]; form.dispatchEvent(new Event('submit')); }
};

// ─── Submit handler with SSE streaming ──────────────────────
form.addEventListener('submit', async function(e) {
    e.preventDefault();
    var query = input.value.trim();
    if (!query || isStreaming) return;

    input.value = ''; input.style.height = 'auto';
    submitBtn.disabled = true; isStreaming = true;
    if (emptyHero) emptyHero.style.display = 'none';

    // User message
    var userMsg = document.createElement('div');
    userMsg.className = 'message user';
    userMsg.innerHTML = '<div class="message-bubble">' + esc(query) + '</div>';
    chatContainer.appendChild(userMsg);
    scrollBottom();

    // Assistant response container
    var r = buildAssistantResponse();
    chatContainer.appendChild(r.wrap);
    scrollBottom();

    try {
        var resp = await fetch('/firecrawl/search/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, sources: ['web', 'news'] })
        });
        if (!resp.body) throw new Error('No response body');

        var reader = resp.body.getReader();
        var decoder = new TextDecoder();
        var fullMd = '';
        lastFullAnswer = '';

        while (true) {
            var result = await reader.read();
            if (result.done) break;
            var lines = decoder.decode(result.value, { stream: true }).split('\n');

            for (var i = 0; i < lines.length; i++) {
                if (!lines[i].startsWith('data: ')) continue;
                try {
                    var d = JSON.parse(lines[i].slice(6));

                    if (d.type === 'status') {
                        r.status.querySelector('.status-text').textContent = d.message;

                    } else if (d.type === 'sources') {
                        // Hide loading, show sources with staggered animation
                        r.status.style.display = 'none';
                        var webItems = (d.web || []).slice(0, 8);
                        if (webItems.length > 0) {
                            r.srcSection.style.display = 'block';
                            var cardsHtml = '';
                            var showCount = Math.min(webItems.length, 5);
                            for (var j = 0; j < showCount; j++) {
                                cardsHtml += buildSourceCard(webItems[j], j);
                            }
                            r.srcGrid.innerHTML = cardsHtml;

                            // Extra sources count
                            if (webItems.length > 5) {
                                var extraHtml = '<span class="extra-count">+' + (webItems.length - 5) + ' more</span><div class="extra-favicons">';
                                for (var k = 5; k < Math.min(webItems.length, 10); k++) {
                                    extraHtml += '<img src="' + favicon(webItems[k].url) + '" alt="" onerror="this.style.display=\'none\'">';
                                }
                                extraHtml += '</div>';
                                r.srcRight.innerHTML = extraHtml;
                            }
                        }
                        scrollBottom();

                    } else if (d.type === 'chunk') {
                        // Show answer section, stream markdown
                        r.ansSection.style.display = 'block';
                        fullMd += d.content;
                        lastFullAnswer = fullMd;
                        r.mdBody.innerHTML = marked.parse(fullMd);
                        scrollBottom();

                    } else if (d.type === 'follow_ups') {
                        r.relSection.style.display = 'block';
                        var fhtml = '';
                        d.questions.forEach(function(q) {
                            fhtml += '<button class="follow-up-btn" onclick="submitFollowUp(\'' + q.replace(/'/g, "\\'") + '\')">' +
                                '<i class="fa-solid fa-plus"></i>' + esc(q) + '</button>';
                        });
                        r.relList.innerHTML = fhtml;
                        scrollBottom();

                    } else if (d.type === 'error') {
                        r.status.innerHTML = '<i class="fa-solid fa-circle-exclamation" style="color:var(--red)"></i><span style="color:var(--red)">' + esc(d.message) + '</span>';
                    }
                } catch (pe) { console.error('Parse:', pe); }
            }
        }

        // Done streaming
        r.mdBody.classList.remove('streaming-cursor');

        addHistoryItem(query);

    } catch (err) {
        console.error('Fetch:', err);
        r.status.innerHTML = '<i class="fa-solid fa-circle-exclamation" style="color:var(--red)"></i><span style="color:var(--red)">Connection error</span>';
    } finally {
        submitBtn.disabled = false; isStreaming = false; input.focus();
    }
});

// ─── Follow-up / suggestion ────────────────────────────────
window.submitFollowUp = function(q) { input.value = q; form.dispatchEvent(new Event('submit')); };
window.submitSuggestion = function(t) { input.value = t; form.dispatchEvent(new Event('submit')); };

// ─── History ────────────────────────────────────────────────
var historyItems = [];
function addHistoryItem(q) { historyItems.unshift(q); if (historyItems.length > 20) historyItems.pop(); renderHistory(); }
function renderHistory() {
    var s = $('historySection');
    var h = '<div class="history-label">Recent</div>';
    historyItems.forEach(function(q) {
        var short = q.length > 32 ? q.substring(0, 32) + '...' : q;
        h += '<button class="history-item" onclick="submitFollowUp(\'' + q.replace(/'/g, "\\'") + '\')"><i class="fa-regular fa-message"></i>' + esc(short) + '</button>';
    });
    s.innerHTML = h;
}

(async function() {
    try { var r = await fetch('/firecrawl/history'); if (r.ok) { var d = await r.json(); d.slice(0,10).forEach(function(i) { historyItems.push(i.query); }); renderHistory(); } } catch(e) {}
})();
