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
const $Commands = Java.loadClass('net.minecraft.commands.Commands')

// Java 21 HTTP Client classes (whitelisted via kubejs.classfilter.txt in zzz-firma-league-core)
let $URI = null
let $HttpClient = null
let $HttpRequest = null
let $BodyPublishers = null
let $BodyHandlers = null
let $Duration = null
let HTTP_CLIENT = null

try {
    $URI = Java.loadClass('java.net.URI')
    $HttpClient = Java.loadClass('java.net.http.HttpClient')
    $HttpRequest = Java.loadClass('java.net.http.HttpRequest')
    $BodyPublishers = Java.loadClass('java.net.http.HttpRequest$BodyPublishers')
    $BodyHandlers = Java.loadClass('java.net.http.HttpResponse$BodyHandlers')
    $Duration = Java.loadClass('java.time.Duration')
    HTTP_CLIENT = $HttpClient.newBuilder()
        .connectTimeout($Duration.ofSeconds(10))
        .build()
    console.info('[FirmaWebSync] HttpClient inicializado com sucesso!')
} catch (err) {
    console.error('[FirmaWebSync] Falha ao carregar java.net.http.HttpClient. Verifique se zzz-firma-league-core-2.0.0.jar esta atualizado: ' + err)
}

// ----------------------------------------------------------------------------
// 1. CONFIGURAÇÃO E CREDENCIAIS
// ----------------------------------------------------------------------------
function getWebSyncConfig() {
    let cfg = {
        enabled: true,
        api_base_url: 'https://poke-firma.vercel.app',
        secret: ''
    }
    try {
        let raw = JsonIO.read('kubejs/config/web_sync.json')
        if (raw) {
            if (raw.enabled !== undefined) cfg.enabled = Boolean(raw.enabled)
            if (raw.api_base_url) cfg.api_base_url = String(raw.api_base_url).replace(/\/+$/, '')
            if (raw.secret) cfg.secret = String(raw.secret).trim()
        }
    } catch (e) {
        // Ignora se arquivo ainda não existir
    }
    return cfg
}

function postWebhookAsync(endpoint, payloadObj, onSuccess, onError) {
    let cfg = getWebSyncConfig()
    if (!cfg.enabled) return
    if (!cfg.secret || cfg.secret === 'COLE_AQUI_O_VALOR_DO_MINECRAFT_SECRET') {
        console.warn('[FirmaWebSync] MINECRAFT_SECRET ainda nao configurado em kubejs/config/web_sync.json!')
        if (onError) onError('MINECRAFT_SECRET nao configurado no servidor.')
        return
    }
    if (!HTTP_CLIENT) {
        if (onError) onError('HttpClient indisponivel no KubeJS.')
        return
    }

    try {
        let url = cfg.api_base_url + endpoint
        let jsonBody = JSON.stringify(payloadObj)
        let request = $HttpRequest.newBuilder($URI.create(url))
            .header('Content-Type', 'application/json; charset=utf-8')
            .header('X-Minecraft-Secret', cfg.secret)
            .timeout($Duration.ofSeconds(15))
            .POST($BodyPublishers.ofString(jsonBody))
            .build()

        HTTP_CLIENT.sendAsync(request, $BodyHandlers.ofString())
            .thenAccept(response => {
                let status = response.statusCode()
                let body = String(response.body() || '')
                if (status >= 200 && status < 300) {
                    if (onSuccess) onSuccess(status, body)
                } else {
                    console.warn('[FirmaWebSync] Erro HTTP ' + status + ' em ' + endpoint + ': ' + body)
                    if (onError) onError('HTTP ' + status + ': ' + body)
                }
            })
            .exceptionally(ex => {
                console.error('[FirmaWebSync] Excecao na chamada para ' + endpoint + ': ' + ex)
                if (onError) onError(String(ex))
                return null
            })
    } catch (err) {
        console.error('[FirmaWebSync] Erro ao montar requisicao para ' + endpoint + ': ' + err)
        if (onError) onError(String(err))
    }
}

