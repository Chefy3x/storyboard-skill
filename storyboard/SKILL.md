---
name: storyboard
description: >-
  Storyboard a short-form video (Reels, TikTok, Shorts) from its script: split the script
  into shots word for word, give every shot a 9:16 frame, the on-screen text, an edit note
  and the sound, and group the filming into sittings. Writes a storyboard folder with a
  board you can open in the browser, one PNG per frame and a contact sheet. Use when the
  user says "storyboard this", "make a storyboard", "turn this script into shots", "plan
  the shots", "shot list for this script", or has a finished script and is getting ready
  to film or edit. The finished storyboard doubles as the prompt for building the video's
  graphics one shot at a time. Do NOT use to write or rework the script itself.
---

# Storyboard

A storyboard is the shoot plan and the edit plan for one video. It's done when the user can
read it top to bottom, film each sitting, and hand every shot to the edit (or to Claude) with
a clear picture of what goes on screen, what the text says and what the sound is.

**Keep it lean.** Shots and sittings, nothing else. No arc diagram, no per-shot transitions,
no brand kit, no checklist. If the user wants more, they'll ask.

## The format

Every shot has:

| field | what it holds |
|---|---|
| `type` | `face` (talking to camera), `split` (screen on top, face in a rounded box below), `screen` (a screen recording), `graphic` (built in the edit), `b-roll` (real-world footage) |
| `vo` | the exact script words spoken over this shot |
| `on_screen_text` | text burned into the frame, usually blank |
| `edit_note` | one or two lines: what's on screen, what moves, the framing |
| `sfx` | a sound, usually blank |
| `thesis` | `true` on exactly one shot |
| `status` | `real` (the frame IS the footage), `stand-in` (shows the intent), `to-capture` (nothing yet) |

Timing comes from the VO at **3.4 words per second**. Never set it by hand.

Sittings group the shots by where they get filmed: `label`, `detail` (what to prep) and
`shots` (shot numbers).

## Steps

1. **Get the script.** Ask for it if it isn't in the conversation or a file. If the user
   names a target length, note it. Don't edit the script. If a line reads wrong, say so and
   let the user fix it.
2. **Split the script into shots, word for word.** Joined back together, the `vo` fields
   must equal the script exactly. Don't reword, trim or add a line.
   - **Cut where the picture changes,** not on sentence ends. A comma is a fine cut point.
   - **Aim for 2 to 6 seconds a shot** (7 to 20 words). Past about 8 seconds, split it,
     unless one continuous picture really carries the line.
   - **Shot 1 has the speaker's face in it** (a `face` or `split` shot). A face in the
     first second holds people.
   - **Mark exactly one `thesis` shot:** the line that says what the video is about.
   - **Last shot: the speaker's face saying the call to action.** If there's a comment
     keyword, it's spoken and lives in the captions, not as a big on-screen pill.
   - **Vary the type.** No three `face` shots in a row. Use `face` for claims, asides and
     the CTA; use `screen` for anything being shown.
3. **Fill the fields sparingly.**
   - `on_screen_text`: shot 1's headline, list numbers (`01 SCRIPT`), and at most one
     punchline. Blank everywhere else; captions carry the rest.
   - `edit_note`: what's on screen, what moves, and the framing (mid or close). Put privacy
     cues here too: blur emails, crop file paths that show a username.
   - `sfx`: two or three in the whole video, only where something lands (a ping on the
     open, a hit when something goes live).
4. **Group the shots into sittings by where they're filmed,** not by shot order.
   - **Face:** one sitting for every face shot plus the face half of every split.
   - **Screens:** one sitting per app or tool session, using the same real project all the
     way through.
   - **Away from the desk:** only if a b-roll shot needs it.
   - **`detail`:** what to prep (which project to open, what to have running, what to
     clear off the screen first).
