# Discord Crime Timer Bot for FiveM

FiveM 犯罪クールタイムをサーバー単位で管理し、残り時間に応じて自動通知するDiscord Bot。

---

## Features

- 犯罪クールタイム登録（/crime_set）
- サーバー共有のタイマー管理
- 状態一覧表示（/crime_status）
- 自動通知（30 / 15 / 10 / 5分前）
- 解禁通知
- @crime ロールメンション対応

---

## Supported Crimes

パレト / 輸送機 / ボブキャ / ナイト / 軍事 / 飛行場  
オイルリグ / 客船 / ヒューメイン / アーティファクト  
ユニオン / パシフィック  

---

## Commands

### /crime_set

クールタイムを登録

```
/crime_set <crime> <minutes>
```

例：

```
/crime_set パシフィック 120
```

---

### /crime_status

現在のクールタイム一覧を表示

```
/crime_status
```

---

### /set_crime_role

通知用ロールを設定

```
/set_crime_role <role>
```

---

## Notification Rules

自動通知タイミング：

- 30分前
- 15分前
- 10分前
- 5分前
- 解禁時

通知先：`@crime` ロール

---

## Architecture

- Python / discord.py（app_commands）
- サーバー単位でデータ管理
- asyncio監視ループ
- メモリ保存（再起動でリセット）

---

## Environment

```
TOKEN=YOUR_BOT_TOKEN
```

---

## Install

```
pip install discord.py python-dotenv
```

---

## Run

```
python bot.py
```

---

## Notes

- 再起動でデータは消えます
- `/set_crime_role` は必須設定
- スラッシュコマンド反映に数分かかる場合あり

---

## Future Improvements

- SQLite永続化
- タイマー編集・削除機能
- UI（Embed化）
- Webダッシュボード
- マルチサーバー対応
```
