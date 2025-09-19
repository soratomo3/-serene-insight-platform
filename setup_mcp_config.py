#!/usr/bin/env python3
"""
Serena洞察プラットフォーム - MCPサーバー起動設定
統合MCPサーバーを適切な設定で起動します。
"""

import os
import sys
import json
from pathlib import Path

def create_mcp_config():
    """MCP接続設定を生成"""
    
    config = {
        "mcpServers": {
            "serena-insight-platform": {
                "command": "python3",
                "args": [
                    str(Path(__file__).parent / "src" / "unified-mcp-server.py")
                ],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent),
                    "MCP_LOG_LEVEL": "INFO"
                }
            }
        }
    }
    
    return config

def create_claude_desktop_config():
    """Claude Desktop用設定ファイルを生成"""
    
    config = create_mcp_config()
    
    # Claude Desktop設定パス
    home_dir = Path.home()
    config_dir = home_dir / "Library" / "Application Support" / "Claude"
    config_file = config_dir / "claude_desktop_config.json"
    
    # ディレクトリ作成
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # 既存設定があれば読み込み
    existing_config = {}
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
        except:
            pass
    
    # 設定をマージ
    if 'mcpServers' not in existing_config:
        existing_config['mcpServers'] = {}
    
    existing_config['mcpServers'].update(config['mcpServers'])
    
    # 設定を保存
    with open(config_file, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    return config_file

def create_serena_mcp_config():
    """Serena用MCP設定を生成"""
    
    config_dir = Path('.serena')
    config_file = config_dir / 'mcp_config.json'
    
    config = {
        "servers": [
            {
                "name": "serena-insight-platform",
                "type": "stdio",
                "command": ["python3", "src/unified-mcp-server.py"],
                "working_directory": str(Path.cwd()),
                "description": "Serena洞察プラットフォーム統合サーバー",
                "capabilities": [
                    "file_operations",
                    "excel_operations", 
                    "data_analysis",
                    "insight_management"
                ]
            }
        ],
        "default_server": "serena-insight-platform"
    }
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    return config_file

def main():
    """メイン設定作成処理"""
    
    print("🔧 Serena洞察プラットフォーム MCP設定作成")
    print("=" * 50)
    
    try:
        # 1. Claude Desktop設定
        claude_config = create_claude_desktop_config()
        print(f"✅ Claude Desktop設定: {claude_config}")
        
        # 2. Serena MCP設定  
        serena_config = create_serena_mcp_config()
        print(f"✅ Serena MCP設定: {serena_config}")
        
        print("\n📋 接続確認手順:")
        print("1. 統合MCPサーバーのテスト起動:")
        print("   python src/unified-mcp-server.py")
        print()
        print("2. Serenaプロジェクトでの使用:")
        print("   プロジェクトを再アクティブ化してください")
        print()
        print("3. Claude Desktop での使用:")
        print("   Claude Desktopを再起動してください")
        
        # 3. 設定情報を表示
        print(f"\n🔗 MCP設定詳細:")
        config = create_mcp_config()
        print(json.dumps(config, indent=2))
        
    except Exception as e:
        print(f"❌ 設定作成エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
