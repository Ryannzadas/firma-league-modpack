import os
import json
import shutil
import zipfile
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(BASE_DIR, "build_temp")
OVERRIDES_DIR = os.path.join(BUILD_DIR, "overrides")
MODS_DIR = os.path.join(OVERRIDES_DIR, "mods")
RP_DIR = os.path.join(OVERRIDES_DIR, "resourcepacks")
DP_DIR = os.path.join(OVERRIDES_DIR, "datapacks")

MC_VERSION = "1.21.1"
LOADER = "fabric"

# Lista completa de slugs do Modrinth para baixar em overrides/mods/
MODRINTH_MODS = [
    # Core & Libraries
    "fabric-api",
    "fabric-language-kotlin",
    "architectury-api",
    "cloth-config",
    "forge-config-api-port",
    "geckolib",
    "athena-ctm",
    "balm",
    "resourceful-lib",
    "cardinal-components-api",
    "iceberg",
    "cobblemon-tim-core",
    "lavender",
    "lithostitched",

    # Cobblemon & História
    "cobblemon",
    "rctapi",
    "rctmod",
    "radical-gyms-structures",
    "more-radical-trainers",
    "cobblemon-pokemon-badges",

    # Competitivo, Efetividade na Batalha, Megas, Breeding, TMs & IVs
    "cobblemon-mega-showdown",
    "cobblemon-battle-extras",
    "cobblemon-effectiveness",
    "simpletms",
    "cobbreeding",
    "cobblemon-utility+",
    "cobblemon-unchained",
    "cobblemon-counter",
    "cobblemon-capture-xp",

    # Lendários, Montarias, Workers & Extras
    "myths-and-legends-cobblemon-sidemod",
    "cobblemon-legendary-structures",
    "cobblemon-spawn-notification",
    "cobblemon-pokenav",
    "cobblemon-box-link",
    "cobblemon-outbreaks",
    "cobblemon-parting-gifts",
    "cobblemon-size-variations",
    "cobblemonrider",
    "cobbleworkers",
    "knowlogy",
    "cobblemon-wiki-gui",
    "cobblemon-integrations",
    "cobblemon-fight-or-flight-reborn",

    # Exploração, Mundo, QOL, RP (Roleplay) & Conquistas Cobbleverse
    "explorers-compass",
    "natures-compass",
    "waystones",
    "terralith",
    "sophisticated-core-unofficial-fabric-port",
    "sophisticated-backpacks-unoffical-fabric-port",
    "sophisticated-storage-fabric",
    "toms-storage",
    "factory-api",
    "better-furnaces-reforged",
    "reborncore",
    "techreborn",
    "powah-refabric",
    "travelersbackpack",
    "cobblefurnies",
    "handcrafted",
    "chipped",
    "xaeros-minimap",
    "xaeros-world-map",
    "emi",
    "jade",
    "simple-voice-chat",
    "sound-physics-remastered",
    "bendy-lib",
    "playeranimator",
    "emotecraft",
    "cobbledollars",
    "exposure",
    "owo-lib",
    "accessories",
    "simplehats",
    "lootr",
    "advancement-plaques",
    "better-advancements",
    "controlling",
    "searchables",
    "zoomify",
    "yacl",

    # Performance
    "lithium",
    "ferrite-core",
    "krypton",
    "chunky",
    "sodium",
    "iris",
    "entityculling",
    "immediatelyfast"
]

MODRINTH_RESOURCEPACKS = [
    "cobblemon-advancement-plaques",
    "cobblemon-interface",
    "cobblemon-interface-modded",
    "radical-trainer-textures-plus",
    "e19-cobblemon-minimap-icons"
]


def search_modrinth_slug(query_text):
    url = f"https://api.modrinth.com/v2/search?query={urllib.parse.quote(query_text)}&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "FirmaLeagueModpackBuilder/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        hits = data.get("hits", [])
        if hits:
            return hits[0]["slug"]
    return None


