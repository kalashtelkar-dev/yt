exec(open('retakes.py').read().split("log('retakes start')")[0])
OV['A4'] = make([('A4', '', '', None, None)])[0][1]; json.dump({k: v for k, v in OV.items() if v}, open(HI + 'overrides.json', 'w'), indent=1); log('A4 plain done')
