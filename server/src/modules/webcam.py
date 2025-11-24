import json
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
import av

import lib.modules as m
from lib.config import CONFIG
CONFIG = CONFIG["modules"]["webcam"]

class V4L2Track(VideoStreamTrack):
    """Minimal VideoStreamTrack from V4L2 device with safe stop on error."""

    def __init__(self, device: str):
        super().__init__()
        self.container = av.open(device, format="v4l2", options=CONFIG["camera"])
        self.stream = self.container.streams.video[0]
        m.log.info(f"Webcam opened: {self.stream.width}x{self.stream.height} @ {self.stream.average_rate}")

    async def recv(self) -> av.VideoFrame:
        while True:
            try:
                if not self.container:
                    raise RuntimeError("Container is closed")
                for packet in self.container.demux(self.stream):
                    for frame in packet.decode():
                        if not isinstance(frame, av.VideoFrame):
                            continue
                        if self.stream.time_base is not None:
                            frame.pts = int(frame.time * self.stream.time_base.denominator)
                        frame.time_base = self.stream.time_base
                        return frame
            except Exception as err:
                m.log.error("Trying to stop camera, because error: " + str(err))
                # ensure we release the camera and mark the track stopped on error
                try:
                    self.stop()
                except Exception as err:
                    m.log.error("Stopping did not work: " + str(err))
                raise
            await asyncio.sleep(0)

    def stop(self):
        if self.container:
            self.container.close()
            self.container = None
        super().stop()


async def stream_webcam(parameter) -> str:
    """Handle WebRTC with single request/response (non-trickle ICE)"""
    m.log.info("Trying to start camera stream")
    try:
        # Parse client offer
        data = json.loads(parameter)

        if data["type"] != "offer":
            return json.dumps({"error": "Expected offer"})

        # Create peer connection
        pc = RTCPeerConnection()
        @pc.on("connectionstatechange")
        async def _on_connectionstatechange():
            if pc.connectionState in ("disconnected", "failed"):
                m.log.info("disconnected or failed connection")
                # Stop all tracks and close peer connection on bad state
                for sender in pc.getSenders():
                    if sender.track:
                        sender.track.stop()
                await pc.close()

        pc.addTrack(V4L2Track(data.get("device", "/dev/video0")))

        # Get SDP and replace mDNS if client IP provided
        sdp = data["sdp"]
        if data.get("clientIp"):
            import re
            client_ip = data["clientIp"]
            m.log.info(f"Replacing .local addresses with {client_ip}")
            # Replace all .local addresses with the actual client IP
            sdp = re.sub(r'[\w-]+\.local', client_ip, sdp)

        # Set remote description (client's offer) - now with real IPs
        await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type="offer"))

        # Create answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        # Wait for ICE gathering to complete (vanilla ICE)
        while pc.iceGatheringState != "complete":
            await asyncio.sleep(0.01)

        # Return answer with complete SDP (including all ICE candidates)
        pc_sdp = pc.localDescription.sdp
        m.log.debug("pc.connectionState: " + pc_sdp)
        return json.dumps({
            "type": "answer",
            "sdp": pc_sdp
        })

    except Exception as e:
        m.log.error(f"Closing because of WebRTC error: {e}")
        await pc.close()
        return json.dumps({"error": str(e)})


m.register("webcam", stream_webcam)
