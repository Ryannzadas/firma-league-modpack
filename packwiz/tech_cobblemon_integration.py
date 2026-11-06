"""
Integracao Tech <-> Cobblemon (estilo All The Mons) para a Firma League (NeoForge 1.21.1).

Gera receitas de maquina (Create, Mekanism, Powah!) que produzem/processam itens do Cobblemon:
  - Create: linha de montagem de Pokebolas (Sequenced Assembly), Exp/Rare Candy no Mixer,
            Vitaminas (EV) no Mixer, Crushing de minerios de Pedras de Evolucao, Haunting.
  - Mekanism: Enrichment de minerios de Pedras de Evolucao (2x), Apricorns -> Bio Fuel,
              Itens de evolucao por troca no Metallurgic Infuser.
  - Powah!: Pedras de Evolucao a partir de Gemas de Tipo no Energizing Orb.

Uso: generate(neo_dp_path) -> escreve os JSONs em data/liga/recipe/tech/...
"""
import json
from pathlib import Path

TRANSITIONAL = "create:incomplete_precision_mechanism"

EVO_STONES = ["fire", "water", "thunder", "leaf", "moon", "sun", "shiny", "dusk", "dawn", "ice"]
EXTRA_ORES = {
    "fire": ["nether_fire_stone_ore"],
    "moon": ["dripstone_moon_stone_ore"],
    "sun": ["terracotta_sun_stone_ore"],
}
APRICORNS = ["red", "yellow", "green", "blue", "pink", "black", "white"]


def _w(base: Path, rel: str, data: dict, out: list):
    p = base / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    out.append(rel)


def _deploy(item):
    return {
        "type": "create:deploying",
        "ingredients": [{"item": TRANSITIONAL}, {"item": item}],
        "results": [{"id": TRANSITIONAL}],
    }


def _press():
    return {
        "type": "create:pressing",
        "ingredients": [{"item": TRANSITIONAL}],
        "results": [{"id": TRANSITIONAL}],
    }


def _assembly(base_ing, steps, result_id, count, loops=1):
    return {
        "type": "create:sequenced_assembly",
        "ingredient": base_ing,
        "loops": loops,
        "results": [{"id": result_id, "count": count}],
        "sequence": steps,
        "transitional_item": {"id": TRANSITIONAL},
    }


def _ores_for(stone):
    return [f"{stone}_stone_ore", f"deepslate_{stone}_stone_ore"] + EXTRA_ORES.get(stone, [])


