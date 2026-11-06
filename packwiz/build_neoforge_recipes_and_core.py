import os
import json
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DP = BASE_DIR / "server/datapacks/liga_pokemon_helper"
NEO_DP = BASE_DIR / "server/datapacks/liga_pokemon_neoforge"
NEO_MODS = BASE_DIR / "build_neoforge/overrides/mods"

if NEO_DP.exists():
    shutil.rmtree(NEO_DP)
shutil.copytree(SRC_DP, NEO_DP)

# Remove TechReborn recipes (replaced by Create + Mekanism)
tr_dir = NEO_DP / "data/techreborn"
if tr_dir.exists():
    shutil.rmtree(tr_dir)

# Map TechReborn item IDs to Mekanism / Create equivalents across all JSON recipes
ITEM_MAP = {
    "techreborn:refined_iron_ingot": "create:iron_sheet",
    "techreborn:electronic_circuit": "mekanism:basic_control_circuit",
    "techreborn:advanced_circuit": "mekanism:advanced_control_circuit",
    "techreborn:industrial_circuit": "mekanism:ultimate_control_circuit",
    "techreborn:insulated_copper_cable": "mekanism:basic_universal_cable",
    "powah:capacitor_basic": "create:electron_tube",
}

for p in NEO_DP.rglob("*.json"):
    rel = p.relative_to(NEO_DP).as_posix()
    if "/recipe/" in rel:
        txt = p.read_text(encoding="utf-8")
        for old_id, new_id in ITEM_MAP.items():
            txt = txt.replace(f'"{old_id}"', f'"{new_id}"')
        data = json.loads(txt)
        if "fabric:load_conditions" in data:
            del data["fabric:load_conditions"]
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

# Update Tier 2 & Tier 3 Pokeball material tags for Create + Mekanism + Powah!
tier2_tag = {
    "replace": True,
    "values": [
        "create:iron_sheet",
        "create:andesite_alloy",
        "mekanism:ingot_osmium",
        "mekanism:ingot_steel"
    ]
}
(NEO_DP / "data/cobblemon/tags/item/tier_2_poke_ball_materials.json").write_text(
    json.dumps(tier2_tag, indent=2), encoding="utf-8"
)

tier3_tag = {
    "replace": True,
    "values": [
        "create:brass_sheet",
        "mekanism:alloy_infused",
        "powah:dielectric_paste",
        "powah:steel_energized"
    ]
}
(NEO_DP / "data/cobblemon/tags/item/tier_3_poke_ball_materials.json").write_text(
    json.dumps(tier3_tag, indent=2), encoding="utf-8"
)

# Update Master Ball recipe to use Mekanism Ultimate Control Circuit + Atomic Alloy + Powah Nitro Crystal
master_ball = {
    "type": "minecraft:crafting_shaped",
    "category": "equipment",
    "pattern": [
        "PMP",
        "CNC",
        "ASA"
    ],
    "key": {
        "P": {"item": "cobblemon:pink_apricorn"},
        "M": {"item": "powah:crystal_nitro"},
        "C": {"item": "mekanism:ultimate_control_circuit"},
        "N": {"item": "minecraft:nether_star"},
        "A": {"item": "mekanism:alloy_atomic"},
        "S": {"item": "minecraft:shulker_shell"}
    },
    "result": {
        "id": "cobblemon:master_ball",
        "count": 1
    }
}
(NEO_DP / "data/cobblemon/recipe/master_ball.json").write_text(
    json.dumps(master_ball, indent=2), encoding="utf-8"
)

# Override Omni Ring and all Mega Bracelet / Z-Ring / Character variants in Mega Showdown
ms_jar = NEO_MODS / "mega_showdown-neoforge-1.3.3+1.8.4+1.21.1-release.jar"
ms_recipe_dir = NEO_DP / "data/mega_showdown/recipe"
ms_recipe_dir.mkdir(parents=True, exist_ok=True)

if ms_jar.exists():
    with zipfile.ZipFile(ms_jar, "r") as zms:
        for rpath in zms.namelist():
            if not (rpath.startswith("data/mega_showdown/recipe/") and rpath.endswith(".json")):
                continue
            rname = rpath.split("/")[-1]
            if rname in ("keystone.json", "keystone_block.json", "power_spot.json", "omni_ring.json", "mega_bracelet.json", "z_power_ring.json", "dynamax_band.json", "tera_orb.json"):
                continue
            raw = zms.read(rpath).decode("utf-8")
            if any(k in raw for k in ("mega_showdown:keystone", "mega_showdown:sparkling_stone_light", "mega_showdown:sparkling_stone_dark")):
                rdata = json.loads(raw)
                if rdata.get("type") == "minecraft:crafting_shaped" and "key" in rdata and "pattern" in rdata:
                    # Replace vanilla iron/gold/copper with powah:steel_energized
                    replaced_metal = False
                    for k, v in list(rdata["key"].items()):
                        if isinstance(v, dict) and v.get("item") in ("minecraft:iron_ingot", "minecraft:gold_ingot", "minecraft:copper_ingot"):
                            rdata["key"][k] = {"item": "powah:steel_energized"}
                            replaced_metal = True
                    # Inject mekanism:basic_control_circuit into bottom center of pattern
                    pat = list(rdata["pattern"])
                    if len(pat) == 3 and len(pat[2]) == 3:
                        row2 = list(pat[2])
                        row2[1] = "E"
                        pat[2] = "".join(row2)
                        rdata["pattern"] = pat
                        rdata["key"]["E"] = {"item": "mekanism:basic_control_circuit"}
                    # Remove unused keys if any
                    used_chars = set("".join(rdata["pattern"]))
                    rdata["key"] = {k: v for k, v in rdata["key"].items() if k in used_chars}
                    (ms_recipe_dir / rname).write_text(json.dumps(rdata, indent=2), encoding="utf-8")

