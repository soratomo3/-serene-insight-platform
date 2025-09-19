# コードスタイル・規約 - Serena洞察発見エンジン

## Python コード規約

### ファイル構造
- **エンコーディング**: UTF-8
- **shebang**: `#!/usr/bin/env python3` (実行可能ファイル)
- **docstring**: トップレベルに日本語での機能説明

### 命名規約
- **関数・変数**: snake_case (`search_files`, `max_results`)
- **クラス**: PascalCase (`SerenaInsightEngine`, `ExcelManager`)
- **定数**: UPPER_CASE
- **プライベート**: アンダースコア接頭辞 (`_private_method`)

### コメント・ドキュメンテーション
- **日本語コメント**: 主要機能の説明は日本語
- **docstring**: 関数の説明は日本語で詳細に
- **型ヒント**: 必須 (`typing` モジュール使用)

例:
```python
def search_files(
    directory: str = ".",
    keyword: str = "",
    file_pattern: str = "*.*",
    case_sensitive: bool = False,
    max_results: int = 100,
) -> Dict[str, Any]:
    """
    指定されたディレクトリ内のファイルからキーワードを検索します。
    """
```

### インポート順序
1. 標準ライブラリ
2. サードパーティライブラリ  
3. ローカルモジュール

### エラーハンドリング
- try-except文でエラーを適切にキャッチ
- エラーメッセージは日本語で分かりやすく
- ログは `logging` モジュール使用

## TypeScript コード規約

### 命名規約
- **interface**: PascalCase (`DataPoint`, `Insight`, `TimeSeriesData`)
- **クラス**: PascalCase (`SerenaInsightEngine`)
- **メソッド・変数**: camelCase (`analyzeSeasonality`)
- **型定義**: 明示的な型指定

### コメント
- **日本語コメント**: クラス・メソッドの説明
- **JSDoc形式**: `/** */` を使用

例:
```typescript
/**
 * Serena洞察発見エンジン
 * データから自動的に洞察を抽出し、アクション可能な推奨事項を生成
 */
class SerenaInsightEngine {
  /**
   * 季節性パターン分析
   */
  analyzeSeasonality(data: TimeSeriesData[]): Insight[] {
```

## 共通規約

### 国際化
- UI文字列、メッセージ: 日本語
- 変数名、関数名: 英語
- コメント: 日本語

### データ構造
- 戻り値は明確な型定義
- エラー情報も構造化して返却
- 設定可能なパラメータは明示

### ログ・デバッグ
- ログレベル適切に設定
- 重要な処理にはINFOレベルログ
- エラーはERRORレベルで詳細情報含む