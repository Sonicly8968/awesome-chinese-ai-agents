# 微信客服机器人

一个基于 WeChaty 和 AI 的智能客服机器人,支持自动回复、订单查询、智能对话等功能。

## ✨ 功能特性

- 🤖 **智能问答**: 使用 AI 理解用户意图并自动回复
- 📦 **订单查询**: 自动查询订单状态和物流信息
- 🔄 **关键词触发**: 支持自定义关键词自动回复
- 👤 **人工转接**: 复杂问题自动转接人工客服
- 📊 **数据统计**: 记录对话数据,生成统计报告
- 🌐 **多语言支持**: 支持中英文对话

## 🛠️ 技术栈

- **WeChaty**: 微信机器人框架
- **LangChain**: LLM 应用开发框架
- **Qwen**: 阿里通义千问大模型
- **Redis**: 会话状态存储
- **PostgreSQL**: 对话历史存储

## 📋 前置要求

- Node.js >= 18
- Redis >= 6.0
- PostgreSQL >= 13 (可选)
- WeChaty Token (从 [Wechaty Token](https://wechaty.js.org/docs/puppet-services/) 获取)
- Qwen API Key (从 [阿里云](https://dashscope.aliyun.com/) 获取)

## 🚀 快速开始

### 1. 安装依赖

\`\`\`bash
npm install
\`\`\`

### 2. 配置环境变量

复制 \`.env.example\` 为 \`.env\`:

\`\`\`bash
cp .env.example .env
\`\`\`

编辑 \`.env\` 填入配置:

\`\`\`env
# WeChaty 配置
WECHATY_PUPPET=wechaty-puppet-wechat
WECHATY_TOKEN=your_wechaty_token

# Qwen AI 配置
QWEN_API_KEY=your_qwen_api_key
QWEN_MODEL=qwen-plus

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# 数据库配置 (可选)
DATABASE_URL=postgresql://user:password@localhost:5432/wechat_bot

# 客服配置
CUSTOMER_SERVICE_TIMEOUT=300000  # 5分钟无响应转人工
AUTO_REPLY_ENABLED=true
\`\`\`

### 3. 启动机器人

\`\`\`bash
npm start
\`\`\`

首次运行会生成二维码,用微信扫码登录。

## 📖 使用说明

### 基本对话

用户发送消息,机器人会自动识别意图并回复:

\`\`\`
用户: 你好
机器人: 您好!我是智能客服助手,有什么可以帮您?

用户: 我的订单什么时候发货?
机器人: 请提供您的订单号,我帮您查询
\`\`\`

### 订单查询

\`\`\`
用户: 查询订单 202403100001
机器人:
订单号: 202403100001
状态: 已发货
物流公司: 顺丰速运
运单号: SF1234567890
预计送达: 2024-03-12
\`\`\`

### 转人工客服

当机器人无法回答时,自动转接人工:

\`\`\`
用户: 我要退款
机器人: 您的问题需要人工处理,正在为您转接客服...
[系统通知人工客服]
\`\`\`

## 🔧 配置说明

### 自定义关键词回复

编辑 \`config/keywords.json\`:

\`\`\`json
{
  "keywords": [
    {
      "trigger": ["营业时间", "几点上班"],
      "reply": "我们的营业时间是周一至周五 9:00-18:00"
    },
    {
      "trigger": ["退货", "退款"],
      "reply": "请联系人工客服处理退货退款问题"
    }
  ]
}
\`\`\`

### AI Prompt 配置

编辑 \`config/prompts.js\`:

\`\`\`javascript
export const SYSTEM_PROMPT = \`
你是一位专业的电商客服,需要:
1. 友好、耐心地回答用户问题
2. 对于订单查询,引导用户提供订单号
3. 对于复杂问题,建议转人工客服
4. 使用简洁的中文回复
\`;
\`\`\`

## 📊 数据统计

查看统计数据:

\`\`\`bash
npm run stats
\`\`\`

生成的报告包括:
- 对话总数
- 用户问题分类
- 平均响应时间
- 人工转接率

## 🐛 常见问题

### Q: 扫码后显示"登录失败"

**A**: 可能是 Token 过期,请更换新的 WeChaty Token

### Q: 机器人不回复消息

**A**: 检查:
1. Qwen API Key 是否有效
2. Redis 是否正常运行
3. 查看日志 \`logs/bot.log\`

### Q: 如何处理高并发?

**A**:
1. 增加 Redis 连接池大小
2. 使用负载均衡部署多个实例
3. 开启消息队列缓冲

## 📝 开发指南

### 项目结构

\`\`\`
wechat-customer-service/
├── src/
│   ├── bot.ts              # 机器人主程序
│   ├── handlers/           # 消息处理器
│   │   ├── message.ts
│   │   ├── order.ts
│   │   └── transfer.ts
│   ├── services/           # 业务服务
│   │   ├── ai.ts           # AI 对话
│   │   ├── order.ts        # 订单查询
│   │   └── redis.ts        # 缓存服务
│   └── utils/              # 工具函数
├── config/
│   ├── keywords.json       # 关键词配置
│   └── prompts.js          # AI Prompt
├── tests/                  # 测试文件
├── .env.example
├── package.json
└── README.md
\`\`\`

### 添加新功能

1. 在 \`src/handlers/\` 创建新的处理器
2. 在 \`src/bot.ts\` 中注册处理器
3. 添加相应的测试

### 运行测试

\`\`\`bash
npm test
\`\`\`

## 🚀 部署

### Docker 部署

\`\`\`bash
docker build -t wechat-bot .
docker run -d --env-file .env wechat-bot
\`\`\`

### PM2 部署

\`\`\`bash
pm2 start ecosystem.config.js
\`\`\`

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📞 支持

- GitHub Issues: [提交问题](https://github.com/happydog-intj/awesome-chinese-ai-agents/issues)
- 技术交流群: 见主项目 README

---

⭐ 如果这个项目对你有帮助,请给个 Star!
