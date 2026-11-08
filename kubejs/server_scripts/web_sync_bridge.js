// ============================================================================
// FIRMA LEAGUE - REAL-TIME WEB SYNC BRIDGE (v2.8.0)
// Connects Minecraft Server (Cobblemon 1.8.4 + RCTMod 0.19.2)
// with https://poke-firma.vercel.app (/api/minecraft/*)
// ============================================================================

const $Cobblemon = Java.loadClass('com.cobblemon.mod.common.Cobblemon')
const $CobblemonEvents = Java.loadClass('com.cobblemon.mod.common.api.events.CobblemonEvents')
const $Priority = Java.loadClass('com.cobblemon.mod.common.api.Priority')
const $PokemonSpecies = Java.loadClass('com.cobblemon.mod.common.api.pokemon.PokemonSpecies')
const $Stats = Java.loadClass('com.cobblemon.mod.common.api.pokemon.stats.Stats')
const $PlayerState = Java.loadClass('com.gitlab.srcmc.rctmod.api.data.sync.PlayerState')

// HTTP Client assincrono nativo para KubeJS via FirmaWebClient (zzz-firma-league-core)
// Executa em thread Java daemon nativa sem restricoes de JPMS nem reflexao.
let $FirmaWebClient = null

try {
    $FirmaWebClient = Java.loadClass('com.firmaleague.core.FirmaWebClient')
    console.info('[FirmaWebSync] FirmaWebClient assincrono carregado com sucesso!')
} catch (err) {
    console.warn('[FirmaWebSync] FirmaWebClient nao encontrado: ' + err)
}
// ----------------------------------------------------------------------------
// 1. CONFIGURAÇÃO E CREDENCIAIS
// ----------------------------------------------------------------------------
// ============================================================================
// HELPER COMPATIBILIDADE MINECRAFT / KUBEJS (Player, UUID, Nick, Server)
// ============================================================================
function getPlayerUuid(player) {
    if (!player) return null
    try {
        if (player.uuid) return player.uuid
        if (typeof player.getUuid === 'function') return player.getUuid()
        if (typeof player.getUUID === 'function') return player.getUUID()
        if (player.gameProfile && player.gameProfile.id) return player.gameProfile.id
        if (typeof player.getGameProfile === 'function' && player.getGameProfile()) return player.getGameProfile().getId()
    } catch (e) {}
    return null
}

function getPlayerUuidString(player) {
    if (!player) return ''
    try {
        if (player.stringUuid) return String(player.stringUuid)
        let u = getPlayerUuid(player)
        if (u) return String(u.toString())
    } catch (e) {}
    return ''
}

function getPlayerNick(player) {
    if (!player) return ''
    try {
        if (player.username) return String(player.username)
        if (player.gameProfile && player.gameProfile.name) return String(player.gameProfile.name)
        if (typeof player.getGameProfile === 'function' && player.getGameProfile()) return String(player.getGameProfile().getName())
        if (player.name && player.name.string) return String(player.name.string)
    } catch (e) {}
    return ''
}

function getPlayerServer(player) {
    if (!player) return null
    try {
        if (player.server) return player.server
        if (typeof player.getServer === 'function') return player.getServer()
    } catch (e) {}
    try {
        if (typeof Utils !== 'undefined' && Utils.server) return Utils.server
    } catch (e) {}
    return null
}

function getWebSyncConfig() {
    let cfg = {
        enabled: true,
        only_dedicated_server: true,
        api_base_url: 'https://poke-firma.vercel.app',
        secret: ''
    }
    try {
        let raw = JsonIO.read('kubejs/config/web_sync.json')
        if (raw) {
            if (raw.enabled !== undefined) cfg.enabled = Boolean(raw.enabled)
            if (raw.only_dedicated_server !== undefined) cfg.only_dedicated_server = Boolean(raw.only_dedicated_server)
            if (raw.api_base_url) cfg.api_base_url = String(raw.api_base_url).replace(/\/+$/, '')
            if (raw.secret) cfg.secret = String(raw.secret).trim()
        }
    } catch (e) {
        // Ignora se arquivo ainda não existir
    }
    return cfg
}

