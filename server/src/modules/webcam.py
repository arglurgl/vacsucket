import json
import asyncio
import platform
from typing import Optional

from aiortc import (
    MediaStreamTrack,
    RTCPeerConnection,
    RTCSessionDescription,
)
from aiortc.contrib.media import (
    MediaPlayer,
    #MediaRelay
)

import libs.modules as m
from libs.config import CONFIG
CONFIG = CONFIG["modules"]["webcam"]


def webcam_track(play_from: str = "",
                 options: dict = {"framerate": "30", "video_size": "640x480"}
                ) -> Optional[MediaStreamTrack]:

    # In order to serve the same webcam to multiple users we make use of
    # a `MediaRelay`. The webcam will stay open, so it is our responsability
    # to stop the webcam when the application shuts down in `on_shutdown`.
    os = platform.system()
    match os:
        case "Linux":
            file = play_from if play_from else "/dev/video0"
            webcam = MediaPlayer(file,
                                    format="v4l2",
                                    options=options)

        case "Darwin":
            file = play_from if play_from else "default:none"
            webcam = MediaPlayer(file,
                                    format="avfoundation",
                                    options=options)

        case "Windows":
            file = play_from if play_from else "video=Integrated Camera"
            webcam = MediaPlayer(file,
                                    format="dshow",
                                    options=options)

        case _:
            file = play_from if play_from else "/dev/video0"
            webcam = MediaPlayer("/dev/video0",
                                    format="v4l2",
                                    options=options)

    #relay = MediaRelay()
    #return relay.subscribe(webcam.video)
    return webcam.video



async def stream_webcam(parameter) -> str:
    """Handle WebRTC with single request/response (non-trickle ICE)"""
    m.log.info("Trying to start camera stream")
    pc = RTCPeerConnection()

    try:
        # Parse client offer
        data = json.loads(parameter)

        if data["type"] != "offer":
            return json.dumps({"error": "Expected offer"})

        local_track = webcam_track(data.get("device", "/dev/video0"),
                                   options=CONFIG["camera"])


        # Create peer connection
        @pc.on("connectionstatechange")
        async def _on_connectionstatechange():
            if pc.connectionState in ("disconnected", "failed"):
                m.log.info("disconnected or failed connection")
                # Stop all tracks and close peer connection on bad state
                for sender in pc.getSenders():
                    if sender.track:
                        sender.track.stop()
                await pc.close()


        if local_track is not None:
            pc.addTrack(local_track)
        else:
            raise ValueError("Track must not be None")

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
