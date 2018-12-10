echovr-replay
=============

Game capture and 2D replay for Echo Arena.

https://my.mixtape.moe/zgjzid.mp4

Installation
============
For `record.py` you need:
- requests

For `replay.py` you need:
- pygame

Requires Python >= 3.3.

Usage
=====
Start Echo VR with `-http` and join a match.

Recording
---------

```
./record.py [--framerate FPS]
```

If you are running with `-spectatorstream` this will save games when the
current game ends and Echo VR switches to a different game. No idea how it
behaves in other scenarios. If you hit ^C at any time it will save what it has
captured and then quit.

The `--framerate` option limits the frame capture rate. There isn't much use
setting this over 60 as the capture loop isn't terribly optimized. When the
save file is written the true capture rate is used, not the one specified in
this argument.

Replay
------

```
./replay.py SAVEFILE
```

This should open a pygame window with a cute 2D replay of the captured game.
Since the game API currently says the disc is always at 0,0,0 the disc doesn't
move right now, but no code changes should be needed when this is fixed in the
API. Possession is indicated with a green circle inside the possessing player's
circle. Goal positions are approximate.


Save Format
===========

The save format is very simple. It is a gzipped plaintext JSON file, UTF-8
encoded. The JSON has the following format:

```
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
```

Each frame is exactly as it was retrieved from the Echo VR API. The `frames`
array is time-ordered.

- `caprate` is the capture rate of the save
- `nframes` is the length of the `frames` array
- `frameN` is the complete Nth API response

Reading a Save File
-------------------

```
import gzip

with gzip.open("mysavefile.json.gz", "r") as f:
    savedgame = json.load(f)
```
