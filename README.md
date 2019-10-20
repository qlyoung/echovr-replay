echovr-replay
=============

Game capture and 2D replay for Echo Arena.

Installation
------------
For `record.py` you need:
- aiohttp

For `replay.py` you need:
- pygame

Requires Python >= 3.6.

Recording
---------

```
record.py [-h] [-f FRAMERATE] [-c CONCURRENCY] [-m MINSAVETIME]
```
This will start recording the current game immediately. It saves games when the
current game ends and Echo VR switches to a different game. If you hit ^C at
any time it will save what it has captured and then quit.

`-f` - target frame capture rate. Because the API is tied to the game loop,
       hitting this value will usually require tweaking various things. See the
       section on this below.

       Note that the capture rate recorded in the save file is the actual
       achieved rate, not the target rate.

`-c` - number of concurrent API requests to make. Adjusting this has
       counterintuitive effects. See the section on this below.

`-m` - minimum number of seconds that must be captured for a save file to be
       written to disk. Default 5.

### Factors that influence capture rate

A variety of factors influence the achieved capture rate.

* GPU vsync - if this is on, for various reasons Echo, and consequently your
  API capture, will usually end up locked to the desktop display refresh rate.
  Turn it off in your GPU settings if you want to capture above that rate.
* GPU perf - Echo's maximum framerate is determined by how good your GPU is.
* Concurrency - concurrent API requests *will* increase frame times for the
  game itself. 64 concurrent requests drop it to below 30fps on my R7 1800x /
  1080ti.
* Num. CPU cores - can't tweak this, but it impacts what various `-c` values
  do.

 The best thing to do is to keep `-f` fixed, start with `-c 2`, and increase it
 by 2 until the desired rate is reached. Keep in mind that the achieved rate
 does not vary linearly with `-c` value, e.g. `-f 90 -c 2` may yield 60fps, `-f
 90 -c 4` 30fps, and `-f 90 -c 6` 90fps.

### Save Format

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

Loading the save file is trivial, e.g in Python:

```
import gzip

with gzip.open("mysavefile.json.gz", "r") as f:
    savedgame = json.load(f)
```


2D Replay
---------

```
./replay.py SAVEFILE
```

This should open a pygame window with a cute 2D replay of the captured game.

Possession is indicated with a green circle inside the possessing player's
circle. Goal positions are approximate.

3D Replay
---------
Currently probably broken.
