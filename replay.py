#!/usr/bin/env python3
import pygame, sys
import record
import json
from pygame.locals import *
import time
import argparse

# globals
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 140, 0)

DIMS_ARENA = (30, 20, 80)
DIMS_SCALE = 10
DIMS = (DIMS_ARENA[2] * DIMS_SCALE, DIMS_ARENA[0] * DIMS_SCALE)

EV_FRAME = pygame.USEREVENT + 1

SURFACE = None
FONT = None


def draw_text(position, text):
    text = FONT.render(text, True, WHITE, None)
    textRect = text.get_rect()
    textRect.centerx = position[0]
    textRect.centery = position[1]
    SURFACE.blit(text, textRect)


def refresh():
    SURFACE.fill(BLACK)
    pygame.draw.line(SURFACE, WHITE, (10, 10), (DIMS[0] - 10, 10), 2)
    pygame.draw.line(SURFACE, WHITE, (10, 10), (10, DIMS[1] - 10), 2)
    pygame.draw.line(
        SURFACE, WHITE, (10, DIMS[1] - 10), (DIMS[0] - 10, DIMS[1] - 10), 2
    )
    pygame.draw.line(
        SURFACE, WHITE, (DIMS[0] - 10, 10), (DIMS[0] - 10, DIMS[1] - 10), 2
    )
    g1 = ((20, SURFACE.get_rect().centery - 15), (20, SURFACE.get_rect().centery + 15))
    g2 = (
        (DIMS[0] - 20, SURFACE.get_rect().centery - 15),
        (DIMS[0] - 20, SURFACE.get_rect().centery + 15),
    )
    pygame.draw.line(SURFACE, BLUE, g1[0], g1[1], 2)
    pygame.draw.line(SURFACE, RED, g2[0], g2[1], 2)


def coord_transform(position):
    x = (position[0] + DIMS_ARENA[0] / 2) * DIMS_SCALE
    y = (position[1] + DIMS_ARENA[1] / 2) * DIMS_SCALE
    z = (position[2] + DIMS_ARENA[2] / 2) * DIMS_SCALE

    return (int(z), int(x))


def draw_player(player, color):
    position = coord_transform(player["position"])
    pygame.draw.circle(SURFACE, color, position, 10, 0)
    if player["possession"]:
        pygame.draw.circle(SURFACE, GREEN, position, 5, 0)
    position2 = (position[0], position[1] - 12)
    draw_text(position2, player["name"])


def draw_disc(disc):
    position = coord_transform(disc["position"])
    pygame.draw.circle(SURFACE, WHITE, position, 5, 0)


def draw_frame(frame):
    for team in frame["teams"]:
        color = RED if "ORANGE" in team["team"] else BLUE
        for player in team["players"]:
            draw_player(player, color)
    draw_disc(frame["disc"])
    draw_text((SURFACE.get_rect().centerx, 20), frame["game_clock_display"])
    draw_text((20, 20), str(frame["teams"][0]["stats"]["points"]))
    draw_text((DIMS[0] - 20, 20), str(frame["teams"][1]["stats"]["points"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="save file to play back")
    args = parser.parse_args()
    caprate, nframes, frames = record.load_game(args.file)

    pygame.init()

    SURFACE = pygame.display.set_mode(DIMS, 0, 32)
    FONT = pygame.font.SysFont(None, 20)
    pygame.display.set_caption("Echo VR Replayer")

    d = {"frames": frames}
    print("Capture rate was {} fps".format(caprate))
    print("Rendering frame every {} ms".format(round((1 / caprate) * 1000)))
    pygame.time.set_timer(EV_FRAME, round((1 / caprate) * 1000))
    idx = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == EV_FRAME:
                frame = d["frames"][idx]
                idx += 1
                if idx >= nframes:
                    pygame.quit()
                    sys.exit()
                refresh()
                draw_frame(frame)
                pygame.display.update()