omni_ring_recipe = {
    "type": "minecraft:crafting_shaped",
    "category": "misc",
    "pattern": [
        "CDC",
        "MNZ",
        "PTP"
    ],
    "key": {
        "C": {"item": "mekanism:elite_control_circuit"},
        "D": {"item": "mega_showdown:dynamax_band"},
        "M": [
            {"item": "mega_showdown:mega_bracelet"},
            {"item": "mega_showdown:mega_ring"}
        ],
        "N": {"item": "minecraft:netherite_ingot"},
        "Z": [
            {"item": "mega_showdown:z_power_ring"},
            {"item": "mega_showdown:z_ring"}
        ],
        "P": {"item": "powah:crystal_niotic"},
        "T": {"item": "mega_showdown:tera_orb"}
    },
    "result": {
        "id": "mega_showdown:omni_ring",
        "count": 1
    }
}
(ms_recipe_dir / "omni_ring.json").write_text(
    json.dumps(omni_ring_recipe, indent=2), encoding="utf-8"
)

# Update Radical Gyms & Structures jar in build_neoforge/overrides/mods so Giovanni is optional
rgs_jar = NEO_MODS / "Radical Gyms  Structures - RGS.jar"
if rgs_jar.exists():
    dp_mobs_dir = NEO_DP / "data/rctmod/mobs/trainers/single"
    modified = {}
    for f in dp_mobs_dir.glob("*.json"):
        modified[f.name] = json.loads(f.read_text(encoding="utf-8"))
    tmp_rgs = rgs_jar.with_suffix(".jar.tmp")
    with zipfile.ZipFile(rgs_jar, "r") as zin, zipfile.ZipFile(tmp_rgs, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            fname = item.filename.split("/")[-1]
            if item.filename.startswith("data/rctmod/mobs/trainers/single/") and fname in modified:
                zout.writestr(item, json.dumps(modified[fname], indent=2).encode("utf-8"))
            else:
                zout.writestr(item, zin.read(item.filename))
    os.replace(tmp_rgs, rgs_jar)

# Integracao Tech <-> Cobblemon (Create / Mekanism / Powah processando itens Pokemon)
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tech_cobblemon_integration as tci
tech_rels = tci.generate(NEO_DP)
# Auditoria: todo item de mod referenciado precisa existir em algum jar
mod_models = set()
for jf in NEO_MODS.glob("*.jar"):
    if jf.name.startswith("zzz-firma"):
        continue
    with zipfile.ZipFile(jf) as zj:
        for n in zj.namelist():
            parts = n.split("/")
            if len(parts) == 5 and parts[0] == "assets" and parts[2] == "models" and parts[3] == "item" and n.endswith(".json"):
                mod_models.add(f"{parts[1]}:{parts[4][:-5]}")
missing = sorted(i for i in tci.referenced_items(NEO_DP, tech_rels)
                 if not i.startswith("minecraft:") and i not in mod_models)
if missing:
    raise SystemExit(f"Itens inexistentes nas receitas tech: {missing}")
print(f"Integracao tech: {len(tech_rels)} receitas geradas, todos os itens verificados.")

# Loot de exploracao (Global Loot Modifiers nativos do NeoForge)
import exploration_loot as xl
xres = xl.generate(NEO_DP, NEO_MODS)
xmissing = sorted(i for i in xres["used_items"]
                  if not i.startswith("minecraft:") and i not in mod_models)
if xmissing:
    raise SystemExit(f"Itens inexistentes no loot de exploracao: {xmissing}")
print(f"Loot de exploracao: {len(xres['tables'])} arquivos ({xres['megas']} Mega Stones e {xres['zs']} Z-Crystals no sorteio), itens verificados.")

# Build zzz-firma-league-core-2.0.0.jar for NeoForge 1.21.1 with ordering = "AFTER"
after_mods = [
    "cobblemon", "create", "createaddition", "mekanism", "powah", "ae2",
    "industrialforegoing", "betterfurnacesreforged", "sophisticatedbackpacks",
    "sophisticatedstorage", "toms_storage", "mega_showdown", "cobblemon_utility",
    "cobblemonboxlink", "explorerscompass", "naturescompass", "waystones",
    "rctmod", "rgs", "mr_more_radicaltrainers"
]

toml_lines = [
    'modLoader = "lowcodefml"',
    'loaderVersion = "[2,)"',
    'license = "MIT"',
    'showAsResourcePack = false',
    '',
    '[[mods]]',
    'modId = "zzz_firma_league_core"',
    'version = "2.0.0"',
    'displayName = "Firma League Core (Create + Mekanism + Powah + Cobblemon)"',
    'description = "Receitas integradas Create + Mekanism + Powah + AE2, lideres balanceados e progressao direta de ginasios."',
    ''
]
for m in after_mods:
    toml_lines.extend([
        '[[dependencies.zzz_firma_league_core]]',
        f'modId = "{m}"',
        'type = "optional"',
        'mandatory = false',
        'ordering = "AFTER"',
        'side = "BOTH"',
        ''
    ])
toml_content = "\n".join(toml_lines)

core_jar = NEO_MODS / "zzz-firma-league-core-2.0.0.jar"
with zipfile.ZipFile(core_jar, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("META-INF/neoforge.mods.toml", toml_content)
    zf.writestr("META-INF/mods.toml", toml_content)
    for p in NEO_DP.rglob("*"):
        if p.is_file():
            rel = p.relative_to(NEO_DP).as_posix()
            zf.write(p, rel)

print("Sucesso! zzz-firma-league-core-2.0.0.jar gerado e verificado para NeoForge 1.21.1!")
