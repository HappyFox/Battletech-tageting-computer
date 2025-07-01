import collections

import display
from events import EventDispatcher

Entrys = collections.namedtuple("Entrys", ["gun", "atk", "tar", "other", "rng"])


class RngState:
    NORM = "NORM"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    UNDER_MIN = "UNDER_MIN"


class WeaponsNotFoundError(Exception):
    pass


class Rngs:
    MIN = "Min"
    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"
    OUT_OF = "Out of Range"


class Gator:

    def __init__(self):
        self.gun = 0
        self.atk = 0
        self.tar = 0
        self.other = 0
        self.range = 0

    def to_hit(self):
        return self.gun + self.atk + self.tar + self.other + self.range


class RngBracket:

    def __init__(self, rng_str, mod, name):
        divider_char = "-"
        invalid_rng = "-"

        self.invalid = False

        if rng_str == invalid_rng:
            self.invalid = True

        elif divider_char in rng_str:
            # print(rng_str)
            rngs = rng_str.split(divider_char)
            # print(rngs)

            self.start = int(rngs[0])
            self.end = int(rngs[1])
        else:
            # print(rng_str)
            self.start = int(rng_str)
            self.end = int(rng_str)

        self.mod = mod
        self.name = name

    def inside(self, rng):
        if self.invalid:
            return False

        if self.start <= int(rng) <= self.end:
            return True
        return False

    def __repr__(self):
        return f"RngBracket({self.start}-{self.end}, {self.name}, {self.mod})"


class Ranges:

    divider_char = "-"
    INVALID_RNF = "-"

    RANGES = [
        (Rngs.MIN, "Min", None),
        (Rngs.SHORT, "S", 0),
        (Rngs.MEDIUM, "M", 2),
        (Rngs.LONG, "L", 4),
    ]

    def __init__(self, min, short, medium, long, to_hit_mod):

        self.min = int(min)
        self.short = self._process_rng_str(short)
        self.medium = self._process_rng_str(medium)
        self.long = self._process_rng_str(long)
        self.ranges = [self.min, self.short, self.medium, self.long]
        # print(to_hit_mod)
        self.to_hit_mod = to_hit_mod

    def _process_rng_str(self, rng_str):

        if rng_str == self.INVALID_RNF:
            return self.INVALID_RNF

        return int(rng_str)

    def mod_at(self, rng):
        print(self.to_hit_mod)
        for idx, rng_brk in enumerate(self.ranges):
            if rng_brk == self.INVALID_RNF:
                return Rngs.OUT_OF, None

            print(f"{rng} : {rng_brk}")
            if rng > rng_brk:
                continue
            rng_id, rng_str, mod = self.RANGES[idx]
            if rng_id is Rngs.MIN:
                return Rngs.MIN, self.calc_min(rng) + self.to_hit_mod
            return rng_str, mod + self.to_hit_mod
        return Rngs.OUT_OF, None

    def calc_min(self, rng):
        return (self.min - rng) + 1


def load_weapons(names):

    if not isinstance(names, list):
        raise RuntimeError(f"Invalid parameter {names}")

    found_weapons = []
    found_weap_names = []
    with open("inner_sphere_weapons.txt", "rt") as dat:

        while True:
            lines = []
            weapon = None

            name = dat.readline().strip()

            # print(f"Name multiammo ?  {name}")
            if name.endswith(
                "**"
            ):  # This is for MML and other weapons with multiple ammos
                name = name[:-2]
                # print(f"multiammo {name}")
                _type = dat.readline().strip()
                weapon = MultAmmoWeapon(name, _type)

                while True:
                    lines = []
                    file_pos = dat.tell()

                    for _ in range(7):
                        line = dat.readline().strip()
                        if line == []:
                            # print("breaking!")
                            break
                        lines.append(line)

                    if lines[1] == "-":  # This is a sub-ammo
                        lines[1] = _type
                        weapon.add_ammo_type(Weapon(lines))
                        continue

                    dat.seek(file_pos)
                    # print(f" breaking on {weapon.name}")
                    break
            else:
                lines = [name]
                for _ in range(6):
                    line = dat.readline().strip()
                    if line == []:
                        break
                    lines.append(line)

                weapon = Weapon(lines)

            # print(weapon.name)
            if weapon.name in names:
                found_weapons.append(weapon)
                found_weap_names.append(weapon.name)
            if len(found_weapons) == len(names):
                return found_weapons

    not_found = [weap for weap in names if weap not in found_weap_names]
    raise WeaponsNotFoundError(f"Weapons not found: {not_found}")


class Entry(EventDispatcher):

    def __init__(self, label, encoder, on_pressed=False):
        super().__init__()
        self.value = 0
        self.label = label
        self.encoder = encoder
        self.on_pressed = on_pressed

    def activate(self):
        if self.on_pressed:
            self.encoder.pressed.register_fn(self.on_update)
        else:
            self.encoder.register_fn(self.on_update)
        self.label.text = str(self.value)

    def deactivate(self):
        if self.on_pressed:
            self.encoder.pressed.deregister_fn(self.on_update)
            return
        self.encoder.deregister_fn(self.on_update)

    def on_update(self, diff):
        self.value = max(self.value + diff, 0)
        self.label.text = str(self.value)
        # print(self.callback_fns)
        self.dispatch_event()


