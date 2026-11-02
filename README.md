# 🧪 laboratory

> Personal R&D Sandbox & Experimental Code Base
>
> 日々のアイデア検証、技術スパイク（調査・実験）、プロトタイプ実装を保存・蓄積する実験室リポジトリ。

## 🔬 ディレクトリ構造 (Directory Structure)

```text
laboratory/
└── README.md
```

## 💡 実験一覧 (Experiments)

| 日付         | カテゴリ | 実験タイトル / 概要 | 主な使用技術 |
| ------------ | -------- | ------------------- | ------------ |
| `yyyy-mm-dd` | `xxx`    | aaaaa               | bbbb         |

## 🚀 新規実験の進め方 (Workflow)

1. 適切な言語・カテゴリフォルダ下に新規プロジェクト用ディレクトリを作成
2. 検証が完了したら、ルートの `README.md` のテーブルにログを追記

## 🛡️ 注意事項 (Security Rules)

- **環境変数 / 機密情報**: APIキーや認証トークンは直接記述せず、必ず `.env` などを利用して `.gitignore` の対象とすること。
- **依存関係**: 大規模なライブラリを導入する場合は、各実験フォルダ内で完結させること。
