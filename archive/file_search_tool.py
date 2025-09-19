# file_search_tool.py
from mcp.server.fastmcp import FastMCP
import os
import glob
import datetime
import json
import re
from typing import Dict, List, Union, Optional, Any

# MCPサーバーの初期化
mcp = FastMCP("ファイル検索ツール")


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

    Args:
        directory: 検索するディレクトリのパス。デフォルトは現在のディレクトリ。
        keyword: 検索するキーワード。
        file_pattern: 検索対象のファイルパターン（例: "*.txt", "*.py"）。デフォルトは全ファイル。
        case_sensitive: 大文字小文字を区別するかどうか。デフォルトはFalse。
        max_results: 返す最大結果数。デフォルトは100。

    Returns:
        検索結果を含む辞書
    """
    try:
        directory = os.path.abspath(directory)
        
        if not os.path.exists(directory):
            return {"error": f"ディレクトリ '{directory}' が存在しません。"}
        
        if not os.path.isdir(directory):
            return {"error": f"パス '{directory}' はディレクトリではありません。"}
        
        if not keyword:
            return {"error": "検索キーワードを指定してください。"}
        
        results = []
        matched_files_count = 0
        
        for file_path in glob.glob(os.path.join(directory, file_pattern), recursive=True):
            if os.path.isfile(file_path):
                try:
                    matches = []
                    line_number = 0
                    
                    # テキストファイルとして読み込み可能か確認
                    try:
                        with open(file_path, 'r', encoding='utf-8') as file:
                            for line in file:
                                line_number += 1
                                
                                # 大文字小文字の区別
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
                        # バイナリファイルなど、テキストとして読めない場合はスキップ
                        continue
                    
                    if matches:
                        matched_files_count += 1
                        
                        # 最大結果数のチェック
                        if matched_files_count <= max_results:
                            results.append({
                                "file_path": file_path,
                                "matches": matches,
                                "match_count": len(matches)
                            })
                        else:
                            # 最大結果数に達した場合は中断
                            break
                            
                except Exception as e:
                    # 個別ファイルの処理エラーは記録するが続行
                    print(f"Error processing file {file_path}: {str(e)}")
        
        return {
            "result": {
                "keyword": keyword,
                "directory": directory,
                "file_pattern": file_pattern,
                "case_sensitive": case_sensitive,
                "total_files_matched": matched_files_count,
                "results_limit": max_results,
                "results_returned": len(results),
                "results": results
            }
        }
    except Exception as e:
        return {"error": f"検索中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def list_files(
    directory: str = ".",
    file_pattern: str = "*.*",
    include_directories: bool = True,
    recursive: bool = False,
    max_results: int = 1000,
) -> Dict[str, Any]:
    """
    指定されたディレクトリ内のファイルとディレクトリを一覧表示します。

    Args:
        directory: 一覧表示するディレクトリのパス。デフォルトは現在のディレクトリ。
        file_pattern: 表示するファイルのパターン（例: "*.txt", "*.py"）。デフォルトは全ファイル。
        include_directories: ディレクトリも結果に含めるかどうか。デフォルトはTrue。
        recursive: サブディレクトリも再帰的に探索するかどうか。デフォルトはFalse。
        max_results: 返す最大結果数。デフォルトは1000。

    Returns:
        ファイルとディレクトリの一覧を含む辞書
    """
    try:
        directory = os.path.abspath(directory)
        
        if not os.path.exists(directory):
            return {"error": f"ディレクトリ '{directory}' が存在しません。"}
        
        if not os.path.isdir(directory):
            return {"error": f"パス '{directory}' はディレクトリではありません。"}
        
        files = []
        directories = []
        count = 0
        
        # glob 用のパターンを構築
        glob_pattern = os.path.join(directory, "**", file_pattern) if recursive else os.path.join(directory, file_pattern)
        
        for path in glob.glob(glob_pattern, recursive=recursive):
            if count >= max_results:
                break
            
            if os.path.isdir(path):
                if include_directories:
                    directories.append({
                        "path": path,
                        "name": os.path.basename(path),
                        "type": "directory"
                    })
                    count += 1
            else:
                files.append({
                    "path": path,
                    "name": os.path.basename(path),
                    "type": "file",
                    "size": os.path.getsize(path),
                    "extension": os.path.splitext(path)[1].lower(),
                    "modified": datetime.datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
                })
                count += 1
        
        return {
            "result": {
                "directory": directory,
                "file_pattern": file_pattern,
                "recursive": recursive,
                "total_items": len(files) + len(directories),
                "total_files": len(files),
                "total_directories": len(directories),
                "files": files,
                "directories": directories if include_directories else []
            }
        }
    except Exception as e:
        return {"error": f"ファイル一覧取得中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    ファイルまたはディレクトリの詳細情報を取得します。

    Args:
        file_path: 情報を取得するファイルまたはディレクトリのパス。

    Returns:
        ファイルまたはディレクトリの詳細情報を含む辞書
    """
    try:
        file_path = os.path.abspath(file_path)
        
        if not os.path.exists(file_path):
            return {"error": f"パス '{file_path}' が存在しません。"}
        
        stat_info = os.stat(file_path)
        is_file = os.path.isfile(file_path)
        is_dir = os.path.isdir(file_path)
        
        base_info = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "parent_directory": os.path.dirname(file_path),
            "is_file": is_file,
            "is_directory": is_dir,
            "size_bytes": stat_info.st_size,
            "created_time": datetime.datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified_time": datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "accessed_time": datetime.datetime.fromtimestamp(stat_info.st_atime).isoformat(),
            "permissions_octal": oct(stat_info.st_mode)[-3:],
        }
        
        # ファイル固有の情報
        if is_file:
            extension = os.path.splitext(file_path)[1].lower()
            base_info.update({
                "extension": extension,
                "mime_type": guess_mime_type(extension),
                "is_text_file": is_text_file(file_path),
                "is_binary_file": not is_text_file(file_path),
                "is_executable": os.access(file_path, os.X_OK)
            })
            
            # テキストファイルの場合、行数をカウント
            if is_text_file(file_path) and stat_info.st_size < 10 * 1024 * 1024:  # 10MB未満のファイルのみ
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for _ in f)
                    base_info["line_count"] = line_count
                except UnicodeDecodeError:
                    # テキストファイルと判断されたがデコードできない場合
                    base_info["is_text_file"] = False
                    base_info["is_binary_file"] = True
                    
        # ディレクトリ固有の情報
        elif is_dir:
            try:
                items = os.listdir(file_path)
                files = [item for item in items if os.path.isfile(os.path.join(file_path, item))]
                dirs = [item for item in items if os.path.isdir(os.path.join(file_path, item))]
                
                base_info.update({
                    "item_count": len(items),
                    "file_count": len(files),
                    "directory_count": len(dirs),
                    "is_empty": len(items) == 0
                })
            except PermissionError:
                base_info.update({
                    "permission_error": "ディレクトリの内容を読み取る権限がありません。"
                })
        
        return {"result": base_info}
    except Exception as e:
        return {"error": f"ファイル情報取得中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def find_files(
    directory: str = ".",
    name_pattern: str = "*",
    extension: str = "",
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    modified_after: Optional[str] = None,
    modified_before: Optional[str] = None,
    recursive: bool = True,
    max_results: int = 100,
) -> Dict[str, Any]:
    """
    指定された条件に一致するファイルを検索します。

    Args:
        directory: 検索するディレクトリのパス。デフォルトは現在のディレクトリ。
        name_pattern: ファイル名のパターン（ワイルドカード対応）。デフォルトは全てのファイル。
        extension: ファイル拡張子（例: ".txt", ".py"）。空の場合は全ての拡張子。
        min_size: 最小ファイルサイズ（バイト単位）。デフォルトは制限なし。
        max_size: 最大ファイルサイズ（バイト単位）。デフォルトは制限なし。
        modified_after: この日時以降に変更されたファイルを検索（ISO形式：2023-01-01T00:00:00）。
        modified_before: この日時以前に変更されたファイルを検索（ISO形式：2023-01-01T00:00:00）。
        recursive: サブディレクトリも再帰的に検索するかどうか。デフォルトはTrue。
        max_results: 返す最大結果数。デフォルトは100。

    Returns:
        検索条件に一致するファイルのリストを含む辞書
    """
    try:
        directory = os.path.abspath(directory)
        
        if not os.path.exists(directory):
            return {"error": f"ディレクトリ '{directory}' が存在しません。"}
        
        if not os.path.isdir(directory):
            return {"error": f"パス '{directory}' はディレクトリではありません。"}
        
        # 日付文字列をdatetimeオブジェクトに変換
        modified_after_dt = None
        modified_before_dt = None
        
        if modified_after:
            try:
                modified_after_dt = datetime.datetime.fromisoformat(modified_after)
            except ValueError:
                return {"error": f"不正な日時形式: {modified_after}。ISO形式（例: 2023-01-01T00:00:00）で指定してください。"}
                
        if modified_before:
            try:
                modified_before_dt = datetime.datetime.fromisoformat(modified_before)
            except ValueError:
                return {"error": f"不正な日時形式: {modified_before}。ISO形式（例: 2023-01-01T00:00:00）で指定してください。"}
        
        # 検索パターンの構築
        if extension and not extension.startswith('.'):
            extension = '.' + extension
            
        pattern = name_pattern
        if extension:
            if '*' in name_pattern:
                # ワイルドカードがある場合は注意が必要
                if name_pattern.endswith('*'):
                    # *で終わる場合は拡張子を追加
                    pattern = name_pattern[:-1] + extension
                else:
                    # それ以外の場合は元のパターンと拡張子の組み合わせを検索
                    pattern = name_pattern + extension
            else:
                # ワイルドカードがない場合は単純に拡張子を追加
                pattern = name_pattern + extension
        
        # 検索実行
        matching_files = []
        count = 0
        
        for root, _, files in os.walk(directory):
            if not recursive and root != directory:
                continue
                
            for file_name in files:
                if count >= max_results:
                    break
                    
                file_path = os.path.join(root, file_name)
                
                # ファイル名パターンのチェック
                if not glob.fnmatch.fnmatch(file_name, pattern):
                    continue
                
                # サイズのチェック
                file_size = os.path.getsize(file_path)
                if min_size is not None and file_size < min_size:
                    continue
                if max_size is not None and file_size > max_size:
                    continue
                
                # 更新日時のチェック
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                if modified_after_dt and mtime < modified_after_dt:
                    continue
                if modified_before_dt and mtime > modified_before_dt:
                    continue
                
                # 全ての条件を満たす場合、結果に追加
                matching_files.append({
                    "path": file_path,
                    "name": file_name,
                    "size": file_size,
                    "modified": mtime.isoformat(),
                    "extension": os.path.splitext(file_name)[1].lower(),
                })
                count += 1
            
            if count >= max_results:
                break
        
        return {
            "result": {
                "directory": directory,
                "search_criteria": {
                    "name_pattern": name_pattern,
                    "extension": extension,
                    "min_size": min_size,
                    "max_size": max_size,
                    "modified_after": modified_after,
                    "modified_before": modified_before,
                    "recursive": recursive
                },
                "total_matches": len(matching_files),
                "max_results": max_results,
                "files": matching_files
            }
        }
    except Exception as e:
        return {"error": f"ファイル検索中にエラーが発生しました: {str(e)}"}