class MultAmmoWeapon:

    def __init__(self, name, _type):
        self._name = name
        self.type = _type
        self.ammo_idx = 0
        self.ammo_types = []

    def add_ammo_type(self, ammo):
        # print("appending ammo")
        self.ammo_types.append(ammo)

    @property
    def name(self):
        return self._name

    @property
    def disp_name(self):
        return f"{self._name} - {self.curr_ammo.name}"

    @property
    def ranges(self):
        return self.ammo_types[self.ammo_idx].ranges

    @property
    def to_hit_mod(self):
        return self.ammo_types[self.ammo_idx].to_hit_mod

    @property
    def curr_ammo(self):
        return self.ammo_types[self.ammo_idx]

    def on_ammo_update(self, diff):
        self.ammo_idx = (self.ammo_idx + diff) % len(self.ammo_types)


class Weapon:

    def __init__(self, weap_strs):
        # print(f"{weap_strs}")
        self.weap_strs = weap_strs
        self.name = weap_strs[0]
        self.types = weap_strs[1]

        self.to_hit_mod = int(weap_strs[6])
        self.ranges = Ranges(
            weap_strs[2], weap_strs[3], weap_strs[4], weap_strs[5], self.to_hit_mod
        )

    @property
    def disp_name(self):
        return self.name

    def on_update(self, diff):
        pass

    def __repr__(self):
        return f"Weapon({self.name},{self.types})"

    def on_ammo_update(self, diff):
        pass


class WeaponsList:

    def __init__(self, weapons, enc):
        self.weapons = weapons
        self.weapon_disp = display.WeaponsList(weapons)
        self.idx = 0
        self.weapon_disp.draw_idx(self.idx)
        self.enc = enc
        self._gat = 0
        self._shot_rng = 1

    def activate(self):
        self.weapon_disp.activate()
        self.enc.register_fn(self.update_selected_weapon)
        self.enc.pressed.register_fn(self.update_ammo_selection)

    def deactivate(self):
        self.weapon_disp.deactivate()
        self.enc.deregister_fn(self.update_selected_weapon)
        self.enc.pressed.deregister_fn(self.update_ammo_selection)

    @property
    def selected_weapon(self):
        return self.weapons[self.idx]

    def update_selected_weapon(self, diff):
        # print(f"update weapon idx {id(self.weapons)}")
        self.idx = (self.idx + diff) % len(self.weapons)
        self.weapon_disp.draw_idx(self.idx)

    def update_ammo_selection(self, diff):
        self.selected_weapon.on_ammo_update(diff)
        self.weapon_disp.update_weap_str(self.idx)
        self._update_weap(self.idx, self._gat, self._shot_rng)

    def update_to_hit(self, gat, shot_rng):
        self._gat = gat
        self._shot_rng = shot_rng
        for idx in range(len(self.weapons)):
            self._update_weap(idx, gat, shot_rng)

    def _update_weap(self, idx, gat, shot_rng):
        weap = self.weapons[idx]
        # print(weap.ranges)
        rng, to_hit = weap.ranges.mod_at(shot_rng)
        if rng is Rngs.OUT_OF:
            self.weapon_disp.update_to_hit(idx, "X")
            return
        self.weapon_disp.update_to_hit(idx, to_hit + gat)


class Mech:

    def __init__(self, name, weapons, encoders, labels):
        self.name = name
        self.encoders = encoders
        self.labels = labels

        self.entrys = Entrys(
            Entry(labels.gun, encoders[0], on_pressed=True),
            Entry(labels.atk, encoders[2]),
            Entry(labels.tar, encoders[3]),
            Entry(labels.other, encoders[4]),
            Entry(labels.rng, encoders[5]),
        )

        for entry in self.entrys:
            entry.register_fn(self.update_gator)

        self.weapons = load_weapons(weapons)

        self.weapons = WeaponsList(self.weapons, encoders[1])

    def activate(self):
        self.labels.name.text = self.name
        for entry in self.entrys:
            entry.activate()

        self.weapons.activate()

    def deactivate(self):
        for entry in self.entrys:
            entry.deactivate()
        self.weapons.deactivate()

    def update_gator(self):
        to_hit = 0
        for entry in self.entrys[:-1]:
            to_hit += entry.value

        self.weapons.update_to_hit(to_hit, self.entrys[-1].value)


class MechSwitcher:

    def __init__(self, enc, mechs=None):
        self.enc = enc
        self.enc.register_fn(self.on_update)

        self.mechs = mechs
        self.active_idx = 0
        self.mechs[0].activate()

    def on_update(self, diff):
        self.mechs[self.active_idx].deactivate()
        self.active_idx = (self.active_idx + diff) % len(self.mechs)
        self.mechs[self.active_idx].activate()
