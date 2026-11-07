# 🏆 Firma League - Modpack & Server Repository (Cobblemon NeoForge 1.21.1 — v2.8.0)

Bem-vindo ao repositório oficial da configuração, datapacks, scripts KubeJS, documentação e integração web em tempo real da **Firma League (v2.8.0)**!

## 📌 Visão Geral do Modpack (v2.8.0)
* **Versão do Modpack:** `2.8.0` (`130 mods no cliente` / `115 mods no servidor dedicado`)
* **Versão do Minecraft:** `1.21.1`
* **Modloader:** `NeoForge` (`21.1.248+`)
* **Cobblemon:** `1.8.4` + **Mega Showdown** (Mega Evolução, Terastal, Z-Moves, Dynamax e Omni Ring)
* **Progressão & Ginásios:** Radical Cobblemon Trainers (`RCTMod 0.19.2`) com Level Cap escalonado por temporada (`Kanto: 60` | `Johto: 75` | `Hoenn: 90` | `Sinnoh: 100`)
* **Economia, Vilas & Estruturas:** Cobbleverse BCA Villages, CobbleDollars, Legendary Monuments, Dungeons & Taverns e Repurposed Structures
* **Engenharia da Firma:** Create `6.0.10`, Mekanism `10.7.19`, Powah! `6.2.10` e Applied Energistics 2 (`AE2`)
* **Geração de Pokémon:** Spawns 100% calibrados conforme o Cobbleverse (`1.025` tabelas de spawn pool completas)
* **Portal Web Oficial:** **[poke-firma.vercel.app](https://poke-firma.vercel.app/)**

---

## 📁 Estrutura do Repositório
* 📂 [`docs/`](docs/) - Documentação oficial do modpack, regras, lore e especificação técnica:
  * 📄 [`docs/MODLIST_E_INSTALACAO.md`](docs/MODLIST_E_INSTALACAO.md) - Lista categorizada dos **130 mods da v2.8.0**, funções de cada mod e guia de instalação (Cliente e Servidor).
  * 📄 [`docs/HISTORIA_E_RP_FIRMA_LEAGUE.md`](docs/HISTORIA_E_RP_FIRMA_LEAGUE.md) - Lore oficial *"A Anomalia das 4 Regiões"*, as 4 Eras da Engenharia da Firma e os 4 Atos da campanha.
  * 📄 [`docs/REGRAS_LIGA_POKEMON.md`](docs/REGRAS_LIGA_POKEMON.md) - Regulamento oficial das 4 temporadas, Level Caps (`60/75/90/100`), Clauses Smogon e formato dos torneios (`MD1`/`MD3`).
  * 📄 [`docs/WEB_INTEGRATION_SPEC.md`](docs/WEB_INTEGRATION_SPEC.md) - Documentação técnica da integração em tempo real entre o servidor Minecraft e **[poke-firma.vercel.app](https://poke-firma.vercel.app/)**.
* 📂 [`kubejs/`](kubejs/) - Scripts de receitas integradas, progressão de Level Cap e ponte de sincronização web (`kubejs/server_scripts/web_sync_bridge.js`).
* 📂 [`config/`](config/) - Configurações detalhadas dos mods (Cobblemon, RCTMod, Catch Indicator, Catch Rate Display, Xaero's, etc.).
* 📂 [`defaultconfigs/`](defaultconfigs/) - Configurações padrão de servidor e regras de progressão.
* 📂 [`server/datapacks/`](server/datapacks/) - Datapacks de líderes de ginásio, vilas Cobbleverse BCA e 1.025 tabelas de spawn.
* 📂 [`packwiz/`](packwiz/) - Scripts de empacotamento e automação dos pacotes de cliente e servidor.
* 📄 [`MODLIST.md`](MODLIST.md) - Tabela técnica bruta de todos os 130 arquivos `.jar`, Mod IDs e versões.

---

## 🌐 Integração Web em Tempo Real (`poke-firma.vercel.app`)
O servidor Minecraft conversa em tempo real com **[poke-firma.vercel.app](https://poke-firma.vercel.app/)** através do script [`kubejs/server_scripts/web_sync_bridge.js`](kubejs/server_scripts/web_sync_bridge.js):
1. **Vinculação de Contas (`/vincular`):** Gera um token único no jogo para vincular o perfil do site ao jogador do Minecraft e emitir o **Trainer ID (`TR-001`, `TR-002`...)**.
2. **Sincronização Ao Vivo (`/sincronizar` + Eventos Automáticos):** Atualiza automaticamente Insígnias conquistadas, Level Cap, Pokédex (Vistos e Capturados), **Time Atual (6 Pokémon com IVs, EVs, golpes, item, natureza, habilidade, Tera e Shiny)** e todas as **Boxes do PC**.
3. **Torneios Automatizados (`MD1` e `MD3`):** Ao término de qualquer batalha PvP no servidor entre jogadores inscritos num torneio aberto, o placar, os KOs e os times usados são enviados automaticamente para a chave do site!