# ヘルパー関数
def is_text_file(file_path: str) -> bool:
    """ファイルがテキストファイルかどうかを判定します。"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(4096)  # 最初の4KBを読み取る
        return True
    except UnicodeDecodeError:
        return False
    except Exception:
        return False


def guess_mime_type(extension: str) -> str:
    """ファイル拡張子からMIMEタイプを推測します。"""
    mime_types = {
        '.txt': 'text/plain',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.xml': 'application/xml',
        '.py': 'text/x-python',
        '.java': 'text/x-java',
        '.c': 'text/x-c',
        '.cpp': 'text/x-c++',
        '.h': 'text/x-c',
        '.hpp': 'text/x-c++',
        '.rb': 'text/x-ruby',
        '.go': 'text/x-go',
        '.php': 'text/x-php',
        '.pl': 'text/x-perl',
        '.sh': 'text/x-shellscript',
        '.bat': 'text/x-bat',
        '.csv': 'text/csv',
        '.md': 'text/markdown',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
        '.ico': 'image/x-icon',
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.webm': 'video/webm',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.zip': 'application/zip',
        '.rar': 'application/x-rar-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        '.7z': 'application/x-7z-compressed',
        '.exe': 'application/x-msdownload',
        '.dll': 'application/x-msdownload',
        '.bin': 'application/octet-stream',
        '.iso': 'application/x-iso9660-image',
        '.db': 'application/x-sqlite3',
        '.sql': 'application/sql',
    }
    
    return mime_types.get(extension.lower(), 'application/octet-stream')


# サーバー実行
if __name__ == "__main__":
    print("ファイル検索ツールサーバーを開始します...")
    mcp.run()
    