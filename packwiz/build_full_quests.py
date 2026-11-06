import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTS_DIR = os.path.join(BASE_DIR, "config", "ftbquests", "quests")
CHAPTERS_DIR = os.path.join(QUESTS_DIR, "chapters")
LANG_DIR = os.path.join(QUESTS_DIR, "lang")

os.makedirs(CHAPTERS_DIR, exist_ok=True)
os.makedirs(LANG_DIR, exist_ok=True)

translations = {}

def clean_text(s):
    # Em FTB Quests, '& ' solto causa erro "You must escape whitespace after & with \&!"
    return s.replace(" & ", " e ").replace("& ", "e ")

def snbt_str(s):
    s = clean_text(s)
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'

def make_quest(qid, title, subtitle, desc_lines, icon_id, x, y, deps=None, tasks=None, rewards=None, shape="rsquare", size=1.0, hide_until_deps=False, optional=False):
    qid_hex = f"{qid:016X}"
    translations[f"quest.{qid_hex}.title"] = clean_text(title)
    if subtitle:
        translations[f"quest.{qid_hex}.quest_subtitle"] = clean_text(subtitle)
    if desc_lines:
        translations[f"quest.{qid_hex}.quest_desc"] = [clean_text(l) for l in desc_lines]

    lines = []
    lines.append("\t\t{")
    lines.append(f'\t\t\tid: "{qid_hex}"')
    lines.append(f"\t\t\ttitle: {snbt_str(title)}")
    if subtitle:
        lines.append(f"\t\t\tsubtitle: {snbt_str(subtitle)}")
    lines.append("\t\t\ticon: {")
    lines.append(f'\t\t\t\tid: "{icon_id}"')
    lines.append("\t\t\t}")
    if desc_lines:
        lines.append("\t\t\tdescription: [")
        for dl in desc_lines:
            lines.append(f"\t\t\t\t{snbt_str(dl)}")
        lines.append("\t\t\t]")
    if deps:
        dep_str = ", ".join(f'"{d:016X}"' if isinstance(d, int) else f'"{d}"' for d in deps)
        lines.append(f"\t\t\tdependencies: [{dep_str}]")
    if hide_until_deps:
        lines.append("\t\t\thide_until_deps_complete: true")
    if optional:
        lines.append("\t\t\toptional: true")
    lines.append(f"\t\t\tx: {x:.1f}d")
    lines.append(f"\t\t\ty: {y:.1f}d")
    if shape:
        lines.append(f'\t\t\tshape: "{shape}"')
    if size != 1.0:
        lines.append(f"\t\t\tsize: {size:.2f}d")

    if tasks:
        lines.append("\t\t\ttasks: [")
        for idx, t in enumerate(tasks, 1):
            tid_hex = f"{qid + idx:016X}"
            lines.append("\t\t\t\t{")
            lines.append(f'\t\t\t\t\tid: "{tid_hex}"')
            ttype = t["type"]
            lines.append(f'\t\t\t\t\ttype: "{ttype}"')
            if "title" in t:
                translations[f"task.{tid_hex}.title"] = clean_text(t["title"])
                lines.append(f'\t\t\t\t\ttitle: {snbt_str(t["title"])}')
            if ttype == "item":
                lines.append("\t\t\t\t\titem: {")
                lines.append(f'\t\t\t\t\t\tid: "{t["item"]}"')
                lines.append("\t\t\t\t\t}")
                if t.get("count", 1) > 1:
                    lines.append(f'\t\t\t\t\tcount: {t["count"]}L')
            elif ttype == "advancement":
                lines.append(f'\t\t\t\t\tadvancement: "{t["advancement"]}"')
                lines.append('\t\t\t\t\tcriterion: ""')
            lines.append("\t\t\t\t}")
        lines.append("\t\t\t]")

    if rewards:
        lines.append("\t\t\trewards: [")
        for idx, r in enumerate(rewards, 20):
            rid_hex = f"{qid + idx:016X}"
            lines.append("\t\t\t\t{")
            lines.append(f'\t\t\t\t\tid: "{rid_hex}"')
            lines.append('\t\t\t\t\ttype: "item"')
            lines.append("\t\t\t\t\titem: {")
            lines.append(f'\t\t\t\t\t\tid: "{r["item"]}"')
            lines.append(f'\t\t\t\t\t\tcount: {r.get("count", 1)}')
            lines.append("\t\t\t\t\t}")
            lines.append("\t\t\t\t}")
        lines.append("\t\t\t]")

    lines.append("\t\t}")
    return "\n".join(lines)


