# 🏆 Firma League - Modpack & Server Repository (Cobblemon NeoForge 1.21.1)

Bem-vindo ao repositório oficial da configuração, datapacks, scripts e integração web da **Firma League**!

## 📌 Visão Geral do Modpack
* **Versão do Minecraft:** 1.21.1
* **Modloader:** NeoForge (v21.1.x)
* **Cobblemon:** 1.8.4
* **Progressão & Ginásios:** Radical Cobblemon Trainers (RCTMod) com Level Cap escalonado (Inicial: 20)
* **Economia & Vilas:** Cobbleverse BCA Villages, CobbleDollars e Poké Marts integrados
* **Geração de Pokémon:** Spawns 100% calibrados conforme o Cobbleverse (1.025 tabelas de spawn pool completas)

---

## 📁 Estrutura do Repositório
* 📂 [`docs/`](docs/) - Especificação completa para integração com a plataforma web (Firebase Auth + Firestore).
  * 📄 [`docs/WEB_INTEGRATION_SPEC.md`](docs/WEB_INTEGRATION_SPEC.md) - Manual técnico detalhado para desenvolvedores web e IAs (Cloud Coder / Claude Code).
* 📂 [`kubejs/`](kubejs/) - Scripts de automação, eventos, progressão de Level Cap e webhooks.
* 📂 [`config/`](config/) - Configurações detalhadas dos mods (Cobblemon, RCTMod, Catch Indicator, Catch Rate Display, etc.).
* 📂 [`defaultconfigs/`](defaultconfigs/) - Configurações padrão de servidor (regras de Level Cap e progressão).
* 📂 [`server/datapacks/`](server/datapacks/) - Datapacks de líderes de ginásio, cidades Cobbleverse e balanceamento de itens.
* 📂 [`packwiz/`](packwiz/) - Scripts de build e empacotamento dos pacotes de cliente e servidor.
* 📄 [`MODLIST.md`](MODLIST.md) - Catálogo completo de todos os 130 mods instalados e suas versões.

---

## 🌐 Integração Web em Tempo Real
A plataforma web conversa em tempo real com o servidor Minecraft através de:
1. **Vinculação de Contas:** Comando `/vincular` gera um token temporário para vincular o perfil do Google ao jogador do Minecraft.
2. **Perfil do Treinador:** Exibição ao vivo de Insígnias conquistadas, Pokédex (Vistos vs Capturados) e Time Pokémon atual (com IVs, moveset e status Shiny).
3. **Torneios In-Game:** Placar ao vivo e chaveamento atualizado automaticamente após cada batalha PvP oficial.

Para detalhes completos de schemas do Firestore e rotas de API, consulte o documento [`docs/WEB_INTEGRATION_SPEC.md`](docs/WEB_INTEGRATION_SPEC.md).
