// =============================================================================
// FIRMA LEAGUE - MEGA SHOWDOWN & ARTIFACTS
// =============================================================================
ServerEvents.recipes(event => {
  // Remove receitas originais faceis
  const removeOutputs = [
    'mega_showdown:omni_ring',
    'mega_showdown:mega_bracelet',
    'mega_showdown:mega_ring',
    'mega_showdown:dynamax_band',
    'mega_showdown:tera_orb',
    'mega_showdown:z_power_ring',
    'mega_showdown:z_ring',
    'mega_showdown:gladion_z_power_ring',
    'mega_showdown:hapu_z_power_ring',
    'mega_showdown:hapus_z_ring',
    'mega_showdown:nanu_z_power_ring',
    'mega_showdown:olivia_z_power_ring',
    'mega_showdown:olivias_z_ring',
    'mega_showdown:rocket_z_power_ring',
    'mega_showdown:archie_anchor',
    'mega_showdown:brendan_mega_cuff',
    'mega_showdown:diantha_mega_charm',
    'mega_showdown:korrina_glove',
    'mega_showdown:lisia_mega_tiara',
    'mega_showdown:lysandre_ring',
    'mega_showdown:maxie_glasses',
    'mega_showdown:may_bracelet',
    'mega_showdown:zinnia_mega_anklet'
  ]
  removeOutputs.forEach(id => event.remove({ output: id }))

  // 1. Mega Bracelet (Padrao)
  event.shaped('mega_showdown:mega_bracelet', [
    'IDI',
    'AKA',
    'IEI'
  ], {
    I: 'powah:steel_energized',
    D: 'minecraft:diamond',
    A: 'cobblemon:white_apricorn',
    K: 'mega_showdown:keystone',
    E: 'mekanism:basic_control_circuit'
  })

  // 2. Mega Ring (Variante Preta)
  event.shaped('mega_showdown:mega_ring', [
    'ADA',
    'AKA',
    'IEI'
  ], {
    I: 'powah:steel_energized',
    D: 'minecraft:diamond',
    A: 'cobblemon:black_apricorn',
    K: 'mega_showdown:keystone',
    E: 'mekanism:basic_control_circuit'
  })

  // 3. Tera Orb
  event.shaped('mega_showdown:tera_orb', [
    'SES',
    'GDG',
    'SBS'
  ], {
    S: 'minecraft:amethyst_shard',
    E: 'minecraft:ender_pearl',
    G: 'mekanism:basic_control_circuit',
    D: 'minecraft:diamond',
    B: 'powah:crystal_blazing'
  })

  // 4. Z-Power Ring
  event.shaped('mega_showdown:z_power_ring', [
    'ISI',
    'A A',
    'IEI'
  ], {
    I: 'powah:steel_energized',
    S: 'mega_showdown:sparkling_stone_dark',
    A: 'cobblemon:black_apricorn',
    E: 'mekanism:basic_control_circuit'
  })

  // 5. Z-Ring (Branco)
  event.shaped('mega_showdown:z_ring', [
    'ISI',
    'A A',
    'IEI'
  ], {
    I: 'powah:steel_energized',
    S: 'mega_showdown:sparkling_stone_light',
    A: 'cobblemon:white_apricorn',
    E: 'mekanism:basic_control_circuit'
  })

  // 6. Dynamax Band
  event.shaped('mega_showdown:dynamax_band', [
    'PPP',
    'IWI',
    'BEB'
  ], {
    P: 'cobblemon:pink_apricorn',
    I: 'powah:steel_energized',
    W: 'mega_showdown:wishing_star',
    B: 'cobblemon:blue_apricorn',
    E: 'mekanism:basic_control_circuit'
  })

  // 7. OMNI RING (4 em 1 Definitivo)
  event.shaped('mega_showdown:omni_ring', [
    'CDC',
    'MNZ',
    'PTP'
  ], {
    C: 'mekanism:elite_control_circuit',
    D: 'mega_showdown:dynamax_band',
    M: ['mega_showdown:mega_bracelet', 'mega_showdown:mega_ring'],
    N: 'minecraft:netherite_ingot',
    Z: ['mega_showdown:z_power_ring', 'mega_showdown:z_ring'],
    P: 'powah:crystal_niotic',
    T: 'mega_showdown:tera_orb'
  })
})
