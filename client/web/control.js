// Configuration
const REPEAT_INTERVAL_MS = 100; // Time between repeated commands when holding button/key

let controlWs = null;
let keyboardCaptureEnabled = false;
let statsTimer = null;

const controlElements = {
    status: document.getElementById('controlStatus'),
    connectBtn: document.getElementById('controlConnectBtn'),
    disconnectBtn: document.getElementById('controlDisconnectBtn'),
    wsUrl: document.getElementById('controlWsUrl'),
    directionBtns: document.querySelectorAll('.direction-btn'),
    captureToggle: document.getElementById('captureToggle'),
    captureStatus: document.getElementById('captureStatus'),
    captureText: document.getElementById('captureText')
};

function updateControlStatus(msg) {
    controlElements.status.textContent = `Status: ${msg}`;
    console.log('Control:', msg);
}

function toggleControlButtons(connected) {
    controlElements.connectBtn.disabled = connected;
    controlElements.disconnectBtn.disabled = !connected;
}

function sendCommand(command) {
    if (controlWs && controlWs.readyState === WebSocket.OPEN) {
        controlWs.send(command);
        console.log('Sent:', command);
    } else {
        updateControlStatus('Not connected');
    }
}

function connectControl() {
    toggleControlButtons(true);
    updateControlStatus('Connecting...');

    try {
        controlWs = new WebSocket(controlElements.wsUrl.value);

        controlWs.onopen = () => {
            updateControlStatus('Connected');
            requestStats();
            statsTimer = setInterval(requestStats, 3000);
        };

        controlWs.onclose = () => {
            updateControlStatus('Disconnected');
            toggleControlButtons(false);
            clearInterval(statsTimer);
            statsTimer = null;
        };

        controlWs.onerror = (e) => {
            updateControlStatus('Connection error');
            console.error('WebSocket error:', e);
        };

        controlWs.onmessage = (e) => {
            console.log('Received:', e.data);
            try {
                const payload = JSON.parse(e.data);
                if (Array.isArray(payload) && typeof payload[0] === 'object') {
                    renderWifiStats(payload[0]);
                }
            } catch { /* plain-text message */ }
        };

    } catch (e) {
        updateControlStatus(`Error: ${e.message}`);
        console.error(e);
        disconnectControl();
    }
}

function disconnectControl() {
    if (controlWs) {
        controlWs.close();
        controlWs = null;
    }
    toggleControlButtons(false);
    updateControlStatus('Disconnected');
}

// Keyboard capture toggle
function setKeyboardCapture(enabled) {
    keyboardCaptureEnabled = enabled;
    controlElements.captureStatus.textContent = enabled ? '🟢' : '🔴';
    controlElements.captureText.textContent = enabled ? 'ON' : 'OFF';
    controlElements.captureToggle.style.background = enabled ? '#4CAF50' : '#555';
}

controlElements.captureToggle.addEventListener('click', () => {
    setKeyboardCapture(!keyboardCaptureEnabled);
});

// Button hold/repeat handlers
const activeButtons = new Map(); // button element -> interval ID

controlElements.directionBtns.forEach(btn => {
    const command = btn.getAttribute('data-command');

    // Mouse events
    btn.addEventListener('mousedown', () => {
        if (activeButtons.has(btn)) return;

        sendCommand(command);
        const intervalId = setInterval(() => sendCommand(command), REPEAT_INTERVAL_MS);
        activeButtons.set(btn, intervalId);
    });

    btn.addEventListener('mouseup', () => {
        if (activeButtons.has(btn)) {
            clearInterval(activeButtons.get(btn));
            activeButtons.delete(btn);
        }
    });

    btn.addEventListener('mouseleave', () => {
        if (activeButtons.has(btn)) {
            clearInterval(activeButtons.get(btn));
            activeButtons.delete(btn);
        }
    });

    // Touch events for mobile
    btn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (activeButtons.has(btn)) return;

        sendCommand(command);
        const intervalId = setInterval(() => sendCommand(command), REPEAT_INTERVAL_MS);
        activeButtons.set(btn, intervalId);
    });

    btn.addEventListener('touchend', (e) => {
        e.preventDefault();
        if (activeButtons.has(btn)) {
            clearInterval(activeButtons.get(btn));
            activeButtons.delete(btn);
        }
    });
});

controlElements.connectBtn.addEventListener('click', connectControl);
controlElements.disconnectBtn.addEventListener('click', disconnectControl);

