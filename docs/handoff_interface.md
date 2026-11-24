# 歌詞 → 音楽制作：Lyric Handoff v1

2026-11-24時点の内部受渡し契約。**独自のローカルJSON形式であり、Suno MCP・VOCALOID MCPの公式インターフェースではありません。**

## 実行例（架空の作詞サンプル）

    python scripts/export_handoff.py --lyrics examples/handoff/fictional_lyrics.txt --song-id fictional-receipt-demo --version-id demo-b --scorecard examples/fictional-revision/scorecard-B.json --output output/handoff.json

出力：contract_version 1.0.0、song_id、lyric_version_id、language ja、lyrics_text、lyrics_sha256、任意のeditorial_assessment。
機械可読仕様：[v1 JSON Schema](../schemas/lyric_handoff.v1.schema.json)。

- 改行をLFに統一し、語句・空白・最終改行は修正しない。SHA-256は**変換後の歌詞本文のUTF-8バイト**に対して計算する。
- Version IDは歌詞本文と紐付け、変更後は新しいIDにする。ハッシュ不一致は受け手が拒否する。
- 同梱する採点は作者の仮評価であり、音声の再生・歌詞の想起・リスナー検証の結果ではない。
- 公開用の例は架空の歌詞のみ。未公開作品、試聴者の回答、Suno認証情報は渡さない。

## 実装済みと未実装

| 工程 | 状態 |
|---|---|
| UTF-8歌詞→バージョン管理付きJSON・SHA検査 | 実装済み・自動テスト |
| 8軸編集評価の任意添付 | 実装済み・自動テスト |
| 音符・モーラへの歌詞割当 | 未実装 |
| Suno・VOCALOID公式製品へ自動転送 | 未実装／実機検証待ち |

**注意：本形式はVOCALOIDのVPR/VSQXファイルでも、歌詞整列済みのSong IRでもありません。**
