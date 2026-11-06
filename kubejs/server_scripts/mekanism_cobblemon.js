// =============================================================================
// FIRMA LEAGUE - MEKANISM <-> COBBLEMON INTEGRATION
// =============================================================================
ServerEvents.recipes(event => {
  const stones = ['fire', 'water', 'thunder', 'leaf', 'moon', 'sun', 'shiny', 'dusk', 'dawn', 'ice']

  // 1. ENRICHMENT CHAMBER: 1 MINERIO -> 2 PEDRAS GARANTIDAS
  stones.forEach(st => {
    const ores = [`cobblemon:${st}_stone_ore`, `cobblemon:deepslate_${st}_stone_ore`]
    if (st === 'fire') ores.push('cobblemon:nether_fire_stone_ore')
    if (st === 'moon') ores.push('cobblemon:dripstone_moon_stone_ore')
    if (st === 'sun') ores.push('cobblemon:terracotta_sun_stone_ore')

    ores.forEach(ore => {
      event.custom({
        type: 'mekanism:enriching',
        input: { count: 1, item: ore },
        output: { count: 2, id: `cobblemon:${st}_stone` }
      })
    })
  })

  // 2. CRUSHER: APRICORNS -> 4x BIO FUEL
  const apricorns = ['red', 'yellow', 'green', 'blue', 'pink', 'black', 'white']
  apricorns.forEach(ap => {
    event.custom({
      type: 'mekanism:crushing',
      input: { count: 1, item: `cobblemon:${ap}_apricorn` },
      output: { count: 4, id: 'mekanism:bio_fuel' }
    })
  })

  // 3. METALLURGIC INFUSER: ITENS DE EVOLUCAO POR TROCA
  const infusing = [
    { out: 'cobblemon:metal_coat', item: { tag: 'c:ingots/steel' }, chem: 'mekanism:redstone', amt: 40 },
    { out: 'cobblemon:dragon_scale', item: { item: 'minecraft:prismarine_shard' }, chem: 'mekanism:diamond', amt: 40 },
    { out: 'cobblemon:kings_rock', item: { tag: 'c:ingots/gold' }, chem: 'mekanism:diamond', amt: 20 },
    { out: 'cobblemon:razor_claw', item: { item: 'minecraft:flint' }, chem: 'mekanism:diamond', amt: 20 },
    { out: 'cobblemon:protector', item: { item: 'minecraft:iron_block' }, chem: 'mekanism:refined_obsidian', amt: 20 },
    { out: 'cobblemon:electirizer', item: { item: 'mekanism:alloy_infused' }, chem: 'mekanism:redstone', amt: 80 },
    { out: 'cobblemon:magmarizer', item: { item: 'minecraft:magma_cream' }, chem: 'mekanism:carbon', amt: 80 },
    { out: 'cobblemon:reaper_cloth', item: { item: 'minecraft:phantom_membrane' }, chem: 'mekanism:fungi', amt: 40 },
    { out: 'cobblemon:prism_scale', item: { item: 'minecraft:prismarine_crystals' }, chem: 'mekanism:diamond', amt: 20 }
  ]

  infusing.forEach(inf => {
    let itemInput = { count: 1 }
    if (inf.item.tag) itemInput.tag = inf.item.tag
    if (inf.item.item) itemInput.item = inf.item.item

    event.custom({
      type: 'mekanism:metallurgic_infusing',
      chemical_input: { amount: inf.amt, tag: inf.chem },
      item_input: itemInput,
      output: { count: 1, id: inf.out },
      per_tick_usage: false
    })
  })
})
