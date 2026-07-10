# Discord Crime Timer Bot for FiveM

FiveMの犯罪タイマー・犯罪クールタイムをDiscord上でサーバー単位に管理するBotです。

犯罪タイマーと犯罪クールタイムを完全に分離し、参加者管理・自動通知・解禁管理まで一括で行えます。

---

# Features

- 犯罪タイマー登録（`/crime_set`）
- 犯罪クールタイム登録（`/cool_add`）
- 犯罪タイマー一覧表示（`/crime_status`）
- 犯罪クール一覧表示（`/cool_status`）
- 犯罪クール削除（`/cool_remove`）
- プレイヤー登録・削除・一覧管理
- Embed形式のUI表示
- 自動通知システム
- 解禁通知
- JST（日本時間）対応
- 解禁予定時刻（HH:MM）表示
- 参加者・逮捕者・逃走者・利確情報管理
- 4時間 / 30分クール同時管理
- Crime通知・Cool通知チャンネル分離
- サーバーごとの通知設定管理

---

# Supported Crimes

- パレト
- 輸送機
- ボブキャ
- ナイト
- 軍事
- 飛行場
- オイルリグ
- 客船
- ヒューメイン
- アーティファクト
- ユニオン
- パシフィック

---

# Commands

## Crime Timer

## `/crime_set`

犯罪タイマーを登録します。

```

/crime_set <crime> <minutes>

```

例：

```

/crime_set パシフィック 120

```

登録内容：

- 犯罪名
- 登録時間
- 解禁予定時刻（HH:MM）

自動通知：

- 30分前
- 15分前
- 10分前
- 5分前
- 解禁時

---

## `/crime_status`

現在登録中の犯罪タイマー一覧を表示します。

表示内容：

- 犯罪名
- 残り時間
- 解禁予定時刻（HH:MM）

---

# Crime Cooldown

## `/cool_add`

犯罪クールタイムを登録します。

登録内容：

- 犯罪名
- 参加者
- 逮捕者
- 逃走者
- 利確結果
- シーン終了時間

シーン終了時間を基準に以下のクールを自動管理します。

- 4時間クール
- 30分クール

登録時には：

- 5分前通知時刻
- 解禁予定時刻

を表示します。

---

## `/cool_status`

現在登録中の犯罪クール一覧を表示します。

表示内容：

- 犯罪名
- 参加者
- 適用クール
- 残り時間
- 解禁予定時刻（HH:MM）

---

## `/cool_remove`

登録済み犯罪クールを削除します。

削除対象を選択し、確認後削除します。

---

# Player Management

## `/player_add`

プレイヤーを登録します。

---

## `/player_remove`

登録済みプレイヤーを削除します。

---

## `/player_list`

登録プレイヤー一覧を表示します。

---

# Notification Settings

## `/set_crime_role`

通知用ロールを設定します。

```

/set_crime_role <role>

```

例：

```

/set_crime_role @crime

```

Crime Timer・Crime Cool両方で共通利用されます。

---

## `/set_crime_channel`

Crime Timer通知用チャンネルを設定します。

```

/set_crime_channel <channel>

```

例：

```

/set_crime_channel #crime

```

---

## `/set_cool_channel`

Crime Cool通知用チャンネルを設定します。

```

/set_cool_channel <channel>

```

例：

```

/set_cool_channel #cool

```

---

# Notification Rules

## Crime Timer

通知タイミング：

- 30分前
- 15分前
- 10分前
- 5分前
- 解禁時

通知内容：

- 犯罪名
- 残り時間
- 解禁予定時刻

---

## Crime Cooldown

通知タイミング：

- 15分前
- 5分前
- 解禁時

通知内容：

- 犯罪名
- 参加者
- クール種別
- 残り時間
- 解禁予定時刻

---

# Notification Channels

通知先はCrime TimerとCrime Coolで分離できます。

### Crime Timer

設定：

```

/set_crime_channel

```

通知例：

```

#crime

```

---

### Crime Cool

設定：

```

/set_cool_channel

```

通知例：

```

#cool

```

---

### Notification Role

設定：

```

/set_crime_role

```

Crime Timer・Crime Cool共通の通知ロールとして使用します。

---

# Architecture

- Python
- discord.py（app_commands）
- asyncio Timer Loop
- Embed UI
- Select Menu
- Button UI
- Modal UI
- サーバー単位データ管理
- JST時間管理
- メモリ保存（再起動でリセット）

---

# Environment

```env
TOKEN=YOUR_BOT_TOKEN
```

---

# Install

```bash
pip install discord.py python-dotenv asyncpg
```

---

# Run

```bash
python bot.py
```

---

# Notes

- データはメモリ保存のため、Bot再起動時にタイマー情報はリセットされます
- `/set_crime_role` は通知機能利用時に必須です
- `/set_crime_channel` と `/set_cool_channel` を設定することで通知先を分離できます
- クール登録にはプレイヤー登録が必要です
- スラッシュコマンド反映まで時間がかかる場合があります

---

# Update

## v3

### Crime Timer

追加・改善：

- Embed UIへ刷新
- JSTベースの時間管理へ変更
- 解禁予定時刻（HH:MM）表示追加
- 通知内容改善
- 通知判定ロジック改善
- 重複通知対策

---

### Crime Cooldown

追加・改善：

- Embed UIへ刷新
- 参加者情報表示改善
- 解禁予定時刻表示追加
- 15分前通知追加
- 5分前通知追加
- 解禁通知追加
- クール終了後の自動削除対応

---

### Notification System

追加・改善：

- Crime Timer通知とCrime Cool通知を分離
- 通知チャンネルを個別設定可能に変更
- 通知ロールを共通化
- Oracle本番環境で発生した重複通知問題を修正
- タイマー監視処理の安定化

---

# Future Improvements

- SQLiteによる永続化
- タイマー編集機能
- クール編集機能
- データ自動バックアップ
- Webダッシュボード
- 権限管理
- 通知履歴保存

```

```