// Keyboard controls
const keyMap = {
    'w': 's f',
    'W': 's f',
    'ArrowUp': 's f',
    's': 's b',
    'S': 's b',
    'ArrowDown': 's b',
    'a': 's l',
    'A': 's l',
    'ArrowLeft': 's l',
    'd': 's r',
    'D': 's r',
    'ArrowRight': 's r',
    '1': 'a p gato-miau.mp3',
    '2':'a p miau-loco-rene.mp3'
};

const activeKeys = new Map(); // key -> interval ID

document.addEventListener('keydown', (e) => {
    // ESC disables keyboard capture
    if (e.key === 'Escape') {
        setKeyboardCapture(false);
        // Clear any active keys
        activeKeys.forEach((intervalId) => clearInterval(intervalId));
        activeKeys.clear();
        return;
    }

    // Don't capture if in input field or capture is disabled
    if (!keyboardCaptureEnabled ||
        e.target.tagName === 'INPUT' ||
        e.target.tagName === 'TEXTAREA') {
        return;
    }

    const command = keyMap[e.key];
    if (command) {
        e.preventDefault();

        // Prevent repeated keydown events while held
        if (activeKeys.has(e.key)) return;

        sendCommand(command);
        const intervalId = setInterval(() => sendCommand(command), REPEAT_INTERVAL_MS);
        activeKeys.set(e.key, intervalId);
    }
});

document.addEventListener('keyup', (e) => {
    if (activeKeys.has(e.key)) {
        clearInterval(activeKeys.get(e.key));
        activeKeys.delete(e.key);
    }
});

// Clear all intervals on cleanup
window.addEventListener('beforeunload', () => {
    activeButtons.forEach((intervalId) => clearInterval(intervalId));
    activeKeys.forEach((intervalId) => clearInterval(intervalId));
    disconnectControl();
});

// ── WiFi Stats ────────────────────────────────────────────────

function requestStats() {
    sendCommand('stats wifi');
}

function renderWifiStats(data) {
    const panel = document.getElementById('wifiStats');
    if (!panel) return;

    const ifaceKey = Object.keys(data)[0];
    const iface    = data[ifaceKey];
    const name     = ifaceKey.replace(/:$/, '');
    const { Quality: q, Discarded_packets: dp, Missed_beacon: mb, status } = iface;

    const linkPct = Math.min(100, Math.round((q.link / 70) * 100));
    const sigPct  = Math.max(0, Math.min(100, Math.round(((q.level + 100) / 70) * 100)));

    const [color, label] =
        q.level >= -50 ? ['#4CAF50', 'Excellent'] :
        q.level >= -60 ? ['#8BC34A', 'Good']      :
        q.level >= -70 ? ['#FFC107', 'Fair']       :
                         ['#f44336', 'Poor'];

    const noiseStr   = q.noise <= -255 ? 'N/A' : `${q.noise} dBm`;
    const totalDrops = Object.values(dp).reduce((a, v) => a + v, 0) + mb;

    panel.innerHTML = `
        <div class="ws-header">
            <span>📶</span>
            <span class="ws-iface">${name}</span>
            <span class="ws-quality" style="color:${color}">${label}</span>
            <span class="ws-time">${new Date().toLocaleTimeString()}</span>
        </div>
        <div class="ws-bars">
            <div class="ws-bar-row">
                <span class="ws-bar-label">Link</span>
                <div class="ws-bar-track">
                    <div class="ws-bar-fill" style="width:${linkPct}%;background:${color}"></div>
                </div>
                <span class="ws-bar-val">${q.link} / 70</span>
            </div>
            <div class="ws-bar-row">
                <span class="ws-bar-label">Signal</span>
                <div class="ws-bar-track">
                    <div class="ws-bar-fill" style="width:${sigPct}%;background:${color}"></div>
                </div>
                <span class="ws-bar-val">${q.level} dBm</span>
            </div>
        </div>
        <div class="ws-meta">
            <span>Noise <strong>${noiseStr}</strong></span>
            <span>Status <strong class="mono">0x${status}</strong></span>
            <span class="${totalDrops > 0 ? 'ws-warn' : ''}">Dropped <strong>${totalDrops}</strong></span>
        </div>
        <div class="ws-subheader">Discarded packets</div>
        <div class="ws-packets">
            ${[['nwid', dp.nwid], ['crypt', dp.crypt], ['frag', dp.frag],
               ['retry', dp.retry], ['misc', dp.misc], ['beacon', mb]
              ].map(([k, v]) => `
                <span class="ws-pkt ${v > 0 ? 'ws-pkt-bad' : ''}">
                    <span class="ws-pkt-name">${k}</span>
                    <span class="ws-pkt-val">${v}</span>
                </span>`).join('')}
        </div>`;
}
