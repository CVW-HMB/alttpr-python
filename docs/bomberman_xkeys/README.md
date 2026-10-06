# Bomberman + xkeys

How to roll the exact "Bomberman xkeys" mode: Bomb-Only with starting bombs, on crosskeys-style settings.

## The mode

| Setting | Value |
|---|---|
| Swords | `bombs` (Bomb-Only). Swords are replaced by 4 Progressive Bombs; you start with 1 |
| Bombs | infinite once you have a Progressive Bombs; B detonates every placed bomb |
| Entrances | crossed |
| Dungeon items | full keysanity: small keys, big keys, maps and compasses all wild |
| Plando | Skull Woods small key in the Skull Woods Pinball Room |
| Key logic | `static` (the DoorDevUnstable static key logic) |
| Accessibility | 100% locations |
| Money | no money balancing: rupees are never moved or created; seeds that would need it are rerolled |
| Goal | fast Ganon (`goal: crystals`): all 7 crystals, then Ganon; no Agahnim 2 needed. Pyramid hole: DR `auto` |
| Shops | shopsanity: shop slots are item locations (potions that land outside shops become Rupees (50), as in normal shopsanity) |
| Other | open, 7/7 crystals, race ROM (tournament flag on) |

Bomb levels work like sword levels. Level 2 ("master bombs") reads tablets and breaks Agahnim's Tower barrier,
level 3 is needed to hurt Ganon, and Ganon's stun phase is hurt by bombs. Agahnim still has to be beaten by
reflecting his shots, so logic wants the Hammer or Bug Net for him, as in swordless.

Everything is defined in [`bomberman_xkeys.yaml`](bomberman_xkeys.yaml) plus four command line flags that the
roll script adds: `--no_money_balance --race --spoiler full --bps`.

## Setup

You need Python 3.10+ and a Zelda no Densetsu: Kamigami no Triforce (Japan) v1.0 ROM
(md5 `03a63945398191337e896e5771f77173`). The ROM is not in this repository and must never be committed.

```bash
git clone -b feature/bomberman-xkeys https://github.com/CVW-HMB/alttpr-python.git
cd alttpr-python
uv sync    # or create a .venv and pip install the dependencies listed in pyproject.toml
```

## Roll

From the repository root:

```bash
docs/bomberman_xkeys/roll.sh "/path/to/Zelda no Densetsu - Kamigami no Triforce (Japan).sfc" 5 out
```

That rolls until 5 seeds generate and pass [`verify_seed.py`](verify_seed.py), then stops. Each seed ends up in
`out/<n>/` with:

- `GK_<seed>_<code>.bps`: the patch to share (apply to the JP 1.0 ROM)
- `GK_<seed>_Spoiler.txt`: the full spoiler; the hash is on the `Hash:` line
- `GK_<seed>_<code>.sfc`: the patched ROM, for local play only. Never commit or upload it.

The single command the script runs per attempt is:

```bash
python DungeonRandomizer.py --customizer docs/bomberman_xkeys/bomberman_xkeys.yaml \
  --no_money_balance --race --spoiler full --bps \
  --rom "/path/to/jp.sfc" --outputpath out/tryN
```

Expect rerolls. About two attempts in three stop with "Money balancing is off ... short N rupees": the seed
would have needed rupees moved or minted, so it is thrown away. A few also fail with "Cannot beat game" or a
RecursionError; those happen in this generator with normal swords too.

`verify_seed.py` checks each seed's ROM and spoiler for: bomb mode on, Ganon vulnerable to bombs, starting bomb
level 1, no bomb capacity, race flag on, the Pinball Room key, 3 Progressive Bombs placed plus 1 starting, no
swords, bomb pickups or bomb upgrades, exactly the base pool's 5 Rupees (300), crossed entrances, 100% locations,
static key logic, fast Ganon and shopsanity.

## Sharing a seed with the online patcher

Host the `.bps` somewhere public (we use GitHub Pages on `CVW-HMB/alttpr-seeds`, under `seed/<name>.bps`), then
link players to:

```
https://alttprpatch.synack.live/patcher.html?patch=<URL-encoded link to the .bps>
```

They choose their JP 1.0 ROM, click "Apply patch", and download the `.sfc`.

## What this branch changes

On top of upstream `main` of `git.gwaa.kiwi/alttpr-gwaa-kiwi/alttpr-python`:

1. **Add bomb-only sword mode (`--swords bombs`).** Ported from the Python the legacy site
   (alttpr-legacy.gwaa.kiwi) runs: `ardnaxelarak/ALttPDoorRandomizer` at f8e427ea. Item pool, logic, boss rules,
   ROM writes, Ganon vulnerability, settings code.
2. **Update baserom.** `data/base2current.bps` rebuilt from `CVW-HMB/alttpr-baserom` branch `feature/bomb-mode`,
   which restores the bomb-only ROM code from `ardnaxelarak/z3randomizer` branch `kara`: item `$C0` Progressive
   Bombs, infinite bombs, B-button detonation, the bomb damage table, bomb collision for Moldorm, Trinexx and
   Helmasaur King, the bombable Agahnim barrier, and HUD/menu icons. It also fixes the SpecialWeapons byte, which
   was assembled at PC `0x18102F` instead of `0x18002F`.
3. **Port static key logic** (`key_logic_algorithm: static`) as it is at aerinon/ALttPDoorRandomizer
   DoorDevUnstable head, via the CVW-HMB OverworldShuffle port.
4. **`--no_money_balance`.** The money balancer only checks: it never swaps or creates rupees and fails the seed
   if a required purchase cannot be afforded. Pool padding never adds rupees with this flag.

### Rebuilding the base patch

Only needed if you change the baserom. With asar and flips on your PATH:

```bash
git clone -b feature/bomb-mode https://github.com/CVW-HMB/alttpr-baserom.git && cd alttpr-baserom
cp /path/to/jp.sfc ../working.sfc
asar --symbols=wla LTTP_RND_GeneralBugfixes.asm ../working.sfc   # run from the baserom directory
flips --create --bps-delta /path/to/jp.sfc ../working.sfc ../base2current.bps
md5 ../working.sfc   # put this in RANDOMIZERBASEHASH in Rom.py, copy base2current.bps to data/
```

The current patch gives md5 `f22707df0da27c4c047bb4d9ca8fef07`.