def fetch_modrinth_file(slug, target_dir, is_resourcepack=False):
    loaders_param = '["minecraft"]' if is_resourcepack else f'["{LOADER}"]'
    versions_param = f'["{MC_VERSION}"]'
    url = (
        f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version"
        f"?game_versions={urllib.parse.quote(versions_param)}"
    )
    if not is_resourcepack:
        url += f"&loaders={urllib.parse.quote(loaders_param)}"

    req = urllib.request.Request(url, headers={"User-Agent": "FirmaLeagueModpackBuilder/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            versions = json.loads(resp.read().decode("utf-8"))
            if not versions:
                # Tenta sem filtro de loader/versão caso seja datapack empacotado ou resourcepack
                url_fallback = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version?game_versions={urllib.parse.quote(versions_param)}"
                req2 = urllib.request.Request(url_fallback, headers={"User-Agent": "FirmaLeagueModpackBuilder/1.0"})
                with urllib.request.urlopen(req2, timeout=15) as resp2:
                    versions = json.loads(resp2.read().decode("utf-8"))

            if not versions and is_resourcepack:
                url_fallback2 = f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version"
                req3 = urllib.request.Request(url_fallback2, headers={"User-Agent": "FirmaLeagueModpackBuilder/1.0"})
                with urllib.request.urlopen(req3, timeout=15) as resp3:
                    versions = json.loads(resp3.read().decode("utf-8"))

            if not versions:
                print(f"  [!] Nenhuma versão 1.21.1 encontrada para: {slug}")
                return None

            latest = versions[0]
            primary_file = next((f for f in latest["files"] if f.get("primary")), latest["files"][0])
            dl_url = primary_file["url"]
            filename = primary_file["filename"]
            dest_path = os.path.join(target_dir, filename)

            if not os.path.exists(dest_path):
                print(f"  [+] Baixando: {filename}")
                urllib.request.urlretrieve(dl_url, dest_path)
            else:
                print(f"  [=] Já existe: {filename}")
            return primary_file
    except urllib.error.HTTPError as e:
        if e.code == 404:
            found_slug = search_modrinth_slug(slug.replace("-", " "))
            if found_slug and found_slug != slug:
                print(f"  [~] Slug '{slug}' resolvido via busca para '{found_slug}'")
                return fetch_modrinth_file(found_slug, target_dir, is_resourcepack)
        print(f"  [x] Erro ao buscar {slug}: {e}")
        return None
    except Exception as e:
        print(f"  [x] Erro ao buscar {slug}: {e}")
        return None


def main():
    print("=================================================================")
    print("  GERADOR DO MODPACK FIRMA LEAGUE (CurseForge .zip + Overrides)  ")
    print("=================================================================")

    os.makedirs(MODS_DIR, exist_ok=True)
    os.makedirs(RP_DIR, exist_ok=True)
    os.makedirs(DP_DIR, exist_ok=True)

    # 1. Copia config/ e datapacks/ para dentro de overrides/
    print("\n[1/4] Copiando Livro de Quests (FTB Quests), Configs e Datapack da Firma League...")
    src_config = os.path.join(BASE_DIR, "config")
    dst_config = os.path.join(OVERRIDES_DIR, "config")
    if os.path.exists(dst_config):
        shutil.rmtree(dst_config)
    shutil.copytree(src_config, dst_config)

    src_dp = os.path.join(BASE_DIR, "server", "datapacks", "liga_pokemon_helper")
    dst_dp = os.path.join(DP_DIR, "liga_pokemon_helper")
    if os.path.exists(dst_dp):
        shutil.rmtree(dst_dp)
    shutil.copytree(src_dp, dst_dp)

    # 2. Baixa todos os mods e resource packs
    print("\n[2/4] Baixando Mods para 1.21.1 Fabric...")
    for slug in MODRINTH_MODS:
        fetch_modrinth_file(slug, MODS_DIR, is_resourcepack=False)

    print("\n[3/4] Baixando Resource Packs (Cobblemon Interface & Conquistas Cobbleverse)...")
    for rp_slug in MODRINTH_RESOURCEPACKS:
        fetch_modrinth_file(rp_slug, RP_DIR, is_resourcepack=True)

    # 3. Cria o manifest.json padrão do CurseForge
    manifest = {
        "minecraft": {
            "version": MC_VERSION,
            "modLoaders": [
                {
                    "id": "fabric-0.19.5",
                    "primary": True
                }
            ]
        },
        "manifestType": "minecraftModpack",
        "manifestVersion": 1,
        "name": "Firma League - Cobblemon & Historia",
        "version": "1.0.0",
        "author": "Firma",
        "files": [],
        "overrides": "overrides"
    }

    manifest_path = os.path.join(BUILD_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # 4. Compacta tudo no arquivo Firma-League-CurseForge-1.0.0.zip
    zip_output = os.path.join(BASE_DIR, "Firma-League-CurseForge-1.0.0.zip")
    print(f"\n[4/4] Gerando pacote importável do CurseForge: {zip_output}")
    with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        for root, _, files in os.walk(OVERRIDES_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, BUILD_DIR)
                zf.write(full_path, rel_path)

    print("\n=================================================================")
    print("  CONCLUÍDO! Arquivo pronto para importar no CurseForge App:")
    print(f"  -> {zip_output}")
    print("=================================================================")


if __name__ == "__main__":
    main()
