// =============================================================================
// FIRMA LEAGUE - COBBLEMON ITENS BASICOS & MASTER BALL
// =============================================================================
ServerEvents.recipes(event => {
  // Master Ball Industrial (High-tech)
  event.remove({ output: 'cobblemon:master_ball' })
  event.shaped('cobblemon:master_ball', [
    'PMP',
    'CNC',
    'ASA'
  ], {
    P: 'cobblemon:pink_apricorn',
    M: 'powah:crystal_nitro',
    C: 'mekanism:ultimate_control_circuit',
    N: 'minecraft:nether_star',
    A: 'mekanism:alloy_atomic',
    S: 'minecraft:shulker_shell'
  })

  // Exp Share
  event.remove({ output: 'cobblemon:exp_share' })
  event.shaped('cobblemon:exp_share', [
    'RAR',
    'LCL',
    'RER'
  ], {
    R: 'minecraft:redstone',
    A: 'cobblemon:red_apricorn',
    L: 'cobblemon:link_cable',
    C: 'mekanism:basic_control_circuit',
    E: 'minecraft:emerald'
  })

  // Healing Machine
  event.remove({ output: 'cobblemon:healing_machine' })
  event.shaped('cobblemon:healing_machine', [
    'RPR',
    'ICI',
    'IAI'
  ], {
    R: 'cobblemon:red_apricorn',
    P: 'cobblemon:potion',
    I: 'create:iron_sheet',
    C: 'mekanism:basic_control_circuit',
    A: 'create:andesite_alloy'
  })

  // PC
  event.remove({ output: 'cobblemon:pc' })
  event.shaped('cobblemon:pc', [
    'III',
    'GCG',
    'IAI'
  ], {
    I: 'create:iron_sheet',
    G: 'minecraft:glass_pane',
    C: 'mekanism:basic_control_circuit',
    A: 'create:andesite_alloy'
  })

  // Pasture
  event.remove({ output: 'cobblemon:pasture' })
  event.shaped('cobblemon:pasture', [
    'HPH',
    'WFW',
    'WCW'
  ], {
    H: 'minecraft:hay_block',
    P: '#minecraft:planks',
    W: '#minecraft:logs',
    F: '#minecraft:fences',
    C: 'mekanism:basic_control_circuit'
  })

  // Box Link
  event.remove({ output: 'cobblemonboxlink:box_link' })
  event.shaped('cobblemonboxlink:box_link', [
    'EPE',
    'ICI',
    'IAI'
  ], {
    E: 'minecraft:ender_pearl',
    P: 'cobblemon:pc',
    I: 'powah:steel_energized',
    C: 'mekanism:basic_control_circuit',
    A: 'powah:dielectric_paste'
  })
})
