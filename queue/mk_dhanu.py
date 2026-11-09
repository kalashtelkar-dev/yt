# -*- coding: utf-8 -*-
import json
S = json.load(open('/private/tmp/claude-501/-Users-kalash-Projects-yt/abe6688e-8269-4edf-a7a5-5ff0d79f368a/scratchpad/dhanushkodi/script_draft.json', encoding='utf-8'))['sections']
PRE = "Hand-painted cinematic illustration, painterly background art, visible soft brush texture, deep teal and gold palette with warm sunset orange, mysterious storybook animation background style, wide 16:9. "
SUF = " No text, no lettering, no signs, no watermark, no logo, no people."
M = " Painterly hand-painted animation look, no cuts, no morphing, calm final shot."
G = "Slow gentle push-in on this scene. Gentle natural motion only (water ripples, light shifts, clouds drift, dust floats), everything solid stays perfectly still."
B = {
'A1': "A calm turquoise sea at golden dusk with a long chain of pale limestone shoals forming a bridge just below the surface, stretching to the horizon, ripples above it.",
'A2': "Aerial view of a narrow sandy tip of land with one lone road and the sea on both sides at golden hour, tiny ruined buildings far ahead.",
'A3': "Large rounded stones glowing softly, floating on turquoise water in a line toward the horizon, mythic mood at dusk.",
'A4': "Underwater view of a chain of pale limestone shoals on the sea floor with shafts of light from above, sand ripples, mysterious and clear.",
'A5': "The roofless whitewashed church ruin at Dhanushkodi at dusk, arched walls, waves close behind, sand drifts.",
'A6': "A thin pale line of limestone shoals meeting the horizon under dawn light, the sea glowing, a feeling of revelation.",
'B1': "Aerial view of the southern tip of an island, a narrow strip of land between two seas at dawn.",
'B2': "A busy old port town at the shore in warm light, a wooden jetty, small boats, a small railway station, lanterns.",
'B3': "A vintage steam train beside a pier with a ferry steamer waiting at dusk.",
'B4': "Dark cyclone clouds swirling over the sea, lightning, huge waves approaching a coastal town, dramatic.",
'B5': "Huge waves crashing over a railway line at night, a train half swallowed by the water, dramatic.",
'B6': "Empty ruined streets filled with drifted sand, broken walls and a lone lamp post under a grey sky.",
'B7': "The ruined Dhanushkodi railway station, a broken platform and tracks sinking into sand, gulls, soft evening light.",
'B8': "Sunrise light on the sea with a faint chain of limestone shoals visible in the shallows, mysterious.",
'C1': "A mythic scene: a long bridge of stones across the sea toward a golden distant city on the horizon, epic light.",
'C2': "Close view of pale limestone shoals in turquoise shallows with ripples and sunlight.",
'C3': "Aerial view of a long chain of shoals stretching across the sea between two shores.",
'C4': "A stylised painted map of the sea strait with the chain of shoals glowing in gold lines, deep teal tones.",
'C5': "A research boat with scientific equipment anchored over turquoise shallows at sunrise.",
'C6': "Stones in the water half natural, half stacked like a bridge, ambiguous and mysterious, dusk.",
'C7': "A white jeep driving on a narrow sand road with the sea on both sides, wide view.",
'C8': "A sandy point where two seas meet, one side deeper blue and the other turquoise, a thin line of waves where they meet.",
'C9': "Sunset over a wide blue sea toward the horizon with a faint line of shoals, peaceful.",
'C10': "A roofless white church ruin with arched windows, sand and evening glow.",
'C11': "The grand corridors of a south Indian temple, endless carved pillars in lamplight.",
'C12': "A modern sea bridge with a raised vertical lift span, seen at sunrise over calm water.",
'C13': "A painted storybook map scene with four landmarks: a sand point, a ruined station, a church ruin and a temple, no text.",
'C14': "A sand spit at the meeting of two seas seen from ground level, footprints in the sand, wave lines.",
'C15': "Rusted railway tracks and a broken platform half buried in sand, close view, no signs.",
'C16': "A close view of an arched church window ruin with sand and sea behind.",
'C17': "A south Indian temple gopuram at sunset with a bright sky.",
'D1': "A road across the sea toward the horizon at dawn.",
'D2': "A modern airport terminal at sunset with an aeroplane in the sky.",
'D3': "A coastal highway with palm trees on a bright morning.",
'D4': "A passenger train crossing a sea bridge, wide shot.",
'D5': "A government bus and a jeep parked at a sandy road end by the sea.",
'D6': "Late afternoon golden light on a sand road and the sea, long shadows, empty.",
'D7': "A cool clear winter morning over a calm sea with a few clouds.",
'E1': "Sunrise over the sea behind palm trees, a new day feeling.",
'E2': "A temple pillared corridor with oil lamps at dawn.",
'E3': "A jeep kicking up sand dust on a coastal sand road in morning light.",
'E4': "A broken railway platform and church ruins in harsh noon sun.",
'E5': "A golden evening sea at a point where two seas meet, waves and birds.",
'E6': "A water bottle, a hat and sunglasses on a sandy rock with the sea behind.",
'E7': "A pair of comfortable shoes on sand with footprints leading away.",
'E8': "A night sky over the sea with stars, a faint glowing line of shoals, a lone ruined arch in the foreground.",
'E9': "A lone lit diya on a rock at the water's edge at dusk with the ruined church behind, warm closing shot.",
'E10': "Moonlight over a calm sea with a chain of limestone shoals shimmering, final shot."}
order = [i for v in S.values() for i, _ in v]; assert set(order) == set(B), set(order) ^ set(B)
json.dump([{'shot': i, 'prompt': PRE + B[i] + SUF, 'idea': G + M} for i in order], open('dhanu.json', 'w'), ensure_ascii=False, indent=1); print(len(order), 'shots')
