"""
Gera o pacote de servidor dedicado (Server Pack) para hosts pagas da Firma League.
Versao: NeoForge 1.21.1 (v2.8.0)

Filtra automaticamente mods exclusivos de cliente (shaders, sodium, minimap, essential, etc.)
e inclui:
  - mods/ (mods compativeis com servidor, incluindo InControl, RCTmod e RCTapi)
  - config/ (FTB Quests, configs balanceadas de maquinas, spawner e pokemon)
  - kubejs/ (todos os scripts de receitas Create, Mekanism, Powah, Megas)
  - server.properties (configurado com allow-flight=true, motd estilizado, view-distance=10)
  - eula.txt (eula=true)
"""
import os
import zipfile
from pathlib import Path

BASE = Path(r"C:\Users\joana\.gemini\antigravity\scratch\cobblemon-liga-modpack")
OVR = BASE / "build_neoforge" / "overrides"
OUT_ZIP = BASE / "Firma-League-Server-NeoForge-2.8.0.zip"

CLIENT_ONLY_MODS = {
    "AdvancementPlaques-1.21.1-neoforge-1.6.8.jar",
    "BetterAdvancements-NeoForge-1.21.1-0.4.3.21.jar",
    "Controlling-neoforge-1.21.1-19.0.5.jar",
    "Essential_1-5-2_neoforge_1-21-1.jar",
    "ImmediatelyFast-NeoForge-1.6.15+1.21.1.jar",
    "MouseTweaks-neoforge-mc1.21-2.26.1.jar",
    "cobeffectiveness-neoforge-0.4.0-beta.1.jar",
    "MoreCobblemonTweaks-neoforge-1.3.6.jar",
    "entityculling-neoforge-1.11.3-mc1.21.1.jar",
    "iris-neoforge-1.8.14-beta.1+mc1.21.1.jar",
    "sodium-neoforge-0.8.13+mc1.21.1.jar",
    "xaerominimap-neoforge-1.21.1-26.6.0.jar",
    "xaeroworldmap-neoforge-1.21.1-1.47.0.jar",
    "entity_texture_features-7.2.7-1.21-neoforge.jar",
    "entity_model_features-3.3.12-1.21-neoforge.jar"
}

server_properties = """# Minecraft Server Properties - Firma League v2.8.0
motd=\\u00A76\\u00A7lFirma League v2.8.0 \\u00A78- \\u00A7bCobblemon, Tech & Historia
server-port=25565
difficulty=normal
gamemode=survival
pvp=true
allow-flight=true
enable-command-block=true
simulation-distance=8
view-distance=10
max-players=20
online-mode=true
sync-chunk-writes=false
spawn-protection=0
network-compression-threshold=256
"""

eula_txt = """# By changing the setting below to TRUE you are indicating your agreement to the EULA (https://aka.ms/MinecraftEULA).
eula=true
"""

def add_folder(zf, folder_path: Path, prefix: str):
    count = 0
    for root, _, files in os.walk(folder_path):
        for f in files:
            full = Path(root) / f
            rel = full.relative_to(folder_path).as_posix()
            zf.write(full, f"{prefix}/{rel}")
            count += 1
    return count

print("Gerando Server Pack v2.8.0...")
with zipfile.ZipFile(OUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. Arquivos base do servidor
    zf.writestr("server.properties", server_properties)
    zf.writestr("eula.txt", eula_txt)

    # 2. Mods filtrados (apenas servidor)
    mods_src = OVR / "mods"
    mod_count = 0
    for f in sorted(os.listdir(mods_src)):
        if not f.endswith(".jar"):
            continue
        if f in CLIENT_ONLY_MODS:
            print(f"  [IGNORADO - CLIENT ONLY] {f}")
            continue
        zf.write(mods_src / f, f"mods/{f}")
        mod_count += 1

    # 3. Pasta config/
    cfg_count = add_folder(zf, OVR / "config", "config")

    # 4. Pasta kubejs/
    kjs_count = add_folder(zf, OVR / "kubejs", "kubejs") if (OVR / "kubejs").exists() else 0

    # 5. Pasta defaultconfigs se existir
    def_count = 0
    if (OVR / "defaultconfigs").exists():
        def_count = add_folder(zf, OVR / "defaultconfigs", "defaultconfigs")

    # 6. Guia rapido
    readme = (
        "COMO INSTALAR NA SUA HOST:\n"
        "=========================\n"
        "1. No painel da sua host (ex: Sparked, Bisect, PebbleHost, etc.), selecione a versao:\n"
        "   - Jogo: Minecraft 1.21.1\n"
        "   - Loader: NeoForge 21.1.248 (ou a mais recente do 1.21.1)\n"
        "2. No Gerenciador de Arquivos (File Manager) da host, envie este arquivo ZIP e clique em 'Unarchive' / 'Extract'.\n"
        "   (Ele vai extrair as pastas mods/, config/, kubejs/, o server.properties e o eula.txt diretamente na raiz).\n"
        "3. Inicie o servidor!\n"
    )
    zf.writestr("LEIA-ME_HOST.txt", readme)

size_mb = OUT_ZIP.stat().st_size / (1024 * 1024)
print(f"\n[SUCESSO] {OUT_ZIP.name} gerado com sucesso!")
print(f"  - Mods incluidos: {mod_count} (15 mods de cliente removidos)")
print(f"  - Arquivos de config: {cfg_count}")
print(f"  - Scripts KubeJS: {kjs_count}")
print(f"  - Tamanho final: {size_mb:.1f} MB")
