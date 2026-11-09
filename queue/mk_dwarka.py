# -*- coding: utf-8 -*-
"""Builds dwarka.json (queue config) and the shot briefs saved next to the script. Photo shots are filled in by photos.json (id -> file, edit prompt)."""
import json, os
D = os.path.dirname(os.path.abspath(__file__)) + '/'
W = '/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/dwarka/'
S = json.load(open(W + 'script_draft.json', encoding='utf-8'))['sections']
PRE = "Hand-painted cinematic illustration, painterly background art, visible soft brush texture, deep teal and gold palette with warm sunset orange, mysterious storybook animation background style, wide 16:9. "
SUF = " No text, no lettering, no signs, no watermark, no logo."
M = " Painterly hand-painted animation look, no cuts, no morphing, calm final shot."
B = {  # id: (picture brief, motion)
'A1': ("Calm Arabian sea at golden dusk with the faint glowing outline of an ancient golden city lying beneath the clear turquoise water, domes and towers visible under the surface, light rays, mysterious and magical, no people.", "Slow gentle push-in over the water. Light ripples shimmer, the glowing city beneath pulses very softly, the sky stays still."),
'A2': ("A lone peacock feather and a bamboo flute resting on a weathered stone ledge by the sea at sunset, waves in the distance, symbolic and quiet, no people.", "Slow gentle push-in. The feather's fibres sway softly in the sea breeze, waves glitter, the flute stays still."),
'A3': ("Underwater view of drowned palace towers, tall pillars and carved arches covered in sand, shafts of golden light from the surface above, small fish, mysterious and serene, no people.", "Slow gentle push-forward. Light shafts shift softly, tiny fish drift, dust floats, the ruins stay still."),
'A5': ("Split composition: the upper half a temple spire with a long saffron flag flying in a sunset sky, the lower half dark sea water with the faint glowing outline of a sunken city under it, no people.", "Slow gentle push-in. The flag flutters softly, light glints on the water, the temple and ruins stay still."),
'A6': ("An old hand-drawn map of a western coastline spread on a wooden table with a brass compass, a rolled scroll and a lit oil lamp, warm window light from the sea, no readable writing, no people.", "Slow gentle push-in. Lamp flame flickers, warm light shifts across the map, the objects stay still."),
'B1': ("An empty ancient chariot travelling on a dusty road toward the western sea at dusk, peacocks along the road, the sea glowing on the horizon, no people.", "Slow gentle push-in following the road. Dust glows, peacock feathers sway, the chariot stays calm."),
'B2': ("Grand ancient coastal capital with golden walls, towering palaces and a great arched gate beside the sea, banners flying, warm evening light, epic and mysterious, no people.", "Slow gentle push-in toward the gate. Banners flutter, the sea glimmers, the architecture stays still."),
'B3': ("A royal hall in chaos by lamplight, overturned goblets, a cracked stone pillar, torn silk curtains and a dim flickering lamp, tense and dark, no people.", "Slow gentle push-in. The lamp flame flickers, curtains stir slightly, the hall stays still."),
'B4': ("A festival ground on a sea shore after a storm, scattered reed clubs and torn banners on wet sand, torches burning in a dark stormy sky, dramatic and sad, no people.", "Slow gentle push-in. Torch flames flicker, wind moves the torn banners, clouds drift, the sand stays still."),
'B5': ("A lone tree in a quiet forest clearing at dusk with a small distant silhouette resting beneath it, golden light shafts through the leaves, calm and sorrowful, no face detail.", "Slow gentle push-in. Light shafts shimmer, leaves sway very softly, the figure stays still."),
'B6': ("A single arrow flying through a dusky forest as a glowing streak of light, tall trees and golden mist, dramatic motion, no people.", "Slow gentle push-in. The glowing streak shimmers, mist drifts, leaves stir, calm final shot."),
'B7': ("A distant hunter silhouette kneeling in tall grass with a bow, peering into forest shadows, golden evening light, no face detail.", "Slow gentle push-in. Tall grass sways softly, light flickers through leaves, the silhouette stays still."),
'B8': ("A single arrow lying on a forest floor beside two softly glowing lotus-shaped footprints, golden light rising upward like a path to the sky, serene, no people.", "Slow gentle upward tilt. The glow shimmers, light motes rise softly, the arrow stays still."),
'B9': ("A small quiet roadside shrine under palm trees near a sandy coast at dusk, a gentle golden glow, calm and sacred, no people.", "Slow gentle push-in. Palm leaves sway softly, the glow breathes, the shrine stays still."),
'B10': ("A huge dark wave rising behind the golden walls of a coastal city under a stormy sky, lightning glow on the clouds, dramatic, no people.", "Slow gentle push-in. Clouds roll slowly, the wave crest glistens, the walls stay still."),
'B12': ("The golden city half drowned, towers and domes rising out of dark waves, water flooding streets, birds flying away into a stormy dusk, no people.", "Slow gentle push-in. Waves rise and fall softly, birds glide away, the towers stay still."),
'B13': ("A calm dark sea at night under a sky full of stars, a faint golden glow shaped like a city beneath the surface, drifting mist, mysterious, no people.", "Slow gentle push-in. Stars twinkle, mist drifts, the glow pulses very softly."),
'C1': ("A research boat deck at dawn with a diving lantern, coiled ropes and air tanks, the calm sea beyond, mysterious pale light, no people.", "Slow gentle push-in. Sea shimmers, the lantern glows softly, the deck stays still."),
'C2': ("A small boat anchored over turquoise water near a stone coast, ropes into the sea and diver equipment on board, bright morning light, no people.", "Slow gentle push-in. Water ripples, the boat bobs very slightly, the coast stays still."),
'C3': ("The seabed with ancient triangular stone anchors, carved stone blocks and the curved outline of a wall in the sand, light shafts from above, mysterious and clear, no people.", "Slow gentle push-forward. Light shafts shimmer, sand dust floats, the stones stay still."),
'C4': ("A weathered three-holed ancient stone anchor half buried in sand on the seabed, coral and tiny fish around it, soft glowing light, mysterious, no people.", "Slow gentle push-in. Tiny fish drift past, light ripples across the stone, the anchor stays still."),
'C5': ("A modern research boat with sonar equipment and a radar mast at sunrise on a calm sea near a coast, golden light on the water, no people.", "Slow gentle push-in. Water glitters, the radar turns slowly, the boat stays calm."),
'C7': ("A tiny silhouette of a diver sitting on the seabed with folded hands before ancient submerged pillars glowing softly, blue-gold light shafts, reverent and quiet, no face detail.", "Slow gentle push-in. Light shafts shimmer, bubbles rise, the silhouette stays still."),
'C9': ("A five-storey ancient Indian coastal temple with a tall carved spire and a long flag, warm sunset sky, seen from the street below, no people.", "Slow gentle push-in. The flag flutters, clouds drift, the temple stays still."),
'C10': ("Close view of a temple spire top with a very long saffron flag streaming in a strong sea wind against a bright sky, no people.", "Slow gentle push-in. The flag streams and ripples, clouds race softly, the spire stays still."),
'C11': ("A wide river mouth meeting the sea at sunset with stone ghat steps going down to the water, sandbars and birds, golden light, no people.", "Slow gentle push-in. Water ripples, birds glide, light shifts, the steps stay still."),
'C12': ("An ornate ancient stone temple with intricately carved walls and sculpted panels in evening light, a calm courtyard, no people.", "Slow gentle push-in. Warm light slides across the carvings, the stone stays still."),
'C13': ("A small island seen across the sea with a long cable-stayed bridge arching toward it, fishing boats below, golden hour, no people.", "Slow gentle push-in. Waves glitter, boats bob softly, the bridge stays still."),
'C16': ("A painted storybook map scene: a temple, a river ghat, an ornate small temple and an island with a bridge, arranged along a coastline, bright and clear, no text.", "Slow gentle push-in. Little waves shimmer, flags flutter, the map stays still."),
'C17': ("The five-storey coastal temple with a tall spire and flag, bright day, no people.", "Slow gentle push-in. The flag flutters, clouds drift, the temple stays still."),
'C18': ("A river mouth meeting the sea with stone ghat steps, evening light, no people.", "Slow gentle push-in. Water ripples, light shifts, the steps stay still."),
'C19': ("An ornate carved stone temple in warm light, no people.", "Slow gentle push-in. Light slides over the carvings, the stone stays still."),
'C20': ("An island with a long bridge over the sea, bright afternoon, no people.", "Slow gentle push-in. Waves glitter, the bridge stays still."),
'D1': ("A quiet coastal road at dawn leading toward a glowing temple town by the sea, painted, soft light, no text, no people.", "Slow gentle push-in along the road. Light warms, mist drifts, the road stays calm."),
'D2': ("A small railway platform at dawn with a train waiting, old stone arches and warm light, no lettering, no people.", "Slow gentle push-in. Light shifts, steam drifts, the train stays still."),
'D6': ("A narrow bazaar lane with hanging flower garlands leading toward a grand temple gate in the morning, no vehicles, no people.", "Slow gentle push-in down the lane. Garlands sway, light shifts, the lane stays still."),
'D7': ("An open temple gateway facing the sea with stone steps and a gentle blue sea breeze, welcoming morning glow, no signs, no people.", "Slow gentle push-in. Curtains and garlands sway softly, the glow breathes, the gate stays still."),
'D8': ("A temple doorway with a lit brass lamp and a hanging brass bell, painted wooden door, warm light, no text, no people.", "Slow gentle push-in. The lamp flickers, the bell sways very slightly, the door stays still."),
'D9': ("A signpost with blank wooden boards beside a temple path, bright morning, no writing, no people.", "Slow gentle push-in. Light shifts, leaves stir, the post stays still."),
'D10': ("A long cable-stayed bridge across the sea at dawn, empty road, calm water, soft mist, no people.", "Slow gentle push-forward along the bridge. Mist drifts, the water shimmers, the bridge stays still."),
'D11': ("A cool pleasant winter morning with mist over the sea and a temple on the shore, soft golden light, no people.", "Slow gentle push-in. Mist drifts, waves glint, the temple stays still."),
'E1': ("Sunrise over the sea behind a temple town with small fishing boats, new day feeling, no people.", "Slow gentle push-in. The sun brightens, waves glitter, boats bob softly."),
'E2': ("A temple courtyard at dawn lit by oil lamps, first light on the spire, no people.", "Slow gentle push-in. Lamp flames flicker, light warms, the courtyard stays still."),
'E3': ("A river ghat in the morning with moored wooden boats and wide steps, soft light, no people.", "Slow gentle push-in. Water ripples, boats bob, the steps stay still."),
'E5': ("A sea bridge and island in bright afternoon sun, the sea sparkling, no people.", "Slow gentle push-in. The sea sparkles, clouds drift, the bridge stays still."),
'E6': ("Evening aarti lamps glowing on temple steps with the sea behind, golden reflections, no people.", "Slow gentle push-in. Flames flicker, reflections shimmer, the steps stay still."),
'E7': ("A row of small wooden storage lockers by a temple gate, warm light, no text, no numbers, no people.", "Slow gentle push-in. Light shifts, a leaf drifts by, the lockers stay still."),
'E8': ("Neatly folded simple cotton clothes in cream and saffron on a stone bench, warm light, no people.", "Slow gentle push-in. Light shifts softly, the cloth stays still."),
'E9': ("A copper water bottle and a pair of comfortable sandals on temple steps in the morning, no people.", "Slow gentle push-in. Light glints on the copper, the steps stay still."),
'E10': ("A night sea under stars with the faint golden outline of a drowned city glowing under the water, a lone lit temple on the shore, mysterious and calm, no people.", "Slow gentle push-in. Stars twinkle, the underwater glow pulses very softly, the shore stays still."),
'E11': ("A full moon over the sea with a single small lit diya floating on the waves, calm and magical, no people.", "Slow gentle push-in toward the diya. The flame flickers, moonlight ripples, the horizon stays still."),
'E12': ("A lit diya on a stone ledge by the sea at dusk with a glowing temple spire behind and a lighthouse in the distance, warm closing shot, no people.", "Slow gentle push-in toward the diya. The flame flickers softly, the sea shimmers, the temple glows."),
}

