# 🌐 Firma League - Especificação Técnica de Integração Web (Cobblemon ⇄ Firebase)

Este documento foi elaborado para desenvolvedores e agentes de IA (como Cloud Coder / Claude Code) implementarem a ponte de sincronização entre o servidor de **Minecraft (Firma League / Cobblemon 1.21.1)** e a **Plataforma Web (Firebase Auth + Cloud Firestore)**.

---

## 🏗️ 1. Arquitetura da Solução

```mermaid
flowchart TD
    subgraph Minecraft["🎮 Servidor Minecraft (NeoForge 1.21.1)"]
        KJS["KubeJS 2101.8.5 Server Scripts"]
        CBL["Cobblemon 1.8.4 API"]
        RCT["Radical Cobblemon Trainers (Progression)"]
        BDG["BadgeBox / Pokemon Badges"]
    end

    subgraph WebApp["🌐 Plataforma Web (Next.js / Node.js)"]
        API["Webhooks REST (/api/minecraft/...)"]
        AUTH["Firebase Authentication (Google)"]
        FS["Cloud Firestore (Realtime Database)"]
        ADMIN["Painel Admin (Torneios & Chaveamento)"]
        UI["Interface Reativa (React / onSnapshot)"]
    end

    CBL --> KJS
    RCT --> KJS
    BDG --> KJS
    KJS -->|"POST JSON (X-Minecraft-Secret)"| API
    API --> FS
    AUTH --> UI
    FS -->|"onSnapshot() [Tempo Real]"| UI
    FS -->|"Lista de Treinadores Vinculados"| ADMIN
```

---

## 🔐 2. Autenticação e Segurança entre Servidor e Web
Todas as requisições enviadas do Minecraft para a API do site carregam um cabeçalho HTTP de segurança:
```http
X-Minecraft-Secret: <SUA_CHAVE_SECRETA_CONFIGURADA_NO_ENV>
Content-Type: application/json
```
O backend web deve validar esse header antes de processar qualquer webhook.

---

## 🎟️ 3. Fluxo de Vinculação de Conta (OTP Token) & Atribuição de Trainer ID

### Como funciona:
1. O jogador entra no Minecraft e digita `/vincular`.
2. O servidor gera um código alfanumérico curto (ex: `FIRMA-8K2P`), com validade de 15 minutos.
3. O servidor envia uma requisição para a rota `POST /api/minecraft/link/create`:
   ```json
   {
     "token": "FIRMA-8K2P",
     "minecraft_uuid": "d94721b0-7454-4d13-a691-d76a9c40cf4c",
     "minecraft_nick": "AshKetchum",
     "expires_at": 1793990000000
   }
   ```
4. O usuário entra no site, faz login com Google (Firebase Auth), vai até o perfil e digita o token `FIRMA-8K2P`.
5. A aplicação web verifica se o token existe em `link_tokens/{token}` e não expirou:
   * **Gera um Trainer ID oficial único** para esse jogador (ex: formato incremental ou padronizado como `TR-001`, `TR-002`, `TR-1042`).
   * Associa o `trainer_id`, `minecraft_uuid` e `minecraft_nick` no documento `users/{uid}`.
   * Cria/atualiza o registro em `players/{minecraft_uuid}` com o `trainer_id` e o `user_uid`.
   * Remove o documento temporário `link_tokens/{token}`.
6. A partir desse instante, a conta está vinculada e o jogador já possui seu ID Oficial de Treinador no ecossistema da liga.

#### Schema Firestore (`users/{uid}`):
```json
{
  "uid": "google_user_uid",
  "email": "treinador@gmail.com",
  "display_name": "Ash Ketchum",
  "minecraft": {
    "trainer_id": "TR-001",
    "uuid": "d94721b0-7454-4d13-a691-d76a9c40cf4c",
    "nick": "AshKetchum",
    "linked_at": "TIMESTAMP"
  }
}
```

---

## 📊 4. Schema de Dados do Jogador no Firestore (`players/{minecraft_uuid}`)

O servidor Minecraft envia periodicamente (ao conectar, desconectar, após capturas e conquistas de insígnias) um payload para `POST /api/minecraft/sync/player`.

```json
{
  "uuid": "d94721b0-7454-4d13-a691-d76a9c40cf4c",
  "trainer_id": "TR-001",
  "nick": "AshKetchum",
  "level_cap": 20,
  "current_series": "kanto",
  "badges": [
    {
      "id": "boulder_badge",
      "name": "Boulder Badge",
      "region": "kanto",
      "obtained_at": "2026-11-06T18:00:00Z"
    },
    {
      "id": "cascade_badge",
      "name": "Cascade Badge",
      "region": "kanto",
      "obtained_at": "2026-11-06T18:30:00Z"
    }
  ],
  "pokedex": {
    "seen_count": 85,
    "caught_count": 42,
    "total_species": 1025,
    "completion_percentage": 4.1,
    "seen_pokemon": ["bulbasaur", "ivysaur", "charmander", "charmeleon", "pikachu"],
    "caught_pokemon": ["charmander", "pikachu"]
  },
  "party": [
    {
      "slot": 1,
      "species": "pikachu",
      "nickname": "Sparky",
      "level": 20,
      "is_shiny": true,
      "gender": "MALE",
      "ability": "Static",
      "nature": "Timid",
      "held_item": "light_ball",
      "moves": [
        { "name": "Thunderbolt", "type": "electric" },
        { "name": "Quick Attack", "type": "normal" },
        { "name": "Iron Tail", "type": "steel" },
        { "name": "Thunder Wave", "type": "electric" }
      ],
      "ivs": { "hp": 31, "atk": 12, "def": 28, "spa": 31, "spd": 25, "spe": 31 },
      "evs": { "hp": 0, "atk": 0, "def": 4, "spa": 252, "spd": 0, "spe": 252 }
    }
  ],
  "updated_at": "2026-11-06T18:30:00Z"
}
```

