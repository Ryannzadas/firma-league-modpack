"""
Gera os pacotes de distribuicao do Firma League (NeoForge 1.21.1):

  1. Firma-League-NeoForge-<versao>.zip   -> modpack COMPLETO no formato CurseForge
                                             (importar no CurseForge App / Prism Launcher)
  2. Firma-League-NeoForge-Atualizacao.zip -> so os arquivos que mudam com frequencia
                                             (core mod + quests + configs), para quem ja tem o pack
"""
import json
import os
import zipfile
from pathlib import Path

VERSION = "2.8.0"
NEOFORGE = "neoforge-21.1.248"  # minimo exigido pelos mods (createaddition 1.7.2)

BASE = Path(__file__).resolve().parent.parent
OVR = BASE / "build_neoforge" / "overrides"

manifest = {
    "minecraft": {"version": "1.21.1", "modLoaders": [{"id": NEOFORGE, "primary": True}]},
    "manifestType": "minecraftModpack",
    "manifestVersion": 1,
    "name": "Firma League - Cobblemon & Historia (NeoForge)",
    "version": VERSION,
    "author": "Firma",
    "files": [],
    "overrides": "overrides",
}
manifest_bytes = json.dumps(manifest, indent=2).encode("utf-8")


def add_tree(zf, src: Path, prefix: str):
    n = 0
    for root, _, files in os.walk(src):
        for f in files:
            full = Path(root) / f
            zf.write(full, f"{prefix}/{full.relative_to(src).as_posix()}")
            n += 1
    return n


# 1) Pack completo
full_zip = BASE / f"Firma-League-NeoForge-{VERSION}.zip"
with zipfile.ZipFile(full_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("manifest.json", manifest_bytes)
    total = add_tree(zf, OVR, "overrides")
print(f"[OK] {full_zip.name}: {total} arquivos, {full_zip.stat().st_size / 1e6:.1f} MB")

# 2) Atualizacao (copiar por cima da pasta da instancia)
upd_zip = BASE / "Firma-League-NeoForge-Atualizacao.zip"
with zipfile.ZipFile(upd_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    core = OVR / "mods" / "zzz-firma-league-core-2.0.0.jar"
    zf.write(core, f"mods/{core.name}")
    rgs = OVR / "mods" / "Radical Gyms  Structures - RGS.jar"
    if rgs.exists():
        zf.write(rgs, f"mods/{rgs.name}")
    
    # Adiciona os mods mais recentes
    extra_jars = [
        "kubejs-neoforge-2101.7.2-build.381.jar",
        "rhino-2101.2.8-build.91.jar",
        "kubejs-create-neoforge-2101.3.1-build.18.jar",
        "kubejs-mekanism-neoforge-2101.1.7-build.18.jar",
        "Essential_1-5-2_neoforge_1-21-1.jar",
        "cobblemore_lib-neoforge-1.2.10.jar",
        "cobblemonraiddens-neoforge-0.13.5+1.21.1.jar",
        "zamega-neoforge-1.8.2+1.8.2.jar",
        "PastureLoot-neoforge-2.0.0+1.21.1.jar",
        "SafePastures(Neoforge)-1.1.2+1.21.1.jar",
        "missingmons-cobblemon-3.6.1.jar",
        "playerxp-neoforge-1.1.2+1.21.1.jar",
        "MoreCobblemonTweaks-neoforge-1.3.6.jar",
        "dungeons-and-taverns-v4.4.4.jar",
        "artifacts-neoforge-13.2.5.jar",
        "simplyswords-neoforge-1.70.2-1.21.1.jar",
        "SimplyTooltips-neoforge-0.1.5.jar",
        "fzzy_config-0.7.7+fix1+1.21+neoforge.jar",
        "sparsestructures-neoforge-1.21.1-3.0.jar",
        "dummmmmmy-1.21-2.1.2-neoforge.jar",
        "moonlight-1.21.1-3.8.2-neoforge.jar",
        "repurposed_structures-7.5.22+1.21.1-neoforge.jar",
        "entity_texture_features-7.2.7-1.21-neoforge.jar",
        "entity_model_features-3.3.12-1.21-neoforge.jar",
        "incontrol-1.21-10.3.1.jar",
        "rctmod-neoforge-1.21.1-0.19.2-beta.jar",
        "rctapi-neoforge-1.21.1-0.16.2-beta.jar",
        "huge-structure-blocks-neoforge-1.1.6.jar"
    ]
    for kjar in extra_jars:
        kp = OVR / "mods" / kjar
        if kp.exists():
            zf.write(kp, f"mods/{kjar}")

    n_cfg = add_tree(zf, OVR / "config", "config")
    n_kjs = add_tree(zf, OVR / "kubejs", "kubejs") if (OVR / "kubejs").exists() else 0
    n_rp = add_tree(zf, OVR / "resourcepacks", "resourcepacks") if (OVR / "resourcepacks").exists() else 0
    if (OVR / "options.txt").exists():
        zf.write(OVR / "options.txt", "options.txt")

    zf.writestr(
        "LEIA-ME.txt",
        "FIRMA LEAGUE v2.8.0 - ATUALIZACAO COMPLETA (VILAS DO COBBLEVERSE & SOUNDTRACK)\n"
        "=============================================================================\n"
        "1. Extraia este zip DENTRO da pasta da instancia do Minecraft (onde ficam mods/, config/, kubejs/ e resourcepacks/)\n"
        "   e aceite substituir os arquivos.\n"
        "2. VILAS IDENTICAS AO COBBLEVERSE (BCA):\n"
        "   - Todas as vilas do Minecraft agora geram usando a arquitetura oficial do Cobbleverse (BCA - Better Cobblemon Architecture)!\n"
        "   - Casas com design tematico de Pokemon, floriculturas, apiarios, academias e o Poke Mart oficial integrado.\n"
        "   - Mod 'Huge Structure Blocks' adicionado para renderizar perfeitamente as estruturas grandes.\n"
        "3. COBBLEVERSE SOUNDTRACK OFICIAL:\n"
        "   - Trilha sonora oficial e temas de Pokemon do Cobbleverse integrados no pacote!\n"
        "4. ECONOMIA COBBLEDOLLARS (POKE MOEDAS):\n"
        "   - Ganhe Poke Coins (CobbleDollars) batalhando contra Pokemons selvagens e treinadores!\n"
        "   - Use Poke Coins nos atendentes do Poke Mart das vilas para comprar Poke Balls, pocoes, revives, etc.!\n"
        "5. CALIBRACAO DO SPAWNER E FIM DO SPAM DE CHAT:\n"
        "   - Spawns agora acontecem em ritmo equilibrado (1.5s) com tempo de vida de 2 a 5 minutos (sem sumir na hora!).\n"
        "   - Raros e Ultrararos restaurados para raridades especiais autenticas de Pokemon.\n"
        "   - Chat limpo: apenas Lendarios, Miticos e Shinies recebem alertas!\n"
        "6. ECOSSISTEMA DO THE END:\n"
        "   - 25 novos spawns no The End (Unown nativo na End Stone, Elgyem, Beldum, Gastly, Clefairy, Dreepy, Metagross e Dragapult)!\n",
    )
print(f"[OK] {upd_zip.name}: {n_cfg + n_kjs + n_rp + len(extra_jars) + 3} arquivos, {upd_zip.stat().st_size / 1e6:.1f} MB")