function isDedicatedServerInstance(server) {
    if (!server) return false
    try {
        let s = String(server)
        if (s.indexOf('DedicatedServer') !== -1) return true
        if (s.indexOf('IntegratedServer') !== -1) return false
        if (typeof server.isDedicated === 'function') return Boolean(server.isDedicated())
    } catch (e) {}
    return true
}

function isAllowedServerEnvironment(server) {
    let cfg = getWebSyncConfig()
    if (!cfg.enabled) return false
    if (cfg.only_dedicated_server && server && !isDedicatedServerInstance(server)) {
        return false
    }
    return true
}

function postWebhookAsync(server, endpoint, payloadObj, onSuccess, onError) {
    let cfg = getWebSyncConfig()
    if (!cfg.enabled) return
    if (!cfg.secret || cfg.secret === 'COLE_AQUI_O_VALOR_DO_MINECRAFT_SECRET') {
        console.warn('[FirmaWebSync] MINECRAFT_SECRET ainda nao configurado em kubejs/config/web_sync.json!')
        if (onError) onError('MINECRAFT_SECRET nao configurado no servidor.')
        return
    }
    if (!$FirmaWebClient) {
        let msg = 'FirmaWebClient indisponivel no servidor. Verifique zzz-firma-league-core-2.0.0.jar.'
        console.warn('[FirmaWebSync] ' + msg)
        if (onError) onError(msg)
        return
    }

    let urlStr = cfg.api_base_url + endpoint
    let jsonBody = JSON.stringify(payloadObj)

    try {
        $FirmaWebClient.postAsync(urlStr, jsonBody, cfg.secret, (status, respText) => {
            if (server) {
                server.scheduleInTicks(1, () => {
                    if (status >= 200 && status < 300) {
                        if (onSuccess) onSuccess(status, String(respText || ''))
                    } else {
                        console.warn('[FirmaWebSync] Erro HTTP ' + status + ' em ' + endpoint + ': ' + respText)
                        if (onError) onError('HTTP ' + status + ': ' + respText)
                    }
                })
            }
        })
    } catch (err) {
        console.error('[FirmaWebSync] Erro ao disparar requisicao web: ' + err)
        if (onError) onError(String(err))
    }
}