---

## 🏆 5. Sistema de Torneios & Painel Administrativo de Cadastro

### 5.1. Painel Admin - Seleção de Jogadores Cadastrados
Na área de administração (`/admin/tournaments`):
* O admin **não precisa digitar o nick manualmente** (evitando erros de digitação como maiúsculas/minúsculas).
* O painel disponibiliza um componente **Select / Autocomplete de Treinadores Vinculados**, que busca diretamente da coleção `players`:
  * Exemplo de exibição no seletor:
    `[ 🔘 AshKetchum | ID: TR-001 (UUID: d947...) ]`
    `[ 🔘 GaryOak    | ID: TR-002 (UUID: 8e12...) ]`
* Ao selecionar os jogadores, o torneio associa o `trainer_id`, `uuid` e `nick` de cada participante.

### 5.2. Estrutura do Torneio (`tournaments/{tournament_id}`):
```json
{
  "id": "torneio-inauguracao-01",
  "title": "Torneio Cerulean Cup",
  "status": "in_progress", // upcoming | in_progress | completed
  "format": "single_elimination",
  "rounds_total": 3,
  "matches": [
    {
      "match_id": "r1_m1",
      "round": 1,
      "player1": {
        "trainer_id": "TR-001",
        "uuid": "d94721b0-7454-4d13-a691-d76a9c40cf4c",
        "nick": "AshKetchum"
      },
      "player2": {
        "trainer_id": "TR-002",
        "uuid": "8e123456-7454-4d13-a691-d76a9c40cf4c",
        "nick": "GaryOak"
      },
      "winner_uuid": null,
      "score": null,
      "status": "in_progress" // pending | in_progress | completed
    }
  ]
}
```

### 5.3. Webhook de Resultado de Partida (`POST /api/minecraft/tournament/match-result`):
Quando dois jogadores terminam uma batalha PvP de torneio dentro do Minecraft, o KubeJS detecta o vencedor pelo UUID e dispara:
```json
{
  "tournament_id": "torneio-inauguracao-01",
  "match_id": "r1_m1",
  "winner_uuid": "d94721b0-7454-4d13-a691-d76a9c40cf4c",
  "loser_uuid": "8e123456-7454-4d13-a691-d76a9c40cf4c",
  "score": "6-4",
  "duration_seconds": 184
}
```
* O backend compara o `winner_uuid` com os UUIDs da partida `r1_m1` e confirma a vitória com 100% de precisão.
* Como o chaveamento no site usa `onSnapshot`, o vencedor avança de fase **ao vivo na tela**, e o perfil dele já ganha o registro da vitória!

---

## 💻 6. Exemplo de Implementação KubeJS (Lado Servidor Minecraft)

O arquivo `kubejs/server_scripts/web_sync_bridge.js` utiliza a API Java `java.net.http.HttpClient` nativa do Java 21 para disparar webhooks sem congelar a thread do servidor:

```javascript
// Exemplo de envio assíncrono em KubeJS
const HttpClient = Java.loadClass('java.net.http.HttpClient');
const HttpRequest = Java.loadClass('java.net.http.HttpRequest');
const HttpResponse = Java.loadClass('java.net.http.HttpResponse');
const URI = Java.loadClass('java.net.URI');

function sendWebhook(endpoint, payload) {
    let client = HttpClient.newHttpClient();
    let jsonBody = JSON.stringify(payload);
    let request = HttpRequest.newBuilder()
        .uri(URI.create("https://seu-site.vercel.app/api/minecraft/" + endpoint))
        .header("Content-Type", "application/json")
        .header("X-Minecraft-Secret", "SEU_TOKEN_SECRETO")
        .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
        .build();

    client.sendAsync(request, HttpResponse.BodyHandlers.ofString());
}
```

---

## 🛡️ 7. Regras de Segurança do Firestore (`firestore.rules`)
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Perfil do Usuário
    match /users/{userId} {
      allow read: if true;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Dados sincronizados do Minecraft e Lista de Treinadores
    match /players/{playerId} {
      allow read: if true;
      allow write: if false; // Apenas a API com Admin SDK pode escrever
    }
    
    // Torneios
    match /tournaments/{tournamentId} {
      allow read: if true;
      allow write: if false; // Apenas a API com Admin SDK pode escrever
    }
  }
}
```
