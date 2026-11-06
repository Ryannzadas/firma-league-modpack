// =============================================================================
// FIRMA LEAGUE - STORAGE, MOCHILAS & FORNALHAS
// =============================================================================
ServerEvents.recipes(event => {
  // 1. SOPHISTICATED BACKPACKS (Preservando inventario e upgrades)
  event.remove({ output: 'sophisticatedbackpacks:iron_backpack' })
  event.custom({
    type: 'sophisticatedbackpacks:backpack_upgrade',
    category: 'misc',
    pattern: [
      'ISI',
      'IBI',
      'IAI'
    ],
    key: {
      I: { item: 'create:iron_sheet' },
      S: { item: 'minecraft:string' },
      B: { item: 'sophisticatedbackpacks:backpack' },
      A: { item: 'cobblemon:red_apricorn' }
    },
    result: { id: 'sophisticatedbackpacks:iron_backpack', count: 1 }
  })

  event.remove({ output: 'sophisticatedbackpacks:gold_backpack' })
  event.custom({
    type: 'sophisticatedbackpacks:backpack_upgrade',
    category: 'misc',
    pattern: [
      'GGG',
      'GBG',
      'GCG'
    ],
    key: {
      G: { tag: 'c:ingots/gold' },
      B: { item: 'sophisticatedbackpacks:iron_backpack' },
      C: { item: 'mekanism:basic_control_circuit' }
    },
    result: { id: 'sophisticatedbackpacks:gold_backpack', count: 1 }
  })

  event.remove({ output: 'sophisticatedbackpacks:diamond_backpack' })
  event.custom({
    type: 'sophisticatedbackpacks:backpack_upgrade',
    category: 'misc',
    pattern: [
      'DDD',
      'DBD',
      'DED'
    ],
    key: {
      D: { tag: 'c:gems/diamond' },
      B: { item: 'sophisticatedbackpacks:gold_backpack' },
      E: { item: 'powah:steel_energized' }
    },
    result: { id: 'sophisticatedbackpacks:diamond_backpack', count: 1 }
  })

  // 2. SOPHISTICATED STORAGE (Tier Upgrades)
  event.remove({ output: 'sophisticatedstorage:basic_to_iron_tier_upgrade' })
  event.shaped('sophisticatedstorage:basic_to_iron_tier_upgrade', [
    'ISI',
    'RBR',
    'IAI'
  ], {
    I: 'create:iron_sheet',
    S: '#minecraft:planks',
    R: 'minecraft:redstone_torch',
    B: 'create:andesite_alloy',
    A: 'cobblemon:red_apricorn'
  })

  event.remove({ output: 'sophisticatedstorage:iron_to_gold_tier_upgrade' })
  event.shaped('sophisticatedstorage:iron_to_gold_tier_upgrade', [
    'GGG',
    'RBR',
    'GCG'
  ], {
    G: '#c:ingots/gold',
    R: 'minecraft:redstone_torch',
    B: 'create:iron_sheet',
    C: 'mekanism:basic_control_circuit'
  })

  event.remove({ output: 'sophisticatedstorage:gold_to_diamond_tier_upgrade' })
  event.shaped('sophisticatedstorage:gold_to_diamond_tier_upgrade', [
    'DDD',
    'RBR',
    'DED'
  ], {
    D: '#c:gems/diamond',
    R: 'minecraft:redstone_torch',
    B: 'mekanism:basic_control_circuit',
    E: 'powah:steel_energized'
  })

  // 3. TOM'S SIMPLE STORAGE
  event.remove({ output: 'toms_storage:storage_terminal' })
  event.shaped('toms_storage:storage_terminal', [
    'IGI',
    'GCG',
    'IAI'
  ], {
    I: 'create:iron_sheet',
    G: '#c:glass_blocks',
    C: 'mekanism:basic_control_circuit',
    A: 'create:andesite_alloy'
  })

  event.remove({ output: 'toms_storage:crafting_terminal' })
  event.shaped('toms_storage:crafting_terminal', [
    'W W',
    'CTC',
    'EDE'
  ], {
    W: 'minecraft:crafting_table',
    C: 'mekanism:basic_control_circuit',
    T: 'toms_storage:storage_terminal',
    E: 'powah:steel_energized',
    D: '#c:gems/diamond'
  })

  event.remove({ output: 'toms_storage:adv_wireless_terminal' })
  event.shaped('toms_storage:adv_wireless_terminal', [
    'ENE',
    'WTW',
    'ECE'
  ], {
    E: 'minecraft:ender_eye',
    N: 'minecraft:netherite_ingot',
    W: 'toms_storage:wireless_terminal',
    T: 'toms_storage:crafting_terminal',
    C: 'mekanism:elite_control_circuit'
  })

  // 4. BETTER FURNACES REFORGED
  event.remove({ output: 'betterfurnacesreforged:iron_furnace' })
  event.shaped('betterfurnacesreforged:iron_furnace', [
    'III',
    'IFI',
    'IAI'
  ], {
    I: 'create:iron_sheet',
    F: 'minecraft:furnace',
    A: 'create:andesite_alloy'
  })

  event.remove({ output: 'betterfurnacesreforged:gold_furnace' })
  event.shaped('betterfurnacesreforged:gold_furnace', [
    'GGG',
    'GFG',
    'GCG'
  ], {
    G: '#c:ingots/gold',
    F: 'betterfurnacesreforged:iron_furnace',
    C: 'mekanism:basic_control_circuit'
  })

  event.remove({ output: 'betterfurnacesreforged:diamond_furnace' })
  event.shaped('betterfurnacesreforged:diamond_furnace', [
    'DDD',
    'DFD',
    'DED'
  ], {
    D: '#c:gems/diamond',
    F: 'betterfurnacesreforged:gold_furnace',
    E: 'powah:steel_energized'
  })

  event.remove({ output: 'betterfurnacesreforged:netherhot_furnace' })
  event.shaped('betterfurnacesreforged:netherhot_furnace', [
    'NNN',
    'NFN',
    'NBN'
  ], {
    N: 'minecraft:nether_bricks',
    F: 'betterfurnacesreforged:diamond_furnace',
    B: 'powah:crystal_blazing'
  })

  // 5. WAYSTONES & COMPASS
  event.remove({ output: 'waystones:warp_stone' })
  event.shaped('waystones:warp_stone', [
    'DED',
    'EPE',
    'DED'
  ], {
    D: '#c:dyes/purple',
    E: 'minecraft:ender_pearl',
    P: 'powah:steel_energized'
  })

  event.remove({ output: 'explorerscompass:explorerscompass' })
  event.shaped('explorerscompass:explorerscompass', [
    'ECE',
    'CPC',
    'ECE'
  ], {
    E: 'minecraft:cracked_stone_bricks',
    C: 'create:iron_sheet',
    P: 'minecraft:compass'
  })

  event.remove({ output: 'naturescompass:naturescompass' })
  event.shaped('naturescompass:naturescompass', [
    'ECE',
    'CPC',
    'ECE'
  ], {
    E: '#minecraft:saplings',
    C: 'create:andesite_alloy',
    P: 'minecraft:compass'
  })
})
