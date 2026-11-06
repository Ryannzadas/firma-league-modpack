import os
import json
import shutil
import zipfile
import urllib.request
import urllib.parse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEO_DIR = os.path.join(BASE_DIR, "build_neoforge")
OVERRIDES_DIR = os.path.join(NEO_DIR, "overrides")
MODS_DIR = os.path.join(OVERRIDES_DIR, "mods")
RP_DIR = os.path.join(OVERRIDES_DIR, "resourcepacks")
CONFIG_DIR = os.path.join(OVERRIDES_DIR, "config")

MC_VERSION = "1.21.1"
LOADER = "neoforge"

# Lista completa de mods NeoForge 1.21.1 no Modrinth
MODRINTH_MODS = [
    # Core & Libraries NeoForge
    "kotlin-for-forge",
    "architectury-api",
    "cloth-config",
    "geckolib",
    "athena-ctm",
    "balm",
    "resourceful-lib",
    "iceberg",
    "cobblemon-tim-core",
    "lithostitched",
    "curios",
    "accessories",
    "owo-lib",
    "yacl",
    "searchables",
    "controlling",
    "mousetweaks",
    "zume",

    # Cobblemon & História
    "cobblemon",
    "rctapi",
    "rctmod",
    "radical-gyms-structures",
    "more-radical-trainers",
    "cobblemon-pokemon-badges",
    "cobblemon-badgebox",

    # Competitivo, Megas, Breeding, TMs & IVs
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

    # Tech, Create, Mekanism, Powah, AE2, Industrial Foregoing & Storage
    "create",
    "createaddition",
    "mekanism",
    "mekanism-generators",
    "mekanism-tools",
    "powah",
    "ae2",
    "guideme",
    "titanium",
    "industrial-foregoing",
    "sophisticated-core",
    "sophisticated-backpacks",
    "sophisticated-storage",
    "toms-storage",
    "factory-api",
    "better-furnaces-reforged",
    "travelersbackpack",

    # Exploração, Decoração, Multiplayer & QoL
    "explorers-compass",
    "natures-compass",
    "waystones",
    "terralith",
    "cobblefurnies",
    "handcrafted",
    "chipped",
    "xaeros-minimap",
    "xaeros-world-map",
    "jei",
    "emi",
    "jade",
    "simple-voice-chat",
    "sound-physics-remastered",
    "playeranimator",
    "emotecraft",
    "cobbledollars",
    "exposure",
    "lootr",
    "advancement-plaques",
    "better-advancements",
    "appleskin",
    "polymorph",
    "trashslot",
    "carry-on",

    # Performance (NeoForge 1.21.1)
    "sodium",
    "iris",
    "lithium",
    "ferrite-core",
    "entityculling",
    "immediatelyfast",
    "chunky"
]

FTB_NEOFORGE_URLS = [
    ("ftb-library-neoforge-2101.1.39.jar", "https://maven.ftb.dev/releases/dev/ftb/mods/ftb-library-neoforge/2101.1.39/ftb-library-neoforge-2101.1.39.jar"),
    ("ftb-teams-neoforge-2101.1.12.jar", "https://maven.ftb.dev/releases/dev/ftb/mods/ftb-teams-neoforge/2101.1.12/ftb-teams-neoforge-2101.1.12.jar"),
    ("ftb-quests-neoforge-2101.1.38.jar", "https://maven.ftb.dev/releases/dev/ftb/mods/ftb-quests-neoforge/2101.1.38/ftb-quests-neoforge-2101.1.38.jar"),
    ("ftb-ultimine-neoforge-2101.1.15.jar", "https://maven.ftb.dev/releases/dev/ftb/mods/ftb-ultimine-neoforge/2101.1.15/ftb-ultimine-neoforge-2101.1.15.jar"),
]