// ----------------------------------------------------------------------------
// 2. MAPEAMENTO DE INSÍGNIAS & CAPÍTULOS (RCTMod -> poke-firma.vercel.app)
// ----------------------------------------------------------------------------
const BADGE_TRAINER_MAP = {
    // Kanto (Capítulo 1)
    'kanto-1': ['leader_brock_019e', 'leader_brock_0038', 'kantoleader_brock', 'kanto_brock'],
    'kanto-2': ['leader_misty_019f', 'leader_misty_0020', 'leader_misty_0030', 'kantoleader_misty', 'kanto_misty'],
    'kanto-3': ['leader_lt_surge_01a0', 'leader_lt_surge_0033', 'kantoleader_ltsurge', 'kanto_ltsurge'],
    'kanto-4': ['leader_erika_01a1', 'leader_erika_0041', 'kantoleader_erika', 'kanto_erika'],
    'kanto-5': ['leader_koga_01a2', 'kantoleader_koga', 'kantoleader_janine', 'kanto_koga'],
    'kanto-6': ['leader_sabrina_01a4', 'kantoleader_sabrina', 'kanto_sabrina'],
    'kanto-7': ['leader_blaine_01a3', 'kantoleader_blaine', 'kanto_blaine'],
    'kanto-8': ['boss_giovanni_015d', 'boss_giovanni_0045', 'boss_giovanni_015c', 'leader_giovanni_015e', 'kantoleader_giovanni', 'kanto_giovanni'],
    'kanto-elite': ['elite_four_lance_019d', 'elite_four_lance_0056', 'elite_four_lance_0057', 'elite_four_lance_02e2', 'kanto_league_lance'],
    'kanto-campeao': ['champion_terry_01b6', 'champion_terry_01b7', 'champion_terry_01b8', 'champion_terry_02e3', 'champion_terry_02e4', 'champion_terry_02e5', 'kantochampion_blue', 'kanto_champion_blue'],

    // Johto (Capítulo 2)
    'johto-1': ['leader_falkner_002b', 'leader_falkner_002d', 'johtoleader_falkner', 'johto_valerio'],
    'johto-2': ['leader_bugsy_0008', 'leader_bugsy_002f', 'leader_bugsy_004b', 'johtoleader_bugsy', 'johto_raffaello'],
    'johto-3': ['leader_whitney_0031', 'leader_whitney_004c', 'johtoleader_whitney', 'johto_chiara'],
    'johto-4': ['leader_morty_001c', 'leader_morty_0034', 'johtoleader_morty', 'johto_angelo'],
    'johto-5': ['leader_chuck_013d', 'johtoleader_chuck', 'johto_furio'],
    'johto-6': ['leader_jasmine_001d', 'leader_jasmine_003e', 'leader_jasmine_003f', 'leader_jasmine_0040', 'johtoleader_jasmine', 'johto_jasmine'],
    'johto-7': ['leader_pryce_003a', 'leader_pryce_003b', 'leader_pryce_003c', 'leader_pryce_004f', 'johtoleader_pryce', 'johto_alfredo'],
    'johto-8': ['leader_clair_004a', 'leader_clair_0026', 'johtoleader_clair', 'johto_sandra'],
    'johto-elite': ['johtoelitefour_karen', 'champion_lance_0027', 'johto_league_karen'],
    'johto-campeao': ['champion_lance_0027', 'johtochampion_lance', 'johto_champion_lance'],

    // Hoenn (Capítulo 3)
    'hoenn-1': ['hoennleader_roxanne', 'defeat_hoennleader_roxanne', 'hoenn_petra'],
    'hoenn-2': ['hoennleader_brawly', 'defeat_hoennleader_brawly', 'hoenn_rudi'],
    'hoenn-3': ['hoennleader_wattson', 'defeat_hoennleader_wattson', 'hoenn_walter'],
    'hoenn-4': ['hoennleader_flannery', 'defeat_hoennleader_flannery', 'hoenn_fiammetta'],
    'hoenn-5': ['hoennleader_norman', 'defeat_hoennleader_norman', 'hoenn_norman'],
    'hoenn-6': ['hoennleader_winona', 'defeat_hoennleader_winona', 'hoenn_alice'],
    'hoenn-7': ['hoennleader_tate', 'hoennleader_liza', 'defeat_hoennleader_liza', 'hoenn_tell', 'hoenn_pat'],
    'hoenn-8': ['hoennleader_wallace', 'hoennleader_juan', 'defeat_hoennleader_wallace', 'hoenn_adriano'],
    'hoenn-elite': ['hoennelitefour_drake', 'defeat_hoennelitefour_drake', 'hoenn_league_drake'],
    'hoenn-campeao': ['hoennchampion_steven', 'defeat_hoennchampion_steven', 'hoenn_champion_rocco'],

    // Sinnoh (Capítulo 4)
    'sinnoh-1': ['gym_leader_roark_0395', 'gym_leader_roark_058a', 'sinnohleader_roark', 'sinnoh_pedro'],
    'sinnoh-2': ['gym_leader_gardenia_03d6', 'gym_leader_gardenia_058b', 'sinnohleader_gardenia', 'sinnoh_gardenia'],
    'sinnoh-3': ['gym_leader_maylene_03d8', 'gym_leader_maylene_058d', 'sinnohleader_maylene', 'sinnoh_marzia'],
    'sinnoh-4': ['gym_leader_wake_03d7', 'gym_leader_wake_058c', 'sinnohleader_crasherwake', 'sinnoh_omar'],
    'sinnoh-5': ['gym_leader_fantina_03d9', 'gym_leader_fantina_058e', 'sinnohleader_fantina', 'sinnoh_fannie'],
    'sinnoh-6': ['gym_leader_byron_0399', 'gym_leader_byron_0590', 'sinnohleader_byron', 'sinnoh_ferruccio'],
    'sinnoh-7': ['gym_leader_candice_03da', 'gym_leader_candice_058f', 'sinnoh_leader_candice_05da', 'sinnohleader_candice', 'sinnoh_bianca'],
    'sinnoh-8': ['gym_leader_volkner_03db', 'gym_leader_volkner_0591', 'sinnohleader_volkner', 'sinnoh_corrado'],
    'sinnoh-elite': ['elite_four_lucian_03a2', 'elite_four_lucian_05a1', 'elite_four_lucian_05a6', 'sinnohelitefour_lucian', 'sinnoh_league_luciano'],
    'sinnoh-campeao': ['champion_cynthia_03a5', 'champion_cynthia_05a2', 'champion_cynthia_05a7', 'sinnohchampion_cynthia', 'sinnoh_champion_camilla']
}

