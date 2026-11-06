"""
Loot de EXPLORACAO da Firma League (NeoForge 1.21.1).

Injeta, via Global Loot Modifiers nativos do NeoForge (neoforge:add_table), uma rolagem extra
nos baus de estruturas vanilla, estruturas lendarias e Raid Dens. Moderado: nao e todo bau,
mas ao explorar uma sessao curta (~30-40 min) costuma render algo util.

Tiers:
  tier1 (estruturas comuns)  -> 30% por bau: doces, vitaminas, pedras, Tera Shards, bolas
  tier2 (estruturas medias)  -> 45% por bau + 12% de achado raro (Keystone, Wishing Star...)
  tier3 (estruturas dificeis)-> 60% por bau + 25% de achado raro (inclui Master Ball, Ability Patch)
"""
import json
import re
import zipfile
from pathlib import Path

TYPES = ["bug", "dark", "dragon", "electric", "fairy", "fighting", "fire", "flying", "ghost",
         "grass", "ground", "ice", "normal", "poison", "psychic", "rock", "steel", "water"]
STONES = ["fire", "water", "thunder", "leaf", "moon", "sun", "dusk", "dawn", "ice", "shiny"]
VITAMINS = ["hp_up", "protein", "iron", "calcium", "zinc", "carbos"]

# alvo (id da loot table) -> tier
TARGETS = {
    # tier 1: estruturas comuns
    "minecraft:chests/simple_dungeon": 1,
    "minecraft:chests/abandoned_mineshaft": 1,
    "minecraft:chests/desert_pyramid": 1,
    "minecraft:chests/jungle_temple": 1,
    "minecraft:chests/shipwreck_treasure": 1,
    "minecraft:chests/buried_treasure": 1,
    "minecraft:chests/underwater_ruin_big": 1,
    "minecraft:chests/ruined_portal": 1,
    "minecraft:chests/pillager_outpost": 1,
    "minecraft:chests/igloo_chest": 1,
    "cobblemonraiddens:raid/tier/tier_two": 1,
    "cobblemonraiddens:raid/tier/tier_three": 1,
    "nova_structures:chests/dungeon_1": 1,
    "nova_structures:chests/dungeon_2": 1,
    "nova_structures:chests/dungeon_3": 1,
    "nova_structures:chests/dungeon_4": 1,
    "nova_structures:chests/creeping_crypt/crypt_hallway": 1,
    # tier 2: estruturas medias
    "minecraft:chests/stronghold_corridor": 2,
    "minecraft:chests/stronghold_crossing": 2,
    "minecraft:chests/stronghold_library": 2,
    "minecraft:chests/woodland_mansion": 2,
    "minecraft:chests/bastion_treasure": 2,
    "minecraft:chests/bastion_other": 2,
    "minecraft:chests/nether_bridge": 2,
    "minecraft:chests/trial_chambers/reward": 2,
    "legends_untold:chests/tera_den": 2,
    "cobblemonraiddens:raid/tier/tier_four": 2,
    "cobblemonraiddens:raid/tier/tier_five": 2,
    "nova_structures:chests/dungeon_5": 2,
    "nova_structures:chests/dungeon_6": 2,
    "nova_structures:chests/dungeon_7": 2,
    "nova_structures:chests/creeping_crypt/vault_creeping": 2,
    "nova_structures:chests/shrine/combat_treasure_1": 2,
    "nova_structures:chests/lone_citadel/c_vault": 2,
    "nova_structures:chests/nether_keep/vault_keep": 2,
    "minecraft:chests/illager_mansion/evoker_chest": 2,
    "artifacts:chests/campsite_chest": 2,
    # tier 3: estruturas dificeis
    "minecraft:chests/end_city_treasure": 3,
    "minecraft:chests/ancient_city": 3,
    "minecraft:chests/trial_chambers/reward_ominous": 3,
    "legends_untold:chests/sky_pillar": 3,
    "cobblemonraiddens:raid/tier/tier_six": 3,
    "cobblemonraiddens:raid/tier/tier_seven": 3,
    "nova_structures:chests/shrine/vault_shrine_ominous": 3,
    "nova_structures:chests/lone_citadel/c_vault_boss": 3,
    "nova_structures:chests/end_castle/greater_loot": 3,
    "nova_structures:chests/end_castle/vault_slope": 3,
    "minecraft:chests/illager_mansion/ancient_city_raid_chest": 3,
}

CHANCE = {1: 0.30, 2: 0.45, 3: 0.60}
RARE_CHANCE = {2: 0.12, 3: 0.25}


def item(name, weight, lo=None, hi=None):
    e = {"type": "minecraft:item", "name": name, "weight": weight}
    if lo is not None:
        e["functions"] = [{
            "function": "minecraft:set_count",
            "count": lo if lo == hi else {"type": "minecraft:uniform", "min": float(lo), "max": float(hi)},
        }]
    return e


def table(entries, chance):
    return {
        "type": "minecraft:chest",
        "pools": [{
            "rolls": 1,
            "bonus_rolls": 0.0,
            "conditions": [{"condition": "minecraft:random_chance", "chance": chance}],
            "entries": entries,
        }],
    }


def _scan_ms(neo_mods: Path):
    """Le o jar do Mega Showdown para listar Mega Stones e Z-Crystals reais."""
    jars = list(Path(neo_mods).glob("mega_showdown*.jar"))
    if not jars:
        return [], []
    with zipfile.ZipFile(jars[0]) as z:
        names = z.namelist()
    models = {n.split("/")[-1][:-5] for n in names
              if n.startswith("assets/mega_showdown/models/item/") and n.endswith(".json")}
    recipes = {n.split("/")[-1][:-5] for n in names
               if n.startswith("data/mega_showdown/recipe/") and n.endswith(".json")}
    megas = sorted(m for m in models if m in recipes and re.search(r"ite(_x|_y|z)?$", m)
                   and not m.startswith("tera_pouch"))
    zs = sorted(m for m in models if m in recipes and m.endswith("ium_z"))
    return megas, zs