def generate(neo_dp: Path) -> list:
    base = Path(neo_dp) / "data/liga/recipe/tech"
    out = []

    # ------------------------------------------------------------------ CREATE
    # 1) Linha de montagem de Pokebolas (Deployers + Press numa esteira)
    _w(base, "create/assembly_poke_ball.json", _assembly(
        {"item": "create:iron_sheet"},
        [_deploy("cobblemon:red_apricorn"), _deploy("minecraft:stone_button"), _press()],
        "cobblemon:poke_ball", 4), out)
    _w(base, "create/assembly_great_ball.json", _assembly(
        {"item": "create:iron_sheet"},
        [_deploy("cobblemon:blue_apricorn"), _deploy("cobblemon:red_apricorn"),
         _deploy("minecraft:stone_button"), _press()],
        "cobblemon:great_ball", 4), out)
    _w(base, "create/assembly_ultra_ball.json", _assembly(
        {"item": "create:brass_sheet"},
        [_deploy("cobblemon:yellow_apricorn"), _deploy("cobblemon:black_apricorn"),
         _deploy("create:electron_tube"), _press()],
        "cobblemon:ultra_ball", 4), out)
    _w(base, "create/assembly_premier_ball.json", _assembly(
        {"item": "create:iron_sheet"},
        [_deploy("cobblemon:white_apricorn"), _deploy("cobblemon:white_apricorn"),
         _deploy("minecraft:stone_button"), _press()],
        "cobblemon:premier_ball", 4), out)

    # 2) Doces de experiencia no Mixer (Experience Nuggets vem do Crushing do Create)
    _w(base, "create/mixing_exp_candy_s.json", {
        "type": "create:mixing", "heat_requirement": "heated",
        "ingredients": [{"item": "create:experience_nugget"}] * 4 + [{"item": "minecraft:sugar"}],
        "results": [{"id": "cobblemon:exp_candy_s"}]}, out)
    _w(base, "create/mixing_exp_candy_m.json", {
        "type": "create:mixing", "heat_requirement": "heated",
        "ingredients": [{"item": "cobblemon:exp_candy_s"}] * 3 + [{"item": "minecraft:honey_bottle"}],
        "results": [{"id": "cobblemon:exp_candy_m"}]}, out)
    _w(base, "create/mixing_exp_candy_l.json", {
        "type": "create:mixing", "heat_requirement": "superheated",
        "ingredients": [{"item": "cobblemon:exp_candy_m"}] * 3 + [{"item": "minecraft:glow_berries"}],
        "results": [{"id": "cobblemon:exp_candy_l"}]}, out)
    _w(base, "create/mixing_rare_candy.json", {
        "type": "create:mixing", "heat_requirement": "superheated",
        "ingredients": [{"item": "cobblemon:exp_candy_l"}] * 2 + [{"item": "minecraft:golden_apple"}],
        "results": [{"id": "cobblemon:rare_candy"}]}, out)

    # 3) Vitaminas (EVs) no Mixer aquecido
    vitamins = {
        "hp_up": "minecraft:golden_carrot",
        "protein": "minecraft:cooked_beef",
        "iron": "create:iron_sheet",
        "calcium": "minecraft:bone_block",
        "zinc": "minecraft:prismarine_crystals",
        "carbos": "minecraft:sugar_cane",
    }
    for vit, extra in vitamins.items():
        _w(base, f"create/mixing_{vit}.json", {
            "type": "create:mixing", "heat_requirement": "heated",
            "ingredients": [
                {"item": "cobblemon:medicinal_leek"},
                {"item": extra},
                {"item": "minecraft:sugar"},
                {"type": "neoforge:single", "amount": 250, "fluid": "minecraft:water"},
            ],
            "results": [{"id": f"cobblemon:{vit}"}]}, out)

    # 4) Crushing Wheel: minerios de Pedra de Evolucao -> pedras + bonus
    for st in EVO_STONES:
        for ore in _ores_for(st):
            _w(base, f"create/crushing_{ore}.json", {
                "type": "create:crushing", "processing_time": 300,
                "ingredients": [{"item": f"cobblemon:{ore}"}],
                "results": [
                    {"id": f"cobblemon:{st}_stone"},
                    {"id": f"cobblemon:{st}_stone", "chance": 0.5},
                    {"id": "create:experience_nugget", "chance": 0.75},
                ]}, out)

    # 5) Haunting (ventilador + fogo de alma): Moon Stone -> Dusk Stone
    _w(base, "create/haunting_dusk_stone.json", {
        "type": "create:haunting",
        "ingredients": [{"item": "cobblemon:moon_stone"}],
        "results": [{"id": "cobblemon:dusk_stone"}]}, out)

    # ---------------------------------------------------------------- MEKANISM
    # 1) Enrichment Chamber: minerio -> 2 pedras
    for st in EVO_STONES:
        for ore in _ores_for(st):
            _w(base, f"mekanism/enriching_{ore}.json", {
                "type": "mekanism:enriching",
                "input": {"count": 1, "item": f"cobblemon:{ore}"},
                "output": {"count": 2, "id": f"cobblemon:{st}_stone"}}, out)

    # 2) Crusher: Apricorns -> Bio Fuel (energia para a base)
    for ap in APRICORNS:
        _w(base, f"mekanism/crushing_{ap}_apricorn_biofuel.json", {
            "type": "mekanism:crushing",
            "input": {"count": 1, "item": f"cobblemon:{ap}_apricorn"},
            "output": {"count": 4, "id": "mekanism:bio_fuel"}}, out)

    # 3) Metallurgic Infuser: itens de evolucao por troca
    infusing = [
        ("metal_coat", {"tag": "c:ingots/steel"}, "mekanism:redstone", 40),
        ("dragon_scale", {"item": "minecraft:prismarine_shard"}, "mekanism:diamond", 40),
        ("kings_rock", {"tag": "c:ingots/gold"}, "mekanism:diamond", 20),
        ("razor_claw", {"item": "minecraft:flint"}, "mekanism:diamond", 20),
        ("protector", {"item": "minecraft:iron_block"}, "mekanism:refined_obsidian", 20),
        ("electirizer", {"item": "mekanism:alloy_infused"}, "mekanism:redstone", 80),
        ("magmarizer", {"item": "minecraft:magma_cream"}, "mekanism:carbon", 80),
        ("reaper_cloth", {"item": "minecraft:phantom_membrane"}, "mekanism:fungi", 40),
        ("prism_scale", {"item": "minecraft:prismarine_crystals"}, "mekanism:diamond", 20),
    ]
    for res, item_in, chem, amt in infusing:
        _w(base, f"mekanism/infusing_{res}.json", {
            "type": "mekanism:metallurgic_infusing",
            "chemical_input": {"amount": amt, "tag": chem},
            "item_input": dict(count=1, **item_in),
            "output": {"count": 1, "id": f"cobblemon:{res}"},
            "per_tick_usage": False}, out)

    # ------------------------------------------------------------------ POWAH!
    # Energizing Orb: 2 Gemas de Tipo + 1 Ametista -> Pedra de Evolucao
    gem_to_stone = {
        "fire": "fire", "water": "water", "electric": "thunder", "grass": "leaf",
        "ice": "ice", "fairy": "moon", "normal": "sun", "psychic": "dawn",
        "ghost": "dusk", "dragon": "shiny",
    }
    for gem, st in gem_to_stone.items():
        _w(base, f"powah/energizing_{st}_stone.json", {
            "type": "powah:energizing",
            "ingredients": [
                {"item": f"cobblemon:{gem}_gem"},
                {"item": f"cobblemon:{gem}_gem"},
                {"item": "minecraft:amethyst_shard"},
            ],
            "energy": 30000,
            "result": {"id": f"cobblemon:{st}_stone", "count": 1}}, out)

    return out


ALL_ITEMS_USED_PREFIXES = ("cobblemon:", "create:", "mekanism:", "powah:")


def referenced_items(neo_dp: Path, rels: list) -> set:
    """Retorna todos os IDs de item (mod:item) usados nas receitas geradas, para auditoria."""
    ids = set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("item", "id") and isinstance(v, str):
                    ids.add(v)
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    base = Path(neo_dp) / "data/liga/recipe/tech"
    for r in rels:
        walk(json.loads((base / r).read_text(encoding="utf-8")))
    return ids
