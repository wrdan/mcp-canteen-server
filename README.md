# 餐厅数据 MCP Server

本服务用于查询职工餐厅就餐人数数据，提供指定日期范围内的早餐和午餐就餐人数统计。

docs: https://modelcontextprotocol.io/quickstart/server

## 服务运行测试

```shell
    uv run canteen.py 
```

## 功能说明

服务提供以下功能：

- `get_canteen_data`: 查询指定日期范围内的餐厅就餐人数数据
  - 参数: 
    - `start_date`: 开始日期，格式为YYYYMMDD（如20250331）
    - `end_date`: 结束日期，格式为YYYYMMDD（如20250331）
  - 返回: 包含早餐人数、午餐人数和总计人数的文本统计

## 使用 Claude for Desktop 作为客户端测试

### 配置

打开并编辑文件： ~/Library/Application\ Support/Claude/claude_desktop_config.json，内容如下：

```json
    {
    "mcpServers": {
        "canteen": {
            "command": "uv",
            "args": [
                "--directory",
                "/mcp-canteen-server",
                "run",
                "canteen.py"
            ],
            "env": {
                "CANTEEN_API_TOKEN": "CANTEEN_API_TOKEN",
                "CANTEEN_API_BASE": "CANTEEN_API_BASE"
            }
        }
    }
}
```

### 重启 Claude for Desktop

重启不报错，且有`锤子`图标显示可用的 MCP Tool，即为成功；否则，查看日志排查

## Claude for Desktop 日志

日志文件夹：~/Library/Logs/Claude

来自具体 MCP Server 的日志：mcp-server-canteen.log

MCP 连接通用日志：mcp.log

## 工作原理

1. 客户将您的查询发送给 Claude
2. Claude 分析可用的工具并决定使用哪一个
3. 客户端通过 MCP 服务器执行所选工具
4. 结果被发回给 Claude
5. Claude 制定了自然语言响应
6. 答案已经展示给你了！