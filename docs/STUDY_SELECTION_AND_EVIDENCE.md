# 歌詞評価・リスナー試験の層別と証拠ゲート（2026-11-25）

実際に試験を実施する前に、**何を変え、何の因果効果を主張できるか**を選定する。試験計画の合格は、歌詞の品質向上や実測結果ではない。

| 層 | 適用対象 | 主張できる範囲 | 対応状況 |
|---|---|---|---|
| **TEXT_ONLY** | 歌詞本文のみA/B | 文字で読んだ理解・印象。歌唱の評価はできない | 事前検査を実装、聴取者実測NOT_RUN |
| **LYRICS_ONLY_AUDIO_IF_CONTROLS_ACTUALLY_HOLD** | 同じメロディー・声・編曲・テンポ・ラウドネス等で歌詞だけ変更 | 他の条件が本当に同じと確認できれば歌詞差の評価候補 | 比較用WAV未収集。CIは仮の条件だけ検査 |
| **COMPOSITE_AUDIO_ONLY** | Suno等で別々に生成した2音源を比較 | 音楽作品全体の違い。歌詞だけの効果としない | 比較用WAV・実測なし |

## 実行コード

    python scripts/study_preflight.py --plan examples/study_preflight/unfinished_lyrics_only_plan.json
    python scripts/study_preflight.py --plan examples/study_preflight/hypothetical_composite_plan.json
    python scripts/study_preflight.py --plan examples/study_preflight/hypothetical_text_only_plan.json

機械可読仕様：[Study Plan v1 Schema](../schemas/study_plan.v1.schema.json)。分類器は、参加者への同意計画、ランダム提示計画、主要結果の事前設定、比較対象の制御条件を確認する。偽のPASSや未知フィールドは拒否する。

## 接続方式の選択との関係

- 音源制作前に実施できるのは **TEXT_ONLY** の計画。歌詞版IDと内容SHAは[Lyric Handoff v1](handoff_interface.md)で追跡。
- 曲を別々にSunoで生成した場合、音色・旋律・編曲が異なる可能性があるため **COMPOSITE_AUDIO_ONLY**。
- 純正VOCALOIDで歌詞のみを変えて再レンダリングする場合も、実際の音声が同条件になったか（発声時間等）を確認し、単独因果を断定しない。
- [制作側の公式／非公式IF選定表](https://github.com/Gacky-Lab/AI-VOCALOID-STUDIO/blob/main/docs/INTERFACE_SELECTION.md) は別資料。双方のCI成功はリスナーの実測にはならない。

## 未検証事項

現時点でリスナーの実測、効果サイズ、採点者間一致、翌日想起の結果は **すべてNOT_RUN**。計画ファイルの`measurement_state`は`NOT_RUN`のみ許容し、実測成果の記録は同意済みの別管理で行う。未公開の楽曲・個人の回答をGitHubに載せない。

架空のサンプルは実際の試験や有効性を証明するものではない。
