# Discord Crime Timer Bot for FiveM

FiveM 犯罪クールタイムをサーバー単位で管理し、残り時間に応じて自動通知するDiscord Bot。

犯罪タイマーと犯罪クール管理を分離し、シーン管理・参加者管理・解禁通知まで対応。

---

## Features

- 犯罪タイマー登録（/crime_set）
- 犯罪クールタイム登録（/cool_add）
- サーバー共有のタイマー管理
- 状態一覧表示（/crime_status）
- クールタイム一覧表示（/cool_status）
- クールタイム削除（/cool_remove）
- 自動通知（30 / 15 / 10 / 5分前）
- 解禁通知
- @crime ロールメンション対応
- Embed形式の通知・一覧表示
- 参加者情報の保存・表示
- 複数ルールクール管理（4時間 / 30分）

---

## Supported Crimes

パレト / 輸送機 / ボブキャ / ナイト / 軍事 / 飛行場
オイルリグ / 客船 / ヒューメイン / アーティファクト
ユニオン / パシフィック

---

## Commands

### /crime_set

犯罪タイマーを登録

```
/crime_set <crime> <minutes>
```

例：

```
/crime_set パシフィック 120
```

登録後：

- 30分前
- 15分前
- 10分前
- 5分前
- 解禁時

に自動通知。

---

### /crime_status

現在登録中の犯罪タイマー一覧を表示

```
/crime_status
```

Embed形式で表示。

---

### /cool_add

犯罪クールタイムを登録

```
/cool_add
```

登録内容：

- 犯罪名
- 参加者
- 逮捕者
- 逃走者
- 利確結果
- シーン終了時間

を保存。

登録したシーン時間を基準に：

- 4時間クール
- 30分クール

を自動管理。

---

### /cool_status

現在の犯罪クール一覧を表示

```
/cool_status
```

表示内容：

- 犯罪名
- 参加者
- 残り時間
- 適用クール

Embed形式で表示。

---

### /cool_remove

登録済みクールを削除

```
/cool_remove
```

削除対象を選択し、確認後削除。

---

### /set_crime_role

通知用ロールを設定

```
/set_crime_role <role>
```

例：

```
/set_crime_role @crime
```

---

## Notification Rules

自動通知タイミング：

### 犯罪タイマー

- 30分前
- 15分前
- 10分前
- 5分前
- 解禁時

### 犯罪クール

- 5分前
- 解禁時

通知先：

`@crime` ロール

---

## Architecture

- Python / discord.py（app_commands）
- サーバー単位でデータ管理
- asyncio監視ループ
- Embed UI
- Select / Button UI
- メモリ保存（再起動でリセット）

---

## Environment

```
TOKEN=YOUR_BOT_TOKEN
```

---

## Install

```
pip install discord.py python-dotenv asyncpg
```

---

## Run

```
python bot.py
```

---

## Notes

- 再起動でデータは消えます
- `/set_crime_role` は通知機能利用時に必須
- クール登録には参加者管理が含まれます
- スラッシュコマンド反映に時間がかかる場合があります

---

## Update

### v2

追加：

- 犯罪クール管理システム追加
- `/cool_add` 追加
- `/cool_status` 追加
- `/cool_remove` 追加
- 参加者情報保存
- 複数クール管理対応
- Embed UI対応
- 削除確認UI追加
- 通知システム改善
- ロール通知統一

---

## Future Improvements

- SQLite永続化
- タイマー編集機能
- クール編集機能
- Webダッシュボード
- マルチサーバー対応
- 権限管理

```

```
