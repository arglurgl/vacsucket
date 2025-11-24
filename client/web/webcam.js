let ws = null;
let pc = null;
const elements = {
    video: document.getElementById('video'),
    status: document.getElementById('status'),
    connectBtn: document.getElementById('connectBtn'),
    disconnectBtn: document.getElementById('disconnectBtn'),
    wsUrl: document.getElementById('wsUrl'),
    device: document.getElementById('device'),
    clientIp: document.getElementById('clientIp'),
    stunServer: document.getElementById('stunServer')
};

function updateStatus(msg) {
    elements.status.textContent = `Status: ${msg}`;
    console.log(msg);
}

function toggleButtons(connected) {
    elements.connectBtn.disabled = connected;
    elements.disconnectBtn.disabled = !connected;
}

async function waitForEvent(target, event, condition = null) {
    return new Promise((resolve) => {
        if (condition && condition()) {
            resolve();
            return;
        }
        const handler = () => {
            if (!condition || condition()) {
                target.removeEventListener(event, handler);
                resolve();
            }
        };
        target.addEventListener(event, handler);
    });
}

async function connect() {
    toggleButtons(true);
    updateStatus('Creating WebRTC connection...');

    try {
        // Build ICE servers array
        const iceServers = [];
        const stunUrl = elements.stunServer.value.trim();
        if (stunUrl) {
            iceServers.push({ urls: stunUrl });
        }

        pc = new RTCPeerConnection({ iceServers });

        pc.ontrack = (e) => {
            updateStatus('Receiving video');
            elements.video.srcObject = e.streams[0];
        };

        pc.onconnectionstatechange = () => {
            console.log('Connection state:', pc.connectionState);
            if (pc.connectionState === 'connected') {
                updateStatus('Connected');
            } else if (pc.connectionState === 'failed') {
                updateStatus('Connection failed');
                disconnect();
            }
        };

        const offer = await pc.createOffer({
            offerToReceiveVideo: true,
            offerToReceiveAudio: false
        });
        await pc.setLocalDescription(offer);

        // Vanilla ICE: wait for all candidates before sending
        updateStatus('Gathering ICE candidates...');
        if (pc.iceGatheringState !== 'complete') {
            await waitForEvent(pc, 'icegatheringstatechange',
                () => pc.iceGatheringState === 'complete');
        }

        updateStatus('Connecting to server...');
        ws = new WebSocket(elements.wsUrl.value);
        await waitForEvent(ws, 'open');

        ws.send('webcam ' + JSON.stringify({
            type: 'offer',
            sdp: pc.localDescription.sdp,
            device: elements.device.value,
            clientIp: elements.clientIp.value.trim() || null
        }));

        const response = await new Promise((resolve) => {
            ws.onmessage = (e) => resolve(e.data);
        });

        const answer = JSON.parse(response);
        if (answer.error) throw new Error(answer.error);

        await pc.setRemoteDescription(new RTCSessionDescription(answer));
        updateStatus('Waiting for connection...');

    } catch (e) {
        updateStatus(`Error: ${e.message}`);
        console.error(e);
        disconnect();
    }
}

function disconnect() {
    if (pc) {
        pc.close();
        pc = null;
    }
    if (ws) {
        ws.close();
        ws = null;
    }
    elements.video.srcObject = null;
    toggleButtons(false);
    updateStatus('Disconnected');
}

elements.connectBtn.addEventListener('click', connect);
elements.disconnectBtn.addEventListener('click', disconnect);
window.addEventListener('beforeunload', disconnect);
