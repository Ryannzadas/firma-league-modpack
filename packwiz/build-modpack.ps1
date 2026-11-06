# ==============================================================================
# Script Automatizado para Montar o Modpack (.mrpack) via Packwiz
# Minecraft 1.21.1 (Fabric) - Cobblemon: Liga & História
# ==============================================================================

$ErrorActionPreference = "Stop"
Write-Host "=== Montando Modpack: Cobblemon Liga & Historia (1.21.1 Fabric) ===" -ForegroundColor Cyan

# Verifica se o packwiz está instalado no PATH
if (-not (Get-Command "packwiz" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] O utilitário 'packwiz' não foi encontrado no PATH." -ForegroundColor Yellow
    Write-Host "    Você pode instalar via Go ('go install github.com/packwiz/packwiz@latest') ou usar o Modrinth App seguindo docs/MODLIST_E_INSTALACAO.md." -ForegroundColor Yellow
    exit 1
}

# Lista de Slugs do Modrinth (Core, Cobblemon, História, Competitivo, Mundo, QOL, Performance)
$modrinthMods = @(
    # Core & APIs
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

    # Cobblemon & Modo História (Radical Trainers + Estruturas)
    "cobblemon",
    "rctapi",
    "rctmod",
    "radicaltrainersstructures",
    "more-radical-trainers",
    "cobblemon-pokemon-badges",
    "odyssey-quests",

    # Competitivo, Interface de Batalha (Efetividade), Megas, TMs, Breeding & IV/EV
    "cobblemon-mega-showdown",
    "cobblemon-battle-extras",
    "cobblemon-effectiveness",
    "cobblemon-move-inspector",
    "simpletms",
    "cobbreeding",
    "cobblemon-utility+",
    "cobblemon-unchained",
    "cobblemon-counter",
    "cobblemon-capture-xp",

    # Lendários, Montarias, Workers & Add-ons Extras de Cobblemon
    "myths-and-legends-cobblemon-sidemod",
    "cobblemon-legendary-structures",
    "cobblemon-spawn-notification",
    "cobblemon-pokenav",
    "cobblemon-box-link",
    "cobblemon-outbreaks",
    "releaserewards",
    "cobblemon-size-variations",
    "cobblemon-show-held-items",
    "cobblemonrider",
    "cobbleworkers",
    "knowlogy",
    "cobblemon-wiki-gui",
    "cobblemon-integrations",
    "cobblemon-fight-or-flight-reborn",

    # Mundo, Exploração, Decoração & QOL
    "explorers-compass",
    "natures-compass",
    "waystones",
    "terralith",
    "travelers-backpack",
    "cobblefurnies",
    "xaeros-minimap",
    "xaeros-world-map",
    "emi",
    "jade",
    "simple-voice-chat",
    "lootr",
    "iceberg",
    "advancement-plaques",
    "better-advancements",

    # Resource Packs (Estilo Cobbleverse - Conquistas & Interface)
    "cobblemon-advancement-plaques",
    "cobblemon-interface",
    "cobblemon-interface-modded",
    "radical-trainer-textures-plus",
    "e19-cobblemon-minimap-icons",

    # Performance (Cliente + Servidor)
    "lithium",
    "ferritecore",
    "krypton",
    "c2me-fabric",
    "chunky",
    "sodium",
    "iris",
    "entityculling",
    "immediatelyfast"
)

foreach ($slug in $modrinthMods) {
    Write-Host "-> Adicionando do Modrinth: $slug" -ForegroundColor Green
    packwiz modrinth add $slug -y
}

# Mods do CurseForge (FTB Quests + Dependências)
$curseforgeMods = @(
    "ftb-library-fabric",
    "ftb-teams-fabric",
    "ftb-quests-fabric"
)

foreach ($cfSlug in $curseforgeMods) {
    Write-Host "-> Adicionando do CurseForge: $cfSlug" -ForegroundColor Magenta
    packwiz curseforge add $cfSlug -y
}

# Copia a pasta config/ para dentro do diretório packwiz antes de exportar
Copy-Item -Path "..\config" -Destination ".\config" -Recurse -Force

Write-Host "-> Exportando arquivo .mrpack para Modrinth App / Prism Launcher..." -ForegroundColor Cyan
packwiz modrinth export -o "..\Cobblemon-Liga-Historia-1.0.0.mrpack"

Write-Host "=== Concluído! Arquivo Cobblemon-Liga-Historia-1.0.0.mrpack gerado! ===" -ForegroundColor Green
