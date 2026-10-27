# Storyboard skill for Claude

Turn a short-form video script into a storyboard: every line gets its own shot with a 9:16
frame, the on-screen text, an edit note and the sound, and the filming is grouped into
sittings. Then the storyboard becomes the prompt: you have Claude build every graphic one
shot at a time, straight off it.

![The example storyboard](example/claude-edits-my-videos/frames/out/contact-sheet.jpg)

## Install

Paste this into Claude Code:

```
Install this Claude skill for me: https://github.com/chefy3x/storyboard-skill. Copy the storyboard folder into ~/.claude/skills/.
```

Or by hand:

```bash
git clone https://github.com/chefy3x/storyboard-skill
cp -r storyboard-skill/storyboard ~/.claude/skills/
```

In the Claude app (claude.ai or Desktop), zip the `storyboard` folder and upload it under
Settings → Capabilities → Skills.

Rendering the frames needs Python 3 and Google Chrome (or Chromium / Edge). `pip install
pillow` adds the contact sheet.

## Use

Start a new session and paste your script:

```
Storyboard this script. It's a 45 second Reel. [paste your script]
```

You get a `storyboard/<video>/` folder with `storyboard.json`, a frame per shot and
`board.html`, the whole board on one page. Drop `frames/face.jpg` (a still of you) in the
folder and re-render to put your face in the face shots.

Then build from it:

```
Build shot 4 from the storyboard as a 9:16 motion graphic: match the frame, the on-screen text and the edit note.
```

## What's in it

- `storyboard/SKILL.md`: the method (how to split a script, which shot types, the safe zones)
- `storyboard/kit/frame-kit.css`: the building blocks for frames (headline, terminal, chat, table, face box)
- `storyboard/kit/render.py`: renders the frames, the contact sheet and the board
- `example/`: the storyboard for the video this came from

By [@palalneish](https://www.instagram.com/palalneish). MIT license.
