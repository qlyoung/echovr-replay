#!/usr/bin/env python3

# Game capture for Echo Arena.
# Copyright (C) 2019 Quentin Young
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA 02110-1301 USA

import aiohttp
import argparse
import asyncio
import gzip
import json
import pprint
import sys
import time

CAPRATE_HZ = 60.0
CONCURRENCY = 4
MINSAVETIME = 5


class EchoCapture(object):
    recordstates = ["playing", "score", "round_start", "round_over"]

    def __init__(self, caprate, concurrency, greed, minsavetime):
        self.caprate = float(caprate)
        self.concurrency = concurrency
        self.greed = greed
        self.minsavetime = minsavetime

        self.frames = []
        self.laststate = "none"
        self.state = "none"
        self.lastclock = 0.0
        self.totalframetime = 0.0

    def save_game(self):
        fname = ""
        for team in self.frames[0]["teams"]:
            for player in team["players"]:
                fname += player["name"] + "_"
            fname += "VS_"
        fname = fname[:-4] + ".json.gz"

        # the +1 is to avoid a /0 in the initial case, and the branch to check for it
        actual_caprate = 1.0 / (self.totalframetime / (len(self.frames) + 1))
        out = {
            "caprate": actual_caprate,
            "nframes": len(self.frames),
            "frames": self.frames,
        }

        with gzip.open(fname, mode="w+") as save:
            save.write(json.dumps(out).encode(encoding="UTF-8"))

        return (fname, out)

    def check_save(self):
        save = self.totalframetime >= self.minsavetime
        if save:
            print("\nSaving game...", end="", flush=True)
            (sname, out) = self.save_game()
            del out["frames"]
            print("Done.")
            pprint.pprint(out)
            print("Saved {} frames to {}\n".format(len(self.frames), sname))
        else:
            print("\nSkipping save, less than 5 seconds of data")

        return save

    async def rx_frame(self):
        resp = await self.session.get("http://127.0.0.1/session")
        if resp.content_type != "application/json":
            return

        frame = await resp.json()
        self.laststate = self.state
        self.state = frame["game_status"]

        if self.state != self.laststate and not (
            self.state == "post_match" and len(self.frames) == 0
        ):
            print("\n{} -> {}".format(self.laststate, self.state.strip()))

        if self.state == "post_match":
            return

        if self.state in EchoCapture.recordstates:
            currtime = time.time()
            if self.laststate not in EchoCapture.recordstates:
                self.lastclock = currtime - (1.0 / self.caprate)
            elapsed = currtime - self.lastclock
            cfg_min_elapsed = 1.0 / self.caprate
            min_elapsed = cfg_min_elapsed - self.greed

            if elapsed >= min_elapsed:
                self.lastclock = currtime
                self.totalframetime += elapsed
                # the +1 is to avoid a /0 in the initial case, and the branch to check for it
                avg_ft = self.totalframetime / (len(self.frames) + 1)
                self.frames.append(frame)
                if (len(self.frames) % 3) == 0:
                    sys.stdout.write(
                        "\rCaptured frame {} ({:.2f} avg fps ({:.9f} curr), min {:.6f}, cfg {:.6f})".format(
                            len(self.frames),
                            1.0 / avg_ft,
                            1.0 / elapsed,
                            min_elapsed,
                            cfg_min_elapsed,
                        )
                    )
                    sys.stdout.flush()

    async def capture(self):
        async with aiohttp.ClientSession() as s:
            self.session = s

            while self.state != "post_match":
                await asyncio.gather(
                    *[
                        asyncio.create_task(self.rx_frame())
                        for _ in range(1, self.concurrency)
                    ]
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--framerate",
        type=float,
        help="Target capture framerate; default 60 fps",
        default=CAPRATE_HZ,
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        help="Number of concurrent API calls; default 4",
        default=CONCURRENCY,
    )
    parser.add_argument(
        "-m",
        "--minsavetime",
        type=float,
        help="Minimum length of time that must be captured in order for a capture to be eligible for saving; default 5s",
        default=MINSAVETIME,
    )
    args = parser.parse_args()

    cfg_min_elapsed = 1.0 / args.framerate
    greed = cfg_min_elapsed / 10.0
    min_elapsed = cfg_min_elapsed - greed

    print("Capture rate:   {} fps".format(args.framerate))
    print("Greed:          {:.6f} sec".format(greed))
    print("Min frame time: {:.6f} sec".format(min_elapsed))
    print("Min save time:  {} sec".format(args.minsavetime))
    print("Concurrency:    {} req".format(args.concurrency))

    while True:
        currcap = EchoCapture(
            caprate=args.framerate,
            concurrency=args.concurrency,
            greed=greed,
            minsavetime=args.minsavetime,
        )

        try:
            asyncio.run(currcap.capture())
        except KeyboardInterrupt:
            print("\nCapture interrupted, cleaning up and exiting...")
            currcap.check_save()
            break
        except ConnectionError:
            print("\nCouldn't connect to Echo client")
            currcap.check_save()
            break

        # if we got zero frames, we're probably waiting on a match to start
        if len(currcap.frames) > 0:
            try:
                currcap.check_save()
            except KeyboardInterrupt:
                break
