# Serena洞察発見エンジン - プロジェクト概要

## プロジェクトの目的
このプロジェクトは「Serena洞察発見エンジン」で、データから自動的に意味のあるパターンを抽出し、ビジネス価値の高い洞察とアクション可能な推奨事項を生成する統合システムです。

## 技術スタック

### Python (メインサーバー)
- **Python >= 3.12** (pyproject.tomlで指定)
- **MCP (Model Context Protocol)** - コア通信プロトコル
- **xlwings** - Excel操作
- **pandas, numpy** - データ処理・分析
- **matplotlib, plotly** - データ可視化

### TypeScript (洞察エンジン)
- **TypeScript** - 洞察分析アルゴリズム実装
- `src/insight-engine.ts` - メイン分析エンジン
- `src/insight-demo.ts` - デモンストレーション

### 開発・テストツール
- **pytest** - Pythonテストフレームワーク
- **black** - Pythonコードフォーマッター
- **isort** - インポート整理

## 主要機能
1. **ファイル操作・検索** - 高度なファイル検索とパターンマッチ
2. **Excel統合** - セル操作、数式実行
3. **時系列分析** - 季節性検出、トレンド分析
4. **顧客セグメンテーション** - RFM分析
5. **相関関係分析** - 複数要因の関係性発見
6. **異常値検出** - 統計的手法による例外検出

## エントリーポイント
- **メインサーバー**: `src/unified-mcp-server.py`
- **設定セットアップ**: `setup_mcp_config.py`

## プロジェクト構造
```
/
├── src/
│   ├── unified-mcp-server.py (メインPythonサーバー)
│   ├── insight-engine.ts (TypeScript洞察エンジン)
│   └── insight-demo.ts (デモ実装)
├── pyproject.toml (Python依存関係)
├── requirements.txt (詳細依存関係)
└── README.md (詳細ドキュメント)
```