def search_modrinth_slug(query_text):
    url = f"https://api.modrinth.com/v2/search?query={urllib.parse.quote(query_text)}&limit=3"
    req = urllib.request.Request(url, headers={"User-Agent": "FirmaLeagueModpackBuilder/2.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        hits = data.get("hits", [])
        if hits:
            return hits[0]["slug"]
    return None


def fetch_modrinth_neoforge(slug, target_dir):
    versions_param = f'["{MC_VERSION}"]'
    loaders_param = f'["{LOADER}"]'
    url = (
        f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version"
        f"?game_versions={urllib.parse.quote(versions_param)}&loaders={urllib.parse.quote(loaders_param)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "FirmaLeagueModpackBuilder/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            versions = json.loads(resp.read().decode("utf-8"))
            if not versions:
                # Tenta 1.21 se 1.21.1 exato não estiver marcado, mas ainda neoforge
                url_121 = (
                    f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version"
                    f'?game_versions=%5B%221.21.1%22,%221.21%22%5D&loaders={urllib.parse.quote(loaders_param)}'
                )
                req2 = urllib.request.Request(url_121, headers={"User-Agent": "FirmaLeagueModpackBuilder/2.0"})
                with urllib.request.urlopen(req2, timeout=15) as resp2:
                    versions = json.loads(resp2.read().decode("utf-8"))

            if not versions and slug in ("radical-gyms-structures", "more-radical-trainers", "cobblemon-legendary-structures"):
                # Datapacks empacotados como mod
                url_dp = (
                    f"https://api.modrinth.com/v2/project/{urllib.parse.quote(slug)}/version"
                    f"?game_versions={urllib.parse.quote(versions_param)}"
                )
                req3 = urllib.request.Request(url_dp, headers={"User-Agent": "FirmaLeagueModpackBuilder/2.0"})
                with urllib.request.urlopen(req3, timeout=15) as resp3:
                    versions = json.loads(resp3.read().decode("utf-8"))

            if not versions:
                found_slug = search_modrinth_slug(slug.replace("-", " "))
                if found_slug and found_slug != slug:
                    print(f"  [~] Slug '{slug}' -> tentando '{found_slug}'")
                    return fetch_modrinth_neoforge(found_slug, target_dir)
                print(f"  [!] Sem build NeoForge 1.21.1 para: {slug}")
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
                print(f"  [=] Ja existe: {filename}")
            return filename
    except urllib.error.HTTPError as e:
        if e.code == 404:
            found_slug = search_modrinth_slug(slug.replace("-", " "))
            if found_slug and found_slug != slug:
                print(f"  [~] 404 '{slug}' -> tentando '{found_slug}'")
                return fetch_modrinth_neoforge(found_slug, target_dir)
        print(f"  [x] Erro HTTP {slug}: {e}")
        return None
    except Exception as e:
        print(f"  [x] Erro {slug}: {e}")
        return None


def main():
    os.makedirs(MODS_DIR, exist_ok=True)
    os.makedirs(RP_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Copia resourcepacks já baixados
    old_rp = os.path.join(BASE_DIR, "build_temp", "overrides", "resourcepacks")
    if os.path.exists(old_rp):
        for f in os.listdir(old_rp):
            src = os.path.join(old_rp, f)
            dst = os.path.join(RP_DIR, f)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)

    print("=== Baixando Mods NeoForge 1.21.1 do Modrinth ===")
    missing = []
    for slug in MODRINTH_MODS:
        res = fetch_modrinth_neoforge(slug, MODS_DIR)
        if not res:
            missing.append(slug)

    print("\n=== Baixando FTB Suite (NeoForge 1.21.1) do Maven Oficial FTB ===")
    for fname, url in FTB_NEOFORGE_URLS:
        dest = os.path.join(MODS_DIR, fname)
        if not os.path.exists(dest):
            print(f"  [+] Baixando FTB: {fname}")
            req = urllib.request.Request(url, headers={"User-Agent": "FirmaLeagueModpackBuilder/2.0"})
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest, "wb") as out:
                shutil.copyfileobj(resp, out)
        else:
            print(f"  [=] Ja existe FTB: {fname}")

    print("\n===================================================")
    print(f"Total de .jar baixados em build_neoforge/overrides/mods: {len(os.listdir(MODS_DIR))}")
    print(f"Mods sem versao NeoForge no Modrinth ({len(missing)}): {missing}")


if __name__ == "__main__":
    main()
