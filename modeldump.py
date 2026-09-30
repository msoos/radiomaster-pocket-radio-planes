#!/usr/bin/env python3
# Decoded one-line-per-item dump of EdgeTX models, for diffing. Usage: ./modeldump.py [-d] model02 [model03 ...]
import difflib, re, sys, yaml
from pathlib import Path

MODELS = Path(__file__).parent / 'backup/MODELS'
POS = {'0': '↑', '1': '-', '2': '↓'}


def load(arg):
    p = Path(arg)
    if not p.exists():
        p = MODELS / (arg if arg.endswith('.yml') else arg + '.yml')
    return p.stem, yaml.load(p.read_text(), Loader=yaml.BaseLoader)


def dump(d):
    sensors = {int(k): s['label'] for k, s in (d.get('telemetrySensors') or {}).items()}
    inputs = {int(k): v['val'] for k, v in (d.get('inputNames') or {}).items()}
    outs = {int(k): l['name'] for k, l in (d.get('limitData') or {}).items()}

    def ch(n):
        n = int(n)
        return f'CH{n + 1}' + (f'({outs[n]})' if outs.get(n) else '')

    def src(s):
        s = re.sub(r'tele\((\d+)\)', lambda m: sensors.get(int(m[1]), m[0]), s)
        s = re.sub(r'^I(\d+)$', lambda m: 'I:' + inputs.get(int(m[1]), m[1]), s)
        s = re.sub(r'ch\((\d+)\)', lambda m: ch(m[1]), s)
        return re.sub(r'^(S[A-H]|L\d+)([012])$', lambda m: m[1] + POS[m[2]] if m[1][0] == 'S' else m[0], s)

    def curve(c):
        t, v = c['type'], c['value']
        return '' if v == '0' else {'0': f' diff{v}', '1': f' expo{v}', '3': f' curve{v}'}.get(t, f' c{t}/{v}')

    o = [f"name {d['header']['name']}"]
    for k, t in (d.get('timers') or {}).items():
        o.append(f"timer{int(k) + 1} {t['name']} mode={t['mode']} sw={src(t['swtch'])} minuteBeep={t['minuteBeep']}")
    for k, m in (d.get('flightModeData') or {}).items():
        trims = ' '.join(f"t{i}={'off' if v['mode'] == '31' else ('FM%d' % (int(v['mode']) >> 1)) + ('+' if int(v['mode']) & 1 else '')}"
                         for i, v in sorted(m.get('trim', {}).items()) if k != '0' or v['mode'] != '0')
        o.append(f"FM{k} {m.get('name')!r} sw={src(m.get('swtch', ''))} {trims}".rstrip())
    for e in d.get('expoData') or []:
        o.append(f"input {inputs.get(int(e['chn']), e['chn'])} <- {src(e['srcRaw'])} w{e['weight']}{curve(e['curve'])}"
                 f" sw={src(e['swtch'])}" + (f" off{e['offset']}" if e['offset'] != '0' else '') + (f" name={e['name']}" if e['name'] else ''))
    for m in d.get('mixData') or []:
        extra = ''.join(f' {k}={m[k]}' for k in ('offset', 'swtch', 'flightModes', 'mltpx', 'carryTrim')
                        if m[k] not in ('0', 'NONE', '000000000', 'ADD'))
        o.append(f"mix {ch(m['destCh'])} {m['name']!r} <- {src(m['srcRaw'])} w{m['weight']}{curve(m['curve'])}{extra}")
    for k, l in (d.get('limitData') or {}).items():
        o.append(f"out {ch(k)} rev={l['revert']} min={l['min']} max={l['max']} sub={l['offset']}")
    for k, l in (d.get('logicalSw') or {}).items():
        o.append(f"L{int(k) + 1} {l['func']} {src(l['def'].split(',')[0])},{l['def'].split(',', 1)[1]}"
                 f" delay={int(l['delay']) / 10}s and={src(l['andsw'])}")
    for k, c in sorted((d.get('customFn') or {}).items(), key=lambda kv: int(kv[0])):
        dv = c['def'].replace('\x00', '')
        if c['func'] == 'OVERRIDE_CHANNEL':
            n, rest = dv.split(',', 1)
            dv = f'{ch(n)},{rest}'
        o.append(f"SF {src(c['swtch'])} {c['func']} {dv}")
    o.append('startup ' + ' '.join(f"{s}={p['pos']}" for s, p in (d.get('switchWarning') or {}).items())
             + f" pots={d.get('potsWarnMode')}")
    for k, s in (d.get('screens') or {}).items():
        for li, line in (s['u'].get('lines') or {}).items():
            cols = (line if isinstance(line, dict) else {}).get('sources') or {}
            o.append(f"screen{k} line{li} " + ' | '.join(src(cols[c]['val']) if c in cols else '-' for c in ('0', '1')))
    v = d.get('varioData') or {}
    o.append(f"vario src={src('tele(%s)' % v['source']) if v.get('source', 'none') != 'none' else 'none'} "
             + ' '.join(f'{k}={v[k]}' for k in ('centerSilent', 'centerMin', 'centerMax', 'min', 'max')))
    crsf = d['moduleData']['0']['mod']['crsf']
    o.append(f"crsf arming={crsf['crsfArmingMode']} trigger={src(crsf['crsfArmingTrigger'])}")
    o.append('sensors ' + ' '.join(sorted(sensors.values())))
    return o


def main(argv):
    diffmode = argv[:1] == ['-d']
    models = [load(a) for a in argv[diffmode:]]
    if diffmode:
        (na, a), (nb, b) = models
        sys.stdout.writelines(l + '\n' for l in difflib.unified_diff(dump(a), dump(b), na, nb, n=0, lineterm=''))
    else:
        for name, d in models:
            print('\n'.join(f'{name}: {l}' if len(models) > 1 else l for l in dump(d)))


main(sys.argv[1:] or sorted(p.stem for p in MODELS.glob('*.yml')))
