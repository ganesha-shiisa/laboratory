# 🧪 laboratory

> Personal R&D Sandbox & Experimental Code Base
>
> 日々のアイデア検証、技術スパイク（調査・実験）、プロトタイプ実装を保存・蓄積する実験室リポジトリ。

## 🔬 ディレクトリ構造 (Directory Structure)

```text
laboratory/
├── docs/                      # GitHub Pages 公開用 Web アプリ群
├── euclidean_algorithm/       # ユークリッドの互除法による幾何分割
├── logarithmic_spiral/        # 正多角形による対数螺旋
├── fermat_spiral/             # フェルマー螺旋の可視化
├── congruence/                # 合同算術の可視化
└── README.md
```

## 💡 実験一覧 (Experiments)

| 日付         | カテゴリ | 実験タイトル / 概要                | 主な使用技術                      | 備考                              |
| ------------ | -------- | ---------------------------------- | --------------------------------- | --------------------------------- |
| `2026-11-06` | `Math`   | ユークリッドの互除法による幾何分割 | Python (Pygame), HTML5 Canvas, JS | 数学から創るジェネラティブアート, |
| `2026-11-08` | `Math`   | 正多角形による対数螺旋             | Python (Pygame), HTML5 Canvas, JS | 数学から創るジェネラティブアート, |
| `2026-11-10` | `Math`   | フェルマー螺旋の描画・比率検証     | Python (Pygame), HTML5 Canvas, JS | 数学から創るジェネラティブアート, |
| `2026-11-13` | `Math`   | 合同算術の可視化                   | Python (Pygame), HTML5 Canvas, JS | 数学から創るジェネラティブアート, |
| `Plan`       | `Math`   | セルオートマトン                   |                                   | 数学から創るジェネラティブアート, |
| `Plan`       | `Math`   | 正六角形セルオートマトン           |                                   | 数学から創るジェネラティブアート, |
| `Plan`       | `Math`   | 曲線                               |                                   | 数学から創るジェネラティブアート, |

## 🚀 新規実験の進め方 (Workflow)

1. 適切な言語・カテゴリフォルダ下に新規プロジェクト用ディレクトリを作成
2. 検証が完了したら、ルートの `README.md` のテーブルにログを追記

## 🛡️ 注意事項 (Security Rules)

- **環境変数 / 機密情報**: APIキーや認証トークンは直接記述せず、必ず `.env` などを利用して `.gitignore` の対象とすること。
- **依存関係**: 大規模なライブラリを導入する場合は、各実験フォルダ内で完結させること。

## 📚 参考文献 (References)

- **『数学から創るジェネラティブアート ― Processingで学ぶかたちのデザイン』**
  - 著者: 巴山竜来
  - 出版社: 技術評論社 (2019)
  - [書籍詳細 (gihyo.jp)](https://gihyo.jp/book/2019/978-4-297-10463-4)
  - ※ `euclidean_algorithm`（幾何分割）、`logarithmic_spiral`（対数螺旋描画）、`fermat_spiral`（フェルマー螺旋描画）、および `congruence`（合同算術の可視化）のアルゴリズムの参考にしました。