def write_chapter(cid, group_id, order_idx, filename, title, icon_id, default_shape, quests_snbt):
    cid_hex = f"{cid:016X}"
    translations[f"chapter.{cid_hex}.title"] = clean_text(title)
    lines = [
        "{",
        f'\tid: "{cid_hex}"',
        f'\tgroup: "{group_id:016X}"',
        f"\torder_index: {order_idx}",
        f'\tfilename: "{filename}"',
        f"\ttitle: {snbt_str(title)}",
        "\ticon: {",
        f'\t\tid: "{icon_id}"',
        "\t}",
        f'\tdefault_quest_shape: "{default_shape}"',
        "\tdefault_hide_dependency_lines: false",
        "\tquests: [",
        "\n".join(quests_snbt),
        "\t]",
        "}"
    ]
    with open(os.path.join(CHAPTERS_DIR, f"{filename}.snbt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ==============================================================================
# GRUPOS DE CAPÍTULOS
# ==============================================================================
GRP_HISTORIA = 0x1000000000000001
GRP_TECH     = 0x1000000000000002
GRP_LIGA     = 0x1000000000000003

translations[f"chapter_group.{GRP_HISTORIA:016X}.title"] = "&eModo Historia e Regioes"
translations[f"chapter_group.{GRP_TECH:016X}.title"]     = "&bEngenharia Tech e Armazenamento"
translations[f"chapter_group.{GRP_LIGA:016X}.title"]     = "&cCompetitivo e Firma League"

with open(os.path.join(QUESTS_DIR, "chapter_groups.snbt"), "w", encoding="utf-8") as f:
    f.write("{\n\tchapter_groups: [\n")
    f.write(f'\t\t{{ id: "{GRP_HISTORIA:016X}", title: "&eModo Historia e Regioes" }}\n')
    f.write(f'\t\t{{ id: "{GRP_TECH:016X}", title: "&bEngenharia Tech e Armazenamento" }}\n')
    f.write(f'\t\t{{ id: "{GRP_LIGA:016X}", title: "&cCompetitivo e Firma League" }}\n')
    f.write("\t]\n}\n")


# ==============================================================================
# CAPÍTULO 0A: CRÔNICAS DA FIRMA (A LORE OFICIAL DO MUNDO)
# ==============================================================================
c_lore_quests = [
    make_quest(
        0x00A0000000000010,
        "&6Capitulo I: A Grande Convergencia",
        "O cataclismo que uniu os mundos",
        [
            "Ha eras incontaveis, os universos viviam em dimensoes separadas.",
            "",
            "Porem, um cataclismo de energia cosmica rasgou o tecido do espaco-tempo: em um piscar de olhos, as quatro regioes lendarias — &cKanto&r, &eJohto&r, &aHoenn&r e &dSinnoh&r — colidiram e se fundiram a imensidao de biomas, cavernas e minerios deste mundo!",
            "",
            "Ginasios ancestrais se enraizaram pelo relevo, santuarios adormecidos emergiram nas montanhas e centenas de especies de Pokemon agora habitam cada canto da terra."
        ],
        "rctmod:trainer_card", 0.0, 0.0, None,
        [{"type": "checkmark", "title": "Testemunhei a Grande Convergencia!"}],
        [{"item": "cobblemon:exp_candy_s", "count": 10}, {"item": "cobblemon:poke_ball", "count": 15}],
        shape="hexagon", size=1.5
    ),
    make_quest(
        0x00A0000000000020,
        "&bCapitulo II: O Colapso da Silph Co. e a Era das Maquinas",
        "Por que a industria se tornou essencial",
        [
            "O pulso eletromagnetico da Convergencia desintegrou as velhas linhas de producao da Silph Co. Nao existem mais lojas de conveniencia vendendo Pokebolas infinitas nem pedras de evolucao prontas.",
            "",
            "Para sobreviver e triunfar, os treinadores precisaram se tornar &bEngenheiros&r:",
            "• &6Create:&r Monta esteiras automatizadas de Pokebolas e sintetiza doces de EXP no Mixer.",
            "• &bMekanism:&r Duplica minerios de evolucao, forja itens de troca e gera Bio Fuel das Apricorns.",
            "• &9Powah!:&r Energiza metais e funde pedras evolutivas em Orbes de laser.",
            "",
            "A tecnologia e o poder dos Pokemon agora andam de maos dadas!"
        ],
        "create:cogwheel", 2.5, 0.0, [0x00A0000000000010],
        [{"type": "checkmark", "title": "Entendi a importancia da industria no mundo!"}],
        [{"item": "create:andesite_alloy", "count": 8}, {"item": "minecraft:iron_ingot", "count": 8}]
    ),
    make_quest(
        0x00A0000000000030,
        "&dCapitulo III: Anomalias e os Quatro Fenomenos",
        "Megas, Z-Moves, Dynamax, Terastal e o Mito do Omni Ring",
        [
            "A fusao dimensional gerou uma anomalia energetica sem precedentes na historia: todos os quatro fenomenos de batalha se manifestaram no mesmo planeta!",
            "",
            "• &dMega Evolucao:&r Keystones e Mega Stones cristalizaram no subsolo.",
            "• &eZ-Moves:&r A luz dos guardioes impregnou as Sparkling Stones.",
            "• &cDynamax:&r Wishing Stars e pontos de energia estao espalhados pelo relevo.",
            "• &bTerastal:&r Cristais Tera brotaram em geodos profundos.",
            "",
            "&6A Profecia do Omni Ring:&r As lendas dizem que o treinador capaz de sintetizar todos os quatro artefatos com Netherite e Circuitos de Elite do Mekanism forjara o &6Omni Ring&r — a joia definitiva que controla todas as transformacoes em uma so peca!"
        ],
        "mega_showdown:omni_ring", 5.0, -1.2, [0x00A0000000000020],
        [{"type": "checkmark", "title": "Estudarei os 4 Grandes Fenomenos!"}],
        [{"item": "cobblemon:rare_candy", "count": 3}, {"item": "cobblemon:link_cable", "count": 1}]
    ),
    make_quest(
        0x00A0000000000040,
        "&cCapitulo IV: As Quatro Sombras do Passado",
        "Equipes Rocket, Magma, Aqua e Galactic a espreita",
        [
            "Onde ha tanto poder concentrado, a ambicao dos viloes despertou.",
            "",
            "As grandes organizacoes do passado renasceram e espreitam nos biomas:",
            "• &cEquipe Rocket:&r Giovanni, Archer e Ariana operam nas sombras de Kanto e Johto atras do clone supremo, Mewtwo.",
            "• &4Equipes Magma e Aqua:&r Maxie e Archie travam embates nos mares e vulcoes de Hoenn para acordar Kyogre e Groudon.",
            "• &5Equipe Galactic:&r Cyrus e seus comandantes estudam as fendas de Sinnoh para distorcer o proprio tempo com Dialga e Palkia.",
            "",
            "Eles estao soltos pelo mundo — prepare sua equipe para quando cruzar com eles!"
        ],
        "cobblemon:dusk_ball", 5.0, 1.2, [0x00A0000000000020],
        [{"type": "checkmark", "title": "Estou alerta contra os viloes das regioes!"}],
        [{"item": "cobblemon:hyper_potion", "count": 5}, {"item": "cobblemon:revive", "count": 3}]
    ),
    make_quest(
        0x00A0000000000050,
        "&6&lCapitulo V: O Juramento da Firma",
        "As 4 Temporadas, a gloria dos Ginasios e a Copa da Firma",
        [
            "Diante da imensidao deste novo mundo, formou-se a guilda mais ambiciosa de todas: &6A FIRMA&r.",
            "",
            "O nosso caminho esta tracado em 4 Temporadas:",
            "1. Conquistar sequencialmente os 32 Ginasios (8 de Kanto ➔ 8 de Johto ➔ 8 de Hoenn ➔ 8 de Sinnoh).",
            "2. Derrotar a Elite Four e o Grande Campeao de cada regiao.",
            "3. Erguer usinas e fabricas para suprir a equipe com as melhores ferramentas e Pokebolas.",
            "4. Reunir todos os amigos na grande arena ao final para disputar &cA Copa da Firma (Torneio PvP)&r, onde so um sera coroado o Supremo Campeao!",
            "",
            "Sua jornada comeca agora. Pegue seu kit, escolha seu parceiro e honre a Firma!"
        ],
        "cobblemon:luxury_ball", 7.5, 0.0, [0x00A0000000000030, 0x00A0000000000040],
        [{"type": "checkmark", "title": "Faco o Juramento da Firma League!"}],
        [{"item": "cobblemon:luxury_ball", "count": 10}, {"item": "cobblemon:rare_candy", "count": 5}, {"item": "cobblemon:ability_patch", "count": 1}],
        shape="gear", size=1.8
    )
]
write_chapter(0x00A0000000000001, GRP_HISTORIA, 0, "00_lore_da_firma", "&6📜 Cronicas da Firma: A Lore do Mundo", "minecraft:book", "rsquare", c_lore_quests)


# ==============================================================================
# CAPÍTULO 0: ESCOLA POKÉMON (GUIA INICIANTE COM CONQUISTAS REAIS)
# ==============================================================================
c0_quests = [
    make_quest(
        0x0000000000000010,
        "&e1. Bem-vindo ao Mundo Pokemon!",
        "Os botoes basicos para quem nunca jogou",
        [
            "Bem-vindo a &6Firma League&r! Mesmo que voce nunca tenha jogado Pokemon na vida, este capitulo vai te ensinar tudo passo a passo!",
            "",
            "• &6Tecla [M]:&r Abre o menu para escolher seu &aPokemon Inicial&r (Charmander, Squirtle, Bulbasaur, etc.).",
            "• &6Tecla [R]:&r Arremessa seu Pokemon para fora da Pokebola. Se voce mirar num Pokemon selvagem e apertar &e[R]&r, voce inicia uma Batalha!",
            "• &6Setas Cima/Baixo (ou Scroll segurando R):&r Escolhe qual dos seus 6 Pokemon sera enviado.",
            "",
            "&aObjetivo:&r Escolha seu inicial no menu &e[M]&r e faca ou pegue suas primeiras Pokebolas!"
        ],
        "cobblemon:poke_ball", 0.0, 0.0, None,
        [{"type": "checkmark", "title": "Escolhi meu Pokemon Inicial no menu [M]!"}],
        [{"item": "cobblemon:poke_ball", "count": 15}, {"item": "cobblemon:potion", "count": 10}],
        shape="pentagon", size=1.5
    ),
    make_quest(
        0x0000000000000040,
        "&c2. Sua Primeira Captura!",
        "Enfraqueca antes de jogar a Pokebola",
        [
            "Se voce jogar uma Pokebola direto num Pokemon com a vida cheia, ele quase sempre vai escapar!",
            "",
            "&eComo capturar qualquer Pokemon facil:&r",
            "1. Mire no Pokemon selvagem e aperte &e[R]&r para lutar.",
            "2. Use ataques ate a barra de vida dele ficar &eAmarela&r ou &cVermelha&r (cuidado para nao desmaiar ele!).",
            "3. Se usar golpes que causam &dSono (Sleep)&r ou &eParalisia (Thunder Wave)&r, a chance de captura dobra!",
            "4. Clique em &bBag (Mochila) -> Pokebolas&r e arremesse a Pokebola!",
            "",
            "&aObjetivo:&r Capture seu primeiro Pokemon selvagem (Conquista oficial &eFirst Catch&r)!"
        ],
        "cobblemon:great_ball", 2.5, 0.0, [0x0000000000000010],
        [{"type": "advancement", "advancement": "cobblemon:catching/first_catch", "title": "Capture seu 1o Pokemon selvagem!"}],
        [{"item": "cobblemon:great_ball", "count": 10}, {"item": "cobblemon:super_potion", "count": 5}]
    ),
    make_quest(
        0x0000000000000070,
        "&a3. Tabela de Tipos e Efetividade [2x / 4x]",
        "O mod mostra na tela qual golpe usar!",
        [
            "Todo Pokemon e todo golpe tem um &bTipo Elemental&r (como Pedra, Papel e Tesoura):",
            "• &9Agua&r vence &cFogo&r, &6Terra&r e &7Pedra&r (&a2x de dano!&r).",
            "• &aPlanta&r vence &9Agua&r, &6Terra&r e &7Pedra&r (&a2x de dano!&r).",
            "• &cFogo&r vence &aPlanta&r, &bGelo&r, &2Inseto&r e &7Metalico&r (&a2x de dano!&r).",
            "• &eEletrico&r vence &9Agua&r e &bVoador&r, mas &6Terra&r e &cImune (0x)&r a Eletrico!",
            "",
            "&6DICA DE OURO:&r Durante a batalha, olhe para os seus 4 botoes de ataque! O nosso mod &bCobblemon Battle Extras&r ja escreve &a[2x]&r ou &a[4x]&r nos golpes Super Efetivos!"
        ],
        "cobblemon:water_stone", 2.5, -2.0, [0x0000000000000010],
        [{"type": "checkmark", "title": "Vi o indicador [2x] nos botoes de ataque!"}],
        [{"item": "cobblemon:exp_candy_s", "count": 10}]
    ),
    make_quest(
        0x00000000000000A0,
        "&b4. Equipe Completa (6 Pokemon)",
        "Monte um time variado para nao ter fraquezas",
        [
            "Voce pode carregar ate &e6 Pokemon&r na sua equipe ativa (os demais vao automaticamente para o seu &bPC&r!).",
            "",
            "• Tente ter tipos diferentes no time (ex.: 1 de Fogo, 1 de Agua, 1 de Planta/Eletrico, 1 Voador, 1 de Terra/Pedra e 1 Psiquico/Fantasma).",
            "",
            "&aObjetivo:&r Complete uma equipe de 6 Pokemon na sua Party!"
        ],
        "cobblemon:safari_ball", 5.0, 0.0, [0x0000000000000040],
        [{"type": "advancement", "advancement": "cobblemon:catching/full_party", "title": "Tenha 6 Pokemon na sua equipe!"}],
        [{"item": "cobblemon:quick_ball", "count": 10}, {"item": "cobblemon:revive", "count": 3}]
    ),
    make_quest(
        0x00000000000000D0,
        "&d5. Evoluindo e Trocando Golpes no Menu [M]",
        "Seu Pokemon nao evolui sozinho no meio da luta!",
        [
            "No Cobblemon, quando seu Pokemon atinge o nivel de evoluir, aparece uma notificacao no chat e um &bbrilho ao lado dele&r:",
            "1. Aperte &e[M]&r para abrir sua equipe.",
            "2. Clique no Pokemon e clique no botao &bEvolve (Evoluir)&r!",
            "3. Nessa mesma tela, clique em &eMoves (Golpes)&r: voce pode reaprender ou trocar os 4 ataques dele a qualquer hora de graca!",
            "4. &6Dica:&r Digite &e/pwiki nome_do_pokemon&r no chat para ver em qual nivel ou com qual pedra qualquer Pokemon evolui!"
        ],
        "cobblemon:rare_candy", 5.0, 2.0, [0x0000000000000040],
        [{"type": "advancement", "advancement": "cobblemon:catching/first_evolution", "title": "Evolua um Pokemon pela primeira vez!"}],
        [{"item": "cobblemon:rare_candy", "count": 5}, {"item": "cobblemon:exp_candy_m", "count": 5}]
    ),
    make_quest(
        0x0000000000000100,
        "&66. Ataque Fisico vs. Ataque Especial",
        "O segredo para causar o dobro de dano",
        [
            "Todo Pokemon tem dois atributos de ataque nos Status dele (aperte &e[M] -> Summary -> Stats&r):",
            "• &cAttack (Ataque Fisico):&r Alto em Pokemon musculosos (Machamp, Gyarados, Garchomp, Scizor). Coloque neles golpes com o icone de &cExplosao Vermelha (Physical)&r!",
            "• &9Special Attack (Ataque Especial):&r Alto em Pokemon magicos/elementais (Alakazam, Gengar, Starmie, Gardevoir). Coloque neles golpes com o icone de &9Ondas Azuis (Special)&r!",
            "• &7Status (Cinza):&r Golpes que nao tiram vida direto, mas dao buffs (Swords Dance, Dragon Dance), curam (Recover) ou colocam armadilhas (Stealth Rock)."
        ],
        "cobblemon:muscle_band", 7.5, 0.0, [0x0000000000000070, 0x00000000000000A0, 0x00000000000000D0],
        [{"type": "checkmark", "title": "Entendi a diferenca entre Golpe Fisico e Especial!"}],
        [{"item": "cobblemon:lucky_egg", "count": 1}, {"item": "cobblemon:leftovers", "count": 1}],
        shape="octagon", size=1.5
    )
]
write_chapter(0x0000000000000001, GRP_HISTORIA, 1, "00_guia_iniciante_pokemon", "&b0. Escola Pokemon (Iniciantes)", "cobblemon:exp_share", "rsquare", c0_quests)


# ==============================================================================
# CAPÍTULO 1: O INÍCIO DA JORNADA & EXPLORAÇÃO
# ==============================================================================
c1_quests = [
    make_quest(
        0x0100000000000010,
        "&6PROLOGO: A Grande Convergencia",
        "A Lore Oficial da Firma League (Edicao NeoForge)",
        [
            "Um fenomeno catastrofico chamado &eA Grande Convergencia&r fundiu terras, Ginasios e Santuarios Lendarios de &cKanto&r, &eJohto&r, &aHoenn&r e &dSinnoh&r em um unico mundo!",
            "",
            "O pulso eletromagnetico da fenda colapsou a tecnologia antiga da Silph Co. e espalhou cristais de &dMega Evolucao&r e &bTerastal&r pelo subsolo. A &cEquipe Rocket&r de Giovanni ja comecou a saquear os templos antigos.",
            "",
            "A Associacao Pokemon convocou voces — &6A FIRMA&r — para erguer as fabricas do &eCreate&r, as usinas do &bMekanism&r e do &9Powah!&r, derrotar os Lideres das 4 Regioes e disputar os torneios da &6Firma League&r!"
        ],
        "rctmod:trainer_card", 0.0, 0.0, None,
        [{"type": "checkmark", "title": "Recebi meu Trainer Card e meu Kit Inicial!"}],
        [{"item": "rctmod:trainer_card", "count": 1}, {"item": "cobblemon:exp_candy_s", "count": 10}, {"item": "cobblemon:poke_ball", "count": 15}],
        shape="hexagon", size=1.6
    ),
    make_quest(
        0x0100000000000040,
        "&eColhendo Apricorns pelo Mundo",
        "A bio-energia das Pokebolas e Circuitos",
        [
            "Encontre arvores de &eApricorn&r pelo mapa e clique com o botao direito nas frutas maduras para colhe-las (elas crescem de novo sozinhas!).",
            "",
            "Na &6Engenharia da Convergencia&r, as Apricorns nao servem so para Pokebolas: a bio-energia delas tambem alimenta os &aCircuitos de Controle Basicos&r da Silph Co.!"
        ],
        "cobblemon:red_apricorn", 2.5, -2.0, [0x0100000000000010],
        [
            {"type": "item", "item": "cobblemon:red_apricorn", "count": 8},
            {"type": "item", "item": "cobblemon:yellow_apricorn", "count": 4},
            {"type": "item", "item": "cobblemon:blue_apricorn", "count": 4}
        ],
        [{"item": "cobblemon:great_ball", "count": 10}, {"item": "cobblemon:sitrus_berry", "count": 8}]
    ),
    make_quest(
        0x0100000000000070,
        "&bConstruindo sua Pokedex",
        "Registre todas as especies e drops",
        [
            "Com &fChapas de Ferro (Create)&r, Cobre, Red Apricorn e o seu primeiro &aCircuito de Controle Basico (Mekanism)&r, construa a sua &cPokedex&r!",
            "",
            "Segure o botao direito com a Pokedex apontando para um Pokemon para escanea-lo e registrar todas as informacoes dele!"
        ],
        "cobblemon:pokedex_red", 2.5, 0.0, [0x0100000000000010],
        [{"type": "item", "item": "cobblemon:pokedex_red", "count": 1}],
        [{"item": "cobblemon:exp_candy_s", "count": 12}]
    ),
    make_quest(
        0x01000000000000A0,
        "&aSeu Proprio Centro Pokemon (PC e Healer)",
        "Cura e organizacao com Chapas do Create e Circuitos do Mekanism",
        [
            "Construa uma &aHealing Machine&r e um &bPC&r na sua base!",
            "",
            "• &eReceita da Firma:&r Diferente do Cobblemon comum (que pedia Max Revive raro de achar), a nossa Healing Machine usa &fChapas de Ferro (Create) + Cobre + Pink Apricorn + Circuito Basico (Mekanism) + Diamante&r!",
            "• O &bPC&r usa &fChapas de Ferro + Vidro + Red e Blue Apricorn + Circuito Basico&r."
        ],
        "cobblemon:healing_machine", 5.0, 0.0, [0x0100000000000070],
        [
            {"type": "item", "item": "cobblemon:healing_machine", "count": 1},
            {"type": "item", "item": "cobblemon:pc", "count": 1}
        ],
        [{"item": "cobblemon:revive", "count": 5}, {"item": "cobblemon:hyper_potion", "count": 10}]
    ),
    make_quest(
        0x01000000000000D0,
        "&eCapacete Neural: Exp. Share",
        "Divida experiencia com seu time",
        [
            "Construa um &eExp. Share&r usando Capacete de Ferro, Ouro, Lapis Lazuli, Ametista e &a1 Circuito de Controle Basico&r!",
            "",
            "Equipando o Exp. Share como Held Item em um Pokemon da sua equipe, ele ganha XP em todas as batalhas mesmo sem entrar em campo!"
        ],
        "cobblemon:exp_share", 5.0, -2.0, [0x0100000000000040, 0x0100000000000070],
        [{"type": "item", "item": "cobblemon:exp_share", "count": 1}],
        [{"item": "cobblemon:exp_candy_m", "count": 8}]
    ),
    make_quest(
        0x0100000000000100,
        "&dPasture Block: Workers e Breeding",
        "Coloque seus Pokemon para trabalhar na base!",
        [
            "O &dPasture Block&r (feito com PC + Circuito Basico + Green Apricorn + Funil) libera duas mecanicas essenciais:",
            "1. &eCobbleworkers:&r Seus Pokemon soltos no Pasture colhem plantacoes de Apricorns, Berries e lavouras automaticamente e guardam nos baus ao lado!",
            "2. &dCobbreeding:&r Coloque dois Pokemon compativeis para cruzar e gerar Ovos com heranca de IVs e Nature!"
        ],
        "cobblemon:pasture", 7.5, 0.0, [0x01000000000000A0],
        [{"type": "item", "item": "cobblemon:pasture", "count": 1}],
        [{"item": "cobblemon:destiny_knot", "count": 1}, {"item": "cobblemon:everstone", "count": 1}]
    ),
    make_quest(
        0x0100000000000130,
        "&6Bussolas de Ginasios e Biomas",
        "Explorer's Compass e Nature's Compass",
        [
            "Para localizar os predios dos &cGinasios (Pewter, Cerulean, Vermilion...)&r, as &5Estruturas Lendarias&r e os biomas onde cada Pokemon da spawn:",
            "• Receba seu kit de exploracao inicial aqui (e voce pode fabricar novas bussolas com Circuito Basico e Apricorns!).",
            "• Clique com o botao direito com a &6Explorer's Compass&r e pesquise por &eGym&r!"
        ],
        "explorerscompass:explorerscompass", 2.5, 2.0, [0x0100000000000010],
        [{"type": "item", "item": "minecraft:compass", "count": 1}],
        [{"item": "explorerscompass:explorerscompass", "count": 1}, {"item": "naturescompass:naturescompass", "count": 1}]
    ),
    make_quest(
        0x0100000000000160,
        "&5Rede de Teleporte: Waystones",
        "Viaje entre Ginasios, Vilas e a Arena da Liga",
        [
            "Forje uma &5Warp Stone&r (Ender Pearl + Ametista + Esmeralda + Circuito Basico) e construa &bWaystones&r para marcar os Ginasios encontrados e teleportar instantaneamente entre as bases dos amigos!"
        ],
        "waystones:waystone", 5.0, 2.0, [0x0100000000000130],
        [{"type": "item", "item": "waystones:warp_stone", "count": 1}],
        [{"item": "waystones:waystone", "count": 2}]
    ),
    make_quest(
        0x0100000000000190,
        "&9Radar PokeNav e Camera Fotografica (RP)",
        "Rastreie spawns e registre a historia da Firma",
        [
            "• &bPokeNav:&r Mostra todos os Pokemon que dao spawn no bioma onde voce esta e a chance de cada um!",
            "• &eCamera (Exposure):&r Tire fotos reais dos seus Pokemon, das construcoes e do podio dos torneios da Firma League para revelar quadros!"
        ],
        "exposure:camera", 7.5, 2.0, [0x0100000000000160],
        [{"type": "item", "item": "exposure:camera", "count": 1}],
        [{"item": "exposure:color_film", "count": 3}, {"item": "cobblemon:quick_ball", "count": 10}]
    )
]
write_chapter(0x0100000000000001, GRP_HISTORIA, 2, "01_inicio_jornada", "&a1. O Inicio da Jornada", "cobblemon:pokedex_red", "circle", c1_quests)


# ==============================================================================
# CAPÍTULO 2: TEMPORADA 1 - LIGA KANTO (16 QUESTS TRANCADAS POR CONQUISTA REAL!)
# ==============================================================================
c2_quests = [
    make_quest(
        0x0200000000000010,
        "&71o Ginasio: Brock (Pewter Gym)",
        "Tipo Pedra | Level Cap para desafiar: Nv. 15",
        [
            "Localize o &7Pewter Gym&r com a Explorer's Compass e derrote o Lider &7Brock&r!",
            "",
            "• &cLevel Cap atual:&r Nv. 15 (Libera ate Nv. 27 ao vencer!)",
            "• &eTime do Brock (Balanceado):&r Geodude (Nv. 12), Vulpix (Nv. 12), Onix (Nv. 14).",
            "• &aRequisito Real:&r Esta quest so destrava ao derrotar o Brock de verdade no mundo!"
        ],
        "cobblemonpokemonbadges:boulder_badge", 0.0, 0.0, [0x0100000000000010],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_brock", "title": "Derrote o Lider Brock!"}],
        [{"item": "cobblemonpokemonbadges:boulder_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}, {"item": "cobblemon:great_ball", "count": 15}]
    ),
    make_quest(
        0x0200000000000020,
        "&b2o Ginasio: Misty (Cerulean Gym)",
        "Tipo Agua | Level Cap: Nv. 27",
        [
            "Localize o &bCerulean Gym&r e venca a Lider &bMisty&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 27 (Libera ate Nv. 36 ao vencer!)",
            "• &eTime da Misty:&r Psyduck (Nv. 24), Goldeen (Nv. 25), Starmie (Nv. 27).",
            "• &aDica:&r Leve ataques Eletricos ou de Planta e cuidado com o Scald e Ice Beam da Starmie!"
        ],
        "cobblemonpokemonbadges:cascade_badge", 2.5, 0.0, [0x0200000000000010],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_misty", "title": "Derrote a Lider Misty!"}],
        [{"item": "cobblemonpokemonbadges:cascade_badge", "count": 1}, {"item": "cobblemon:water_stone", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x0200000000000030,
        "&e3o Ginasio: Lt. Surge (Vermilion Gym)",
        "Tipo Eletrico | Level Cap: Nv. 36",
        [
            "Enfrente o Comandante Eletrico &eLt. Surge&r no &eVermilion Gym&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 36 (Libera ate Nv. 44 ao vencer!)",
            "• &eTime do Surge:&r Voltorb (Nv. 32), Magnemite (Nv. 32), Electabuzz (Nv. 34), Raichu (Nv. 35)."
        ],
        "cobblemonpokemonbadges:thunder_badge", 5.0, 0.0, [0x0200000000000020],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_lt_surge", "title": "Derrote o Lider Lt. Surge!"}],
        [{"item": "cobblemonpokemonbadges:thunder_badge", "count": 1}, {"item": "cobblemon:thunder_stone", "count": 1}, {"item": "cobblemon:ultra_ball", "count": 15}]
    ),
    make_quest(
        0x0200000000000040,
        "&a4o Ginasio: Erika (Celadon Gym)",
        "Tipo Planta | Level Cap: Nv. 44",
        [
            "Desafie a Lider &aErika&r no &aCeladon Gym&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 44",
            "• &eTime da Erika:&r Tangela (Nv. 40), Weepinbell (Nv. 41), Vileplume (Nv. 43), Bellossom (Nv. 43)."
        ],
        "cobblemonpokemonbadges:rainbow_badge", 7.5, 0.0, [0x0200000000000030],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_erika", "title": "Derrote a Lider Erika!"}],
        [{"item": "cobblemonpokemonbadges:rainbow_badge", "count": 1}, {"item": "cobblemon:leaf_stone", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0200000000000050,
        "&c[Opcional] Invasao Rocket I: Giovanni (Game Corner)",
        "Cacada Bonus Opcional (Savana ou Badlands)",
        [
            "&a[MISSAO OPCIONAL]:&r Voce NAO precisa encontrar o Giovanni para avancar nos Ginasios! Mas se quiser recompensas extras, procure-o após vencer a Erika!",
            "",
            "• &bOnde encontrar:&r Biomas de &6Savana (Savanna)&r ou &cMesa (Badlands)&r, ou colocando um &eUpgrade&r em um bloco Trainer Spawner.",
            "• &eTime do Giovanni I:&r Onix (Nv. 43), Rhyhorn (Nv. 44), Nidorino (Nv. 44), Kangaskhan (Nv. 46)."
        ],
        "cobblemon:luxury_ball", 7.5, -2.5, [0x0200000000000040],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_boss_giovanni_1", "title": "Derrote Giovanni (1o Encontro - Opcional)!"}],
        [{"item": "cobblemon:black_glasses", "count": 1}, {"item": "cobblemon:ultra_ball", "count": 15}],
        shape="hexagon", size=1.2, optional=True
    ),
    make_quest(
        0x0200000000000060,
        "&55o Ginasio: Koga (Fuchsia Gym)",
        "Tipo Venenoso | Destrava direto apos a Erika!",
        [
            "Use sua &6Explorer's Compass&r para localizar a estrutura do &5Fuchsia Gym&r (`rgs:fuchsia_gym`) e desafie o mestre ninja &5Koga&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 56",
            "• &eTime do Koga:&r Golbat (Nv. 51), Muk (Nv. 52), Venomoth (Nv. 53), Weezing (Nv. 54)."
        ],
        "cobblemonpokemonbadges:soul_badge", 10.0, 0.0, [0x0200000000000040],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_koga", "title": "Derrote o Lider Koga!"}],
        [{"item": "cobblemonpokemonbadges:soul_badge", "count": 1}, {"item": "cobblemon:black_sludge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0200000000000070,
        "&c[Opcional] Invasao Rocket II: Silph Co. (Giovanni II)",
        "Cacada Bonus Opcional (Savana, Badlands ou Nether)",
        [
            "&a[MISSAO OPCIONAL]:&r Missao bonus para quem quiser cacar o &4Giovanni II&r!",
            "",
            "• &bOnde encontrar:&r Biomas de &6Savana&r, &cBadlands&r ou &4Nether&r, ou colocando um &eDubious Disc&r em um Trainer Spawner.",
            "• &eTime do Giovanni II:&r Nidoqueen (Nv. 53), Machamp (Nv. 53), Rhydon (Nv. 54), Nidoking (Nv. 55), Honchkrow (Nv. 56)."
        ],
        "cobblemon:dubious_disc", 10.0, -2.5, [0x0200000000000060],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_boss_giovanni_2", "title": "Derrote Giovanni (2o Encontro - Opcional)!"}],
        [{"item": "cobblemon:upgrade", "count": 1}, {"item": "cobblemon:life_orb", "count": 1}],
        shape="hexagon", size=1.2, optional=True
    ),
    make_quest(
        0x0200000000000080,
        "&d6o Ginasio: Sabrina (Saffron Gym)",
        "Tipo Psiquico | Destrava direto apos o Koga!",
        [
            "Localize o &dSaffron Gym&r (`rgs:saffron_gym`) com sua Explorer's Compass e enfrente a prodígio psiquica &dSabrina&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 59",
            "• &eTime da Sabrina:&r Mr. Mime (Nv. 55), Espeon (Nv. 56), Slowbro (Nv. 57), Alakazam (Nv. 59)."
        ],
        "cobblemonpokemonbadges:marsh_badge", 10.0, 2.5, [0x0200000000000060],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_sabrina", "title": "Derrote a Lider Sabrina!"}],
        [{"item": "cobblemonpokemonbadges:marsh_badge", "count": 1}, {"item": "cobblemon:twisted_spoon", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0200000000000090,
        "&c7o Ginasio: Blaine (Cinnabar Gym)",
        "Tipo Fogo | Destrava direto apos a Sabrina!",
        [
            "Viaje ate o &cCinnabar Gym&r (`rgs:cinnabar_gym`) e supere o poder vulcanico de &cBlaine&r!",
            "",
            "• &cLevel Cap para desafiar:&r Nv. 64",
            "• &eTime do Blaine:&r Rapidash (Nv. 60), Ninetales (Nv. 61), Flareon (Nv. 62), Arcanine (Nv. 63), Magmortar (Nv. 64)."
        ],
        "cobblemonpokemonbadges:volcano_badge", 5.0, 2.5, [0x0200000000000080],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_blaine", "title": "Derrote o Lider Blaine!"}],
        [{"item": "cobblemonpokemonbadges:volcano_badge", "count": 1}, {"item": "cobblemon:fire_stone", "count": 1}, {"item": "cobblemon:charcoal_stick", "count": 1}]
    ),
    make_quest(
        0x02000000000000A0,
        "&98o Ginasio: Clair (Blackthorn / Viridian Gym)",
        "8a Insignia | Destrava direto apos o Blaine!",
        [
            "Use sua &6Explorer's Compass&r para encontrar o 8o Ginasio (`rgs:blackthorn_gym`) e conquiste a 8a Insignia derrotando &9Clair&r! (Nao precisa procurar o Giovanni para lutar com ela!)",
            "",
            "• &eTime da Clair:&r Gyarados (Nv. 64), Dragonair (Nv. 65), Altaria (Nv. 65), Ampharos (Nv. 66), Kingdra (Nv. 68)."
        ],
        "cobblemonpokemonbadges:earth_badge", 0.0, 2.5, [0x0200000000000090],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_leader_clair", "title": "Derrote a 8a Lider Clair!"}],
        [{"item": "cobblemonpokemonbadges:earth_badge", "count": 1}, {"item": "cobblemon:leftovers", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x02000000000000B0,
        "&4[Boss Opcional] Giovanni Final e Mewtwo (Nv. 80)!",
        "Super-Chefe Opcional (Savana, Badlands ou Nether)",
        [
            "&a[SUPER-BOSS OPCIONAL]:&r Voce NAO precisa encontrar o Giovanni para enfrentar a Clair ou a Elite Four! Mas para os cacadores corajosos, ele guarda uma luta epica usando &5Mewtwo (Nv. 80)&r!",
            "",
            "• &bOnde encontrar:&r Biomas de &6Savana&r, &cBadlands (Mesa)&r ou &4Nether&r, ou colocando um &dDestiny Knot&r num Trainer Spawner.",
            "• &eTime Final do Giovanni:&r Dugtrio (Nv. 75), Nidoqueen (Nv. 76), Nidoking (Nv. 76), Garchomp (Nv. 77), Rhyperior (Nv. 78) e &5Mewtwo (Nv. 80)&r!"
        ],
        "cobblemon:cherish_ball", 5.0, 0.5, [0x0200000000000090],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_boss_giovanni_3", "title": "Derrote Giovanni e seu Mewtwo Nv. 80 (Opcional)!"}],
        [{"item": "cobblemon:focus_sash", "count": 2}, {"item": "cobblemon:ability_capsule", "count": 1}],
        shape="hexagon", size=1.3, optional=True
    ),
    make_quest(
        0x02000000000000C0,
        "&bElite Four 1: Lorelei (Gelo)",
        "Indigo Plateau — Destrava direto apos a 8a Insignia (Clair)!",
        [
            "Com as 8 Insignias em maos, use sua &6Explorer's Compass&r para encontrar o predio da &6Kanto League&r (`rgs:kanto_league`) e comece derrotando &bLorelei&r!"
        ],
        "cobblemon:never_melt_ice", 0.0, 5.0, [0x02000000000000A0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_lorelei", "title": "Derrote Lorelei da Elite Four!"}],
        [{"item": "cobblemon:max_revive", "count": 3}]
    ),
    make_quest(
        0x02000000000000D0,
        "&cElite Four 2: Bruno (Lutador)",
        "Indigo Plateau — 2a Batalha da Liga",
        [
            "Avance para a 2a sala e derrote o mestre das artes marciais e Rocha, &cBruno&r!"
        ],
        "cobblemon:black_belt", 5.0, 5.0, [0x02000000000000C0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_bruno", "title": "Derrote Bruno da Elite Four!"}],
        [{"item": "cobblemon:max_revive", "count": 3}]
    ),
    make_quest(
        0x02000000000000E0,
        "&5Elite Four 3: Agatha (Fantasma)",
        "Indigo Plateau — 3a Batalha da Liga",
        [
            "Superando Bruno, enfrente os Gengars e espectros de &5Agatha&r na 3a sala!"
        ],
        "cobblemon:spell_tag", 7.5, 5.0, [0x02000000000000D0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_agatha", "title": "Derrote Agatha da Elite Four!"}],
        [{"item": "cobblemon:max_revive", "count": 3}]
    ),
    make_quest(
        0x02000000000000F0,
        "&9Elite Four 4: Lance (Dragao)",
        "Indigo Plateau — O Guardiao Final da Elite Four",
        [
            "Enfrente o lider da Elite Four, &9Lance&r, e sua esquadra de Dragoes!"
        ],
        "cobblemon:dragon_fang", 10.0, 5.0, [0x02000000000000E0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_lance", "title": "Derrote Lance da Elite Four!"}],
        [{"item": "cobblemon:Full_restore" if False else "cobblemon:max_potion", "count": 5}]
    ),
    make_quest(
        0x0200000000000100,
        "&6&lGRANDE CAMPEAO DE KANTO!",
        "Destrava a Temporada 2 (Johto) e a 1a Copa da Firma!",
        [
            "Derrote o &6Campeao de Kanto&r no salao principal da Liga!",
            "",
            "&aO QUE ESTA CONQUISTA DESTRAVA:&r",
            "1. Libera oficialmente todo o capitulo da &eTemporada 2: Liga Johto&r!",
            "2. Classifica voce para disputar a &61a Liga da Firma (Copa Kanto PvP)&r!",
            "3. Premia voce com sua primeira &5Master Ball&r e &dAbility Patch&r!"
        ],
        "cobblemon:master_ball", 10.0, 7.5, [0x02000000000000F0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_kanto", "title": "Zere a Liga Kanto derrotando o Campeao!"}],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "cobblemon:ability_patch", "count": 1}, {"item": "cobblemon:rare_candy", "count": 15}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0200000000000001, GRP_HISTORIA, 3, "02_ginasios_historia", "&6Temp. 1: Liga Kanto (Historia)", "cobblemonpokemonbadges:boulder_badge", "octagon", c2_quests)


# ==============================================================================
# CAPÍTULO 2B: TEMPORADA 2 - LIGA JOHTO (BLOQUEADO ATÉ ZERAR KANTO!)
# ==============================================================================
KANTO_CHAMP_ID = 0x0200000000000100

c2b_quests = [
    make_quest(
        0x0220000000000010,
        "&eAto II: Rumo a Regiao de Johto!",
        "BLOQUEADO ate vencer o Campeao de Kanto!",
        [
            "&6[LORE - ATO II]:&r Com a queda de Giovanni em Kanto, os generais remanescentes da Equipe Rocket tomaram a &cTorre de Radio de Johto&r! As ondas de radio despertaram &eRaikou, Entei e Suicune&r na Burned Tower e agitaram &6Ho-Oh&r e &9Lugia&r!",
            "",
            "&cRequisito de Desbloqueio:&r Voce precisa ter vencido a &6Liga Kanto&r no Capitulo anterior para iniciar Johto!"
        ],
        "cobblemon:love_ball", 0.0, 0.0, [KANTO_CHAMP_ID],
        [{"type": "checkmark", "title": "Iniciei minha expedicao em Johto apos zerar Kanto!"}],
        [{"item": "cobblemon:ultra_ball", "count": 20}, {"item": "cobblemon:exp_candy_l", "count": 8}],
        shape="pentagon", size=1.5
    ),
    make_quest(
        0x0220000000000020,
        "&b1o Ginasio Johto: Falkner (Violet Gym)",
        "Tipo Voador | Insignia Zephyr",
        ["Derrote o Lider &bFalkner&r no &bViolet Gym&r para conquistar a &fZephyr Badge&r!"],
        "cobblemonpokemonbadges:zephyr_badge", 2.5, 0.0, [0x0220000000000010],
        [{"type": "item", "item": "cobblemon:sharp_beak", "count": 1}],
        [{"item": "cobblemonpokemonbadges:zephyr_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x0220000000000030,
        "&a2o Ginasio Johto: Bugsy (Azalea Gym)",
        "Tipo Inseto | Insignia Hive",
        ["Supere o Scyther de &aBugsy&r no &aAzalea Gym&r e conquiste a &aHive Badge&r!"],
        "cobblemonpokemonbadges:hive_badge", 5.0, 0.0, [0x0220000000000020],
        [{"type": "item", "item": "cobblemon:silver_powder", "count": 1}],
        [{"item": "cobblemonpokemonbadges:hive_badge", "count": 1}, {"item": "cobblemon:net_ball", "count": 15}]
    ),
    make_quest(
        0x0220000000000040,
        "&f3o Ginasio Johto: Whitney (Goldenrod Gym)",
        "Tipo Normal | Insignia Plain",
        ["Enfrente a temida Miltank com Rollout da &fWhitney&r no &fGoldenrod Gym&r!"],
        "cobblemonpokemonbadges:plain_badge", 7.5, 0.0, [0x0220000000000030],
        [{"type": "item", "item": "cobblemon:silk_scarf", "count": 1}],
        [{"item": "cobblemonpokemonbadges:plain_badge", "count": 1}, {"item": "cobblemon:love_ball", "count": 10}]
    ),
    make_quest(
        0x0220000000000050,
        "&54o Ginasio Johto: Morty (Ecruteak Gym)",
        "Tipo Fantasma | Insignia Fog",
        ["Derrote o vidente &5Morty&r e seu Gengar em &5Ecruteak&r para ganhar a &5Fog Badge&r!"],
        "cobblemonpokemonbadges:fog_badge", 10.0, 0.0, [0x0220000000000040],
        [{"type": "item", "item": "cobblemon:spell_tag", "count": 1}],
        [{"item": "cobblemonpokemonbadges:fog_badge", "count": 1}, {"item": "cobblemon:dusk_ball", "count": 15}]
    ),
    make_quest(
        0x0220000000000060,
        "&6As Torres de Ecruteak e Ilhas Redemoinho",
        "Burned Tower, Bell Tower (Ho-Oh) e Whirl Islands (Lugia)",
        [
            "Em Ecruteak e na costa de Johto, investigue as 3 grandes estruturas da historia:",
            "• &cBurned Tower:&r Onde despertam &eRaikou, Entei e Suicune&r.",
            "• &6Bell Tower:&r O santuario de &6Ho-Oh&r.",
            "• &9Whirl Islands:&r As cavernas abissais de &9Lugia&r."
        ],
        "cobblemon:heavy_ball", 10.0, 2.5, [0x0220000000000050],
        [{"type": "item", "item": "cobblemon:max_revive", "count": 1}],
        [{"item": "cobblemon:heavy_ball", "count": 15}, {"item": "cobblemon:fast_ball", "count": 15}],
        shape="hexagon", size=1.3
    ),
    make_quest(
        0x0220000000000070,
        "&c5o Ginasio Johto: Chuck (Cianwood Gym)",
        "Tipo Lutador | Insignia Storm",
        ["Venca o mestre marcial &cChuck&r no &cCianwood Gym&r!"],
        "cobblemonpokemonbadges:storm_badge", 7.5, 2.5, [0x0220000000000050],
        [{"type": "item", "item": "cobblemon:black_belt", "count": 1}],
        [{"item": "cobblemonpokemonbadges:storm_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0220000000000080,
        "&76o Ginasio Johto: Jasmine (Olivine Gym)",
        "Tipo Metalico | Insignia Mineral",
        ["Derrote &7Jasmine&r e seu poderoso Steelix no &7Olivine Gym&r!"],
        "cobblemonpokemonbadges:mineral_badge", 5.0, 2.5, [0x0220000000000070],
        [{"type": "item", "item": "cobblemon:metal_coat", "count": 1}],
        [{"item": "cobblemonpokemonbadges:mineral_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0220000000000090,
        "&b7o Ginasio Johto: Pryce (Mahogany Gym)",
        "Tipo Gelo | Insignia Glacier",
        ["Domine o frio de &bPryce&r no &bMahogany Gym&r e expulse os Rockets da Radio Tower!"],
        "cobblemonpokemonbadges:glacier_badge", 2.5, 2.5, [0x0220000000000080],
        [{"type": "item", "item": "cobblemon:never_melt_ice", "count": 1}],
        [{"item": "cobblemonpokemonbadges:glacier_badge", "count": 1}, {"item": "cobblemon:ice_stone", "count": 1}]
    ),
    make_quest(
        0x02200000000000A0,
        "&98o Ginasio Johto: Clair (Blackthorn Gym)",
        "Tipo Dragao | Insignia Rising",
        ["Conquiste a 8a Insignia de Johto no covil dos dragoes de &9Blackthorn&r!"],
        "cobblemonpokemonbadges:rising_badge", 0.0, 2.5, [0x0220000000000090],
        [{"type": "item", "item": "cobblemon:dragon_scale", "count": 1}],
        [{"item": "cobblemonpokemonbadges:rising_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 10}]
    ),
    make_quest(
        0x02200000000000B0,
        "&6&lCAMPEAO DE JOHTO (LANCE) E DUELO CONTRA RED!",
        "Destrava a Temporada 3 (Hoenn) e a 2a Copa da Firma!",
        [
            "Venca o Campeao &6Lance&r e o lendario treinador &cRed&r!",
            "",
            "&aO QUE ESTA CONQUISTA DESTRAVA:&r",
            "1. Libera oficialmente todo o capitulo da &aTemporada 3: Liga Hoenn&r!",
            "2. Classifica voce para a &62a Liga da Firma (Copa Johto PvP)&r!"
        ],
        "cobblemon:master_ball", 0.0, 5.0, [0x02200000000000A0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_trainer_red", "title": "Derrote o lendario Red para fechar Johto!"}],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "cobblemon:ability_patch", "count": 1}, {"item": "cobblemon:rare_candy", "count": 15}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0220000000000001, GRP_HISTORIA, 4, "02b_temporada_2_johto", "&eTemp. 2: Liga Johto (Historia)", "cobblemonpokemonbadges:rising_badge", "octagon", c2b_quests)


# ==============================================================================
# CAPÍTULO 2C: TEMPORADA 3 - LIGA HOENN (15 QUESTS COM CONQUISTAS REAIS!)
# ==============================================================================
JOHTO_CHAMP_ID = 0x02200000000000B0

c2c_quests = [
    make_quest(
        0x0230000000000010,
        "&aAto III: A Expedicao para Hoenn!",
        "BLOQUEADO ate concluir a Temporada 2 (Johto)!",
        [
            "&6[LORE - ATO III]:&r As fendas de Mega Evolucao despertaram os titas primordiais em &aHoenn&r: &cGroudon&r e &9Kyogre&r! Enquanto a &cTeam Magma (Maxie)&r e a &9Team Aqua (Archie)&r guerreiam, conquiste os 8 Ginasios de Hoenn, suba ao &2Sky Pillar&r e enfrente o Campeao &bSteven Stone&r!"
        ],
        "cobblemon:premier_ball", 0.0, 0.0, [JOHTO_CHAMP_ID],
        [{"type": "checkmark", "title": "Iniciei a Temporada 3 em Hoenn!"}],
        [{"item": "cobblemon:dive_ball", "count": 20}, {"item": "cobblemon:exp_candy_l", "count": 10}],
        shape="pentagon", size=1.5
    ),
    make_quest(
        0x0230000000000020,
        "&71o Ginasio Hoenn: Roxanne (Rustboro Gym)",
        "Tipo Pedra | Stone Badge",
        ["Derrote a Lider &7Roxanne&r no Rustboro Gym!"],
        "cobblemonpokemonbadges:stone_badge", 2.5, 0.0, [0x0230000000000010],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_roxanne", "title": "Derrote a Lider Roxanne!"}],
        [{"item": "cobblemonpokemonbadges:stone_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x0230000000000030,
        "&c2o Ginasio Hoenn: Brawly (Dewford Gym)",
        "Tipo Lutador | Knuckle Badge",
        ["Derrote o surfista marcial &cBrawly&r no Dewford Gym!"],
        "cobblemonpokemonbadges:knuckle_badge", 5.0, 0.0, [0x0230000000000020],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_brawly", "title": "Derrote o Lider Brawly!"}],
        [{"item": "cobblemonpokemonbadges:knuckle_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x0230000000000040,
        "&e3o Ginasio Hoenn: Wattson (Mauville Gym)",
        "Tipo Eletrico | Dynamo Badge",
        ["Venca a alta voltagem de &eWattson&r no Mauville Gym!"],
        "cobblemonpokemonbadges:dynamo_badge", 7.5, 0.0, [0x0230000000000030],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_wattson", "title": "Derrote o Lider Wattson!"}],
        [{"item": "cobblemonpokemonbadges:dynamo_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0230000000000050,
        "&64o Ginasio Hoenn: Flannery (Lavaridge Gym)",
        "Tipo Fogo | Heat Badge",
        ["Supere o Torkoal e o Overheat de &6Flannery&r no Lavaridge Gym!"],
        "cobblemonpokemonbadges:heat_badge", 10.0, 0.0, [0x0230000000000040],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_flannery", "title": "Derrote a Lider Flannery!"}],
        [{"item": "cobblemonpokemonbadges:heat_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0230000000000060,
        "&f5o Ginasio Hoenn: Norman (Petalburg Gym)",
        "Tipo Normal | Balance Badge",
        ["Derrote &fNorman&r e seus poderosos Slakings no Petalburg Gym!"],
        "cobblemonpokemonbadges:balance_badge", 10.0, 2.5, [0x0230000000000050],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_norman", "title": "Derrote o Lider Norman!"}],
        [{"item": "cobblemonpokemonbadges:balance_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0230000000000070,
        "&c[Boss Opcional] Maxie (Magma) e Archie (Aqua)",
        "Cacada Opcional de Hoenn",
        ["&a[MISSAO OPCIONAL]:&r Voce pode ir direto de Norman para Winona! Mas se encontrar os lideres &cMaxie (Team Magma)&r e &9Archie (Team Aqua)&r, derrote-os para ganhar recompensas extras!"],
        "mega_showdown:archie_anchor", 10.0, 5.0, [0x0230000000000060],
        [
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_magma_leader_maxie", "title": "Derrote Maxie da Team Magma (Opcional)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_aqua_leader_archie", "title": "Derrote Archie da Team Aqua (Opcional)!"}
        ],
        [{"item": "cobblemon:timer_ball", "count": 20}, {"item": "cobblemon:rare_candy", "count": 8}],
        shape="hexagon", size=1.2, optional=True
    ),
    make_quest(
        0x0230000000000080,
        "&b6o Ginasio Hoenn: Winona (Fortree Gym)",
        "Tipo Voador | Feather Badge (Destrava direto apos Norman!)",
        ["Derrote a graciosa &bWinona&r e sua Altaria no Fortree Gym!"],
        "cobblemonpokemonbadges:feather_badge", 6.5, 2.5, [0x0230000000000060],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_winona", "title": "Derrote a Lider Winona!"}],
        [{"item": "cobblemonpokemonbadges:feather_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0230000000000090,
        "&d7o Ginasio Hoenn: Tate e Liza (Mossdeep Gym)",
        "Tipo Psiquico | Mind Badge",
        ["Supere os gemeos psiquicos em &dMossdeep&r!"],
        "cobblemonpokemonbadges:mind_badge", 3.5, 2.5, [0x0230000000000080],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_liza", "title": "Derrote Tate e Liza!"}],
        [{"item": "cobblemonpokemonbadges:mind_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x02300000000000A0,
        "&98o Ginasio Hoenn: Wallace (Sootopolis Gym)",
        "Tipo Agua | Rain Badge",
        ["Conquiste a 8a Insignia de Hoenn derrotando o mestre das aguas &9Wallace&r!"],
        "cobblemonpokemonbadges:rain_badge", 0.0, 2.5, [0x0230000000000090],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennleader_wallace", "title": "Derrote o Lider Wallace!"}],
        [{"item": "cobblemonpokemonbadges:rain_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 10}]
    ),
    make_quest(
        0x02300000000000B0,
        "&8Elite Four de Hoenn: Sidney, Phoebe, Glacia e Drake",
        "Ever Grande City — Os 4 Guardioes de Hoenn",
        ["Derrote os 4 membros da &aElite Four de Hoenn&r em sequencia para chegar ate o Campeao Steven!"],
        "cobblemon:ultra_ball", 3.0, 5.0, [0x02300000000000A0],
        [
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennelitefour_sidney", "title": "Derrote Sidney (Noturno)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennelitefour_phoebe", "title": "Derrote Phoebe (Fantasma)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennelitefour_glacia", "title": "Derrote Glacia (Gelo)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennelitefour_drake", "title": "Derrote Drake (Dragao)!"}
        ],
        [{"item": "cobblemon:max_revive", "count": 5}, {"item": "cobblemon:rare_candy", "count": 10}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x02300000000000C0,
        "&6&lCAMPEAO DE HOENN: STEVEN STONE!",
        "Destrava a Temporada 4 (Sinnoh) e a 3a Copa da Firma!",
        [
            "Venca o &bCampeao Steven Stone&r e seu Mega Metagross!",
            "",
            "&aO QUE ESTA CONQUISTA DESTRAVA:&r",
            "1. Abre o capitulo final da historia: &dTemporada 4: Liga Sinnoh&r!",
            "2. Classifica voce para a &63a Liga da Firma (Copa Hoenn PvP)&r!"
        ],
        "cobblemon:master_ball", 7.5, 5.0, [0x02300000000000B0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_hoennchampion_steven", "title": "Derrote o Campeao Steven Stone!"}],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "cobblemon:ability_patch", "count": 2}, {"item": "cobblemon:rare_candy", "count": 15}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0230000000000001, GRP_HISTORIA, 5, "02c_temporada_3_hoenn", "&aTemp. 3: Liga Hoenn (Historia)", "cobblemonpokemonbadges:rain_badge", "octagon", c2c_quests)


# ==============================================================================
# CAPÍTULO 2D: TEMPORADA 4 - LIGA SINNOH (13 QUESTS COM CONQUISTAS REAIS!)
# ==============================================================================
HOENN_CHAMP_ID = 0x02300000000000C0

c2d_quests = [
    make_quest(
        0x0240000000000010,
        "&dAto Final: A Ruptura em Sinnoh!",
        "BLOQUEADO ate derrotar o Campeao Steven em Hoenn!",
        [
            "&6[LORE - ATO FINAL]:&r Steven descobriu que a Grande Convergencia se originou no topo do &5Spear Pillar, em Sinnoh&r, onde &8Cyrus e a Equipe Galactica&r tentam controlar &9Dialga, Palkia e Giratina&r! Conquiste os 8 Ginasios de Sinnoh, sele a fenda e enfrente a lendaria &6Campea Cynthia&r!"
        ],
        "cobblemon:cherish_ball", 0.0, 0.0, [HOENN_CHAMP_ID],
        [{"type": "checkmark", "title": "Iniciei a Temporada 4 em Sinnoh!"}],
        [{"item": "cobblemon:dusk_ball", "count": 25}, {"item": "cobblemon:exp_candy_xl", "count": 10}],
        shape="pentagon", size=1.5
    ),
    make_quest(
        0x0240000000000020,
        "&71o Ginasio Sinnoh: Roark (Oreburgh Gym)",
        "Tipo Pedra | Coal Badge",
        ["Derrote o Lider &7Roark&r e seu Cranidos/Rampardos!"],
        "cobblemonpokemonbadges:coal_badge", 2.5, 0.0, [0x0240000000000010],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_roark_1", "title": "Derrote o Lider Roark!"}],
        [{"item": "cobblemonpokemonbadges:coal_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0240000000000030,
        "&a2o Ginasio Sinnoh: Gardenia (Eterna Gym)",
        "Tipo Planta | Forest Badge",
        ["Venca &aGardenia&r e sua Roserade no Eterna Gym!"],
        "cobblemonpokemonbadges:forest_badge", 5.0, 0.0, [0x0240000000000020],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_gardenia_1", "title": "Derrote a Lider Gardenia!"}],
        [{"item": "cobblemonpokemonbadges:forest_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0240000000000040,
        "&c3o Ginasio Sinnoh: Maylene (Veilstone Gym)",
        "Tipo Lutador | Cobble Badge",
        ["Enfrente &cMaylene&r e seu Lucario no Veilstone Gym!"],
        "cobblemonpokemonbadges:cobble_badge", 7.5, 0.0, [0x0240000000000030],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_maylene_1", "title": "Derrote a Lider Maylene!"}],
        [{"item": "cobblemonpokemonbadges:cobble_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 6}]
    ),
    make_quest(
        0x0240000000000050,
        "&94o Ginasio Sinnoh: Crasher Wake (Pastoria Gym)",
        "Tipo Agua | Fen Badge",
        ["Supere o Floatzel e Gyarados de &9Crasher Wake&r!"],
        "cobblemonpokemonbadges:fen_badge", 10.0, 0.0, [0x0240000000000040],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_wake_1", "title": "Derrote Crasher Wake!"}],
        [{"item": "cobblemonpokemonbadges:fen_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x0240000000000060,
        "&55o Ginasio Sinnoh: Fantina (Hearthome Gym)",
        "Tipo Fantasma | Relic Badge",
        ["Derrote a estrela dos espectros &5Fantina&r e seu Mismagius!"],
        "cobblemonpokemonbadges:relic_badge", 10.0, 2.5, [0x0240000000000050],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_fantina_1", "title": "Derrote a Lider Fantina!"}],
        [{"item": "cobblemonpokemonbadges:relic_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x0240000000000070,
        "&76o Ginasio Sinnoh: Byron (Canalave Gym)",
        "Tipo Metalico | Mine Badge",
        ["Quebre a defesa de aco de &7Byron&r e seu Bastiodon!"],
        "cobblemonpokemonbadges:mine_badge", 7.5, 2.5, [0x0240000000000060],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_byron_1", "title": "Derrote o Lider Byron!"}],
        [{"item": "cobblemonpokemonbadges:mine_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x0240000000000080,
        "&b7o Ginasio Sinnoh: Candice (Snowpoint Gym)",
        "Tipo Gelo | Icicle Badge",
        ["Venca a nevasca de &bCandice&r no norte gelado de Sinnoh!"],
        "cobblemonpokemonbadges:icicle_badge", 5.0, 2.5, [0x0240000000000070],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_candice_1", "title": "Derrote a Lider Candice!"}],
        [{"item": "cobblemonpokemonbadges:icicle_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 8}]
    ),
    make_quest(
        0x0240000000000090,
        "&5[Boss Opcional] Chefe Cyrus da Equipe Galactica",
        "Cacada Opcional de Sinnoh",
        ["&a[MISSAO OPCIONAL]:&r Voce pode ir direto de Candice para Volkner! Se encontrar o lider da Equipe Galactica, &9Cyrus&r, derrote-o para ganhar os Orbes de Dialga e Palkia!"],
        "mega_showdown:adamant_orb", 4.0, 5.0, [0x0240000000000080],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_team_galactic_boss_cyrus_1", "title": "Derrote Cyrus da Equipe Galactica (Opcional)!"}],
        [{"item": "mega_showdown:adamant_orb", "count": 1}, {"item": "mega_showdown:lustrous_orb", "count": 1}],
        shape="hexagon", size=1.2, optional=True
    ),
    make_quest(
        0x02400000000000A0,
        "&e8o Ginasio Sinnoh: Volkner (Sunyshore Gym)",
        "Tipo Eletrico | Beacon Badge (Destrava direto apos Candice!)",
        ["Conquiste a ultima Insignia de Sinnoh derrotando &eVolkner&r!"],
        "cobblemonpokemonbadges:beacon_badge", 1.5, 2.5, [0x0240000000000080],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_gym_leader_volkner_1", "title": "Derrote o Lider Volkner!"}],
        [{"item": "cobblemonpokemonbadges:beacon_badge", "count": 1}, {"item": "cobblemon:rare_candy", "count": 12}]
    ),
    make_quest(
        0x02400000000000B0,
        "&dElite Four de Sinnoh: Aaron, Bertha, Flint e Lucian",
        "Os 4 Guardioes Finais antes de Cynthia",
        ["Venca os 4 membros da &dElite Four de Sinnoh&r em sequencia!"],
        "cobblemon:luxury_ball", 3.0, 5.0, [0x02400000000000A0],
        [
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_aaron_1", "title": "Derrote Aaron (Inseto)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_bertha_1", "title": "Derrote Bertha (Terra)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_flint_1", "title": "Derrote Flint (Fogo)!"},
            {"type": "advancement", "advancement": "rctmod:trainers/defeat_elite_four_lucian_1", "title": "Derrote Lucian (Psiquico)!"}
        ],
        [{"item": "cobblemon:max_revive", "count": 8}, {"item": "cobblemon:rare_candy", "count": 15}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x02400000000000C0,
        "&6&lCAMPEA SUPREMA: CYNTHIA!",
        "Zere as 4 Regioes e abra a Grande Liga Mundial!",
        [
            "Enfrente e derrote a lendaria &6Campea Cynthia&r e seu Garchomp!",
            "",
            "Parabens! Voce salvou o mundo da Grande Convergencia, zerou as 4 Regioes e esta classificado para a &6&lGrande Final da Firma League (Liga Mundial e Copa Ubers)&r!"
        ],
        "cobblemon:master_ball", 7.5, 5.0, [0x02400000000000B0],
        [{"type": "advancement", "advancement": "rctmod:trainers/defeat_champion_cynthia_1", "title": "Derrote a Campea Cynthia!"}],
        [{"item": "cobblemon:master_ball", "count": 2}, {"item": "cobblemon:cherish_ball", "count": 10}, {"item": "cobblemon_utility:goldencap", "count": 1}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0240000000000001, GRP_HISTORIA, 6, "02d_temporada_4_sinnoh", "&dTemp. 4: Liga Sinnoh (Final)", "cobblemonpokemonbadges:beacon_badge", "octagon", c2d_quests)


# ==============================================================================
# CAPÍTULO 3B: ENGENHARIA DA CONVERGÊNCIA (CREATE + MEKANISM + POWAH + FORNALHAS) - 20 QUESTS!
# ==============================================================================
c3b_quests = [
    make_quest(
        0x03B0000000000010,
        "&61. Era 1 (Create): Liga de Andesito e Roda D'Agua",
        "Energia Rotacional (SU) e Engrenagens!",
        [
            "Bem-vindo a Engenharia do &6Create&r! Antes da eletricidade, as fabricas da Firma usam forca mecanica:",
            "1. Misture &7Andesito + Pepitas de Ferro (ou Zinco)&r na bancada para criar &eAndesite Alloy (Liga de Andesito)&r.",
            "2. Construa uma &bWater Wheel (Roda D'Agua)&r e coloque uma correnteza de agua passando por ela para gerar &eForca Rotacional (SU)&r.",
            "3. Use &6Shafts (Eixos)&r e &6Cogwheels (Engrenagens)&r para levar a rotacao ate suas maquinas!",
            "• &bDica de Ouro:&r Segure a tecla &e[W] (Ponder)&r em cima de qualquer item do Create no inventario para ver uma animacao 3D ensinando a montar!"
        ],
        "create:water_wheel", 0.0, 0.0, None,
        [
            {"type": "item", "item": "create:andesite_alloy", "count": 16},
            {"type": "item", "item": "create:water_wheel", "count": 1},
            {"type": "item", "item": "create:cogwheel", "count": 8}
        ],
        [{"item": "create:andesite_casing", "count": 8}, {"item": "create:wrench", "count": 1}],
        shape="pentagon", size=1.4
    ),
    make_quest(
        0x03B0000000000020,
        "&f2. Prensa Mecanica e Chapas de Ferro (Pokebolas Tier 2!)",
        "Prensando lingotes para Great Ball, Heavy Ball e Maquinas!",
        [
            "Construa uma &eMechanical Press (Prensa Mecanica)&r e ligue um eixo nela!",
            "",
            "• Jogue &fBarras de Ferro&r embaixo da Prensa (no chao, num Depot ou numa esteira) para prensar &fIron Sheets (Chapas de Ferro)&r!",
            "• &6Uso nas Pokebolas:&r Na Firma League, a &fChapa de Ferro&r (ou Liga de Andesito / Osmio) e a base de &bTODAS as Pokebolas Tier 2 (Great Ball, Fast Ball, Heavy Ball, Level Ball, Moon Ball...)&r e tambem do PC, Healer e Pokedex!"
        ],
        "create:mechanical_press", 2.5, -1.5, [0x03B0000000000010],
        [
            {"type": "item", "item": "create:mechanical_press", "count": 1},
            {"type": "item", "item": "create:iron_sheet", "count": 12}
        ],
        [{"item": "cobblemon:great_ball", "count": 15}, {"item": "create:iron_sheet", "count": 8}]
    ),
    make_quest(
        0x03B0000000000030,
        "&e3. Misturador Mecanico, Latao (Brass) e Automacao Create",
        "Brass Sheet, Electron Tube e Deployer!",
        [
            "Evolua sua oficina do &6Create&r para o nivel de &eLatao (Brass)&r:",
            "• Use o &6Mechanical Mixer + Basin + Blaze Burner&r para misturar Cobre e Zinco em &eBrass Ingot (Latao)&r e prense em &eBrass Sheet&r (que tambem serve para Pokebolas Tier 3!).",
            "• Crie &cElectron Tubes&r (Rose Quartz Polido + Chapa de Ferro) e o &eDeployer&r (a mao mecanica que monta itens e Pokebolas sozinha na esteira!)."
        ],
        "create:deployer", 5.0, -2.5, [0x03B0000000000020],
        [
            {"type": "item", "item": "create:mechanical_mixer", "count": 1},
            {"type": "item", "item": "create:brass_sheet", "count": 8},
            {"type": "item", "item": "create:deployer", "count": 1}
        ],
        [{"item": "create:electron_tube", "count": 4}, {"item": "create:precision_mechanism", "count": 2}]
    ),
    make_quest(
        0x03B0000000000040,
        "&b4. Ponte Eletrica: Create Crafts & Additions!",
        "Transforme Rotacao (SU) em Energia (FE) e vice-versa!",
        [
            "O addon &bCreate Crafts & Additions&r conecta o Create ao Mekanism e ao Powah!:",
            "• &6Alternator (Alternador):&r Gire ele com Rodas D'Agua ou Moinhos do Create para gerar &aEnergia Eletrica (FE)&r gratis!",
            "• &bElectric Motor (Motor Eletrico):&r Alimente ele com cabos de energia do Mekanism/Powah para girar qualquer maquina do Create em alta velocidade sem precisar de mil engrenagens (zero lag de FPS na base)!"
        ],
        "createaddition:electric_motor", 7.5, -2.5, [0x03B0000000000030],
        [
            {"type": "item", "item": "createaddition:alternator", "count": 1},
            {"type": "item", "item": "createaddition:electric_motor", "count": 1}
        ],
        [{"item": "createaddition:capacitor", "count": 4}]
    ),
    make_quest(
        0x03B0000000000050,
        "&35. Era 1 (Mekanism): Minerando Osmio e Infusor Metalurgico",
        "A maquina mais importante do Mekanism!",
        [
            "Minere &bOsmium Ore (Minerio de Osmio)&r nas cavernas e construa a sua primeira maquina do &bMekanism&r: o &3Metallurgic Infuser (Infusor Metalurgico)&r!",
            "",
            "• &eDica:&r Voce pode ligar o Metallurgic Infuser colocando ate mesmo &cRedstone&r no slot de energia dele no comeco, ou conectando a um &6Heat Generator&r (do Mekanism Generators) / &6Alternator&r!"
        ],
        "mekanism:metallurgic_infuser", 2.5, 1.0, [0x03B0000000000010],
        [
            {"type": "item", "item": "mekanism:ingot_osmium", "count": 12},
            {"type": "item", "item": "mekanism:metallurgic_infuser", "count": 1}
        ],
        [{"item": "mekanism:ingot_osmium", "count": 8}, {"item": "minecraft:redstone", "count": 16}],
        shape="pentagon", size=1.4
    ),
    make_quest(
        0x03B0000000000060,
        "&a6. Circuito de Controle Basico e Liga Infundida",
        "O Coracao Eletronico da Silph Co.!",
        [
            "Existem &e2 formas&r de produzir o &aBasic Control Circuit (Circuito de Controle Basico)&r e a &cInfused Alloy (Liga Infundida)&r:",
            "1. &bNo Metallurgic Infuser:&r Infunda &fOsmio + Redstone&r para criar o Circuito Basico, e &fFerro + Redstone&r para criar a Infused Alloy!",
            "2. &aReceita Bio-Eletronica da Firma (na Bancada):&r 6 Cabos Universais Basicos + 1 Redstone + 1 Chapa de Ferro (Create) + &e1 Apricorn de qualquer cor&r!",
            "",
            "• &bOnde o Circuito Basico e usado:&r PC Pokemon, Healing Machine, Pasture Block, Pokedex, Exp. Share, Fornalha de Ouro, Mochila de Ouro, Storage Terminal, Explorer's Compass, Mega Bracelet e Tera Orb!"
        ],
        "mekanism:basic_control_circuit", 5.0, 0.0, [0x03B0000000000020, 0x03B0000000000050],
        [
            {"type": "item", "item": "mekanism:basic_control_circuit", "count": 4},
            {"type": "item", "item": "mekanism:alloy_infused", "count": 4}
        ],
        [{"item": "mekanism:basic_control_circuit", "count": 2}, {"item": "mekanism:basic_universal_cable", "count": 16}],
        shape="hexagon", size=1.5
    ),
    make_quest(
        0x03B0000000000070,
        "&67. Fornalhas de Ferro e Ouro (Better Furnaces)",
        "Fundicao ultra-rapida para o seu laboratorio",
        [
            "Chega de esperar a fornalha de pedra! Evolua sua fornalha passando pelos tiers da Firma:",
            "• &fFornalha de Ferro:&r Usa Chapas de Ferro (Create), Bloco Condutor, Cobre e &cRed Apricorn&r.",
            "• &6Fornalha de Ouro:&r Evolui a Fornalha de Ferro com Ouro e &a1 Circuito de Controle Basico (Mekanism)&r!"
        ],
        "betterfurnacesreforged:gold_furnace", 5.0, -1.3, [0x03B0000000000060],
        [
            {"type": "item", "item": "betterfurnacesreforged:iron_furnace", "count": 1},
            {"type": "item", "item": "betterfurnacesreforged:gold_furnace", "count": 1}
        ],
        [{"item": "betterfurnacesreforged:fuel_efficiency_upgrade", "count": 1}, {"item": "betterfurnacesreforged:ore_processing_upgrade", "count": 1}]
    ),
    make_quest(
        0x03B0000000000090,
        "&b8. Dobrando Minerios (Mekanism): Enrichment Chamber e Smelter",
        "1 Minerio Bruto = 2 Barras (e ate 3x/4x/5x depois)!",
        [
            "Monte a sua linha industrial do &bMekanism&r:",
            "• &aEnrichment Chamber (Camara de Enriquecimento):&r Transforma 1 Minerio Bruto em 2 Pos (dobrando seus minerios!) e tambem transforma 1 Redstone/Carvao/Diamante em versão Enriquecida (que rende 8x mais no Metallurgic Infuser!).",
            "• &eCrusher (Triturador):&r Tritura sobras vegetais/Apricorns em &aBio Fuel&r para gerar muita energia!",
            "• &6Energized Smelter:&r Fornalha eletrica de alta precisao."
        ],
        "mekanism:enrichment_chamber", 7.5, -1.0, [0x03B0000000000060],
        [
            {"type": "item", "item": "mekanism:enrichment_chamber", "count": 1},
            {"type": "item", "item": "mekanism:crusher", "count": 1},
            {"type": "item", "item": "mekanism:energized_smelter", "count": 1}
        ],
        [{"item": "mekanism:upgrade_speed", "count": 4}, {"item": "mekanism:upgrade_energy", "count": 4}]
    ),
    make_quest(
        0x03B00000000000B0,
        "&c9. Circuitos Avancado, Elite e Ultimate (Mekanism)",
        "A Escalada Tecnologica ate o Topo!",
        [
            "Combinando as ligas do Mekanism com os cristais do Powah!, escale os 4 Tiers de Circuitos:",
            "• &cAdvanced Control Circuit (Tier 2):&r Circuito Basico + 2 Infused Alloys (ou via bancada com Pasta Dieletrica e Aco Energizado).",
            "• &bElite Control Circuit (Tier 3):&r Circuito Avancado + 2 Reinforced Alloys (Infused Alloy + Po de Diamante no Infuser).",
            "• &dUltimate Control Circuit (Tier 4):&r Circuito Elite + 2 Atomic Alloys (Reinforced Alloy + Obsidiana Refinada no Infuser)."
        ],
        "mekanism:ultimate_control_circuit", 10.0, -1.0, [0x03B0000000000090],
        [
            {"type": "item", "item": "mekanism:advanced_control_circuit", "count": 2},
            {"type": "item", "item": "mekanism:elite_control_circuit", "count": 1}
        ],
        [{"item": "mekanism:ultimate_control_circuit", "count": 1}, {"item": "mekanism:alloy_atomic", "count": 2}]
    ),
    make_quest(
        0x03B00000000000D0,
        "&610. Equipamentos Mekanism: Jetpack e Atomic Disassembler!",
        "Voe pelo mapa e minere tudo instantaneamente!",
        [
            "Recompense seu esforco industrial construindo os equipamentos lendarios do &bMekanism&r:",
            "• &6Jetpack:&r Voe livremente para explorar montanhas e santuarios!",
            "• &dAtomic Disassembler:&r A multitool definitiva de energia (Picareta + Pa + Machado + Espada com mineracao em veia!)."
        ],
        "mekanism:atomic_disassembler", 12.5, -1.0, [0x03B00000000000B0],
        [
            {"type": "item", "item": "mekanism:energy_tablet", "count": 2},
            {"type": "item", "item": "mekanism:atomic_disassembler", "count": 1}
        ],
        [{"item": "mekanism:jetpack", "count": 1}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x03B00000000000F0,
        "&811. Pasta Dieletrica e Pokebolas Tier 3 (Powah!)",
        "O isolante para Ultra Ball, Quick Ball, Dusk Ball e Timer Ball!",
        [
            "Entrando na &eEra 2 (Powah!)&r, aprenda a fazer &7Dielectric Paste (Pasta Dieletrica)&r com Carvao, Argila e Blaze Powder/Lava (rende 24 unidades por receita!).",
            "",
            "• &6Uso nas Pokebolas:&r Na Firma League, a Pasta Dieletrica (ou Aco Energizado / Brass Sheet / Infused Alloy) e o nucleo obrigatorio de &bTODAS as Pokebolas Tier 3 (Ultra Ball, Quick Ball, Dusk Ball, Timer Ball, Luxury Ball)&r!"
        ],
        "powah:dielectric_paste", 5.0, 2.5, [0x03B0000000000060],
        [{"type": "item", "item": "powah:dielectric_paste", "count": 24}],
        [{"item": "cobblemon:ultra_ball", "count": 15}, {"item": "cobblemon:quick_ball", "count": 10}]
    ),
    make_quest(
        0x03B0000000000110,
        "&b12. Orbe de Energizacao (Energizing Orb e Rod)",
        "Como montar o sintetizador da Grande Convergencia!",
        [
            "O &bEnergizing Orb&r e a maquina mais importante do modpack para criar itens de Mega Evolucao, Terastal e Competitivo!",
            "",
            "&eComo montar e usar (Passo a Passo):&r",
            "1. Construa o &bEnergizing Orb&r (Vidro + Ametista + Dielectric Casing + Circuito Basico do Mekanism) e coloque no chao.",
            "2. Construa pelo menos uma &eEnergizing Rod (Starter ou Basic)&r e coloque a ate 3 blocos de distancia do Orbe.",
            "3. Ligue a Energizing Rod a um &aPainel Solar (Solar Panel)&r, &cFurnator&r ou gerador do Mekanism usando cabos de energia!",
            "4. Quando colocar os ingredientes certos dentro do Orbe, a haste vai disparar um raio laser e sintetizar o item!"
        ],
        "powah:energizing_orb", 7.5, 2.5, [0x03B00000000000F0],
        [
            {"type": "item", "item": "powah:energizing_orb", "count": 1},
            {"type": "item", "item": "powah:energizing_rod_starter", "count": 1}
        ],
        [{"item": "powah:solar_panel_starter", "count": 2}, {"item": "powah:energy_cable_starter", "count": 8}],
        shape="hexagon", size=1.5
    ),
    make_quest(
        0x03B0000000000130,
        "&613. Aco Energizado e Cristal Blazing",
        "Energizando metais no Orbe",
        [
            "Coloque no seu &bEnergizing Orb&r:",
            "• &f1 Ferro + 1 Ouro (10.000 FE)&r -> Gera &62x Energized Steel (Aco Energizado)&r!",
            "• &c1 Blaze Rod ou 4 Blaze Powders (90.000 FE)&r -> Gera &61x Blazing Crystal&r!",
            "",
            "Eles sao usados para forjar sua &dMega Bracelet&r, &bTera Orb&r, &bFornalha de Diamante&r, &bMochila de Diamante&r e &cCircuito Avancado&r!"
        ],
        "powah:steel_energized", 10.0, 2.5, [0x03B0000000000110],
        [
            {"type": "item", "item": "powah:steel_energized", "count": 6},
            {"type": "item", "item": "powah:crystal_blazing", "count": 2}
        ],
        [{"item": "powah:energizing_rod_basic", "count": 1}, {"item": "powah:solar_panel_basic", "count": 1}]
    ),
    make_quest(
        0x03B0000000000150,
        "&b14. Fornalhas de Diamante e Netherhot",
        "Velocidade extrema com Cristais Energizados",
        [
            "Use seus &6Cristais Blazing&r e &bCristais Niotic&r para elevar sua Fornalha aos tiers de &bDiamante&r e &cNetherhot&r!"
        ],
        "betterfurnacesreforged:diamond_furnace", 10.0, 0.8, [0x03B0000000000070, 0x03B0000000000130],
        [{"type": "item", "item": "betterfurnacesreforged:diamond_furnace", "count": 1}],
        [{"item": "betterfurnacesreforged:factory_upgrade", "count": 1}]
    ),
    make_quest(
        0x03B0000000000170,
        "&a15. Sintetizacao Pokemon I: Link Cable e Upgrade",
        "Evolua Haunter, Kadabra, Machoke, Graveler e Porygon!",
        [
            "Use as receitas exclusivas da Firma no &bEnergizing Orb&r:",
            "• &aLink Cable (15.000 FE):&r 1 Cabo Universal Basico (Mekanism) + 1 Barra de Ouro + 1 Ender Pearl!",
            "• &bUpgrade (25.000 FE):&r 1 Circuito de Controle Basico + 1 Pistao + 1 Red Apricorn + 1 Blue Apricorn!"
        ],
        "cobblemon:link_cable", 7.5, 5.0, [0x03B0000000000110],
        [
            {"type": "item", "item": "cobblemon:link_cable", "count": 1},
            {"type": "item", "item": "cobblemon:upgrade", "count": 1}
        ],
        [{"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x03B0000000000190,
        "&d16. Sintetizacao Pokemon II: Keystone e Ability Capsule",
        "Crie sua propria pedra de Mega Evolucao no laboratorio!",
        [
            "Mais receitas exclusivas no &bEnergizing Orb&r:",
            "• &eAbility Capsule (50.000 FE):&r 1 Basic Capacitor + 1 Rare Candy + 1 Yellow Apricorn + 1 Pink Apricorn.",
            "• &dKeystone (100.000 FE):&r 1 Diamante + 1 Ametista + 1 Blazing Crystal + 1 Sun Stone + 1 Moon Stone!"
        ],
        "mega_showdown:keystone", 10.0, 5.0, [0x03B0000000000130, 0x03B0000000000170],
        [{"type": "item", "item": "cobblemon:ability_capsule", "count": 1}],
        [{"item": "mega_showdown:keystone", "count": 1}]
    ),
    make_quest(
        0x03B00000000001B0,
        "&917. Era 3 (Hoenn): Box Link — PC Portatil Quantico!",
        "Acesse seus Pokemon de qualquer lugar do mapa!",
        [
            "Com &cCircuito de Controle Avancado (Mekanism)&r + PC + Link Cable + Aco Energizado + Ender Pearl, construa o &dBox Link&r para acessar todos os seus Pokemon do PC de qualquer lugar do mundo (sem precisar ir ao End)!"
        ],
        "cobblemonboxlink:box_link", 12.5, 2.5, [0x03B0000000000130],
        [
            {"type": "item", "item": "mekanism:advanced_control_circuit", "count": 2},
            {"type": "item", "item": "cobblemonboxlink:box_link", "count": 1}
        ],
        [{"item": "powah:crystal_niotic", "count": 2}, {"item": "cobblemon:dubious_disc", "count": 1}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x03B00000000001D0,
        "&b18. Cristais Niotic, Spirited e Nitro (Alta Energia)",
        "Energizando Diamante, Esmeralda e Nether Star!",
        [
            "No &bEnergizing Orb&r:",
            "• &bNiotic Crystal (300.000 FE):&r 1 Diamante.",
            "• &aSpirited Crystal (1.000.000 FE):&r 1 Esmeralda.",
            "• &cNitro Crystal (2.000.000 FE):&r 1 Nether Star + 2 Redstone Blocks + 1 Blazing Crystal Block."
        ],
        "powah:crystal_spirited", 12.5, 5.0, [0x03B00000000001B0],
        [
            {"type": "item", "item": "powah:crystal_niotic", "count": 2},
            {"type": "item", "item": "powah:crystal_spirited", "count": 2}
        ],
        [{"item": "powah:energizing_rod_niotic", "count": 1}, {"item": "powah:solar_panel_niotic", "count": 1}]
    ),
    make_quest(
        0x03B00000000001F0,
        "&519. Era 4 (Sinnoh): Ability Patch, Golden Cap e Master Ball!",
        "O Apice da Engenharia Espaco-Tempo",
        [
            "Com os Cristais de Elite e Circuitos do Mekanism, voce domina o topo da cadeia tecnologica:",
            "• &5Ability Patch (150.000 FE no Orbe):&r Circuito de Controle Avancado + Cristal Niotic + Ability Capsule + Bloco de Ametista.",
            "• &6Golden Bottle Cap (200.000 FE no Orbe ou com as 6 Silver Caps):&r Deixa todos os 6 IVs de um Pokemon em 31!",
            "• &dMaster Ball:&r Cristal Nitro + Circuito de Controle Ultimate + Nether Star + Netherite + Shulker Shell + Pink e Black Apricorn!"
        ],
        "cobblemon:master_ball", 15.0, 3.7, [0x03B00000000001B0, 0x03B00000000001D0],
        [
            {"type": "item", "item": "cobblemon:ability_patch", "count": 1},
            {"type": "item", "item": "cobblemon_utility:goldencap", "count": 1}
        ],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "powah:crystal_nitro", "count": 2}],
        shape="gear", size=1.8
    )
]
write_chapter(0x03B0000000000001, GRP_TECH, 7, "03b_tecnologia_e_automacao", "&b2A. Engenharia Tech (Create, Mekanism e Powah)", "powah:energizing_orb", "rsquare", c3b_quests)


# ==============================================================================
# CAPÍTULO 3C: ARMAZENAMENTO DIGITAL (TOM'S + AE2), FAZENDAS AUTO & MOCHILAS (10 QUESTS!)
# ==============================================================================
c3c_quests = [
    make_quest(
        0x03C0000000000010,
        "&e1. Sua Primeira Mochila (Sophisticated Backpacks)",
        "Mais espaco para Pokebolas, Berries e Minerios!",
        [
            "Construa sua &eMochila Basica&r com Couro, Linha e 1 Bau!",
            "",
            "• Coloque ela no slot de costas (ou abra apertando a tecla &e[B]&r — configure facilmente no menu de controles com a busca do &bControlling&r!).",
            "• Importante: Quando for evoluir a mochila para Cobre/Ferro/Ouro/Diamante na bancada, ela mantem todos os itens e upgrades la dentro!"
        ],
        "sophisticatedbackpacks:backpack", 0.0, 0.0, None,
        [{"type": "item", "item": "sophisticatedbackpacks:backpack", "count": 1}],
        [{"item": "minecraft:leather", "count": 8}]
    ),
    make_quest(
        0x03C0000000000030,
        "&f2. Mochilas de Ferro e Ouro",
        "Evoluindo com Chapas de Ferro (Create) e Circuito Basico (Mekanism)",
        [
            "Seguindo a arvore tecnologica da Firma:",
            "• &fMochila de Ferro:&r Mochila Basica + Chapas de Ferro (Create) + 1 Apricorn.",
            "• &6Mochila de Ouro:&r Mochila de Ferro + Ouro + 1 Circuito de Controle Basico (Mekanism)."
        ],
        "sophisticatedbackpacks:gold_backpack", 2.5, 0.0, [0x03C0000000000010],
        [
            {"type": "item", "item": "sophisticatedbackpacks:iron_backpack", "count": 1},
            {"type": "item", "item": "sophisticatedbackpacks:gold_backpack", "count": 1}
        ],
        [{"item": "sophisticatedbackpacks:pickup_upgrade", "count": 1}]
    ),
    make_quest(
        0x03C0000000000050,
        "&b3. Mochilas de Diamante e Netherite + Upgrades",
        "Ima automatico, Auto-Feeding e Bancada portatil!",
        [
            "• &bMochila de Diamante:&r Usa Diamantes + &6Aco Energizado (Powah)&r!",
            "• &8Mochila de Netherite:&r Feita na Mesa de Ferraria (Smithing Table) com Barra de Netherite.",
            "• &aUpgrades de Mochila:&r Coloque &eMagnet Upgrade&r (puxa drops de longe), &eFeeding Upgrade&r (alimenta voce sozinho) e &eCrafting Upgrade&r!"
        ],
        "sophisticatedbackpacks:diamond_backpack", 5.0, 0.0, [0x03C0000000000030],
        [{"type": "item", "item": "sophisticatedbackpacks:diamond_backpack", "count": 1}],
        [{"item": "sophisticatedbackpacks:magnet_upgrade", "count": 1}, {"item": "sophisticatedbackpacks:feeding_upgrade", "count": 1}]
    ),
    make_quest(
        0x03C0000000000070,
        "&64. Baus por Nivel de Minerio (Sophisticated Storage)",
        "Evolua seus baus sem precisar quebrar!",
        [
            "Com os &eTier Upgrades&r do &6Sophisticated Storage&r, basta segurar o Upgrade na mao e clicar com o botao direito em um Bau ou Barril comum para transforma-lo em &fBau de Ferro&r, &6Ouro&r, &bDiamante&r ou &8Netherite&r!",
            "",
            "• &fUpgrade Ferro:&r Chapa de Ferro (Create) + Tocha de Redstone + Apricorn.",
            "• &6Upgrade Ouro:&r Ouro + Tocha de Redstone + Circuito Basico (Mekanism).",
            "• &bUpgrade Diamante:&r Diamante + Circuito Basico + Aco Energizado."
        ],
        "sophisticatedstorage:basic_to_iron_tier_upgrade", 0.0, 2.5, None,
        [
            {"type": "item", "item": "sophisticatedstorage:basic_to_iron_tier_upgrade", "count": 1},
            {"type": "item", "item": "sophisticatedstorage:iron_to_gold_tier_upgrade", "count": 1}
        ],
        [{"item": "sophisticatedstorage:gold_to_diamond_tier_upgrade", "count": 1}]
    ),
    make_quest(
        0x03C0000000000090,
        "&a5. Rede Inicial: Tom's Simple Storage",
        "Todos os seus baus conectados sem gastar energia!",
        [
            "Monte sua primeira central unificada no inicio do jogo:",
            "1. Coloque varios baus (do Sophisticated Storage) encostados uns nos outros.",
            "2. Coloque 1 &bInventory Connector&r encostado em qualquer um desses baus (ele le todos os baus adjacentes automaticamente!).",
            "3. Coloque o &eStorage Terminal&r em cima ou ao lado do Inventory Connector.",
            "4. Clique no Terminal para ver e pesquisar todos os itens de todos os baus de uma so vez!"
        ],
        "toms_storage:storage_terminal", 2.5, 2.5, [0x03C0000000000070],
        [
            {"type": "item", "item": "toms_storage:inventory_connector", "count": 1},
            {"type": "item", "item": "toms_storage:storage_terminal", "count": 1}
        ],
        [{"item": "toms_storage:inventory_cable", "count": 16}, {"item": "toms_storage:inventory_cable_connector", "count": 2}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x03C00000000000B0,
        "&b6. Crafting Terminal e Acesso Wireless (Tom's)",
        "Crie itens direto da rede de baus!",
        [
            "• &bCrafting Terminal:&r Evolua o seu Storage Terminal com Bancadas, Diamante, Circuito Basico e &6Aco Energizado&r para ter uma grade de Crafting 3x3 integrada ao EMI (clique no `[+]` do EMI para puxar os itens direto dos baus!).",
            "• &dWireless Terminal e Adv. Wireless Terminal:&r Acesse seu sistema de baus sem fio!"
        ],
        "toms_storage:crafting_terminal", 5.0, 2.5, [0x03C0000000000090],
        [{"type": "item", "item": "toms_storage:crafting_terminal", "count": 1}],
        [{"item": "toms_storage:wireless_terminal", "count": 1}],
        shape="octagon", size=1.5
    ),
    make_quest(
        0x03C00000000000D0,
        "&97. Applied Energistics 2 (AE2): Inscriber e Processadores",
        "O Computador Quantico de HDs Digitais!",
        [
            "Quer transformar milhares de itens em dados dentro de disquetes digitais? Entre no &9Applied Energistics 2 (AE2)&r:",
            "1. Encontre um &8Meteorito do AE2&r pelo mapa (use a bussola ou o mapa) para coletar as 4 &bInscriber Presses (Prensas de Silicio, Logica, Calculo e Engenharia)&r e Certus Quartz.",
            "2. Construa um &eCharger&r e um &9Inscriber&r para prensar Processadores Logicos, de Calculo e de Engenharia!",
            "• &bGuia Interativo AE2:&r Segure &e[G]&r em cima de qualquer item do AE2 para abrir o guia visual oficial dentro do jogo!"
        ],
        "ae2:inscriber", 2.5, 5.0, [0x03C0000000000090],
        [
            {"type": "item", "item": "ae2:charger", "count": 1},
            {"type": "item", "item": "ae2:inscriber", "count": 1}
        ],
        [{"item": "ae2:logic_processor", "count": 4}, {"item": "ae2:calculation_processor", "count": 4}, {"item": "ae2:engineering_processor", "count": 4}]
    ),
    make_quest(
        0x03C00000000000F0,
        "&d8. Supercomputador ME: Controller, ME Drive e Celula 16k!",
        "Armazenamento Digital e Autocrafting Ilimitado (AE2)",
        [
            "Monte o seu Supercomputador ME:",
            "• Conecte um &dME Controller&r (alimentado com energia do Mekanism/Powah), um &bME Drive&r e um &aME Crafting Terminal&r usando &9Fluix Glass Cables&r.",
            "• Insira &bME Item Storage Cells (1k, 4k, 16k, 64k)&r dentro do ME Drive para guardar centenas de milhares de itens em um unico bloco!"
        ],
        "ae2:controller", 5.0, 5.0, [0x03C00000000000D0],
        [
            {"type": "item", "item": "ae2:controller", "count": 1},
            {"type": "item", "item": "ae2:drive", "count": 1},
            {"type": "item", "item": "ae2:crafting_terminal", "count": 1}
        ],
        [{"item": "ae2:item_storage_cell_16k", "count": 1}, {"item": "ae2:fluix_glass_cable", "count": 16}],
        shape="hexagon", size=1.5
    ),
    make_quest(
        0x03C0000000000110,
        "&29. Fazendas Industriais: Industrial Foregoing!",
        "Colheita Automatica de Apricorns, Berries e Mints!",
        [
            "Com o &2Industrial Foregoing&r, voce automatiza a agricultura e a pecuaria da base:",
            "1. Extraia Latex de troncos de madeira usando o &eFluid Extractor&r e processe no &bLatex Processing Unit&r para fazer &fPlastic (Plastico)&r.",
            "2. Construa o &aPlant Sower (Plantador)&r e o &2Plant Gatherer (Colhedor)&r para colher plantacoes inteiras de &eApricorns, Berries e Mints&r automaticamente!"
        ],
        "industrialforegoing:plant_gatherer", 7.5, 2.5, [0x03C00000000000B0],
        [
            {"type": "item", "item": "industrialforegoing:machine_frame_pity", "count": 1},
            {"type": "item", "item": "industrialforegoing:plant_gatherer", "count": 1}
        ],
        [{"item": "industrialforegoing:plastic", "count": 16}, {"item": "industrialforegoing:plant_sower", "count": 1}],
        shape="hexagon", size=1.4
    )
]
write_chapter(0x03C0000000000001, GRP_TECH, 8, "03c_armazenamento_e_mochilas", "&a2B. Armazenamento (Tom's, AE2) e Mochilas", "ae2:controller", "rsquare", c3c_quests)


# ==============================================================================
# CAPÍTULO 2C: FÁBRICA POKÉMON (INTEGRAÇÃO TECH <-> COBBLEMON, ESTILO ALL THE MONS)
# ==============================================================================
c3d_quests = [
    make_quest(
        0x03D0000000000010,
        "&e1. Fazenda de Apricorns Automatica",
        "A materia-prima de toda Pokebola",
        [
            "Antes de montar a fabrica, garanta um fluxo constante de &eApricorns&r!",
            "• &6Create:&r Use um &eMechanical Harvester&r num trem/carrinho ou rolamento passando pelas arvores de Apricorn.",
            "• &2Industrial Foregoing:&r O &aPlant Gatherer&r colhe sozinho e manda tudo para os seus baus.",
            "",
            "&7Dica: Apricorns sobrando viram &aBio Fuel&7 no Crusher do Mekanism (4 por Apricorn)!"
        ],
        "cobblemon:red_apricorn", 0.0, 0.0, None,
        [
            {"type": "item", "item": "cobblemon:red_apricorn", "count": 64},
            {"type": "item", "item": "cobblemon:blue_apricorn", "count": 32}
        ],
        [{"item": "create:mechanical_harvester", "count": 2}]
    ),
    make_quest(
        0x03D0000000000020,
        "&c2. Linha de Montagem de Pokebolas (Create)",
        "Sequenced Assembly: 4 Pokebolas por ciclo!",
        [
            "Monte uma esteira (&eMechanical Belt&r) com &eDeployers&r e uma &ePrensa Mecanica&r:",
            "• &fPoke Ball:&r Chapa de Ferro -> Red Apricorn -> Botao de Pedra -> Prensa = &f4x&r",
            "• &9Great Ball:&r Chapa de Ferro -> Blue Apricorn -> Red Apricorn -> Botao -> Prensa = &f4x&r",
            "• &ePremier Ball:&r Chapa de Ferro -> 2 White Apricorn -> Botao -> Prensa = &f4x&r",
            "• &6Ultra Ball:&r Chapa de Latao -> Yellow Apricorn -> Black Apricorn -> Electron Tube -> Prensa = &f4x&r",
            "",
            "Use o &bEMI&r em qualquer Pokebola para ver a sequencia exata!"
        ],
        "create:deployer", 2.5, 0.0, [0x03D0000000000010],
        [{"type": "item", "item": "cobblemon:great_ball", "count": 16}],
        [{"item": "create:deployer", "count": 2}, {"item": "create:mechanical_press", "count": 1}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x03D0000000000030,
        "&b3. Ultra Balls em Massa",
        "Chapas de Latao + Electron Tubes",
        [
            "Automatize a linha de &6Ultra Balls&r com &6Chapas de Latao&r (Brass Sheet) e &bElectron Tubes&r para nunca mais faltar bola boa nas cacadas!"
        ],
        "cobblemon:ultra_ball", 5.0, 0.0, [0x03D0000000000020],
        [{"type": "item", "item": "cobblemon:ultra_ball", "count": 32}],
        [{"item": "cobblemon:dusk_ball", "count": 8}, {"item": "cobblemon:quick_ball", "count": 8}]
    ),
    make_quest(
        0x03D0000000000040,
        "&a4. Fabrica de Doces de EXP (Create Mixer)",
        "Experience Nuggets viram Exp. Candies!",
        [
            "Todo minerio passado na &eCrushing Wheel&r solta &aExperience Nuggets&r. Leve-os ao &eMixer + Basin&r com &cBlaze Burner&r:",
            "• &a4 Experience Nuggets + Acucar&r (aquecido) -> &fExp. Candy S&r",
            "• &f3 Exp. Candy S + Garrafa de Mel&r (aquecido) -> &eExp. Candy M&r",
            "• &e3 Exp. Candy M + Glow Berries&r (&csuperaquecido&r) -> &6Exp. Candy L&r",
            "• &62 Exp. Candy L + Maca Dourada&r (&csuperaquecido&r) -> &dRare Candy&r",
            "",
            "&7Superaquecer: alimente o Blaze Burner com Blaze Cake!"
        ],
        "cobblemon:exp_candy_m", 0.0, 2.5, [0x03D0000000000010],
        [{"type": "item", "item": "cobblemon:exp_candy_m", "count": 8}],
        [{"item": "create:blaze_burner", "count": 1}, {"item": "create:blaze_cake", "count": 2}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x03D0000000000050,
        "&d5. Vitaminas de EV no Mixer",
        "HP Up, Protein, Iron, Calcium, Zinc e Carbos",
        [
            "Base: &aMedicinal Leek + Acucar + 250mB de Agua&r no Mixer aquecido, mais 1 ingrediente:",
            "• &cHP Up:&r Cenoura Dourada | &cProtein:&r Carne Assada | &7Iron:&r Chapa de Ferro",
            "• &9Calcium:&r Bloco de Osso | &bZinc:&r Cristal de Prismarinho | &eCarbos:&r Cana-de-Acucar",
            "",
            "Treine os EVs da equipe inteira para a Firma League!"
        ],
        "cobblemon:protein", 2.5, 2.5, [0x03D0000000000040],
        [{"type": "item", "item": "cobblemon:hp_up", "count": 4}],
        [{"item": "cobblemon:protein", "count": 2}, {"item": "cobblemon:carbos", "count": 2}]
    ),
    make_quest(
        0x03D0000000000060,
        "&66. Pedras de Evolucao: Duplicacao de Minerio",
        "Crushing Wheel (Create) e Enrichment Chamber (Mekanism)",
        [
            "Nao quebre minerios de Pedras de Evolucao na picareta! Processe-os:",
            "• &6Crushing Wheel:&r 1 minerio -> 1 a 2 pedras + Experience Nugget",
            "• &bEnrichment Chamber:&r 1 minerio -> &a2 pedras&r garantidas",
            "",
            "Use &eSilk Touch&r para trazer o minerio inteiro para a base!",
            "&7Bonus: jogue Moon Stones num ventilador com Fogo de Alma (Haunting) para virar &8Dusk Stone&7!"
        ],
        "cobblemon:thunder_stone", 0.0, 5.0, None,
        [{"type": "item", "item": "mekanism:enrichment_chamber", "count": 1}],
        [{"item": "cobblemon:fire_stone", "count": 1}, {"item": "cobblemon:water_stone", "count": 1}, {"item": "cobblemon:thunder_stone", "count": 1}]
    ),
    make_quest(
        0x03D0000000000070,
        "&b7. Gemas de Tipo -> Pedras de Evolucao (Powah!)",
        "Energizing Orb: 2 Gemas + 1 Ametista (30.000 FE)",
        [
            "Transforme Gemas de Tipo em Pedras de Evolucao no &bEnergizing Orb&r:",
            "• &cFire Gem&r -> Fire Stone | &9Water Gem&r -> Water Stone | &eElectric Gem&r -> Thunder Stone",
            "• &aGrass Gem&r -> Leaf Stone | &bIce Gem&r -> Ice Stone | &dFairy Gem&r -> Moon Stone",
            "• &fNormal Gem&r -> Sun Stone | &5Psychic Gem&r -> Dawn Stone | &8Ghost Gem&r -> Dusk Stone",
            "• &6Dragon Gem&r -> &fShiny Stone&r"
        ],
        "cobblemon:shiny_stone", 2.5, 5.0, [0x03D0000000000060],
        [{"type": "item", "item": "cobblemon:shiny_stone", "count": 1}],
        [{"item": "powah:energizing_rod_basic", "count": 1}]
    ),
    make_quest(
        0x03D0000000000080,
        "&58. Itens de Evolucao por Troca (Metallurgic Infuser)",
        "Metal Coat, Dragon Scale, King's Rock, Electirizer...",
        [
            "Fabrique os itens de evolucao por troca no &5Metallurgic Infuser&r do Mekanism:",
            "• &7Metal Coat:&r Lingote de Aco + Redstone | &6King's Rock:&r Ouro + Diamante",
            "• &9Dragon Scale:&r Fragmento de Prismarinho + Diamante | &bPrism Scale:&r Cristal de Prismarinho + Diamante",
            "• &8Razor Claw:&r Silex + Diamante | &7Protector:&r Bloco de Ferro + Obsidiana Refinada",
            "• &eElectirizer:&r Liga Infundida + Redstone | &cMagmarizer:&r Creme de Magma + Carbono",
            "• &5Reaper Cloth:&r Membrana de Phantom + Fungos"
        ],
        "cobblemon:metal_coat", 5.0, 5.0, [0x03D0000000000060],
        [
            {"type": "item", "item": "cobblemon:metal_coat", "count": 1},
            {"type": "item", "item": "cobblemon:dragon_scale", "count": 1}
        ],
        [{"item": "cobblemon:link_cable", "count": 2}],
        shape="hexagon", size=1.4
    )
]
write_chapter(0x03D0000000000001, GRP_TECH, 9, "03d_fabrica_pokemon", "&e2C. Fabrica Pokemon (Tech + Cobblemon)", "create:deployer", "rsquare", c3d_quests)


# ==============================================================================
# CAPÍTULO 3: MEGA EVOLUÇÃO, TERASTAL & TREINO COMPETITIVO (6 QUESTS COM ITENS REAIS!)
# ==============================================================================
c3_quests = [
    make_quest(
        0x0300000000000010,
        "&d1. Forjando a Mega Bracelet!",
        "Liberada em todas as temporadas!",
        [
            "Com &6Aco Energizado (Powah)&r, &bDiamante&r, &fWhite Apricorn&r, &aCircuito de Controle Basico (Mekanism)&r e uma &dKeystone&r (minerada ou sintetizada no Energizing Orb), construa a sua &dMega Bracelet&r!",
            "",
            "• Equipe a Mega Stone correspondente no seu Pokemon (ex.: Charizardite X/Y, Gengarite, Lucarionite) e clique no botao de &dMega Evolucao&r durante a batalha!"
        ],
        "mega_showdown:mega_bracelet", 0.0, 0.0, None,
        [{"type": "item", "item": "mega_showdown:mega_bracelet", "count": 1}],
        [{"item": "cobblemon:rare_candy", "count": 5}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x0300000000000030,
        "&b2. O Orbe Terastal (Tera Orb)",
        "Mude a tipagem defensiva ou ofensiva do seu Pokemon!",
        [
            "Construa seu &bTera Orb&r usando Ametista, Ender Pearl, Diamante, Circuito de Controle Basico (Mekanism) e &6Blazing Crystal&r!",
            "",
            "• Na &6Firma League&r, voce pode usar &e1 Mega Evolucao e/ou 1 Terastal&r por partida! Use Tera Shards para mudar o Tera Type do seu Pokemon."
        ],
        "mega_showdown:tera_orb", 2.5, 0.0, [0x0300000000000010],
        [{"type": "item", "item": "mega_showdown:tera_orb", "count": 1}],
        [{"item": "cobblemon:rare_candy", "count": 5}],
        shape="hexagon", size=1.4
    ),
    make_quest(
        0x0300000000000050,
        "&e3. Z-Power Ring e Dynamax Band (PvE / Extras)",
        "Colecione os artefatos de Z-Move e Dynamax",
        [
            "Com Aco Energizado e Circuito de Controle Basico, construa o &eZ-Power Ring&r e a &cDynamax Band&r para usar contra Bosses e preparar a fusao do Omni Ring!"
        ],
        "mega_showdown:dynamax_band", 5.0, 0.0, [0x0300000000000030],
        [
            {"type": "item", "item": "mega_showdown:z_power_ring", "count": 1},
            {"type": "item", "item": "mega_showdown:dynamax_band", "count": 1}
        ],
        [{"item": "cobblemon:exp_candy_l", "count": 5}]
    ),
    make_quest(
        0x0300000000000060,
        "&6&l4. O Artefato Supremo: Omni Ring (4 em 1)!",
        "Mega Evolucao + Terastal + Z-Move + Dynamax em um unico anel!",
        [
            "Funda os 4 artefatos do &dMega Showdown&r em uma unica reliquia definitiva!",
            "",
            "&eReceita Exclusiva da Firma (Mesa de Trabalho):&r",
            "• &d1x Mega Bracelet&r + &e1x Z-Power Ring&r + &c1x Dynamax Band&r + &b1x Tera Orb&r",
            "• &81x Barra de Netherite&r no nucleo",
            "• &b2x Elite Control Circuits (Mekanism)&r + &b2x Niotic Crystals (Powah!)&r",
            "",
            "Com o &6Omni Ring&r equipado no slot de acessorio, voce nunca mais precisara trocar de pulseira!"
        ],
        "mega_showdown:omni_ring", 7.5, 0.0, [0x0300000000000010, 0x0300000000000030, 0x0300000000000050],
        [{"type": "item", "item": "mega_showdown:omni_ring", "count": 1}],
        [{"item": "cobblemon:rare_candy", "count": 10}, {"item": "cobblemon:ability_patch", "count": 1}],
        shape="gear", size=1.6
    ),
    make_quest(
        0x0300000000000070,
        "&a5. Natures Perfeitas: Plantando Mints!",
        "Adamant, Jolly, Modest, Timid...",
        [
            "A &aNature&r aumenta um atributo do seu Pokemon em &a+10%&r e reduz outro em &c-10%&r:",
            "• &cAdamant&r (+Atk, -SpA) | &eJolly&r (+Spe, -SpA) para atacantes fisicos.",
            "• &9Modest&r (+SpA, -Atk) | &bTimid&r (+Spe, -Atk) para atacantes especiais.",
            "• Colha folhas de Mint (Red, Blue, Cyan, Pink, Green, White) e use uma &aMint&r no seu Pokemon!"
        ],
        "cobblemon:adamant_mint", 0.0, 2.5, None,
        [{"type": "advancement", "advancement": "cobblemon:agriculture/use_mint", "title": "Use uma Mint para ajustar a Nature de um Pokemon!"}],
        [{"item": "cobblemon:jolly_mint", "count": 1}, {"item": "cobblemon:timid_mint", "count": 1}]
    ),
    make_quest(
        0x0300000000000090,
        "&b6. Habilidades e Hidden Ability (Capsule e Patch)",
        "Libere o potencial oculto da sua equipe",
        [
            "• &bAbility Capsule:&r Troca entre a Habilidade 1 e Habilidade 2 normal do Pokemon (pode ser feita no Energizing Orb com 50.000 FE!).",
            "• &dAbility Patch:&r Libera a &6Hidden Ability (Habilidade Oculta)&r rara do Pokemon (feita no Energizing Orb com 150.000 FE!)."
        ],
        "cobblemon:ability_patch", 2.5, 2.5, [0x0300000000000070],
        [{"type": "item", "item": "cobblemon:ability_capsule", "count": 1}],
        [{"item": "cobblemon:choice_scarf", "count": 1}]
    ),
    make_quest(
        0x03000000000000B0,
        "&67. Perfeicao de IVs: Silver e Golden Bottle Caps!",
        "Engenharia Genetica da Firma (IVs 31)",
        [
            "Com Chapa de Ferro (Create), Aco Energizado (Powah), Circuito Basico (Mekanism), Diamante e Mint Leaf, forje &7Silver Bottle Caps&r (maximiza 1 IV para 31) ou a suprema &6Golden Bottle Cap&r (maximiza todos os 6 IVs para 31 de uma vez!)!"
        ],
        "cobblemon_utility:goldencap", 5.0, 2.5, [0x0300000000000090],
        [{"type": "item", "item": "cobblemon_utility:goldencap", "count": 1}],
        [{"item": "cobblemon:assault_vest", "count": 1}, {"item": "cobblemon:life_orb", "count": 1}],
        shape="octagon", size=1.5
    )
]
write_chapter(0x0300000000000001, GRP_LIGA, 10, "03_equipes_vilas_e_megas", "&d3A. Megas, Terastal e Treino IV/EV", "mega_showdown:mega_bracelet", "rsquare", c3_quests)


# ==============================================================================
# CAPÍTULO 4: ESTRUTURAS DA HISTÓRIA & LENDÁRIOS (BLOQUEADOS POR REGIÃO!)
# ==============================================================================
SINNOH_CHAMP_ID = 0x02400000000000C0

c4_quests = [
    make_quest(
        0x0400000000000010,
        "&cLendarios de Kanto: Aves Lendarias e Templo de Mew",
        "Power Plant (Zapdos), Seafoam (Articuno), Volcano (Moltres) e Jungle Temple",
        [
            "Use sua &6Explorer's Compass&r para localizar os Santuarios Lendarios de Kanto:",
            "• &ePower Plant:&r Zapdos",
            "• &bCaverna Glacial:&r Articuno",
            "• &cVulcao:&r Moltres",
            "• &dOvergrown Temple (Selva):&r Mew e Mewtwo!",
            "",
            "&cRequisito:&r Ter derrotado a 4a Insignia de Kanto (Erika) e trazer 10 Ultra Balls para a expedicao!"
        ],
        "cobblemon:ultra_ball", 0.0, 0.0, [0x0200000000000040],
        [{"type": "item", "item": "cobblemon:ultra_ball", "count": 10}],
        [{"item": "cobblemon:timer_ball", "count": 15}, {"item": "cobblemon:dusk_ball", "count": 15}]
    ),
    make_quest(
        0x0400000000000030,
        "&eLendarios de Johto: Burned Tower, Bell Tower e Whirl Islands",
        "Raikou, Entei, Suicune, Ho-Oh, Lugia e Celebi (BLOQUEADO ate zerar Kanto!)",
        [
            "Apos vencer o &6Campeao de Kanto&r, explore os Santuarios Lendarios de Johto:",
            "• &cBurned Tower:&r Raikou, Entei e Suicune",
            "• &6Bell Tower:&r Ho-Oh",
            "• &9Whirl Islands:&r Lugia",
            "• &aIlex Shrine:&r Celebi"
        ],
        "cobblemon:heavy_ball", 2.5, 0.0, [KANTO_CHAMP_ID],
        [{"type": "item", "item": "cobblemon:heavy_ball", "count": 10}],
        [{"item": "cobblemon:max_revive", "count": 5}, {"item": "cobblemon:fast_ball", "count": 15}]
    ),
    make_quest(
        0x0400000000000050,
        "&aLendarios de Hoenn: Sky Pillar, Regi Temples e Meteorito",
        "Groudon, Kyogre, Rayquaza, Regis, Latios/Latias, Jirachi e Deoxys",
        [
            "Apos concluir &eJohto&r, desbrave as estruturas lendarias de Hoenn:",
            "• &cGroudon Volcano&r e &9Kyogre Dome&r",
            "• &2Sky Pillar (Rayquaza)&r",
            "• &7Titan Temples (Regirock, Regice, Registeel)&r",
            "• &dSecret Garden (Latias e Latios)&r, &eWish Cave (Jirachi)&r e &5Deoxys Meteorite&r!"
        ],
        "cobblemon:timer_ball", 5.0, 0.0, [JOHTO_CHAMP_ID],
        [{"type": "item", "item": "cobblemon:timer_ball", "count": 15}],
        [{"item": "cobblemon:cherish_ball", "count": 5}, {"item": "cobblemon:rare_candy", "count": 10}]
    ),
    make_quest(
        0x0400000000000070,
        "&dLendarios de Sinnoh: Os 3 Lagos, Spear Pillar e Hall of Origin",
        "Uxie, Mesprit, Azelf, Dialga, Palkia, Giratina, Darkrai e Arceus!",
        [
            "Apos vencer &bSteven Stone em Hoenn&r, enfrente o panteao mitologico de Sinnoh:",
            "• &bLake Verity, Lake Valor e Lake Acuity&r (Mesprit, Azelf e Uxie)",
            "• &8Turnback Cave e Distortion World&r (Giratina)",
            "• &9Spear Pillar e Hall of Origin&r (Dialga, Palkia e Arceus!)"
        ],
        "cobblemon:master_ball", 7.5, 0.0, [HOENN_CHAMP_ID],
        [{"type": "item", "item": "cobblemon:dusk_ball", "count": 20}],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "cobblemon:cherish_ball", "count": 5}],
        shape="octagon", size=1.5
    )
]
write_chapter(0x0400000000000001, GRP_HISTORIA, 11, "04_lendarios_e_miticos", "&54. Estruturas e Lendarios", "cobblemon:cherish_ball", "hexagon", c4_quests)


# ==============================================================================
# CAPÍTULO 5: A FIRMA LEAGUE (TORNEIOS PVP BLOQUEADOS POR TEMPORADA!)
# ==============================================================================
c5_quests = [
    make_quest(
        0x0500000000000010,
        "&eRegras Oficiais da Firma League (Times Livres!)",
        "Multitype 6v6 Singles | Mega e Terastal Liberados!",
        [
            "Bem-vindo ao painel oficial da &6Firma League&r!",
            "",
            "• &aComposicao Livre (Sem Monotype):&r Monte o time mais equilibrado e criativo combinando qualquer tipo!",
            "• &dGimmicks Liberadas:&r 1 Mega Evolucao e/ou 1 Terastal por partida desde a 1a Temporada!",
            "• &eClausulas Showdown:&r Species Clause (sem repetir especie), Sleep Clause (max 1 dormindo), OHKO Clause, Evasion Clause e proibido usar pocoes da mochila na luta (apenas Held Items!)."
        ],
        "cobblemon:luxury_ball", 0.0, 0.0, None,
        [{"type": "checkmark", "title": "Li e concordo com as Regras da Firma League!"}],
        [{"item": "cobblemon:luxury_ball", "count": 10}],
        shape="pentagon", size=1.4
    ),
    make_quest(
        0x0500000000000030,
        "&61o Torneio Oficial: Copa Kanto",
        "BLOQUEADO ate vencer o Campeao de Kanto na Historia!",
        [
            "Quando voce derrota o &6Campeao de Kanto&r no Capitulo 2, sua vaga na &6Copa Kanto da Firma&r e liberada!",
            "",
            "Dispute a chave com seus amigos na Arena da Liga para coroar o 1o Campeao Regional da Firma!"
        ],
        "cobblemonpokemonbadges:earth_badge", 2.5, -1.5, [0x0500000000000010, KANTO_CHAMP_ID],
        [{"type": "checkmark", "title": "Disputei a Copa Kanto da Firma League!"}],
        [{"item": "cobblemon:choice_band", "count": 1}, {"item": "cobblemon:choice_specs", "count": 1}]
    ),
    make_quest(
        0x0500000000000050,
        "&e2o Torneio Oficial: Copa Johto",
        "BLOQUEADO ate concluir a Temporada 2 (Johto)!",
        [
            "Apos vencer Lance e Red em Johto, dispute a &eCopa Johto da Firma&r com seus novos Pokemon!"
        ],
        "cobblemonpokemonbadges:rising_badge", 2.5, 1.5, [0x0500000000000010, JOHTO_CHAMP_ID],
        [{"type": "checkmark", "title": "Disputei a Copa Johto da Firma League!"}],
        [{"item": "cobblemon:focus_sash", "count": 2}, {"item": "cobblemon:heavy_duty_boots", "count": 1}]
    ),
    make_quest(
        0x0500000000000070,
        "&a3o Torneio Oficial: Copa Hoenn",
        "BLOQUEADO ate derrotar o Campeao Steven em Hoenn!",
        [
            "Apos derrotar Steven Stone em Hoenn, entre na Arena para a &aCopa Hoenn da Firma&r!"
        ],
        "cobblemonpokemonbadges:rain_badge", 5.0, 0.0, [0x0500000000000030, 0x0500000000000050, HOENN_CHAMP_ID],
        [{"type": "checkmark", "title": "Disputei a Copa Hoenn da Firma League!"}],
        [{"item": "cobblemon_utility:goldencap", "count": 1}]
    ),
    make_quest(
        0x0500000000000090,
        "&6&lA GRANDE LIGA MUNDIAL E COPA UBERS!",
        "BLOQUEADO ate derrotar a Campea Cynthia em Sinnoh!",
        [
            "O torneio supremo do servidor apos todos zerarem as 4 Regioes!",
            "• &6Chave Principal:&r 6v6 OU/National Dex (Sem Lendarios Restritos).",
            "• &5Copa Ubers:&r Vale-tudo liberando Mewtwo, Rayquaza, Groudon, Kyogre, Dialga, Palkia, Giratina e Arceus!"
        ],
        "cobblemon:master_ball", 7.5, 0.0, [0x0500000000000070, SINNOH_CHAMP_ID],
        [{"type": "checkmark", "title": "Disputei a Grande Final Mundial da Firma League!"}],
        [{"item": "cobblemon:master_ball", "count": 1}, {"item": "cobblemon_utility:shinycard", "count": 1}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0500000000000001, GRP_LIGA, 12, "05_liga_dos_amigos", "&c5. A Firma League (Torneios PvP)", "cobblemon:luxury_ball", "pentagon", c5_quests)


# ==============================================================================
# CAPÍTULO 6: EXPLORAÇÃO, RAIDS E TESOUROS (SESSOES CURTAS, QUESTS INDEPENDENTES)
# ==============================================================================
c6_quests = [
    make_quest(
        0x0600000000000010,
        "&2O Mapa da Convergencia",
        "Explorar tem recompensa de verdade",
        [
            "Nem tudo se resolve na fabrica! Estruturas, tocas de raid e ruinas lendarias escondem itens que as maquinas NAO produzem:",
            "• &dKeystones&r, &6Wishing Stars&r e &eSparkling Stones&r (Megas, Z-Moves, Dynamax)",
            "• &bTera Shards&r, &aRare Candies&r, vitaminas, pedras de evolucao e itens de batalha",
            "• Com sorte, &dMega Stones&r e &eZ-Crystals&r prontos e ate uma &5Master Ball&r!",
            "",
            "&eComo achar:&r use a &6Explorer's Compass&r para estruturas e a &aNature's Compass&r para biomas.",
            "",
            "&7Sem pressa: uma sessao curta de 30 a 40 minutos ja costuma render algo bom. As quests abaixo sao independentes, faca na ordem que der!&r"
        ],
        "explorerscompass:explorerscompass", 0.0, 0.0, None,
        [{"type": "checkmark", "title": "Entendi: explorar rende itens exclusivos!"}],
        [{"item": "cobblemon:exp_candy_m", "count": 5}],
        shape="hexagon", size=1.5
    ),
    make_quest(
        0x0600000000000020,
        "&bMarque seu Territorio (Waystones)",
        "Viagem rapida para voltar a base",
        [
            "Coloque uma &bWaystone&r na sua base e outra em cada lugar importante que descobrir (ginasios, vilas, tocas de raid).",
            "Assim voce explora longe e volta em segundos, o que ajuda muito quando o tempo de jogo e curto!"
        ],
        "waystones:waystone", 2.5, -1.5, [0x0600000000000010],
        [{"type": "item", "item": "waystones:waystone", "count": 1}],
        [{"item": "cobblemon:rare_candy", "count": 2}, {"item": "cobblemon:great_ball", "count": 10}]
    ),
    make_quest(
        0x0600000000000030,
        "&6Baus So Seus (Lootr)",
        "Cada jogador abre o proprio loot",
        [
            "Nos baus de estruturas, o &6Lootr&r da a cada jogador o seu proprio conteudo: ninguem esvazia o bau dos amigos!",
            "",
            "Abra baus de masmorras, templos, minas e navios naufragados. Cerca de &a1 em cada 3 baus&r traz um item extra de Pokemon, e estruturas mais dificeis dao chances maiores."
        ],
        "minecraft:chest", 2.5, 1.5, [0x0600000000000010],
        [{"type": "checkmark", "title": "Abri baus de estruturas e peguei meu loot!"}],
        [{"item": "cobblemon:exp_candy_l", "count": 3}]
    ),
    make_quest(
        0x0600000000000040,
        "&dCacador de Keystone",
        "A pedra-chave das Megas",
        [
            "A &dKeystone&r e a base da Mega Bracelet e de varios aneis. Ela pode aparecer em &dbaus de estruturas medias e dificeis&r e tambem em minerios nos meteoritos do Mega Showdown.",
            "",
            "Traga uma Keystone para sua base!"
        ],
        "mega_showdown:keystone", 5.0, 1.5, [0x0600000000000030],
        [{"type": "item", "item": "mega_showdown:keystone", "count": 1}],
        [{"item": "cobblemon:exp_candy_xl", "count": 2}, {"item": "cobblemon:rare_candy", "count": 3}]
    ),
    make_quest(
        0x0600000000000050,
        "&9Meteorito do AE2",
        "Sky Stone e Certus Quartz",
        [
            "Procure um &9Meteorito do AE2&r pelo mapa (a Explorer's Compass ajuda). Dentro dele ha &8Sky Stone&r e &bCertus Quartz&r, a base de todo o sistema de armazenamento digital!"
        ],
        "ae2:sky_stone_block", 5.0, -1.5, [0x0600000000000020],
        [
            {"type": "item", "item": "ae2:sky_stone_block", "count": 4},
            {"type": "item", "item": "ae2:certus_quartz_crystal", "count": 4}
        ],
        [{"item": "ae2:charged_certus_quartz_crystal", "count": 2}]
    ),
    make_quest(
        0x0600000000000060,
        "&cSua Primeira Raid Den",
        "Hora de enfrentar um Pokemon gigante em grupo",
        [
            "Encontre uma &cRaid Den&r e participe de uma raid. Voce pode ir sozinho, mas com amigos fica bem mais facil!",
            "",
            "Quem completa raids ganha &6Raid Shards&r e recompensas extras."
        ],
        "cobblemonraiddens:raid_pouch", 7.5, 0.0, [0x0600000000000010],
        [{"type": "advancement", "advancement": "cobblemonraiddens:join_raid", "title": "Participe de uma Raid!"}],
        [{"item": "cobblemon:rare_candy", "count": 3}, {"item": "cobblemon:ultra_ball", "count": 10}]
    ),
    make_quest(
        0x0600000000000070,
        "&6Raid Tier 3",
        "Chame os amigos",
        [
            "Derrote uma raid de &6Tier 3&r. Monte um time equilibrado e use os &bCheers&r (apoio) durante a batalha!"
        ],
        "cobblemonraiddens:cheer_attack", 10.0, 0.0, [0x0600000000000060],
        [{"type": "advancement", "advancement": "cobblemonraiddens:tier_three", "title": "Conclua uma Raid de Tier 3!"}],
        [{"item": "cobblemon:rare_candy", "count": 5}, {"item": "cobblemon:ability_capsule", "count": 1}]
    ),
    make_quest(
        0x0600000000000080,
        "&dRaid Tier 5",
        "Desafio serio",
        [
            "Uma raid de &dTier 5&r pede estrategia: tipos certos, itens de batalha e cura em dia!"
        ],
        "cobblemonraiddens:cheer_defense", 12.5, 0.0, [0x0600000000000070],
        [{"type": "advancement", "advancement": "cobblemonraiddens:tier_five", "title": "Conclua uma Raid de Tier 5!"}],
        [{"item": "cobblemon:ability_patch", "count": 1}, {"item": "cobblemon:exp_candy_xl", "count": 3}]
    ),
    make_quest(
        0x0600000000000090,
        "&5&lRaid Mestre: Tier 7",
        "O maior desafio das Raid Dens",
        [
            "Reuna o grupo todo da Firma e derrote uma raid de &5Tier 7&r!",
            "",
            "As melhores recompensas do pack caem aqui."
        ],
        "cobblemonraiddens:raid_crystal_block", 15.0, 0.0, [0x0600000000000080],
        [{"type": "advancement", "advancement": "cobblemonraiddens:tier_seven", "title": "Conclua uma Raid de Tier 7!"}],
        [{"item": "cobblemon:ability_patch", "count": 2}, {"item": "cobblemon:exp_candy_xl", "count": 5}],
        shape="gear", size=1.7
    ),
    make_quest(
        0x06000000000000A0,
        "&eRuinas Lendarias",
        "Estruturas com Pokemon miticos",
        [
            "Visite uma estrutura lendaria e descubra o seu segredo. Use a Explorer's Compass e leve Pokebolas fortes e bastante cura!"
        ],
        "cobblemon:ultra_ball", 7.5, 3.0, [0x0600000000000040],
        [{"type": "advancement", "advancement": "legends_untold:find_legendary", "title": "Encontre um Pokemon lendario!"}],
        [{"item": "cobblemon:rare_candy", "count": 5}, {"item": "cobblemon:max_revive", "count": 3}]
    ),
    make_quest(
        0x06000000000000B0,
        "&bTera Dens",
        "Cavernas de cristal Tera",
        [
            "As &bTera Dens&r guardam baus com itens raros e cristais Tera. Encontre uma e abra o seu bau!"
        ],
        "mega_showdown:fire_tera_shard", 10.0, 3.0, [0x06000000000000A0],
        [{"type": "advancement", "advancement": "legends_untold:tera_dens", "title": "Descubra uma Tera Den!"}],
        [{"item": "cobblemon:exp_candy_xl", "count": 3}]
    ),
    make_quest(
        0x06000000000000C0,
        "&3Pilar do Ceu",
        "Onde Rayquaza descansa",
        [
            "No alto do &3Pilar do Ceu&r mora o dragao do ceu. Prepare uma equipe forte antes de subir!"
        ],
        "cobblemon:dragon_gem", 12.5, 3.0, [0x06000000000000B0],
        [{"type": "advancement", "advancement": "legends_untold:sky_pillar", "title": "Chegue ao Pilar do Ceu!"}],
        [{"item": "cobblemon:ability_patch", "count": 1}, {"item": "cobblemon:rare_candy", "count": 5}]
    ),
    make_quest(
        0x06000000000000E0,
        "&eO Boneco de Treino (Dummy)",
        "Teste o dano da sua equipe e armas",
        [
            "Para montar a melhor estrategia na Liga ou vencer os lideres de ginasio mais dificeis, voce precisa entender o dano real dos seus ataques!",
            "",
            "O &eBoneco de Treino (Target Dummy)&r pode ser equipado com armaduras completas para simular oponentes reais. Quando atacado, ele exibe numeros flutuantes de dano e mede o seu DPS (dano por segundo)!",
            "",
            "&7Dica:&r Coloque um Dummy na sua base ou arena de treino. Ele e facil de criar usando apenas 1 Fardo de Feno e 1 Suporte de Armaduras."
        ],
        "dummmmmmy:target_dummy", 2.5, -3.0, [0x0600000000000010],
        [{"type": "item", "item": "dummmmmmy:target_dummy", "count": 1}],
        [{"item": "cobblemon:exp_candy_m", "count": 5}, {"item": "cobblemon:rare_candy", "count": 2}]
    ),
    make_quest(
        0x06000000000000F0,
        "&cMasmorras e Tavernas",
        "Ruinas e fortalezas da Convergencia",
        [
            "Grandes masmorras, criptas, fortalezas abandonadas e tavernas surgiram pelo relevo.",
            "",
            "Essas estruturas guardam salas secretas e baus valiosos contendo itens raros de Pokemon (Tera Shards, Vitaminas, Mega Stones e Z-Crystals)!",
            "",
            "&aProtecao Estrutural:&r O pack usa o mod &bSparse Structures&r para garantir que nenhuma dungeon sobreponha ou quebre as vilas pacificas do Cobblemon e seus Poke Centers."
        ],
        "minecraft:chiseled_stone_bricks", 5.0, -3.0, [0x0600000000000010],
        [{"type": "checkmark", "title": "Explorei uma Masmorra ou Taverna!"}],
        [{"item": "cobblemon:exp_candy_l", "count": 3}, {"item": "cobblemon:great_ball", "count": 5}]
    ),
    make_quest(
        0x0600000000000100,
        "&6Reliquias Esquecidas (Artifacts)",
        "Poderes passivos para exploradores",
        [
            "Em acampamentos subterraneos abandonados e baus de estruturas repousam as &6Reliquias Ancestrais&r (Artifacts).",
            "",
            "Itens como &eEverlasting Beef&r (comida infinita), &bBunny Hoppers&r (salto duplo e imunidade a queda), &fCloud in a Bottle&r e &cPower Glove&r concedem efeitos passivos incriveis para sua jornada!",
            "",
            "Encontre ou resgate qualquer reliquia para completar este desafio."
        ],
        "artifacts:everlasting_beef", 7.5, -3.0, [0x06000000000000F0],
        [{"type": "checkmark", "title": "Encontrei uma Reliquia Ancestral!"}],
        [{"item": "cobblemon:rare_candy", "count": 3}, {"item": "cobblemon:ultra_ball", "count": 5}]
    ),
    make_quest(
        0x0600000000000110,
        "&5Arsenal da Convergencia (Simply Swords)",
        "Armas lendarias e tecnicas unicas",
        [
            "Para se defender dos perigos das masmorras e testar golpes no Dummy, forje armas especializadas do &5Simply Swords&r: Claymores, Twinblades, Chakrams, Rapieiras e Foices!",
            "",
            "Nos baus de masmorras medias e avancadas, voce pode encontrar a cobicada &dTabua Runica (Runic Tablet)&r, usada na Forja Runica para despertar habilidades especiais em combate."
        ],
        "simplyswords:runic_tablet", 10.0, -3.0, [0x0600000000000100],
        [{"type": "item", "item": "simplyswords:runic_tablet", "count": 1}],
        [{"item": "cobblemon:ability_capsule", "count": 1}, {"item": "cobblemon:exp_candy_xl", "count": 2}]
    ),
    make_quest(
        0x06000000000000D0,
        "&6&lExplorador da Firma",
        "Voce dominou as terras da Convergencia!",
        [
            "Raids vencidas, masmorras exploradas e ruinas lendarias visitadas: voce e um verdadeiro explorador!",
            "",
            "A Firma reconhece o seu esforco."
        ],
        "cobblemon:master_ball", 17.5, 1.5, [0x0600000000000090, 0x06000000000000C0, 0x0600000000000110],
        [{"type": "checkmark", "title": "Sou um Explorador da Firma!"}],
        [{"item": "cobblemon:rare_candy", "count": 10}, {"item": "cobblemon:ability_patch", "count": 1}, {"item": "cobblemon:exp_candy_xl", "count": 5}],
        shape="gear", size=2.0
    )
]
write_chapter(0x0600000000000001, GRP_HISTORIA, 13, "06_exploracao_e_raids", "&2Exploracao e Raids", "explorerscompass:explorerscompass", "rsquare", c6_quests)


# ==============================================================================
# INDEX.SNBT & ARQUIVOS DE IDIOMA (en_us.snbt e pt_br.snbt)
# ==============================================================================
with open(os.path.join(CHAPTERS_DIR, "index.snbt"), "w", encoding="utf-8") as f:
    f.write("{\n\tdefault_A: [\n")
    for ch in [
        "00_lore_da_firma",
        "00_guia_iniciante_pokemon",
        "01_inicio_jornada",
        "02_ginasios_historia",
        "02b_temporada_2_johto",
        "02c_temporada_3_hoenn",
        "02d_temporada_4_sinnoh",
        "03b_tecnologia_e_automacao",
        "03c_armazenamento_e_mochilas",
        "03d_fabrica_pokemon",
        "03_equipes_vilas_e_megas",
        "04_lendarios_e_miticos",
        "05_liga_dos_amigos",
        "06_exploracao_e_raids"
    ]:
        f.write(f'\t\t"{ch}"\n')
    f.write("\t]\n}\n")

# Gera lang/en_us.snbt e lang/pt_br.snbt no formato oficial do FTB Quests 1.21.1
lang_lines = ["{"]
for k in sorted(translations.keys()):
    val = translations[k]
    if isinstance(val, list):
        lang_lines.append(f"\t{k}: [")
        for line in val:
            lang_lines.append(f"\t\t{snbt_str(line)}")
        lang_lines.append("\t]")
    else:
        lang_lines.append(f"\t{k}: {snbt_str(val)}")
lang_lines.append("}")
lang_content = "\n".join(lang_lines) + "\n"

for locale in ["en_us", "pt_br"]:
    with open(os.path.join(LANG_DIR, f"{locale}.snbt"), "w", encoding="utf-8") as f:
        f.write(lang_content)

# Sincroniza com build_temp/overrides/config/ftbquests e build_neoforge/overrides/config
dst_ftb = os.path.join(BASE_DIR, "build_temp", "overrides", "config", "ftbquests")
if os.path.exists(dst_ftb):
    shutil.rmtree(dst_ftb)
shutil.copytree(os.path.join(BASE_DIR, "config", "ftbquests"), dst_ftb)

dst_neoforge_cfg = os.path.join(BASE_DIR, "build_neoforge", "overrides", "config")
if os.path.exists(dst_neoforge_cfg):
    shutil.rmtree(dst_neoforge_cfg)
shutil.copytree(os.path.join(BASE_DIR, "config"), dst_neoforge_cfg)

print(f"Sucesso! Gerados 14 capitulos com {sum(1 for k in translations if k.startswith('quest.') and k.endswith('.title'))} quests e tabelas de traducao en_us/pt_br (sincronizado com build_neoforge)!")
