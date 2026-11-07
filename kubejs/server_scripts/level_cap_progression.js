// Automatic RCTMod Kanto (radicalred) Series & Level Cap Enforcer
PlayerEvents.loggedIn(event => {
    let player = event.player
    event.server.scheduleInTicks(20, () => {
        if (!player.persistentData.getBoolean('rct_kanto_initialized')) {
            event.server.runCommandSilent(`rctmod player set series radicalred ${player.username}`)
            player.persistentData.putBoolean('rct_kanto_initialized', true)
        }
    })
})
