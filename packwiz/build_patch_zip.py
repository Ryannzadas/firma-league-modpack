import os
import json
import shutil
import zipfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATCH_DIR = os.path.join(BASE_DIR, "build_patch")
OVERRIDES_DIR = os.path.join(PATCH_DIR, "overrides")


def build_offline_curseforge_zip():
    os.makedirs(OVERRIDES_DIR, exist_ok=True)

    # Copia config/ (FTB Quests, Cobblemon, RCTMod)
    src_config = os.path.join(BASE_DIR, "config")
    dst_config = os.path.join(OVERRIDES_DIR, "config")
    if os.path.exists(dst_config):
        shutil.rmtree(dst_config)
    shutil.copytree(src_config, dst_config)

    # Copia datapacks/liga_pokemon_helper (Líderes balanceados, Giovanni c/ Mewtwo, Regras da Firma League)
    src_dp = os.path.join(BASE_DIR, "server", "datapacks", "liga_pokemon_helper")
    dst_dp = os.path.join(OVERRIDES_DIR, "datapacks", "liga_pokemon_helper")
    if os.path.exists(dst_dp):
        shutil.rmtree(dst_dp)
    shutil.copytree(src_dp, dst_dp)

    # Cria manifest.json oficial do CurseForge
    manifest = {
        "minecraft": {
            "version": "1.21.1",
            "modLoaders": [
                {
                    "id": "fabric-0.16.9",
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

    manifest_path = os.path.join(PATCH_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    zip_path = os.path.join(BASE_DIR, "Firma-League-Configs-Quests-CurseForge.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(manifest_path, "manifest.json")
        for root, _, files in os.walk(OVERRIDES_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, PATCH_DIR)
                zf.write(full_path, rel_path)

    shutil.rmtree(PATCH_DIR)
    print(f"Pacote base criado com sucesso: {zip_path}")


if __name__ == "__main__":
    build_offline_curseforge_zip()
