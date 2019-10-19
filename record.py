#!/usr/bin/env python3

import requests
import time
import json
import pprint
import gzip
import sys
import argparse
import pprint

import aiohttp
import asyncio


def save_game(frames, caprate):
    """
    Save time-ordered list of API frames as a gzipped json file.

    Format:
        {
            "caprate": <float>,
            "nframes": <int>,
            "frames": [
                <frame0>,
                <frame1>,
                ...
                <frameN>
            ]
        }

    Each frame is exactly as it was retrieved from the Echo VR API.

    :param frames: list of time-ordered JSON frames
    :param caprate: capture rate of frames in hz
    :return: name of save file
    """
    # build name
    fname = ""
    for team in frames[0]["teams"]:
        for player in team["players"]:
            fname += player["name"] + "_"
        fname += "VS_"
    # cut the last _VS_ out of the name
    fname = fname[:-4] + ".json.gz"

    out = {"caprate": caprate, "nframes": len(frames), "frames": frames}

    with gzip.open(fname, mode="w+") as save:
        save.write(json.dumps(out).encode(encoding="UTF-8"))

    return fname

class RecordState(object):
    frames = []
    saved = True
    laststate = "none"
    state = "none"
    framecount = 0
    clock0 = 0
    lastclock = 0
    connected = False

    recordstates = ["playing", "score", "round_start"]

    def __init__(self, caprate):
        self.caprate = caprate
        self.actual_caprate = self.caprate;

    
async def rx_frame(session, state):
    try:
        resp = await session.get("http://127.0.0.1/session")
    except ConnectionError:
        print("Couldn't connect to Echo client")
        exit()

    try:
        frame = await resp.json()
        state.laststate = state.state
        state.state = frame["game_status"]
    except:
        exit()

    if state.state != state.laststate:
        print("\n{} -> {}".format(state.laststate, state.state))
        state.lastclock = time.time()

    if not state.connected:
        state.connected = True
        print("Connected to Echo VR")

    if state.state == "post_match":
        if not state.saved:
            if len(state.frames) > state.caprate * 5:
                print("\nSaving game...")
                sname = save_game(state.frames, state.actual_caprate)
                print("\nSaved {} frames to {}\n".format(len(state.frames), sname))
            else:
                print("\nSkipping save, less than 5 seconds of data")
            state.frames = []
            state.framecount = 0
            state.saved = True
            state.actual_caprate = state.caprate
            state.clock0 = 0
    elif state.state in RecordState.recordstates:
        if state.saved:
            state.saved = False
            state.clock0 = time.time()
            state.lastclock = time.time()

        # the most ghetto clock on the face of the earth
        state.elapsed = time.time() - state.lastclock
        if state.elapsed >= 1.0 / caprate - 0.001:
            state.lastclock = time.time()
            state.framecount += 1
            state.actual_caprate = float(state.framecount) / (time.time() - state.clock0)
            state.frames.append(frame)
            if (state.framecount % 3) == 0:
                sys.stdout.write(
                    "\rCaptured frame {} ({:.2f} fps)".format(
                        state.framecount, state.actual_caprate
                    )
                )
                sys.stdout.flush()


async def capture(state, session=None):
    """
    Capture game.

    :param session: requests session to use
    :param caprate: fps to capture
    """
    session = session if session is not None else aiohttp.ClientSession()

    try:
        while True:
            try:
                await asyncio.gather(*[asyncio.create_task(rx_frame(session, state)) for i in range(1, 5)])
            except ConnectionError:
                print("Couldn't connect to Echo client")
                exit()

    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt")

    if len(state.frames) > 0:
        sname = save_game(state.frames, state.actual_caprate)
        print("\nSaved {} frames to {}\n".format(len(state.frames), sname))


CAPRATE_HZ = 60.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--framerate",
        type=float,
        help="set capture framerate",
        default=CAPRATE_HZ,
    )
    args = parser.parse_args()

    caprate = args.framerate
    print("Requested caprate: {}".format(caprate))
    asyncio.run(capture(RecordState(caprate)))
