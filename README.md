# 餐厅数据 MCP Server

本服务用于查询职工餐厅就餐人数数据，提供指定日期范围内的早餐和午餐就餐人数统计。

<a href="https://glama.ai/mcp/servers/@wrdan/mcp-canteen-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@wrdan/mcp-canteen-server/badge" alt="Canteen Server MCP server" />
</a>

docs: https://modelcontextprotocol.io/quickstart/server

## 安装

### 通过 pip 安装

```bash
pip install mcp-server-canteen
```

### 通过 uv 安装

```bash
uv pip install mcp-server-canteen
```

### 开发环境安装

```bash
git clone https://github.com/wrdan/mcp-server-canteen.git
cd mcp-server-canteen
uv pip install -e .
```

## 环境变量配置

在使用服务之前，需要配置以下环境变量：

- `CANTEEN_API_TOKEN`: API认证令牌
- `CANTEEN_API_BASE`: API基础URL

### 环境变量获取方式

1. 联系系统管理员获取 API 认证令牌
2. API基础URL通常由系统管理员提供

### 设置环境变量

#### Windows
```bash
set CANTEEN_API_TOKEN=your_token
set CANTEEN_API_BASE=your_base_url
```

#### Linux/Mac
```bash
export CANTEEN_API_TOKEN=your_token
export CANTEEN_API_BASE=your_base_url
```

## 服务运行

### 使用 uv 运行

```bash
uv run mcp-server-canteen
```

### 使用 Python 运行

```bash
python -m mcp_server_canteen.server
```

## 功能说明

服务提供以下功能：

- `get_canteen_data`: 查询指定日期范围内的餐厅就餐人数数据
  - 参数: 
    - `start_date`: 开始日期，格式为YYYYMMDD（如20250331）
    - `end_date`: 结束日期，格式为YYYYMMDD（如20250331）
    - `period`: 相对时间范围，可选值：
      - `today`: 今天
      - `yesterday`: 昨天
      - `day_before_yesterday`: 前天
      - `this_week`: 本周
      - `last_week`: 上周
      - `this_month`: 本月
      - `last_month`: 上月
  - 返回: 包含早餐人数、午餐人数和总计人数的文本统计

## 使用 Claude for Desktop 作为客户端测试

### 配置

打开并编辑文件： ~/Library/Application\ Support/Claude/claude_desktop_config.json，内容如下：

<details>
<summary>使用 uvx</summary>

```json
"mcpServers": {
  "canteen": {
    "command": "uvx",
    "args": ["mcp-server-canteen"],
    "env": {
        "CANTEEN_API_TOKEN": "CANTEEN_API_TOKEN",
        "CANTEEN_API_BASE": "ANTEEN_API_BASE"
    }
  }
}
```
</details>

<details>
<summary>使用 uv</summary>

```json
"mcpServers": {
  "canteen": {
    "command": "uv",
    "args": ["run", "mcp-server-canteen"],
    "env": {
        "CANTEEN_API_TOKEN": "CANTEEN_API_TOKEN",
        "CANTEEN_API_BASE": "ANTEEN_API_BASE"
    }
  }
}
```
</details>

<details>
<summary>本地测试</summary>

```json
"mcpServers": {
  "canteen": {
    "command": "python",
    "args": ["-m", "mcp-server-canteen.server"],
    "env": {
        "CANTEEN_API_TOKEN": "CANTEEN_API_TOKEN",
        "CANTEEN_API_BASE": "ANTEEN_API_BASE"
    }
  }
}
```
</details>

### 重启 Claude for Desktop

重启不报错，且有`锤子`图标显示可用的 MCP Tool，即为成功；否则，查看日志排查

## 错误处理

### 常见错误及解决方案

1. **环境变量未设置**
   - 错误信息：`缺少必要的环境变量配置`
   - 解决方案：确保已正确设置所有必需的环境变量

2. **日期格式错误**
   - 错误信息：`日期格式不正确，请使用YYYYMMDD格式`
   - 解决方案：检查日期格式是否正确，例如：20240321

3. **API请求失败**
   - 错误信息：`HTTP请求失败` 或 `API返回错误`
   - 解决方案：
     - 检查网络连接
     - 验证API令牌是否正确
     - 确认API基础URL是否正确

4. **服务器连接失败**
   - 错误信息：`无法连接到MCP服务器`
   - 解决方案：
     - 确保服务器正在运行
     - 检查端口是否被占用
     - 验证配置文件是否正确

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