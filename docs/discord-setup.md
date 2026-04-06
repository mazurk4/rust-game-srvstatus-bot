# Discord Bot セットアップ手順

このドキュメントでは、本プロジェクトで使用するDiscord Botの作成方法と設定手順を説明します。

---

## 1. Discordアプリケーションの作成

1. 以下のページにアクセスします
   https://discord.com/developers/applications

2. 「New Application」をクリック

3. 任意の名前を入力して作成

---

## 2. Botの作成

1. 作成したアプリケーションを開く
2. 左メニューの「Bot」を選択
3. 「Add Bot」をクリック

---

## 3. Botトークンの取得（重要）

1. 「Bot」タブ内の「Reset Token」をクリック
2. 表示されたトークンをコピー

⚠️ **このトークンは絶対に公開しないでください**

`.env` に設定します：

```
DISCORD_TOKEN=ここにトークンを設定
```

---

## 4. 必要なIntentの有効化

Bot設定画面で以下を有効化してください：

* MESSAGE CONTENT INTENT（必要に応じて）

---

## 5. Botをサーバーに招待

1. 「OAuth2」→「URL Generator」を開く
2. 以下を選択：

### Scopes

* bot

### Bot Permissions

* Send Messages
* Read Messages/View Channels

3. 生成されたURLにアクセス
4. 招待したいサーバーを選択して追加

---

## 6. チャンネルIDの取得

1. Discordの設定で開発者モードを有効化
   ユーザー設定 → 詳細設定 → 開発者モード

2. 投稿したいチャンネルを右クリック → 「IDをコピー」

`.env` に設定：

```
CHANNEL_ID=123456789012345678
```

---

## 7. 動作確認

Botを起動し、以下を確認してください：

* サーバーにBotが表示される
* Botがオンラインになっている

---

## トラブルシューティング

* Botがオフライン
  → トークンが正しいか確認

* メッセージ送信できない
  → 権限設定を確認

* 何も反応しない
  → ログを確認

---

## セキュリティ注意事項

* `.env` ファイルはGitHubに公開しないでください
* `.env.example` を用意して共有するようにしてください