5. **Write `storyboard.json`** in a `storyboard/<video-slug>/` folder in the user's working
   directory (ask if there's a better place):

   ```json
   {
     "title": "AI edits my videos",
     "target_seconds": 50,
     "shots": [
       {"type": "face", "vo": "My last couple of videos were all edited by Claude.",
        "on_screen_text": "CLAUDE EDITS MY VIDEOS", "edit_note": "Mid shot, headline holds 4s.",
        "sfx": "", "thesis": false, "status": "to-capture"}
     ],
     "sittings": [
       {"label": "Face", "detail": "Same shirt and light for every face line.", "shots": [1]}
     ]
   }
   ```

6. **Build a frame for every shot** (next section) as `frames/f01.html`, `frames/f02.html`,
   and so on. The number is the shot's position.
7. **Render:**

   ```bash
   python3 <this skill's folder>/kit/render.py storyboard/<video-slug>
   ```

   It renders `frames/out/fNN.png` at 540x960 with headless Chrome, a
   `frames/out/contact-sheet.jpg`, and `board.html`: every frame next to its VO, text,
   edit note, sound and timing, plus the sittings. It prints the runtime and the face vs
   screen seconds.
8. **Check the contact sheet,** then fix and re-render: text over a face, overlaps, text in
   the safe zones, anything private.
9. **Report back briefly:** shot count, runtime vs the target length, face vs screen
   seconds, and what's still to capture. Open `board.html` for the user.

## Frames

Use the most real source you can get, in this order:

1. **Real material.** A screenshot of the real site or app the shot features (headless
   Chrome or Playwright, 1440 wide for desktop, 390 for mobile), or a still from the user's
   own footage (`ffmpeg -ss <time> -i clip.mp4 -frames:v 1 still.jpg`). Put images in the
   `frames/` folder and reference them by file name.
2. **Built frames.** Write the frame as an HTML body fragment using the classes in
   [kit/frame-kit.css](kit/frame-kit.css). `{{face}}` in a fragment becomes the user's face
   still if `frames/face.jpg` exists, and a neutral silhouette if it doesn't.

   | class | use it for |
   |---|---|
   | `.f` | the frame wrapper, always the outer element |
   | `.hl` | headline at the top, `<em>` on one key word |
   | `.lbl` with `.n` + `.t` | a numbered list label (`01 SCRIPT`) |
   | `.face` | full-frame face (an `<img src="{{face}}">`) |
   | `.facebox` | the face box in a `split` shot |
   | `.term` | a Claude Code terminal (`.p` prompt, `.tool` tool call, `.ok`, `.dim`) |
   | `.chat` + `.bub` + `.vid` | an agent chat message, optionally with a video |
   | `.shot` | a screenshot card (`<div class="shot"><img src="..."></div>`) |
   | `.tbl` | a data table (`.h` header, `.r` rows, `.r.new` a new row) |
   | `.big` | one big punchline |
   | `.room` | a b-roll placeholder with a caption |

   Set the vertical position with an inline `style="top:..px"`. Example fragment:

   ```html
   <div class="f">
     <div class="lbl"><span class="n">01</span><span class="t">SCRIPT</span></div>
     <div class="term" style="top:200px">
       <div class="bar"><i></i><i></i><i></i></div>
       <div class="p">write me a 45 second script about ...</div>
       <div class="ok">  ✓ script.md</div>
     </div>
     <div class="facebox"><img src="{{face}}"></div>
   </div>
   ```

3. **Mock it with real data** when the screen is behind a login you can't get past. Don't
   sign in on the user's behalf. Build the screen from real numbers and mark it a stand-in.

**Frame rules:**

- **Safe zones:** keep text out of the bottom 20% and the right 12% (the like and comment
  rail), and keep the top 8% clear. The kit's positions already respect these.
- **One headline style:** heavy uppercase, one key word in `<em>`. Over a full-frame face
  the kit turns the type white with a soft shadow.
- **Privacy:** no file paths with a username, emails, API keys or `.env` contents in any
  frame. Use fake IDs in tables.

## Using it to build the video

Once the storyboard is approved, it's the prompt. Build the graphics one shot at a time:
"Build shot 4 from the storyboard as a 9:16 motion graphic: match the frame, the on-screen
text and the edit note." The first version is never right; put it in the edit, compare it to
the frame, and go back and forth until it matches.
