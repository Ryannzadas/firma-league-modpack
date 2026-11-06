// =============================================================================
// FIRMA LEAGUE - CREATE <-> COBBLEMON INTEGRATION (All The Mons Style)
// =============================================================================
ServerEvents.recipes(event => {
  const transitional = 'create:incomplete_precision_mechanism'

  // 1. LINHA DE MONTAGEM DE POKEBOLAS (Sequenced Assembly -> 4x Bolas por ciclo)
  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'create:iron_sheet' },
    loops: 1,
    results: [{ id: 'cobblemon:poke_ball', count: 4 }],
    sequence: [
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:red_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'minecraft:stone_button' }], results: [{ id: transitional }] },
      { type: 'create:pressing', ingredients: [{ item: transitional }], results: [{ id: transitional }] }
    ],
    transitional_item: { id: transitional }
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'create:iron_sheet' },
    loops: 1,
    results: [{ id: 'cobblemon:great_ball', count: 4 }],
    sequence: [
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:blue_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:red_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'minecraft:stone_button' }], results: [{ id: transitional }] },
      { type: 'create:pressing', ingredients: [{ item: transitional }], results: [{ id: transitional }] }
    ],
    transitional_item: { id: transitional }
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'create:brass_sheet' },
    loops: 1,
    results: [{ id: 'cobblemon:ultra_ball', count: 4 }],
    sequence: [
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:yellow_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:black_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'create:electron_tube' }], results: [{ id: transitional }] },
      { type: 'create:pressing', ingredients: [{ item: transitional }], results: [{ id: transitional }] }
    ],
    transitional_item: { id: transitional }
  })

  event.custom({
    type: 'create:sequenced_assembly',
    ingredient: { item: 'create:iron_sheet' },
    loops: 1,
    results: [{ id: 'cobblemon:premier_ball', count: 4 }],
    sequence: [
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:white_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'cobblemon:white_apricorn' }], results: [{ id: transitional }] },
      { type: 'create:deploying', ingredients: [{ item: transitional }, { item: 'minecraft:stone_button' }], results: [{ id: transitional }] },
      { type: 'create:pressing', ingredients: [{ item: transitional }], results: [{ id: transitional }] }
    ],
    transitional_item: { id: transitional }
  })

  // 2. FABRICA DE DOCES DE EXP NO MIXER
  event.custom({
    type: 'create:mixing',
    heat_requirement: 'heated',
    ingredients: [
      { item: 'create:experience_nugget' },
      { item: 'create:experience_nugget' },
      { item: 'create:experience_nugget' },
      { item: 'create:experience_nugget' },
      { item: 'minecraft:sugar' }
    ],
    results: [{ id: 'cobblemon:exp_candy_s' }]
  })

  event.custom({
    type: 'create:mixing',
    heat_requirement: 'heated',
    ingredients: [
      { item: 'cobblemon:exp_candy_s' },
      { item: 'cobblemon:exp_candy_s' },
      { item: 'cobblemon:exp_candy_s' },
      { item: 'minecraft:honey_bottle' }
    ],
    results: [{ id: 'cobblemon:exp_candy_m' }]
  })

  event.custom({
    type: 'create:mixing',
    heat_requirement: 'superheated',
    ingredients: [
      { item: 'cobblemon:exp_candy_m' },
      { item: 'cobblemon:exp_candy_m' },
      { item: 'cobblemon:exp_candy_m' },
      { item: 'minecraft:glow_berries' }
    ],
    results: [{ id: 'cobblemon:exp_candy_l' }]
  })

  event.custom({
    type: 'create:mixing',
    heat_requirement: 'superheated',
    ingredients: [
      { item: 'cobblemon:exp_candy_l' },
      { item: 'cobblemon:exp_candy_l' },
      { item: 'minecraft:golden_apple' }
    ],
    results: [{ id: 'cobblemon:rare_candy' }]
  })

  // 3. VITAMINAS DE EV NO MIXER
  const vitamins = [
    { out: 'cobblemon:hp_up', extra: 'minecraft:golden_carrot' },
    { out: 'cobblemon:protein', extra: 'minecraft:cooked_beef' },
    { out: 'cobblemon:iron', extra: 'create:iron_sheet' },
    { out: 'cobblemon:calcium', extra: 'minecraft:bone_block' },
    { out: 'cobblemon:zinc', extra: 'minecraft:prismarine_crystals' },
    { out: 'cobblemon:carbos', extra: 'minecraft:sugar_cane' }
  ]
  vitamins.forEach(v => {
    event.custom({
      type: 'create:mixing',
      heat_requirement: 'heated',
      ingredients: [
        { item: 'cobblemon:medicinal_leek' },
        { item: v.extra },
        { item: 'minecraft:sugar' },
        { type: 'neoforge:single', amount: 250, fluid: 'minecraft:water' }
      ],
      results: [{ id: v.out }]
    })
  })

  // 4. CRUSHING WHEEL: MINERIOS DE PEDRAS DE EVOLUCAO
  const stones = ['fire', 'water', 'thunder', 'leaf', 'moon', 'sun', 'shiny', 'dusk', 'dawn', 'ice']
  stones.forEach(st => {
    const ores = [`cobblemon:${st}_stone_ore`, `cobblemon:deepslate_${st}_stone_ore`]
    if (st === 'fire') ores.push('cobblemon:nether_fire_stone_ore')
    if (st === 'moon') ores.push('cobblemon:dripstone_moon_stone_ore')
    if (st === 'sun') ores.push('cobblemon:terracotta_sun_stone_ore')

    ores.forEach(ore => {
      event.custom({
        type: 'create:crushing',
        processing_time: 300,
        ingredients: [{ item: ore }],
        results: [
          { id: `cobblemon:${st}_stone` },
          { id: `cobblemon:${st}_stone`, chance: 0.5 },
          { id: 'create:experience_nugget', chance: 0.75 }
        ]
      })
    })
  })

  // 5. HAUNTING (Moon Stone -> Dusk Stone)
  event.custom({
    type: 'create:haunting',
    ingredients: [{ item: 'cobblemon:moon_stone' }],
    results: [{ id: 'cobblemon:dusk_stone' }]
  })
})
