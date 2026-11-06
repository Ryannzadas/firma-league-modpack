# ==============================================================================
# Datapack Liga Pokémon & História - Inicialização do Servidor
# ==============================================================================

# Cria placar de Insígnias / Vitórias na Liga (visível no TAB se o admin ativar)
scoreboard objectives add insignias dummy {"text":"🏅 Insígnias","color":"gold","bold":true}
scoreboard objectives add vitorias_liga dummy {"text":"🏆 Vitórias Liga","color":"yellow","bold":true}

# Mensagem de confirmação no console ao carregar o datapack
tellraw @a[tag=admin] [{"text":"[Liga Pokémon] ","color":"gold","bold":true},{"text":"Sistema de Placar e Regras da Liga carregado com sucesso!","color":"green"}]