// ----------------------------------------------------------------------------
// 2. MAPEAMENTO DE INSÍGNIAS & CAPÍTULOS (RCTMod -> poke-firma.vercel.app)
// ----------------------------------------------------------------------------
const BADGE_TRAINER_MAP = {
    // Kanto (Capítulo 1)
    'kanto-1': ['leader_brock_019e', 'leader_brock_0038', 'kantoleader_brock'],
    'kanto-2': ['leader_misty_019f', 'leader_misty_0020', 'leader_misty_0030', 'kantoleader_misty'],
    'kanto-3': ['leader_lt_surge_01a0', 'leader_lt_surge_0033', 'kantoleader_ltsurge'],
    'kanto-4': ['leader_erika_01a1', 'leader_erika_0041', 'kantoleader_erika'],
    'kanto-5': ['leader_koga_01a2', 'kantoleader_koga', 'kantoleader_janine'],
    'kanto-6': ['leader_sabrina_01a4', 'kantoleader_sabrina'],
    'kanto-7': ['leader_blaine_01a3', 'kantoleader_blaine'],
    'kanto-8': ['boss_giovanni_015d', 'boss_giovanni_0045', 'boss_giovanni_015c', 'leader_giovanni_015e', 'kantoleader_giovanni'],
    'kanto-elite': ['elite_four_lance_019d', 'elite_four_lance_0056', 'elite_four_lance_0057', 'elite_four_lance_02e2'],
    'kanto-campeao': ['champion_terry_01b6', 'champion_terry_01b7', 'champion_terry_01b8', 'champion_terry_02e3', 'champion_terry_02e4', 'champion_terry_02e5', 'kantochampion_blue'],

    // Johto (Capítulo 2)
    'johto-1': ['leader_falkner_002b', 'leader_falkner_002d', 'johtoleader_falkner'],
    'johto-2': ['leader_bugsy_0008', 'leader_bugsy_002f', 'leader_bugsy_004b', 'johtoleader_bugsy'],
    'johto-3': ['leader_whitney_0031', 'leader_whitney_004c', 'johtoleader_whitney'],
    'johto-4': ['leader_morty_001c', 'leader_morty_0034', 'johtoleader_morty'],
    'johto-5': ['leader_chuck_013d', 'johtoleader_chuck'],
    'johto-6': ['leader_jasmine_001d', 'leader_jasmine_003e', 'leader_jasmine_003f', 'leader_jasmine_0040', 'johtoleader_jasmine'],
    'johto-7': ['leader_pryce_003a', 'leader_pryce_003b', 'leader_pryce_003c', 'leader_pryce_004f', 'johtoleader_pryce'],
    'johto-8': ['leader_clair_004a', 'leader_clair_0026', 'johtoleader_clair'],
    'johto-elite': ['johtoelitefour_karen', 'champion_lance_0027'],
    'johto-campeao': ['champion_lance_0027', 'johtochampion_lance'],

    // Hoenn (Capítulo 3)
    'hoenn-1': ['hoennleader_roxanne', 'defeat_hoennleader_roxanne'],
    'hoenn-2': ['hoennleader_brawly', 'defeat_hoennleader_brawly'],
    'hoenn-3': ['hoennleader_wattson', 'defeat_hoennleader_wattson'],
    'hoenn-4': ['hoennleader_flannery', 'defeat_hoennleader_flannery'],
    'hoenn-5': ['hoennleader_norman', 'defeat_hoennleader_norman'],
    'hoenn-6': ['hoennleader_winona', 'defeat_hoennleader_winona'],
    'hoenn-7': ['hoennleader_tate', 'hoennleader_liza', 'defeat_hoennleader_liza'],
    'hoenn-8': ['hoennleader_wallace', 'hoennleader_juan', 'defeat_hoennleader_wallace'],
    'hoenn-elite': ['hoennelitefour_drake', 'defeat_hoennelitefour_drake'],
    'hoenn-campeao': ['hoennchampion_steven', 'defeat_hoennchampion_steven'],

    // Sinnoh (Capítulo 4)
    'sinnoh-1': ['gym_leader_roark_0395', 'gym_leader_roark_058a', 'sinnohleader_roark'],
    'sinnoh-2': ['gym_leader_gardenia_03d6', 'gym_leader_gardenia_058b', 'sinnohleader_gardenia'],
    'sinnoh-3': ['gym_leader_maylene_03d8', 'gym_leader_maylene_058d', 'sinnohleader_maylene'],
    'sinnoh-4': ['gym_leader_wake_03d7', 'gym_leader_wake_058c', 'sinnohleader_crasherwake'],
    'sinnoh-5': ['gym_leader_fantina_03d9', 'gym_leader_fantina_058e', 'sinnohleader_fantina'],
    'sinnoh-6': ['gym_leader_byron_0399', 'gym_leader_byron_0590', 'sinnohleader_byron'],
    'sinnoh-7': ['gym_leader_candice_03da', 'gym_leader_candice_058f', 'sinnoh_leader_candice_05da', 'sinnohleader_candice'],
    'sinnoh-8': ['gym_leader_volkner_03db', 'gym_leader_volkner_0591', 'sinnohleader_volkner'],
    'sinnoh-elite': ['elite_four_lucian_03a2', 'elite_four_lucian_05a1', 'elite_four_lucian_05a6', 'sinnohelitefour_lucian'],
    'sinnoh-campeao': ['champion_cynthia_03a5', 'champion_cynthia_05a2', 'champion_cynthia_05a7', 'sinnohchampion_cynthia']
}

