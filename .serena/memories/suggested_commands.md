# 推奨コマンド - Serena洞察発見エンジン

## 開発環境セットアップ
```bash
# Python依存関係のインストール
pip install -r requirements.txt

# または uv使用時
uv sync

# MCP設定のセットアップ
python setup_mcp_config.py
```

## 実行コマンド

### メインサーバーの起動
```bash
# 統合MCPサーバーの起動
python src/unified-mcp-server.py
```

### テスト実行
```bash
# Pytestでテスト実行
pytest

# 非同期テスト対応
pytest-asyncio
```

### コードフォーマット・品質チェック
```bash
# Pythonコードフォーマット
black .

# インポート整理
isort .

# 型チェック（mypy設定があれば）
mypy src/
```

## システムユーティリティ (macOS/Darwin)
```bash
# ファイル一覧
ls -la

# ディレクトリ移動
cd <directory>

# ファイル検索
find . -name "*.py"

# 内容検索
grep -r "pattern" .

# Git操作
git status
git add .
git commit -m "message"
```

## Excelファイル操作
プロジェクトにはxlwingsを使ったExcel連携機能があります：
- Excel操作はPythonサーバー経由で実行
- セル読み書き、数式実行機能を提供

## TypeScript洞察エンジン
TypeScript部分は別途npm/yarnでのセットアップが必要：
```bash
# Node.js環境での実行（package.jsonがある場合）
npm install
npm run build
npm run dev
```

## 注意事項
- このプロジェクトはpython >=3.12が必要
- Windows環境ではpywin32が自動インストールされます
- macOSではExcel操作にMicrosoft Excel appが必要