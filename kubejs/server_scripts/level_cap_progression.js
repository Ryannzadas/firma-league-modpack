// Automatic RCTMod Kanto (radicalred) Series & Level Cap Enforcer (v2.8.0)
const $RCTPlayerState = Java.loadClass('com.gitlab.srcmc.rctmod.api.data.sync.PlayerState')

function ensureRadicalRedSeries(server, player) {
    if (!server || !player) return
    try {
        let needsInit = !player.persistentData.getBoolean('rct_radicalred_v2_init')
        if (!needsInit) {
            let ps = $RCTPlayerState.get(player)
            if (ps != null) {
                let series = String(ps.getCurrentSeries() || '').trim()
                if (!series || series === 'empty' || series === 'null') {
                    needsInit = true
                }
            }
        }
        if (needsInit) {
            let name = String(player.getGameProfile().getName())
            server.runCommandSilent('rctmod player set series radicalred ' + name)
            player.persistentData.putBoolean('rct_radicalred_v2_init', true)
            console.info('[FirmaLeague] Serie inicial radicalred (Level Cap 15) aplicada para ' + name)
        }
    } catch (err) {
        console.warn('[FirmaLeague] Aviso ao inicializar serie radicalred: ' + err)
    }
}

PlayerEvents.loggedIn(event => {
    let player = event.player
    let srv = event.server
    srv.scheduleInTicks(20, () => {
        ensureRadicalRedSeries(srv, player)
    })
})

ServerEvents.loaded(event => {
    let srv = event.server
    srv.scheduleInTicks(40, () => {
        try {
            let players = srv.getPlayerList().getPlayers()
            for (let i = 0; i < players.size(); i++) {
                ensureRadicalRedSeries(srv, players.get(i))
            }
        } catch (e) {}
    })
})
