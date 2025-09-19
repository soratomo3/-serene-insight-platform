# file_operations_server.py
from mcp.server.fastmcp import FastMCP
import os
import shutil

# typingからList, Dict, Unionのみをインポート (Optionalは未使用のため削除)
from typing import List, Dict, Union

# pathlibとjsonは未使用のため削除
# import datetime をファイルの先頭に移動
import datetime

# MCPサーバーの初期化
mcp = FastMCP("ファイル操作ツール")


@mcp.tool()
def list_directory(
    directory_path: str = ".",
) -> Dict[str, Union[List[str], str]]:  # エラー時も考慮してUnionを追加
    """
    指定されたディレクトリ内のファイルとフォルダを一覧表示します。

    Args:
        directory_path: 一覧表示するディレクトリのパス。デフォルトは現在のディレクトリ。

    Returns:
        ディレクトリ内のファイルとフォルダのリストを含む辞書、またはエラーメッセージを含む辞書
    """
    try:
        # pathlib を使う場合 (一例):
        # p = Path(directory_path).resolve()
        # if not p.exists():
        #     return {"error": f"パス '{p}' は存在しません。"}
        # if not p.is_dir():
        #     return {"error": f"パス '{p}' はディレクトリではありません。"}
        # files = [item.name for item in p.iterdir() if item.is_file()]
        # directories = [item.name for item in p.iterdir() if item.is_dir()]
        # return {
        #     "path": str(p),
        #     "directories": directories,
        #     "files": files
        # }

        # os モジュールを使う現在の実装
        directory_path = os.path.abspath(directory_path)
        if not os.path.exists(directory_path):
            return {"error": f"パス '{directory_path}' は存在しません。"}

        if not os.path.isdir(directory_path):
            return {"error": f"パス '{directory_path}' はディレクトリではありません。"}

        contents = os.listdir(directory_path)
        files = []
        directories = []

        for item in contents:
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                directories.append(item)
            else:
                files.append(item)

        return {"path": directory_path, "directories": directories, "files": files}
    except Exception as e:
        return {"error": f"ディレクトリの一覧取得中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def read_file(file_path: str) -> Dict[str, Union[str, int]]:
    """
    指定されたファイルの内容を読み込みます。

    Args:
        file_path: 読み込むファイルのパス

    Returns:
        ファイルの内容と情報を含む辞書、またはエラーメッセージを含む辞書
    """
    try:
        file_path = os.path.abspath(file_path)
        if not os.path.exists(file_path):
            return {"error": f"ファイル '{file_path}' は存在しません。"}

        if not os.path.isfile(file_path):
            return {"error": f"パス '{file_path}' はファイルではありません。"}

        file_size = os.path.getsize(file_path)

        # ファイルサイズ制限 (1MB)
        MAX_FILE_SIZE = 1_000_000
        if file_size > MAX_FILE_SIZE:
            return {
                "error": f"ファイルサイズが大きすぎます ({file_size} バイト)。{MAX_FILE_SIZE // 1024 // 1024}MBを超えるファイルは読み込めません。"
            }

        try:
            # encodingは指定せず、バイナリとして読み込み、後でデコードを試みる方が堅牢な場合もある
            # ここではutf-8を維持
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # より具体的なエラーメッセージ
            return {
                "error": f"ファイル '{file_path}' はUTF-8でデコードできませんでした。テキストファイルではないか、エンコーディングが異なります。"
            }
        except Exception as e:  # ファイルオープン時の他のエラーもキャッチ
            return {
                "error": f"ファイル '{file_path}' のオープン中にエラーが発生しました: {str(e)}"
            }

        return {"path": file_path, "size": file_size, "content": content}
    except Exception as e:
        # このトップレベルのexceptは、abspathやgetsizeなどのエラーをキャッチ
        return {
            "error": f"ファイル読み込み処理中に予期せぬエラーが発生しました: {str(e)}"
        }


@mcp.tool()
def write_file(file_path: str, content: str, overwrite: bool = False) -> Dict[str, str]:
    """
    指定されたパスにファイルを書き込みます。

    Args:
        file_path: 書き込むファイルのパス
        content: ファイルに書き込む内容
        overwrite: 既存のファイルを上書きするかどうか。デフォルトはFalse。

    Returns:
        操作の結果を含む辞書
    """
    try:
        file_path = os.path.abspath(file_path)
        directory = os.path.dirname(file_path)

        # ディレクトリかどうかのチェックを追加
        if os.path.isdir(file_path):
            return {
                "error": f"指定されたパス '{file_path}' はディレクトリです。ファイルパスを指定してください。"
            }

        if os.path.exists(file_path) and not overwrite:
            return {
                "error": f"ファイル '{file_path}' は既に存在します。上書きするには overwrite=True を指定してください。"
            }

        # ディレクトリが存在しない場合は作成 (makedirsは存在していてもエラーにならない)
        os.makedirs(directory, exist_ok=True)  # exist_ok=True を追加

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "path": file_path,
            "status": "success",
            "message": f"ファイル '{file_path}' への書き込みが完了しました。",
        }
    except Exception as e:
        return {"error": f"ファイル書き込み中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def copy_file(
    source_path: str, destination_path: str, overwrite: bool = False
) -> Dict[str, str]:
    """
    ファイルをコピーします。

    Args:
        source_path: コピー元のファイルパス
        destination_path: コピー先のファイルパス
        overwrite: 既存のファイルを上書きするかどうか。デフォルトはFalse。

    Returns:
        操作の結果を含む辞書
    """
    try:
        source_path = os.path.abspath(source_path)
        destination_path = os.path.abspath(destination_path)

        if not os.path.exists(source_path):
            return {"error": f"コピー元ファイル '{source_path}' は存在しません。"}

        if not os.path.isfile(source_path):
            return {"error": f"コピー元パス '{source_path}' はファイルではありません。"}

        # コピー先がディレクトリの場合の考慮 (ファイル名を維持してコピー)
        if os.path.isdir(destination_path):
            destination_file = os.path.join(
                destination_path, os.path.basename(source_path)
            )
        else:
            destination_file = destination_path

        if os.path.exists(destination_file) and not overwrite:
            return {
                "error": f"コピー先ファイル '{destination_file}' は既に存在します。上書きするには overwrite=True を指定してください。"
            }

        # ディレクトリが存在しない場合は作成
        destination_dir = os.path.dirname(destination_file)
        os.makedirs(destination_dir, exist_ok=True)  # exist_ok=True を追加

        shutil.copy2(source_path, destination_file)  # copy2はメタデータもコピーする

        return {
            "source": source_path,
            "destination": destination_file,  # 実際のコピー先パスを返す
            "status": "success",
            "message": f"ファイル '{source_path}' から '{destination_file}' へのコピーが完了しました。",
        }
    except Exception as e:
        return {"error": f"ファイルコピー中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def move_file(
    source_path: str, destination_path: str, overwrite: bool = False
) -> Dict[str, str]:
    """
    ファイルを移動（または名前変更）します。

    Args:
        source_path: 移動元のファイルパス
        destination_path: 移動先のファイルパス
        overwrite: 既存のファイルを上書きするかどうか。デフォルトはFalse。

    Returns:
        操作の結果を含む辞書
    """
    try:
        source_path = os.path.abspath(source_path)
        destination_path = os.path.abspath(destination_path)

        if not os.path.exists(source_path):
            return {
                "error": f"移動元 '{source_path}' は存在しません。"
            }  # ファイル/ディレクトリ両方に対応

        # 移動元がディレクトリの場合も考慮 (shutil.moveはディレクトリも扱える)
        # if not os.path.isfile(source_path):
        #     return {"error": f"移動元パス '{source_path}' はファイルではありません。"}

        # 移動先がディレクトリの場合の考慮
        if os.path.isdir(destination_path):
            destination_target = os.path.join(
                destination_path, os.path.basename(source_path)
            )
        else:
            destination_target = destination_path

        # 上書きチェック (shutil.moveは上書きしてしまうため、事前チェックが必要)
        if os.path.exists(destination_target):
            if overwrite:
                # 上書きする場合、既存のファイル/ディレクトリを削除する必要がある場合がある
                # (特にファイル -> ディレクトリ、ディレクトリ -> ファイルの場合など)
                # shutil.move は既存のファイルは上書きするが、ディレクトリの上書きは挙動が異なる場合がある
                # より安全にするなら、削除処理を入れる
                try:
                    if os.path.isfile(destination_target):
                        os.remove(destination_target)
                    elif os.path.isdir(destination_target):
                        # ディレクトリの上書きは危険なので、エラーにするか、削除するか要検討
                        # shutil.rmtree(destination_target)
                        return {
                            "error": f"移動先 '{destination_target}' はディレクトリです。ディレクトリの上書きは現在サポートされていません。"
                        }
                except Exception as remove_e:
                    return {
                        "error": f"既存の移動先 '{destination_target}' の削除中にエラー: {remove_e}"
                    }
            else:
                return {
                    "error": f"移動先 '{destination_target}' は既に存在します。上書きするには overwrite=True を指定してください。"
                }

        # ディレクトリが存在しない場合は作成
        destination_dir = os.path.dirname(destination_target)
        os.makedirs(destination_dir, exist_ok=True)  # exist_ok=True を追加

        shutil.move(source_path, destination_target)

        return {
            "source": source_path,
            "destination": destination_target,  # 実際の移動先パスを返す
            "status": "success",
            "message": f"'{source_path}' から '{destination_target}' への移動が完了しました。",
        }
    except Exception as e:
        return {"error": f"ファイル/ディレクトリ移動中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def delete_file(file_path: str) -> Dict[str, str]:
    """
    ファイルを削除します。

    Args:
        file_path: 削除するファイルのパス

    Returns:
        操作の結果を含む辞書
    """
    try:
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            # 存在しない場合はエラーではなく成功としても良いかもしれない (冪等性)
            return {"error": f"ファイル '{file_path}' は存在しません。"}

        if not os.path.isfile(file_path):
            return {
                "error": f"パス '{file_path}' はファイルではありません。ディレクトリを削除するには delete_directory を使用してください。"
            }

        os.remove(file_path)

        return {
            "path": file_path,
            "status": "success",
            "message": f"ファイル '{file_path}' の削除が完了しました。",
        }
    except Exception as e:
        return {"error": f"ファイル削除中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def create_directory(directory_path: str) -> Dict[str, str]:
    """
    ディレクトリを作成します。

    Args:
        directory_path: 作成するディレクトリのパス

    Returns:
        操作の結果を含む辞書
    """
    try:
        directory_path = os.path.abspath(directory_path)

        # ファイルが既に存在する場合のエラーを追加
        if os.path.isfile(directory_path):
            return {"error": f"パス '{directory_path}' には既にファイルが存在します。"}

        # 既にディレクトリが存在する場合は成功として扱う (冪等性)
        if os.path.isdir(directory_path):
            return {
                "path": directory_path,
                "status": "success",
                "message": f"ディレクトリ '{directory_path}' は既に存在します。",
            }

        # makedirs は親ディレクトリも含めて作成, exist_ok=Trueで存在してもエラーにしない
        os.makedirs(directory_path, exist_ok=True)

        return {
            "path": directory_path,
            "status": "success",
            "message": f"ディレクトリ '{directory_path}' の作成が完了しました。",
        }
    except Exception as e:
        return {"error": f"ディレクトリ作成中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def delete_directory(directory_path: str, recursive: bool = False) -> Dict[str, str]:
    """
    ディレクトリを削除します。

    Args:
        directory_path: 削除するディレクトリのパス
        recursive: ディレクトリ内のファイルとサブディレクトリも削除するかどうか。デフォルトはFalse。

    Returns:
        操作の結果を含む辞書
    """
    try:
        directory_path = os.path.abspath(directory_path)

        if not os.path.exists(directory_path):
            # 存在しない場合はエラーではなく成功としても良いかもしれない (冪等性)
            return {"error": f"ディレクトリ '{directory_path}' は存在しません。"}

        if not os.path.isdir(directory_path):
            return {
                "error": f"パス '{directory_path}' はディレクトリではありません。ファイルを削除するには delete_file を使用してください。"
            }

        # ディレクトリが空でない場合
        if os.listdir(directory_path) and not recursive:
            return {
                "error": f"ディレクトリ '{directory_path}' は空ではありません。再帰的に削除するには recursive=True を指定してください。"
            }

        if recursive:
            shutil.rmtree(directory_path)
        else:
            # 空でなければ上でエラーになるので、ここは常に空のはず
            os.rmdir(directory_path)

        return {
            "path": directory_path,
            "status": "success",
            "message": f"ディレクトリ '{directory_path}' の削除が完了しました。",
        }
    except Exception as e:
        return {"error": f"ディレクトリ削除中にエラーが発生しました: {str(e)}"}


@mcp.tool()
def get_file_info(file_path: str) -> Dict[str, Union[str, int, bool]]:
    """
    ファイルまたはディレクトリの情報を取得します。

    Args:
        file_path: 情報を取得するファイルやディレクトリのパス

    Returns:
        ファイルまたはディレクトリの詳細情報を含む辞書、またはエラーメッセージを含む辞書
    """
    try:
        file_path = os.path.abspath(file_path)

        if not os.path.exists(file_path):
            return {"error": f"パス '{file_path}' は存在しません。"}

        stat_info = os.stat(file_path)
        is_file = os.path.isfile(file_path)
        is_dir = os.path.isdir(file_path)

        # datetime はファイルの先頭でインポート済み
        ctime = datetime.datetime.fromtimestamp(
            stat_info.st_ctime
        ).isoformat()  # ISO 8601形式推奨
        mtime = datetime.datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        atime = datetime.datetime.fromtimestamp(stat_info.st_atime).isoformat()

        info = {
            "path": file_path,
            "name": os.path.basename(file_path),
            "is_file": is_file,
            "is_directory": is_dir,
            "size_bytes": stat_info.st_size,
            "created_time": ctime,
            "modified_time": mtime,
            "accessed_time": atime,
            # パーミッションはプラットフォーム依存性が高いので注意
            "permissions_octal": oct(stat_info.st_mode)[-3:],
        }

        return info
    except Exception as e:
        return {"error": f"ファイル情報の取得中にエラーが発生しました: {str(e)}"}


# サーバーの実行
if __name__ == "__main__":
    # 実行時のトランスポートを指定できるようにする (例: stdio, websocket)
    # transport = os.environ.get("MCP_TRANSPORT", "stdio") # 環境変数から取得するなど
    # print(f"Starting MCP server with transport: {transport}")
    # mcp.run(transport=transport)
    mcp.run()  # デフォルト (おそらくstdio)
