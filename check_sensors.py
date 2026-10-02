#!/usr/bin/env python3
# Check that tele(N) references still point at the intended sensors. Usage: ./check_sensors.py [model02 ...]
import re, sys
from modeldump import MODELS, load

# (line, column) -> sensor shown on the telemetry screen
SCREEN = {(0, 1): 'RxBt', (1, 1): 'Alt', (2, 0): 'TPWR', (2, 1): 'RQly'}
SCREEN_BY_MODEL = {
    'air75': {(0, 0): 'RxBt', (1, 0): 'FM', (1, 1): 'Capa', (2, 0): 'TPWR'},
    'Tanar': {(0, 1): 'RxBt', (2, 0): 'TPWR', (2, 1): 'RQly'},
}


def check(d):
    sensors = {int(k): s['label'] for k, s in (d.get('telemetrySensors') or {}).items()}

    def label(s):
        m = re.match(r'tele\((\d+)\)', s)
        return m and sensors.get(int(m[1]), f'{m[0]} (no such sensor)')

    errs = []

    def expect(what, got, want):
        if got != want:
            errs.append(f'{what} is {got}, expected {want}')

    lsw = d.get('logicalSw') or {}
    for c in (d.get('customFn') or {}).values():
        if c['func'] == 'PLAY_TRACK' and c['def'].startswith('lowbat'):
            m = re.fullmatch(r'L(\d+)', c['swtch'])
            src = m and lsw.get(str(int(m[1]) - 1), {}).get('def', '')
            expect(f"lowbat switch {c['swtch']}", src and label(src), 'RxBt')
        elif c['func'] == 'PLAY_VALUE' and label(c['def']):
            expect(f"PLAY_VALUE on {c['swtch']}", label(c['def']), 'Alt')

    shown = {}
    for line, l in ((d.get('screens') or {}).get('0', {}).get('u', {}).get('lines') or {}).items():
        for col, cell in (l.get('sources') if isinstance(l, dict) else {}).items():
            if label(cell['val']):
                shown[int(line), int(col)] = label(cell['val'])
    want = SCREEN_BY_MODEL.get(d['header']['name'], SCREEN)
    for pos in sorted(shown.keys() | want.keys()):
        expect(f'screen line{pos[0]} col{pos[1]}', shown.get(pos, 'empty'), want.get(pos, 'empty'))

    vario = (d.get('varioData') or {}).get('source', 'none')
    if vario != 'none':
        expect('vario source', label(f'tele({vario})'), 'VSpd')
    return errs


bad = 0
for arg in sys.argv[1:] or sorted(p.stem for p in MODELS.glob('*.yml')):
    name, d = load(arg)
    for e in check(d):
        bad += 1
        print(f"{name} ({d['header']['name']}): {e}")
sys.exit(bad > 0)
