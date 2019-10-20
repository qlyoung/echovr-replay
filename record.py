#!/usr/bin/env python3

import requests
import time
import json
import pprint
import gzip
import sys
import argparse
import pprint


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


def capture(caprate, session=None):
    """
    Capture game.

    :param session: requests session to use
    :param caprate: fps to capture
    """
    caprate = float(caprate)
    session = session if session is not None else requests.session()

    frames = []
    saved = True
    laststate = "none"
    state = "none"
    framecount = 0
    clock0 = 0
    actual_caprate = caprate
    lastclock = 0

    recordstates = ["playing", "score", "round_start"]

    try:
        while True:
            result = session.get("http://127.0.0.1/session")
            trash = result.content

            try:
                # ignore cute null byte
                frame = json.loads(result.text)
                laststate = state
                state = frame["game_status"]
            except:
                continue

            if state == "post_match":
                if not saved:
                    if len(frames) > caprate * 5:
                        print("\nSaving game...")
                        sname = save_game(frames, actual_caprate)
                        print("\nSaved {} frames to {}\n".format(len(frames), sname))
                    else:
                        print("\nSkipping save, less than 5 seconds of data")
                    frames = []
                    framecount = 0
                    saved = True
                    actual_caprate = caprate
                    clock0 = 0
            elif state in recordstates:
                if saved:
                    saved = False
                    clock0 = time.time()
                    lastclock = time.time()

                # the most ghetto clock on the face of the earth
                elapsed = time.time() - lastclock
                if elapsed >= 1.0 / caprate - 0.001:
                    lastclock = time.time()
                    framecount += 1
                    actual_caprate = float(framecount) / (time.time() - clock0)
                    frames.append(frame)
                    sys.stdout.write(
                        "\rCaptured frame {} ({:.2f} fps)".format(
                            framecount, actual_caprate
                        )
                    )
                    sys.stdout.flush()

            if state != laststate:
                print("\n{} -> {}".format(laststate, state))

    except:
        print("\nCaught exception")

    if len(frames) > 0:
        sname = save_game(frames, actual_caprate)
        print("\nSaved {} frames to {}\n".format(len(frames), sname))


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
    capture(caprate)
