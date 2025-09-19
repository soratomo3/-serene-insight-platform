#!/usr/bin/env python3
"""
Excel連携MCPサーバー - 基本版
設置場所: C:\Users\[ユーザー名]\Documents\MCP\excel-connector\excel_mcp_server.py
"""

import asyncio
import logging
from typing import Any, Optional
import xlwings as xw
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelMCPServer:
    def __init__(self):
        self.app: Optional[xw.App] = None
        self.workbook: Optional[xw.Book] = None
        self.server = Server("excel-connector")
        self._register_tools()

    def _register_tools(self):
        """MCPツールの登録"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="open_excel_file",
                    description="Excelファイルを開く",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "開くExcelファイルのパス"
                            },
                            "visible": {
                                "type": "boolean",
                                "description": "Excelアプリケーションを表示するか",
                                "default": True
                            }
                        },
                        "required": ["file_path"]
                    }
                ),
                Tool(
                    name="read_cell",
                    description="指定されたセルの値を読み取る",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sheet_name": {
                                "type": "string",
                                "description": "シート名"
                            },
                            "cell_address": {
                                "type": "string",
                                "description": "セルアドレス (例: A1, B2)"
                            }
                        },
                        "required": ["sheet_name", "cell_address"]
                    }
                ),
                Tool(
                    name="write_cell",
                    description="指定されたセルに値を書き込む",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sheet_name": {
                                "type": "string",
                                "description": "シート名"
                            },
                            "cell_address": {
                                "type": "string",
                                "description": "セルアドレス (例: A1, B2)"
                            },
                            "value": {
                                "type": ["string", "number", "boolean"],
                                "description": "書き込む値"
                            }
                        },
                        "required": ["sheet_name", "cell_address", "value"]
                    }
                ),
                Tool(
                    name="execute_formula",
                    description="指定されたセルに数式を設定する",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "sheet_name": {
                                "type": "string",
                                "description": "シート名"
                            },
                            "cell_address": {
                                "type": "string",
                                "description": "セルアドレス (例: A1, B2)"
                            },
                            "formula": {
                                "type": "string",
                                "description": "Excel数式 (例: =SUM(A1:A10))"
                            }
                        },
                        "required": ["sheet_name", "cell_address", "formula"]
                    }
                ),
                Tool(
                    name="save_workbook",
                    description="ワークブックを保存する",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "保存先ファイルパス（省略時は現在のファイル）"
                            }
                        }
                    }
                ),
                Tool(
                    name="list_sheets",
                    description="ワークブック内のシート一覧を取得する",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
            try:
                if name == "open_excel_file":
                    return await self._open_excel_file(
                        arguments["file_path"],
                        arguments.get("visible", True)
                    )
                elif name == "read_cell":
                    return await self._read_cell(
                        arguments["sheet_name"],
                        arguments["cell_address"]
                    )
                elif name == "write_cell":
                    return await self._write_cell(
                        arguments["sheet_name"],
                        arguments["cell_address"],
                        arguments["value"]
                    )
                elif name == "execute_formula":
                    return await self._execute_formula(
                        arguments["sheet_name"],
                        arguments["cell_address"],
                        arguments["formula"]
                    )
                elif name == "save_workbook":
                    return await self._save_workbook(
                        arguments.get("file_path")
                    )
                elif name == "list_sheets":
                    return await self._list_sheets()
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [TextContent(type="text", text=f"エラー: {str(e)}")]

    async def _open_excel_file(self, file_path: str, visible: bool = True) -> list[TextContent]:
        """Excelファイルを開く"""
        try:
            if self.app is None:
                self.app = xw.App(visible=visible)
            
            self.workbook = self.app.books.open(file_path)
            
            return [TextContent(
                type="text", 
                text=f"Excelファイルを開きました: {file_path}\n"
                     f"シート数: {len(self.workbook.sheets)}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"ファイルを開けませんでした: {str(e)}")]

    async def _read_cell(self, sheet_name: str, cell_address: str) -> list[TextContent]:
        """セルの値を読み取る"""
        if not self.workbook:
            return [TextContent(type="text", text="Excelファイルが開かれていません")]
        
        try:
            sheet = self.workbook.sheets[sheet_name]
            value = sheet.range(cell_address).value
            
            return [TextContent(
                type="text",
                text=f"セル {sheet_name}!{cell_address} の値: {value}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"セル読み取りエラー: {str(e)}")]

    async def _write_cell(self, sheet_name: str, cell_address: str, value: Any) -> list[TextContent]:
        """セルに値を書き込む"""
        if not self.workbook:
            return [TextContent(type="text", text="Excelファイルが開かれていません")]
        
        try:
            sheet = self.workbook.sheets[sheet_name]
            sheet.range(cell_address).value = value
            
            return [TextContent(
                type="text",
                text=f"セル {sheet_name}!{cell_address} に値を書き込みました: {value}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"セル書き込みエラー: {str(e)}")]

    async def _execute_formula(self, sheet_name: str, cell_address: str, formula: str) -> list[TextContent]:
        """数式を実行する"""
        if not self.workbook:
            return [TextContent(type="text", text="Excelファイルが開かれていません")]
        
        try:
            sheet = self.workbook.sheets[sheet_name]
            sheet.range(cell_address).formula = formula
            result = sheet.range(cell_address).value
            
            return [TextContent(
                type="text",
                text=f"セル {sheet_name}!{cell_address} に数式を設定しました\n"
                     f"数式: {formula}\n"
                     f"結果: {result}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"数式実行エラー: {str(e)}")]

    async def _save_workbook(self, file_path: Optional[str] = None) -> list[TextContent]:
        """ワークブックを保存する"""
        if not self.workbook:
            return [TextContent(type="text", text="Excelファイルが開かれていません")]
        
        try:
            if file_path:
                self.workbook.save(file_path)
                message = f"ワークブックを保存しました: {file_path}"
            else:
                self.workbook.save()
                message = "ワークブックを保存しました"
            
            return [TextContent(type="text", text=message)]
        except Exception as e:
            return [TextContent(type="text", text=f"保存エラー: {str(e)}")]

    async def _list_sheets(self) -> list[TextContent]:
        """シート一覧を取得する"""
        if not self.workbook:
            return [TextContent(type="text", text="Excelファイルが開かれていません")]
        
        try:
            sheet_names = [sheet.name for sheet in self.workbook.sheets]
            sheets_text = "\n".join([f"- {name}" for name in sheet_names])
            
            return [TextContent(
                type="text",
                text=f"シート一覧:\n{sheets_text}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"シート一覧取得エラー: {str(e)}")]

    async def run(self):
        """MCPサーバーを開始する"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="excel-connector",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )

    def __del__(self):
        """リソースのクリーンアップ"""
        if self.workbook:
            self.workbook.close()
        if self.app:
            self.app.quit()

async def main():
    """メイン関数"""
    server = ExcelMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
