// Automatic RCTMod Kanto Series & Level Cap Enforcer
PlayerEvents.loggedIn(event => {
    let player = event.player
    // Ensure player is on kanto series if they don't have it set
    event.server.scheduleInTicks(20, () => {
        if (!player.persistentData.getBoolean('rct_kanto_initialized')) {
            event.server.runCommandSilent(`rctmod player set series kanto ${player.username}`)
            player.persistentData.putBoolean('rct_kanto_initialized', true)
        }
    })
})