def generate(neo_dp: Path, neo_mods: Path):
    neo_dp = Path(neo_dp)
    base = neo_dp / "data/liga"
    out = {"tables": [], "used_items": set()}

    def write(rel, data):
        p = neo_dp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        out["tables"].append(rel)

    megas, zs = _scan_ms(neo_mods)

    # sub-tabelas de sorteio uniforme
    if megas:
        write("data/liga/loot_table/exploration/mega_stone_random.json", {
            "type": "minecraft:chest",
            "pools": [{"rolls": 1, "entries": [item(f"mega_showdown:{m}", 1) for m in megas]}],
        })
    if zs:
        write("data/liga/loot_table/exploration/z_crystal_random.json", {
            "type": "minecraft:chest",
            "pools": [{"rolls": 1, "entries": [item(f"mega_showdown:{z}", 1) for z in zs]}],
        })

    def common(tier):
        mult = {1: (1, 2), 2: (2, 3), 3: (3, 4)}[tier]
        e = [
            item("cobblemon:rare_candy", 10, mult[0], mult[1]),
            item("cobblemon:exp_candy_m", 14, 1, 3),
            item("cobblemon:exp_candy_l", 8, 1, 2),
            item("cobblemon:pp_up", 3, 1, 1),
            item("mega_showdown:dynamax_candy", 6, 1, 2),
            item("cobblemon:great_ball", 6, 2, 5),
            item("cobblemon:ultra_ball", 5, 2, 4),
            item("cobblemon:quick_ball", 3, 2, 3),
            item("cobblemon:dusk_ball", 3, 2, 3),
        ]
        e += [item(f"cobblemon:{v}", 3, 1, 1) for v in VITAMINS]
        e += [item(f"cobblemon:{s}_stone", 2, 1, 1) for s in STONES]
        e += [item(f"mega_showdown:{t}_tera_shard", 1 if tier == 1 else 2, 1, 2 if tier > 1 else 1) for t in TYPES]
        if tier >= 2:
            e += [
                item("cobblemon:exp_candy_xl", 4, 1, 1),
                item("cobblemon:pp_max", 2, 1, 1),
                item("cobblemon:ability_capsule", 3, 1, 1),
                item("cobblemon:link_cable", 2, 1, 1),
            ]
            e += [item(f"cobblemon:{h}", 2, 1, 1) for h in
                  ["choice_band", "choice_specs", "choice_scarf", "assault_vest", "life_orb",
                   "leftovers", "focus_sash", "destiny_knot"]]
        return e

    def rare(tier):
        e = [
            item("mega_showdown:keystone", 6 if tier == 2 else 8, 1, 1),
            item("mega_showdown:wishing_star", 6 if tier == 2 else 8, 1, 1),
            item("mega_showdown:sparkling_stone_light", 5 if tier == 2 else 6, 1, 1),
            item("mega_showdown:sparkling_stone_dark", 5 if tier == 2 else 6, 1, 1),
            item("cobblemon:ability_patch", 2 if tier == 2 else 4, 1, 1),
            item("simplyswords:runic_tablet", 3 if tier == 2 else 5, 1, 1),
            item("cobblemon_utility:defsilvercap", 2, 1, 1),
            item("cobblemon_utility:atksilvercap", 2, 1, 1),
            item("cobblemon_utility:speedsilvercap", 2, 1, 1),
            item("cobblemon_utility:hpsilvercap", 2, 1, 1),
        ]
        if tier == 3:
            e.append(item("cobblemon:master_ball", 1, 1, 1))
            e.append(item("cobblemon_utility:goldencap", 2, 1, 1))
        if megas:
            e.append({"type": "minecraft:loot_table", "value": "liga:exploration/mega_stone_random",
                      "weight": 10 if tier == 2 else 12})
        if zs:
            e.append({"type": "minecraft:loot_table", "value": "liga:exploration/z_crystal_random",
                      "weight": 6 if tier == 2 else 8})
        return e

    for tier in (1, 2, 3):
        t = table(common(tier), CHANCE[tier])
        if tier in RARE_CHANCE:
            t["pools"].append({
                "rolls": 1, "bonus_rolls": 0.0,
                "conditions": [{"condition": "minecraft:random_chance", "chance": RARE_CHANCE[tier]}],
                "entries": rare(tier),
            })
        write(f"data/liga/loot_table/exploration/tier{tier}.json", t)

    # um modificador por alvo + lista global
    entries = []
    for target, tier in TARGETS.items():
        mod_id = "explore_" + re.sub(r"[^a-z0-9_]", "_", target.split(":", 1)[1].lower()) \
                 + "_" + target.split(":", 1)[0]
        write(f"data/liga/loot_modifiers/{mod_id}.json", {
            "type": "neoforge:add_table",
            "conditions": [{"condition": "neoforge:loot_table_id", "loot_table_id": target}],
            "table": f"liga:exploration/tier{tier}",
        })
        entries.append(f"liga:{mod_id}")
    write("data/neoforge/loot_modifiers/global_loot_modifiers.json", {"replace": False, "entries": entries})

    # itens usados (para auditoria)
    for rel in out["tables"]:
        if "/loot_table/" in rel:
            blob = json.loads((neo_dp / rel).read_text(encoding="utf-8"))
            for pool in blob["pools"]:
                for en in pool["entries"]:
                    if en.get("type") == "minecraft:item":
                        out["used_items"].add(en["name"])
    out["megas"], out["zs"] = len(megas), len(zs)
    return out