// Level Caps progressivos por insígnia caso RCTMod retorne fallback
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
                let rctCap = ps.getLevelCap()
                if (rctCap > 0 && rctCap <= 100) {
                    levelCap = rctCap
                }
            } catch (e) {}
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Aviso ao ler PlayerState do RCTMod: ' + err)
    }

    // Também verifica se o jogador tem insígnias salvas em persistentData
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

    // Determina o capítulo atual (1=Kanto, 2=Johto, 3=Hoenn, 4=Sinnoh) e o Level Cap
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
    let uuid = String(player.uuid)
    let nick = String(player.username)
    let progress = extractBadgesAndProgress(player)

    // 1. Party (até 6 Pokémon)
    let partyArr = []
    try {
        let partyStore = $Cobblemon.INSTANCE.getStorage().getParty(player)
        for (let i = 0; i < 6; i++) {
            let pkmn = partyStore.get(i)
            if (pkmn != null) {
                let serialized = serializePokemon(pkmn, null)
                if (serialized) partyArr.push(serialized)
            }
        }
    } catch (err) {
        console.warn('[FirmaWebSync] Erro ao ler Party de ' + nick + ': ' + err)
    }

    // 2. PC Boxes
    let pcArr = []
    try {
        let pcStore = $Cobblemon.INSTANCE.getStorage().getPC(player)
        let boxes = pcStore.getBoxes()
        for (let b = 0; b < boxes.size(); b++) {
            let box = boxes.get(b)
            for (let s = 0; s < 30; s++) {
                let pkmn = box.get(s)
                if (pkmn != null) {
                    let serialized = serializePokemon(pkmn, {
                        caixa: b + 1,
                        slot: s + 1
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
        let dexManager = $Cobblemon.INSTANCE.getPlayerDataManager().getPokedexData(player)
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

    // Garante que todos os Pokémon da Party e do PC também constem como vistos/capturados
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

// Debounce por jogador para evitar flood de requisições seguidas
const LAST_SYNC_TIME = {}

function syncPlayerToWeb(player, forceImmediate, feedbackCallback) {
    if (!player || player.level.isClientSide()) return
    let uuid = String(player.uuid)
    let now = Date.now()
    if (!forceImmediate && LAST_SYNC_TIME[uuid] && (now - LAST_SYNC_TIME[uuid] < 4000)) {
        return
    }
    LAST_SYNC_TIME[uuid] = now

    let payload = buildPlayerSyncPayload(player)
    postWebhookAsync(
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
                let token = generateLinkCode()
                let expiresAt = Date.now() + 3600 * 1000 // 1 hora

                player.tell(Text.of('§e[Firma League] §7Gerando codigo de vinculacao com §bpoke-firma.vercel.app§7...'))

                // Sincroniza os dados atuais do jogador (Party, PC, Pokédex, Insígnias)
                syncPlayerToWeb(player, true, null)

                postWebhookAsync(
                    '/api/minecraft/link/create',
                    {
                        token: token,
                        minecraft_uuid: String(player.uuid),
                        minecraft_nick: String(player.username),
                        expires_at: expiresAt
                    },
                    (status, body) => {
                        player.server.execute(() => {
                            player.tell(Text.of('§6====================================================='))
                            player.tell(Text.of('§a§l✔ CODIGO DE VINCULACAO GERADO COM SUCESSO!'))
                            player.tell(Text.of('§fSeu codigo: §b§l' + token + ' §7(valido por 1 hora)'))
                            player.tell(Text.of('§71. Acesse §b§nhttps://poke-firma.vercel.app/perfil'))
                            player.tell(Text.of('§72. Faca login e cole o codigo §e' + token))
                            player.tell(Text.of('§73. Voce recebera seu §aTrainer ID (TR-XXX)§7 verificado!'))
                            player.tell(Text.of('§6====================================================='))
                        })
                    },
                    (err) => {
                        player.server.execute(() => {
                            player.tell(Text.of('§c[Firma League] Falha ao comunicar com o site: ' + err))
                        })
                    }
                )
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
                    player.server.execute(() => {
                        if (ok) {
                            player.tell(Text.of('§a[Firma League] ✔ Perfil sincronizado ao vivo em §bpoke-firma.vercel.app§a!'))
                        } else {
                            player.tell(Text.of('§c[Firma League] Erro ao sincronizar: ' + info))
                        }
                    })
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

// Registra os hooks nos eventos do Cobblemon uma única vez por inicialização
if (!global.firmaCobblemonHooksRegistered) {
    global.firmaCobblemonHooksRegistered = true

    // Captura de Pokémon
    $CobblemonEvents.POKEMON_CAPTURED.subscribe($Priority.NORMAL, event => {
        try {
            let player = event.getPlayer()
            if (player) {
                player.server.scheduleInTicks(20, () => {
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
            if (player) {
                player.server.scheduleInTicks(20, () => {
                    syncPlayerToWeb(player, false, null)
                })
            }
        } catch (e) {}
    })

    // Ovo chocado
    $CobblemonEvents.HATCH_EGG_POST.subscribe($Priority.NORMAL, event => {
        try {
            let player = event.getPlayer()
            if (player) {
                player.server.scheduleInTicks(20, () => {
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

            // Sincroniza todos os jogadores humanos envolvidos na batalha (ex: após vencer Líder de Ginásio)
            let playersList = battle.getPlayers()
            for (let i = 0; i < playersList.size(); i++) {
                let p = playersList.get(i)
                if (p) {
                    p.server.scheduleInTicks(40, () => {
                        syncPlayerToWeb(p, true, null)
                    })
                }
            }

            // Se for Batalha PvP (1v1 entre jogadores), envia resultado para o Torneio no site!
            if (battle.isPvP() && winners.size() >= 1 && losers.size() >= 1) {
                let winnerActor = winners.get(0)
                let loserActor = losers.get(0)

                let winnerUuid = String(winnerActor.getUuid())
                let loserUuid = String(loserActor.getUuid())
                let battleId = String(battle.getBattleId())

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
}