const KANTO_CAP_LADDER = [15, 27, 33, 41, 50, 50, 54, 57, 60, 60]

function extractBadgesAndProgress(player) {
    let insignias = []
    let levelCap = 15
    let capitulo = 1

    try {
        let ps = $PlayerState.get(player)
        if (ps != null) {
            for (let badgeId in BADGE_TRAINER_MAP) {
                let trainerIds = BADGE_TRAINER_MAP[badgeId]
                let defeated = false
                for (let i = 0; i < trainerIds.length; i++) {
                    if (ps.getTrainerDefeatCount(trainerIds[i]) > 0) {
                        defeated = true
                        break
                    }
                }
                if (defeated) {
                    insignias.push(badgeId)
                }
            }
            try {
                let currentSeries = String(ps.getCurrentSeries() || '').trim()
                let rctCap = ps.getLevelCap()
                if (currentSeries && currentSeries !== 'empty' && currentSeries !== 'null' && rctCap > 0 && rctCap <= 100) {
                    levelCap = rctCap
                }
            } catch (e) {}
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Aviso ao ler PlayerState do RCTMod: ' + err)
    }

    try {
        if (player.persistentData.contains('firma_badges')) {
            let customBadges = player.persistentData.getCompound('firma_badges')
            let keys = customBadges.getAllKeys().toArray()
            for (let i = 0; i < keys.length; i++) {
                let k = String(keys[i])
                if (customBadges.getBoolean(k) && insignias.indexOf(k) === -1) {
                    insignias.push(k)
                }
            }
        }
    } catch (e) {}

    let hasSinnoh = insignias.some(b => b.indexOf('sinnoh-') === 0)
    let hasHoenn = insignias.some(b => b.indexOf('hoenn-') === 0) || insignias.indexOf('johto-campeao') !== -1
    let hasJohto = insignias.some(b => b.indexOf('johto-') === 0) || insignias.indexOf('kanto-campeao') !== -1

    if (hasSinnoh || insignias.indexOf('hoenn-campeao') !== -1) {
        capitulo = 4
        if (levelCap < 90) levelCap = 100
    } else if (hasHoenn) {
        capitulo = 3
        if (levelCap < 75) levelCap = 90
    } else if (hasJohto) {
        capitulo = 2
        if (levelCap < 60) levelCap = 75
    } else {
        capitulo = 1
        let kantoCount = insignias.filter(b => b.indexOf('kanto-') === 0).length
        let minCap = KANTO_CAP_LADDER[Math.min(kantoCount, KANTO_CAP_LADDER.length - 1)]
        if (levelCap < minCap) levelCap = minCap
    }

    return {
        insignias: insignias,
        capitulo: capitulo,
        level_cap: levelCap
    }
}

// ----------------------------------------------------------------------------
// 3. SERIALIZAÇÃO DE POKÉMON (Party, PC e Pokédex)
// ----------------------------------------------------------------------------
function serializePokemon(pkmn, extraFields) {
    if (!pkmn) return null
    try {
        let species = pkmn.getSpecies()
        let dex = species.getNationalPokedexNumber()
        let especie = String(species.getName()).toLowerCase()

        let forma = null
        try {
            let formObj = pkmn.getForm()
            if (formObj) {
                let formName = String(formObj.getName() || '')
                if (formName && formName.toLowerCase() !== 'normal' && formName.toLowerCase() !== 'standard') {
                    forma = formName.toLowerCase()
                }
            }
        } catch (e) {}

        let apelido = null
        try {
            let nickComp = pkmn.getNickname()
            if (nickComp) {
                let nickStr = String(nickComp.getString() || '').trim()
                if (nickStr && nickStr.toLowerCase() !== especie) {
                    apelido = nickStr
                }
            }
        } catch (e) {}

        let sexo = null
        try {
            let genderName = String(pkmn.getGender().name())
            if (genderName === 'MALE') sexo = 'M'
            else if (genderName === 'FEMALE') sexo = 'F'
        } catch (e) {}

        let habilidade = null
        try {
            if (pkmn.getAbility()) {
                habilidade = String(pkmn.getAbility().getName())
            }
        } catch (e) {}

        let natureza = null
        try {
            if (pkmn.getNature() && pkmn.getNature().getName()) {
                natureza = String(pkmn.getNature().getName().getPath())
            }
        } catch (e) {}

        let item = null
        try {
            let held = pkmn.heldItem()
            if (held && !held.isEmpty()) {
                item = String(held.getHoverName().getString())
            }
        } catch (e) {}

        let tera = null
        try {
            if (pkmn.getTeraType()) {
                tera = String(pkmn.getTeraType().showdownId())
            }
        } catch (e) {}

        let golpes = []
        try {
            let movesList = pkmn.getMoveSet().getMoves()
            for (let i = 0; i < movesList.size(); i++) {
                let mv = movesList.get(i)
                if (mv) {
                    golpes.push(String(mv.getName()))
                }
            }
        } catch (e) {}

        let ivsObj = pkmn.getIvs()
        let evsObj = pkmn.getEvs()

        let data = {
            dex: dex,
            especie: especie,
            forma: forma,
            apelido: apelido,
            nivel: pkmn.getLevel(),
            sexo: sexo,
            shiny: Boolean(pkmn.getShiny()),
            habilidade: habilidade,
            natureza: natureza,
            item: item,
            tera: tera,
            golpes: golpes,
            ivs: {
                hp: ivsObj.getOrDefault($Stats.HP),
                atk: ivsObj.getOrDefault($Stats.ATTACK),
                def: ivsObj.getOrDefault($Stats.DEFENCE),
                spa: ivsObj.getOrDefault($Stats.SPECIAL_ATTACK),
                spd: ivsObj.getOrDefault($Stats.SPECIAL_DEFENCE),
                spe: ivsObj.getOrDefault($Stats.SPEED)
            },
            evs: {
                hp: evsObj.getOrDefault($Stats.HP),
                atk: evsObj.getOrDefault($Stats.ATTACK),
                def: evsObj.getOrDefault($Stats.DEFENCE),
                spa: evsObj.getOrDefault($Stats.SPECIAL_ATTACK),
                spd: evsObj.getOrDefault($Stats.SPECIAL_DEFENCE),
                spe: evsObj.getOrDefault($Stats.SPEED)
            }
        }

        if (extraFields) {
            for (let k in extraFields) {
                data[k] = extraFields[k]
            }
        }
        return data
    } catch (err) {
        console.warn('[FirmaWebSync] Erro ao serializar Pokemon: ' + err)
        return null
    }
}

function buildPlayerSyncPayload(player) {
    let playerUuidObj = getPlayerUuid(player)
    let uuid = getPlayerUuidString(player)
    let nick = getPlayerNick(player)
    let progress = extractBadgesAndProgress(player)

    // 1. Party (usa iterator() para não colidir com PokemonStore.get(UUID) no Rhino!)
    let partyArr = []
    try {
        let partyStore = $Cobblemon.INSTANCE.getStorage().getParty(player)
        let partyIter = partyStore.iterator()
        while (partyIter.hasNext()) {
            let pkmn = partyIter.next()
            if (pkmn != null) {
                let serialized = serializePokemon(pkmn, null)
                if (serialized) partyArr.push(serialized)
            }
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Erro ao ler Party de ' + nick + ': ' + err)
    }

    // 2. PC Boxes (usa getNonEmptySlots() para evitar colisão de sobrecarga e otimizar leitura)
    let pcArr = []
    try {
        let pcStore = $Cobblemon.INSTANCE.getStorage().getPC(player)
        let boxes = pcStore.getBoxes()
        for (let b = 0; b < boxes.size(); b++) {
            let box = boxes.get(b)
            let nonEmpty = box.getNonEmptySlots()
            let slotEntries = nonEmpty.entrySet().toArray()
            for (let j = 0; j < slotEntries.length; j++) {
                let slotEntry = slotEntries[j]
                let slotIdx = Number(slotEntry.getKey())
                let pkmn = slotEntry.getValue()
                if (pkmn != null) {
                    let serialized = serializePokemon(pkmn, {
                        caixa: b + 1,
                        slot: slotIdx + 1
                    })
                    if (serialized) pcArr.push(serialized)
                }
            }
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Erro ao ler PC de ' + nick + ': ' + err)
    }

    // 3. Pokédex (Vistos e Capturados)
    let vistosSet = {}
    let capturadosSet = {}
    try {
        let dexManager = $Cobblemon.INSTANCE.getPlayerDataManager().getPokedexData(playerUuidObj)
        let records = dexManager.getSpeciesRecords()
        let entries = records.entrySet().toArray()
        for (let i = 0; i < entries.length; i++) {
            let entry = entries[i]
            let speciesId = entry.getKey()
            let record = entry.getValue()
            let knowledge = String(record.getKnowledge().name())
            if (knowledge === 'CAUGHT' || knowledge === 'ENCOUNTERED') {
                let sp = $PokemonSpecies.getByIdentifier(speciesId)
                if (sp != null) {
                    let dexNum = sp.getNationalPokedexNumber()
                    if (dexNum > 0) {
                        vistosSet[dexNum] = true
                        if (knowledge === 'CAUGHT') {
                            capturadosSet[dexNum] = true
                        }
                    }
                }
            }
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Erro ao ler Pokedex de ' + nick + ': ' + err)
    }

    for (let i = 0; i < partyArr.length; i++) {
        let d = partyArr[i].dex
        if (d > 0) {
            vistosSet[d] = true
            capturadosSet[d] = true
        }
    }
    for (let i = 0; i < pcArr.length; i++) {
        let d = pcArr[i].dex
        if (d > 0) {
            vistosSet[d] = true
            capturadosSet[d] = true
        }
    }

    let vistos = Object.keys(vistosSet).map(Number).sort((a, b) => a - b)
    let capturados = Object.keys(capturadosSet).map(Number).sort((a, b) => a - b)

    return {
        uuid: uuid,
        nick: nick,
        capitulo: progress.capitulo,
        level_cap: progress.level_cap,
        insignias: progress.insignias,
        pokedex: {
            vistos: vistos,
            capturados: capturados,
            total_vistos: vistos.length,
            total_capturados: capturados.length
        },
        party: partyArr,
        pc: pcArr
    }
}

const LAST_SYNC_TIME = {}

function syncPlayerToWeb(player, forceImmediate, feedbackCallback) {
    if (!player) return
    let srv = getPlayerServer(player)
    if (!isAllowedServerEnvironment(srv)) {
        if (feedbackCallback) feedbackCallback(false, 'Sincronizacao ativa apenas no servidor dedicado oficial (EnxadaHost).')
        return
    }
    let uuid = getPlayerUuidString(player)
    let now = Date.now()
    if (!forceImmediate && LAST_SYNC_TIME[uuid] && (now - LAST_SYNC_TIME[uuid] < 4000)) {
        return
    }
    LAST_SYNC_TIME[uuid] = now

    let payload = buildPlayerSyncPayload(player)
    postWebhookAsync(
        srv,
        '/api/minecraft/sync/player',
        payload,
        (status, body) => {
            if (feedbackCallback) feedbackCallback(true, body)
        },
        (err) => {
            if (feedbackCallback) feedbackCallback(false, err)
        }
    )
}

// ----------------------------------------------------------------------------
// 4. COMANDOS IN-GAME: /vincular E /sincronizar
// ----------------------------------------------------------------------------
function generateLinkCode() {
    let chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
    let code = 'FIRMA-'
    for (let i = 0; i < 4; i++) {
        let idx = Math.floor(Math.random() * chars.length)
        code += chars.charAt(idx)
    }
    return code
}

ServerEvents.commandRegistry(event => {
    const { commands: Commands } = event

    // /vincular -> gera código único de vinculação e já sincroniza a ficha do jogador
    event.register(
        Commands.literal('vincular')
            .executes(ctx => {
                let player = ctx.source.playerOrException
                let srv = getPlayerServer(player)
                if (!isAllowedServerEnvironment(srv)) {
                    player.tell(Text.of('§c[Firma League] O comando /vincular so pode ser usado dentro do servidor oficial da EnxadaHost!'))
                    return 0
                }
                let token = generateLinkCode()
                let expiresAt = Date.now() + 3600 * 1000 // 1 hora
                let uuidStr = getPlayerUuidString(player)
                let nickStr = getPlayerNick(player)

                player.tell(Text.of('§e[Firma League] §7Gerando codigo de vinculacao com §bpoke-firma.vercel.app§7...'))

                postWebhookAsync(
                    srv,
                    '/api/minecraft/link/create',
                    {
                        token: token,
                        minecraft_uuid: uuidStr,
                        minecraft_nick: nickStr,
                        expires_at: expiresAt
                    },
                    (status, body) => {
                        player.tell(Text.of('§6====================================================='))
                        player.tell(Text.of('§a§l✔ CODIGO DE VINCULACAO GERADO COM SUCESSO!'))
                        player.tell(Text.of('§fSeu codigo: §b§l' + token + ' §7(valido por 1 hora)'))
                        player.tell(Text.of('§71. Acesse §b§nhttps://poke-firma.vercel.app/perfil'))
                        player.tell(Text.of('§72. Faca login e cole o codigo §e' + token))
                        player.tell(Text.of('§73. Voce recebera seu §aTrainer ID (TR-XXX)§7 verificado!'))
                        player.tell(Text.of('§6====================================================='))
                    },
                    (err) => {
                        player.tell(Text.of('§c[Firma League] Falha ao comunicar com o site: ' + err))
                    }
                )

                // Sincroniza os dados atuais do jogador (Party, PC, Pokédex, Insígnias)
                srv.scheduleInTicks(10, () => {
                    syncPlayerToWeb(player, true, null)
                })
                return 1
            })
    )

    // /sincronizar -> força atualização imediata do perfil no site
    event.register(
        Commands.literal('sincronizar')
            .executes(ctx => {
                let player = ctx.source.playerOrException
                player.tell(Text.of('§e[Firma League] §7Sincronizando Time, PC, Pokedex e Insignias com o site...'))
                syncPlayerToWeb(player, true, (ok, info) => {
                    if (ok) {
                        player.tell(Text.of('§a[Firma League] ✔ Perfil sincronizado ao vivo em §bpoke-firma.vercel.app§a!'))
                    } else {
                        player.tell(Text.of('§c[Firma League] Erro ao sincronizar: ' + info))
                    }
                })
                return 1
            })
    )
})

// ----------------------------------------------------------------------------
// 5. EVENTOS AUTOMÁTICOS DE JOGADOR & COBBLEMON
// ----------------------------------------------------------------------------
PlayerEvents.loggedIn(event => {
    let player = event.player
    event.server.scheduleInTicks(60, () => {
        syncPlayerToWeb(player, true, null)
    })
})

PlayerEvents.loggedOut(event => {
    syncPlayerToWeb(event.player, true, null)
})

ServerEvents.loaded(serverEvent => {
    // Captura de Pokémon
    $CobblemonEvents.POKEMON_CAPTURED.subscribe($Priority.NORMAL, event => {
        try {
            let player = event.getPlayer()
            let srv = getPlayerServer(player)
            if (player && srv) {
                srv.scheduleInTicks(20, () => {
                    syncPlayerToWeb(player, false, null)
                })
            }
        } catch (e) {}
    })

    // Evolução concluída
    $CobblemonEvents.EVOLUTION_COMPLETE.subscribe($Priority.NORMAL, event => {
        try {
            let pkmn = event.getPokemon()
            let player = pkmn ? pkmn.getOwnerPlayer() : null
            let srv = getPlayerServer(player)
            if (player && srv) {
                srv.scheduleInTicks(20, () => {
                    syncPlayerToWeb(player, false, null)
                })
            }
        } catch (e) {}
    })

    // Ovo chocado
    $CobblemonEvents.HATCH_EGG_POST.subscribe($Priority.NORMAL, event => {
        try {
            let player = event.getPlayer()
            let srv = getPlayerServer(player)
            if (player && srv) {
                srv.scheduleInTicks(20, () => {
                    syncPlayerToWeb(player, false, null)
                })
            }
        } catch (e) {}
    })

    // Vitória em Batalha (Sincroniza Insígnias PvE + Reporta Torneios PvP!)
    $CobblemonEvents.BATTLE_VICTORY.subscribe($Priority.NORMAL, event => {
        try {
            let battle = event.getBattle()
            if (!battle) return

            let winners = event.getWinners()
            let losers = event.getLosers()

            let playersList = battle.getPlayers()
            for (let i = 0; i < playersList.size(); i++) {
                let p = playersList.get(i)
                let psrv = getPlayerServer(p)
                if (p && psrv) {
                    psrv.scheduleInTicks(40, () => {
                        syncPlayerToWeb(p, true, null)
                    })
                }
            }

            if (battle.isPvP() && winners.size() >= 1 && losers.size() >= 1) {
                let winnerActor = winners.get(0)
                let loserActor = losers.get(0)

                let winnerUuid = String(winnerActor.getUuid().toString())
                let loserUuid = String(loserActor.getUuid().toString())
                let battleId = String(battle.getBattleId().toString())

                let winnerTeamDex = []
                let winnerFaintedCount = 0
                let winnerPkmnList = winnerActor.getPokemonList()
                for (let i = 0; i < winnerPkmnList.size(); i++) {
                    let bp = winnerPkmnList.get(i)
                    if (bp && bp.getOriginalPokemon()) {
                        winnerTeamDex.push(bp.getOriginalPokemon().getSpecies().getNationalPokedexNumber())
                        if (bp.getHealth() <= 0) winnerFaintedCount++
                    }
                }

                let loserTeamDex = []
                let loserFaintedCount = 0
                let loserPkmnList = loserActor.getPokemonList()
                for (let i = 0; i < loserPkmnList.size(); i++) {
                    let bp = loserPkmnList.get(i)
                    if (bp && bp.getOriginalPokemon()) {
                        loserTeamDex.push(bp.getOriginalPokemon().getSpecies().getNationalPokedexNumber())
                        if (bp.getHealth() <= 0) loserFaintedCount++
                    }
                }

                let koWinner = loserFaintedCount > 0 ? loserFaintedCount : loserPkmnList.size()
                let koLoser = winnerFaintedCount

                postWebhookAsync(
                    serverEvent.server,
                    '/api/minecraft/tournament/match-result',
                    {
                        battle_id: battleId,
                        winner_uuid: winnerUuid,
                        loser_uuid: loserUuid,
                        ko_winner: koWinner,
                        ko_loser: koLoser,
                        team_winner_dex: winnerTeamDex,
                        team_loser_dex: loserTeamDex
                    },
                    (status, body) => {
                        console.info('[FirmaWebSync] Resultado PvP enviado (' + battleId + '): ' + body)
                    },
                    (err) => {
                        console.warn('[FirmaWebSync] Aviso ao enviar resultado PvP (' + battleId + '): ' + err)
                    }
                )
            }
        } catch (err) {
            console.error('[FirmaWebSync] Erro ao processar BATTLE_VICTORY: ' + err)
        }
    })
})
