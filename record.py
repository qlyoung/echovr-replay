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
    Save time-ordered list of JSON frames as a gzipped text file.

    Format:
        <caprate><LF>
        <nframes><LF>
        <frame 0><LF>
        <frame 1><LF>
        ...
        <frame N><LF>

    LF = linefeed = 0x0A
    caprate = float
    nframes = int

    Each frame is encoded as a minified JSON string.

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
    fname = fname[:-4] + ".gz"
    with gzip.open(fname, mode="w+") as save:
        save.write(str(caprate).encode(encoding="UTF-8"))
        save.write(b"\n")
        save.write(str(len(frames)).encode(encoding="UTF-8"))
        save.write(b"\n")
        for frame in frames:
            save.write(json.dumps(frame).encode(encoding="UTF-8"))
            save.write(b"\n")

    return fname


def load_game(savefilename):
    """
    Read a saved game file and return the saved game.

    :param savefilename: path to save file
    :return: 3-tuple (caprate, nframes, frames) where caprate is the framerate
    in hz, nframes is the number of frames and frames is a list of time-ordered
    JSON frames
    """

    with gzip.open(savefilename, mode="r") as savefile:
        contents = savefile.read().decode(encoding="UTF-8")
        split = contents.split("\n")[:-1]
        caprate = float(split[0])
        nframes = int(split[1])
        frames = list(map(json.loads, split[2:]))

    return (caprate, nframes, frames)


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
            result = session.get("http://localhost/session")
            trash = result.content

            try:
                # ignore cute null byte
                frame = json.loads(result.text[:-1])
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
    parser.add_argument("-l", "--load", type=str, help="Load save file")
    parser.add_argument(
        "-s", "--show", type=str, help="Show frames from save file (e.g. '-s 0,40,100')"
    )
    args = parser.parse_args()
    if args.load is not None:
        caprate, nframes, frames = load_game(args.load)
        print("Loaded '{}'".format(args.load))
        print("Framerate: {}".format(caprate))
        print("Frames: {}".format(nframes))
        if nframes != len(frames):
            print(
                "[!] Save file claims it has {} frames, but got {}".format(
                    nframes, len(frames)
                )
            )
        if args.show is not None:
            showframes = list(map(int, args.show.split(",")))
            for fidx in showframes:
                pprint.pprint(frames[fidx])
    else:
        caprate = args.framerate
        capture(caprate)
