"""Check a generated bomberman+xkeys ROM and its spoiler."""
import json, sys, re
rom_path, spoiler_path = sys.argv[1], sys.argv[2]
rom = open(rom_path, 'rb').read()
full = open(spoiler_path, encoding='utf-8').read()
txt = full
loc = full.split('\nLocations:\n',1)[1].split('\nShops:\n',1)[0]
items = [l.rsplit(': ',1)[1].strip() for l in loc.splitlines() if ': ' in l]
ok = True
def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(f"  [{'ok' if cond else 'FAIL'}] {name} {detail}")
check('SpecialWeapons = 0x81 (bomb mode)', rom[0x18002F] == 0x81, hex(rom[0x18002F]))
check('Ganon vulnerable to bombs (0x18002E low bits = 4)', rom[0x18002E] & 0x7F == 0x04, hex(rom[0x18002E]))
check('starting bomb level 1 (init SRAM 0x1833C3)', rom[0x1833C3] == 1, str(rom[0x1833C3]))
check('starting max bombs 0 (0x180034)', rom[0x180034] == 0, str(rom[0x180034]))
check('tournament flag (0x180213)', rom[0x180213] == 1, str(rom[0x180213]))
check('Pinball Room = SW small key', re.search(r"^Skull Woods - Pinball Room: Small Key \(Skull Woods\)$", loc, re.M) is not None)
m = re.search(r'^Starting Inventory:\s+(.*)$', full, re.M)
check('starting Progressive Bombs in spoiler', m and 'Progressive Bombs' in m.group(1))
pb = items.count("Progressive Bombs")
check('3 Progressive Bombs placed', pb == 3, str(pb))
for bad in ['Progressive Sword', 'Fighter Sword', 'Master Sword', 'Tempered Sword', 'Golden Sword', 'Bomb Upgrade', 'Bombs (10)', 'Bombs (3)', 'Single Bomb']:
    n = sum(1 for i in items if i == bad or i.startswith(bad + ' ('))
    check(f'no {bad} placed', n == 0, str(n) if n else '')
r300 = items.count('Rupees (300)')
check('Rupees (300) count equals the base pool (5, no minting)', r300 == 5, str(r300))
for key, want in [('Swords', 'bombs'), ('Entrance Shuffle', 'crossed'), ('Accessibility', 'locations'), ('Key Logic Algorithm', 'static')]:
    m = re.search(rf"^{re.escape(key)}:\s+(\S+)", txt, re.M)
    check(f'{key}: {want}', m and m.group(1).lower() == want, m.group(1) if m else 'missing')
print('ALL OK' if ok else 'PROBLEMS FOUND')
sys.exit(0 if ok else 1)
