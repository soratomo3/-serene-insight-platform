#!/usr/bin/env python3
"""
統合MCPサーバー - Serena洞察プラットフォーム用
ファイル操作、検索、Excel連携、洞察分析を統合

機能:
- ファイル操作 (読み書き、移動、削除)
- 高度なファイル検索 (パターンマッチ、内容検索)
- Excel操作 (セル読み書き、数式実行)
- 洞察データ管理 (結果保存、履歴管理)
"""

import asyncio
import logging
import os
import glob
import datetime
import json
from typing import Dict, List, Union, Optional, Any
import xlwings as xw
from mcp.server.fastmcp import FastMCP

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCPサーバーの初期化（Webダッシュボード無効化）
mcp = FastMCP("Serena統合プラットフォーム")

# ================================================================================
# ファイル検索・操作機能
# ================================================================================

@mcp.tool()
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
    try:
        directory = os.path.abspath(directory)
        
        if not os.path.exists(directory):
            return {"error": f"ディレクトリ '{directory}' が存在しません。"}
        
        if not keyword:
            return {"error": "検索キーワードを指定してください。"}
        
        results = []
        matched_files_count = 0
        
        for file_path in glob.glob(os.path.join(directory, file_pattern), recursive=True):
            if os.path.isfile(file_path):
                try:
                    matches = []
                    line_number = 0
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            for line in file:
                                line_number += 1
                                
                                if case_sensitive:
                                    if keyword in line:
                                        matches.append({
                                            "line_number": line_number,
                                            "content": line.strip()
                                        })
                                else:
                                    if keyword.lower() in line.lower():
                                        matches.append({
                                            "line_number": line_number,
                                            "content": line.strip()
                                        })
                    except UnicodeDecodeError:
                        continue
                    
                    if matches:
                        matched_files_count += 1
                        
                        if matched_files_count <= max_results:
                            results.append({
                                "file_path": file_path,
                                "matches": matches,
                                "match_count": len(matches)
                            })
                        else:
                            break
                            
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {str(e)}")
        
        return {
            "result": {
                "keyword": keyword,
                "directory": directory,
                "file_pattern": file_pattern,
                "total_files_matched": matched_files_count,
                "results": results
            }
        }
    except Exception as e:
        return {"error": f"検索中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def read_file(file_path: str) -> Dict[str, Any]:
    """
    指定されたファイルの内容を読み込みます。
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return {"error": f"ファイル '{file_path}' が存在しません。"}
        
        if not os.path.isfile(file_path):
            return {"error": f"パス '{file_path}' はファイルではありません。"}
        
        # ファイルサイズチェック（10MB以上は警告）
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:
            return {"error": f"ファイルサイズが大きすぎます（{file_size} bytes）。10MB未満のファイルのみ対応。"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            # バイナリファイルの場合
            with open(file_path, 'rb') as file:
                content = file.read()
                return {
                    "result": {
                        "path": file_path,
                        "size": file_size,
                        "type": "binary",
                        "message": "バイナリファイルです。内容は表示できません。"
                    }
                }
        
        return {
            "result": {
                "path": file_path,
                "size": file_size,
                "content": content,
                "type": "text",
                "line_count": len(content.splitlines()) if content else 0
            }
        }
    except Exception as e:
        return {"error": f"ファイル読み込み中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def write_file(
    file_path: str,
    content: str,
    overwrite: bool = False
) -> Dict[str, Any]:
    """
    指定されたパスにファイルを書き込みます。
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if os.path.exists(file_path) and not overwrite:
            return {"error": f"ファイル '{file_path}' は既に存在します。上書きするには overwrite=True を指定してください。"}
        
        # ディレクトリが存在しない場合は作成
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        
        return {
            "result": {
                "path": file_path,
                "size": len(content.encode('utf-8')),
                "message": "ファイルの書き込みが完了しました。"
            }
        }
    except Exception as e:
        return {"error": f"ファイル書き込み中にエラーが発生しました: {str(e)}"}

# ================================================================================
# Excel操作機能
# ================================================================================

class ExcelManager:
    def __init__(self):
        self.app: Optional[xw.App] = None
        self.workbook: Optional[xw.Book] = None
        self._ensure_invisible_excel()

    def _ensure_invisible_excel(self):
        """Excelアプリケーションが確実に非表示になるように設定"""
        try:
            # 既存のExcelプロセスも非表示にする
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                # Windowsの場合、Excelプロセスを非表示にする
                try:
                    subprocess.run(['taskkill', '/f', '/im', 'EXCEL.EXE'], 
                                 capture_output=True, check=False)
                except:
                    pass
            elif platform.system() == "Darwin":  # macOS
                # macOSの場合、Excelアプリケーションを非表示にする
                try:
                    subprocess.run(['osascript', '-e', 
                                  'tell application "System Events" to set visible of process "Microsoft Excel" to false'], 
                                 capture_output=True, check=False)
                except:
                    pass
        except Exception:
            # エラーが発生しても処理を続行
            pass

    def open_workbook(self, file_path: str, visible: bool = False) -> Dict[str, Any]:
        try:
            if self.app is None:
                # Excelアプリケーションを非表示で起動
                self.app = xw.App(visible=False)
                # 追加の非表示設定
                self.app.display_alerts = False
                self.app.screen_updating = False
            
            # ファイルを非表示で開く
            self.workbook = self.app.books.open(file_path)
            # ワークブックも非表示に設定
            if hasattr(self.workbook.app, 'visible'):
                self.workbook.app.visible = False
            
            return {
                "result": {
                    "file_path": file_path,
                    "sheet_count": len(self.workbook.sheets),
                    "sheet_names": [sheet.name for sheet in self.workbook.sheets],
                    "message": "Excelファイルを開きました。"
                }
            }
        except Exception as e:
            return {"error": f"Excelファイルを開けませんでした: {str(e)}"}

    def read_cell(self, sheet_name: str, cell_address: str) -> Dict[str, Any]:
        if not self.workbook:
            return {"error": "Excelファイルが開かれていません。"}
        
        try:
            sheet = self.workbook.sheets[sheet_name]
            value = sheet.range(cell_address).value
            
            return {
                "result": {
                    "sheet": sheet_name,
                    "cell": cell_address,
                    "value": value,
                    "type": type(value).__name__
                }
            }
        except Exception as e:
            return {"error": f"セル読み取りエラー: {str(e)}"}

    def write_cell(self, sheet_name: str, cell_address: str, value: Any) -> Dict[str, Any]:
        if not self.workbook:
            return {"error": "Excelファイルが開かれていません。"}
        
        try:
            sheet = self.workbook.sheets[sheet_name]
            sheet.range(cell_address).value = value
            
            return {
                "result": {
                    "sheet": sheet_name,
                    "cell": cell_address,
                    "value": value,
                    "message": f"セル {sheet_name}!{cell_address} に値を書き込みました。"
                }
            }
        except Exception as e:
            return {"error": f"セル書き込みエラー: {str(e)}"}

    def save_workbook(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        if not self.workbook:
            return {"error": "Excelファイルが開かれていません。"}
        
        try:
            # 保存前にも非表示設定を確認
            if self.app:
                self.app.visible = False
                self.app.display_alerts = False
            
            if file_path:
                self.workbook.save(file_path)
            else:
                self.workbook.save()
            
            return {
                "result": {
                    "message": f"ワークブックを保存しました: {file_path or '現在のファイル'}"
                }
            }
        except Exception as e:
            return {"error": f"保存エラー: {str(e)}"}

# Excel操作のインスタンス
excel_manager = ExcelManager()

@mcp.tool()
def excel_open_file(file_path: str, visible: bool = False) -> Dict[str, Any]:
    """Excelファイルを開く（デフォルトで非表示）"""
    # 強制的に非表示モードで開く
    return excel_manager.open_workbook(file_path, False)

@mcp.tool()
def excel_read_cell(sheet_name: str, cell_address: str) -> Dict[str, Any]:
    """Excelセルの値を読み取る"""
    return excel_manager.read_cell(sheet_name, cell_address)

@mcp.tool()
def excel_write_cell(sheet_name: str, cell_address: str, value: Any) -> Dict[str, Any]:
    """Excelセルに値を書き込む"""
    return excel_manager.write_cell(sheet_name, cell_address, value)

@mcp.tool()
def excel_save_workbook(file_path: Optional[str] = None) -> Dict[str, Any]:
    """Excelワークブックを保存"""
    return excel_manager.save_workbook(file_path)

# ================================================================================
# 洞察データ管理機能
# ================================================================================

@mcp.tool()
def save_insight_result(
    analysis_name: str,
    insights: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    洞察分析結果を保存します。
    """
    try:
        # 保存ディレクトリの作成
        insights_dir = "insights_results"
        if not os.path.exists(insights_dir):
            os.makedirs(insights_dir)
        
        # タイムスタンプ付きファイル名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{analysis_name}_{timestamp}.json"
        file_path = os.path.join(insights_dir, filename)
        
        # 結果データの構造化
        result_data = {
            "analysis_name": analysis_name,
            "timestamp": datetime.datetime.now().isoformat(),
            "total_insights": len(insights),
            "high_priority_count": len([i for i in insights if i.get('priority') == 'high']),
            "metadata": metadata or {},
            "insights": insights
        }
        
        # JSON形式で保存
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        return {
            "result": {
                "file_path": file_path,
                "analysis_name": analysis_name,
                "insights_count": len(insights),
                "message": "洞察結果を保存しました。"
            }
        }
    except Exception as e:
        return {"error": f"洞察結果保存中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def list_insight_results(limit: int = 10) -> Dict[str, Any]:
    """
    保存された洞察結果の一覧を取得します。
    """
    try:
        insights_dir = "insights_results"
        if not os.path.exists(insights_dir):
            return {"result": {"results": [], "message": "保存された洞察結果がありません。"}}
        
        results = []
        files = glob.glob(os.path.join(insights_dir, "*.json"))
        files.sort(key=os.path.getmtime, reverse=True)  # 更新日時でソート
        
        for file_path in files[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                results.append({
                    "file_path": file_path,
                    "analysis_name": data.get("analysis_name", "Unknown"),
                    "timestamp": data.get("timestamp"),
                    "insights_count": data.get("total_insights", 0),
                    "high_priority_count": data.get("high_priority_count", 0)
                })
            except Exception as e:
                logger.warning(f"Error reading insight result file {file_path}: {e}")
        
        return {
            "result": {
                "results": results,
                "total_found": len(results),
                "message": f"{len(results)}件の洞察結果を見つけました。"
            }
        }
    except Exception as e:
        return {"error": f"洞察結果一覧取得中にエラーが発生しました: {str(e)}"}

# ================================================================================
# システム管理機能
# ================================================================================

@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """
    システムの状態を取得します。
    """
    try:
        current_dir = os.getcwd()
        
        # ディスク使用量
        disk_usage = {}
        if os.path.exists(current_dir):
            total, used, free = 0, 0, 0
            try:
                import shutil
                total, used, free = shutil.disk_usage(current_dir)
            except:
                pass
            disk_usage = {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2)
            }
        
        # ファイル統計
        file_stats = {}
        try:
            all_files = glob.glob("**/*", recursive=True)
            files = [f for f in all_files if os.path.isfile(f)]
            dirs = [f for f in all_files if os.path.isdir(f)]
            
            file_stats = {
                "total_files": len(files),
                "total_directories": len(dirs),
                "insight_results": len(glob.glob("insights_results/*.json")) if os.path.exists("insights_results") else 0
            }
        except:
            pass
        
        return {
            "result": {
                "current_directory": current_dir,
                "excel_connected": excel_manager.workbook is not None,
                "disk_usage": disk_usage,
                "file_statistics": file_stats,
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "running"
            }
        }
    except Exception as e:
        return {"error": f"システム状態取得中にエラーが発生しました: {str(e)}"}

# ================================================================================
# サーバー実行
# ================================================================================

if __name__ == "__main__":
    print("🚀 Serena統合MCPサーバーを開始します...")
    print("機能:")
    print("  📁 ファイル操作・検索")
    print("  📊 Excel操作") 
    print("  🧠 洞察データ管理")
    print("  ⚙️  システム管理")
    print("=" * 50)
    
    # Webサーバー無効化のため、環境変数でWebポートを無効化
    os.environ['FASTMCP_DISABLE_WEB'] = '1'
    os.environ['FASTMCP_WEB_PORT'] = '0'
    
    try:
        # MCPサーバーをWebUI無しで起動
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\n👋 サーバーを停止しています...")
        # Excel関連のクリーンアップ（非表示で実行）
        try:
            if excel_manager.workbook:
                excel_manager.workbook.close()
            if excel_manager.app:
                excel_manager.app.visible = False  # 終了時も非表示を保持
                excel_manager.app.quit()
        except Exception as e:
            print(f"Excel終了処理エラー: {e}")
    except Exception as e:
        print(f"❌ サーバー実行エラー: {e}")
