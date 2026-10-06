import copy

from Utils import load_cached_yaml, local_path


class DamageTable:
    def __init__(self, bomb_mode=False):
        self.damage_table = load_cached_yaml(['source', 'enemizer', 'damage_table.yaml'])
        self.enemy_damage = load_cached_yaml(['source', 'enemizer', 'enemy_damage_table.yaml'])
        if bomb_mode:
            # Bomb-only mode sets bit 0x80 of SpecialWeapons, which makes the ROM use Damage_Table_Bombs
            # (data/damage_table_sword_bombs.bin) as the per-sprite subclass table instead of Damage_Table.
            # The yaml is cached and shared, so copy before swapping the subclass table.
            self.damage_table = copy.deepcopy(self.damage_table)
            normal = load_subclass_table('data/damage_table.bin')
            bombs = load_subclass_table('data/damage_table_sword_bombs.bin')
            sub_class_table = self.damage_table['SubClassTable']
            for sprite, row in sub_class_table.items():
                if row == normal.get(sprite):
                    sub_class_table[sprite] = list(bombs[sprite])
                elif sprite in yaml_row_sources and row == normal[yaml_row_sources[sprite]]:
                    # the yaml deliberately uses another sprite's row here; follow that sprite's bomb-mode row
                    sub_class_table[sprite] = list(bombs[yaml_row_sources[sprite]])
                # any other yaml override (synthetic sprite kinds) is kept as is


# yaml SubClassTable rows that are copies of another sprite's row: 0x63 (pit) spawns the 0x64
yaml_row_sources = {0x63: 0x64}


def load_subclass_table(path):
    with open(local_path(path), 'rb') as stream:
        data = stream.read()
    table = {}
    for sprite in range(len(data) // 8):
        row = data[sprite * 8:sprite * 8 + 8]
        table[sprite] = [n for byte in row for n in (byte >> 4, byte & 0x0F)]
    return table
