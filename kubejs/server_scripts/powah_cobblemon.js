// =============================================================================
// FIRMA LEAGUE - POWAH ENERGIZING ORB RECIPES
// =============================================================================
ServerEvents.recipes(event => {
  // 1. PEDRAS DE EVOLUCAO A PARTIR DE GEMAS DE TIPO
  const gemToStone = {
    fire: 'fire', water: 'water', electric: 'thunder', grass: 'leaf',
    ice: 'ice', fairy: 'moon', normal: 'sun', psychic: 'dawn',
    ghost: 'dusk', dragon: 'shiny'
  }

  for (const [gem, st] of Object.entries(gemToStone)) {
    event.custom({
      type: 'powah:energizing',
      ingredients: [
        { item: `cobblemon:${gem}_gem` },
        { item: `cobblemon:${gem}_gem` },
        { item: 'minecraft:amethyst_shard' }
      ],
      energy: 30000,
      result: { id: `cobblemon:${st}_stone`, count: 1 }
    })
  }

  // 2. LINK CABLE (Evolucao sem troca)
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'mekanism:basic_universal_cable' },
      { item: 'minecraft:gold_ingot' },
      { item: 'minecraft:ender_pearl' }
    ],
    energy: 15000,
    result: { id: 'cobblemon:link_cable', count: 1 }
  })

  // 3. UPGRADE (Porygon2)
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'mekanism:basic_control_circuit' },
      { item: 'minecraft:piston' },
      { item: 'cobblemon:red_apricorn' },
      { item: 'cobblemon:blue_apricorn' }
    ],
    energy: 25000,
    result: { id: 'cobblemon:upgrade', count: 1 }
  })

  // 4. DUBIOUS DISC (Porygon-Z)
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'cobblemon:upgrade' },
      { item: 'mekanism:advanced_control_circuit' },
      { item: 'minecraft:ender_eye' },
      { item: 'powah:crystal_blazing' }
    ],
    energy: 50000,
    result: { id: 'cobblemon:dubious_disc', count: 1 }
  })

  // 5. ABILITY CAPSULE
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'create:electron_tube' },
      { item: 'cobblemon:rare_candy' },
      { item: 'cobblemon:yellow_apricorn' },
      { item: 'cobblemon:pink_apricorn' }
    ],
    energy: 50000,
    result: { id: 'cobblemon:ability_capsule', count: 1 }
  })

  // 6. ABILITY PATCH
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'cobblemon:ability_capsule' },
      { item: 'powah:crystal_niotic' },
      { item: 'mekanism:advanced_control_circuit' },
      { item: 'minecraft:netherite_scrap' }
    ],
    energy: 150000,
    result: { id: 'cobblemon:ability_patch', count: 1 }
  })

  // 7. GOLDEN BOTTLE CAP
  event.custom({
    type: 'powah:energizing',
    ingredients: [
      { item: 'cobblemon_utility:defsilvercap' },
      { item: 'cobblemon_utility:atksilvercap' },
      { item: 'cobblemon_utility:speedsilvercap' },
      { item: 'cobblemon_utility:hpsilvercap' },
      { item: 'powah:crystal_nitro' },
      { item: 'minecraft:nether_star' }
    ],
    energy: 250000,
    result: { id: 'cobblemon_utility:goldencap', count: 1 }
  })
})