B.update({
'A4': ("The Dwarkadhish temple on the Gomti waterfront at golden hour: a tall richly carved brown sandstone spire with a long flag, stepped ghat and calm reflecting water, small town buildings around, no people.", "Slow gentle push-in. The flag flutters, the water reflection shimmers, the temple stays still."),
'B9': ("A small white pillared gateway to a quiet roadside shrine under a big banyan tree, a saffron flag and a low whitewashed building, clear midday sky, no lettering, no people.", "Slow gentle push-in. Banyan leaves sway, the flag flutters, the gateway stays still."),
'C9': ("Wide view from the street of the Dwarkadhish temple's tall tiered carved sandstone spire with a large flag against a pale sky, small houses at the base, no people.", "Slow gentle push-in. The flag flutters, clouds drift, the temple stays still."),
'C10': ("Close view of the very top of a carved temple spire with a long swallow-tailed blue and yellow flag streaming in a strong sea wind against a bright sky, no people.", "Slow gentle push-in. The flag streams and ripples, clouds race softly, the spire stays still."),
'C11': ("The Gomti river mouth meeting the sea, golden sandbars with shallow pools and a white egret standing in the water, warm evening light, no people.", "Slow gentle push-in. Water ripples, the egret turns its head slightly, light shifts, the sandbars stay still."),
'C12': ("The small ornate Rukmini Devi temple of carved sandstone with a domed porch and a tall carved spire with a pink flag, dusk sky, empty sandy ground, no people.", "Slow gentle push-in. The flag flutters, warm light slides across the carvings, the temple stays still."),
'C13': ("A low island seen across the calm blue sea with a white domed shrine and a small jetty on its shore, hazy blue sky, no people.", "Slow gentle push-in. The water glitters, a gull glides past, the island stays still."),
'C17': ("Macro view of the richly carved tiers of a brown sandstone temple spire, tiny sculpted figures and arches in bright sunlight, no people.", "Slow gentle upward drift. Light slides across the carvings, the stone stays still."),
'C18': ("A small ancient shrine on the shore where a river meets the sea, grey concrete breakwater blocks in front, evening light on the sea, no people.", "Slow gentle push-in. Waves roll softly, light glints on the water, the shrine stays still."),
'C19': ("Carved white stone wall panels with graceful sculpted figures and pillars of an old temple, soft warm light, no people.", "Slow gentle sideways drift. Light shifts across the carvings, the stone stays still."),
'C20': ("Calm blue sea with seagulls floating on the water and a low rocky coast beyond under a clear sky, no people.", "Slow gentle push-in. Waves ripple, gulls bob and one lifts off, the coast stays still."),
'D2': ("An early morning railway platform with a yellow and grey diesel locomotive, a long canopy and a footbridge, soft light, no lettering, no signboards, no people.", "Slow gentle push-in. Light warms, a little steam drifts, the train stays still."),
'E1': ("Sunrise over the calm sea with the sun just above the horizon and one small fishing boat on the water, golden light, no people.", "Slow gentle push-in. The sun brightens, waves glitter, the boat bobs very slightly."),
})
P = json.load(open(D + 'photos.json')) if os.path.exists(D + 'photos.json') else {}
shots = []; briefs = {}
for sec in 'ABCDE':
    for i, t in S[sec]:
        if i not in B and i not in P: continue
        if i in P:
            shots.append(dict(shot=i, photo=P[i]['file'], edit=P[i]['edit'], idea=P[i].get('idea', "Slow gentle push-in on this scene. Soft natural motion only, the architecture stays still." + M), credit=P[i]['credit']))
            briefs[i] = 'Real photo: ' + P[i]['credit']
        else:
            b, m = B[i]; shots.append(dict(shot=i, prompt=PRE + b + SUF, idea=m + M)); briefs[i] = b
for i in P:
    if i not in [s['shot'] for s in shots]:
        shots.append(dict(shot=i, photo=P[i]['file'], edit=P[i]['edit'], idea=P[i].get('idea', "Slow gentle push-in on this scene. Soft natural motion only, the architecture stays still." + M), credit=P[i]['credit'])); briefs[i] = 'Real photo: ' + P[i]['credit']
order = [i for sec in 'ABCDE' for i, _ in S[sec]]
shots.sort(key=lambda s: order.index(s['shot']) if s['shot'] in order else 99)
json.dump(shots, open(D + 'dwarka.json', 'w'), ensure_ascii=False, indent=1)
json.dump(briefs, open(W + 'briefs.json', 'w'), ensure_ascii=False, indent=1)
print(len(shots), 'shots;', sum(1 for s in shots if 'photo' in s), 'real photos; lines without a shot:', [i for i in order if i not in [s['shot'] for s in shots]])
