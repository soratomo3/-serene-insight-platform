# タスク完了時のチェックリスト

## コード品質チェック

### Python
```bash
# 1. コードフォーマット
black .

# 2. インポート整理
isort .

# 3. 型チェック（設定があれば）
mypy src/

# 4. テスト実行
pytest
pytest-asyncio  # 非同期テスト用
```

### TypeScript
```bash
# TypeScriptコンパイル（tsconfigがあれば）
tsc --noEmit

# Node.jsテスト（package.jsonがあれば）
npm test
```

## 機能テスト

### MCPサーバーテスト
```bash
# サーバー起動テスト
python src/unified-mcp-server.py
```

### 設定確認
```bash
# MCP設定確認
python setup_mcp_config.py
```

## ファイル整理

### 不要ファイル削除
- `__pycache__/` ディレクトリ
- `*.pyc` ファイル
- `.DS_Store` ファイル

### Git状態確認
```bash
git status
git diff
```

## ドキュメント更新

### 変更があった場合のみ
- README.md の更新
- コメント・docstringの更新
- メモリファイル（必要時）

## デプロイ前確認

### 依存関係
- requirements.txt の更新確認
- pyproject.toml のバージョン確認

### 環境変数・設定
- 必要な環境変数の確認
- 設定ファイルの妥当性確認

### セキュリティ
- 秘密情報がコミットされていないか
- .gitignore の適切性

## 注意事項

1. **テスト必須**: 新機能・修正後は必ずテスト実行
2. **フォーマット**: コミット前にblack実行
3. **型安全性**: 型ヒント必須、mypyエラー解決
4. **ログ**: 適切なログレベル設定
5. **エラーハンドリング**: 例外処理の実装確認

## 完了確認
- [ ] コードフォーマット完了
- [ ] テスト実行・パス
- [ ] 型チェック・パス  
- [ ] 不要ファイル削除
- [ ] Git状態確認
- [ ] 機能動作確認