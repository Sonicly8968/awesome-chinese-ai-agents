# 常见问题 FAQ

## 📋 目录

- [通用问题](#通用问题)
- [平台集成](#平台集成)
- [开发问题](#开发问题)
- [部署运维](#部署运维)
- [贡献指南](#贡献指南)

---

## 通用问题

### Q1: 这个项目是做什么的?

**A**: Awesome Chinese AI Agents 是一个精选的中文 AI Agent 资源库,收录了:
- 开发工具和框架
- 平台集成指南(微信/抖音/小红书等)
- 中文 LLM 工具
- API 集成文档
- 实战案例

目标是帮助开发者快速找到构建中文 AI Agent 所需的资源。

---

### Q2: 为什么需要专门的"中文"资源库?

**A**: 因为中国的技术生态与国外不同:

**平台差异**:
- 微信 ≠ WhatsApp
- 抖音 ≠ TikTok
- 小红书国外没有
- 钉钉/飞书国外罕见

**服务差异**:
- 微信支付/支付宝 vs PayPal
- 高德地图/百度地图 vs Google Maps
- 阿里云/腾讯云 vs AWS/Azure

**语言差异**:
- 中文分词和英文分词不同
- 中文 LLM 有特殊优化
- 提示词工程有文化差异

---

### Q3: 我是新手,应该从哪里开始?

**A**: 建议学习路径:

**第1步**: 了解基础
- 阅读 README 的"AI Agent 框架"部分
- 选择一个框架(推荐 LangChain 或 OpenClaw)
- 跟着官方教程做第一个 demo

**第2步**: 选择平台
- 确定你要集成的平台(微信/抖音/小红书等)
- 阅读对应的平台集成指南
- 申请必要的 API 权限

**第3步**: 实战练习
- 查看 `examples/` 目录的实战案例
- 从简单的开始(如关键词自动回复)
- 逐步增加复杂功能

**第4步**: 深入学习
- 阅读"中文文档与教程"部分
- 观看 B 站相关视频
- 加入技术社区交流

---

### Q4: 这些资源都是免费的吗?

**A**: 大部分是免费的,但有些服务需要付费:

**完全免费**:
- 大部分开源框架和工具
- 文档和教程
- 社区支持

**需要付费**:
- LLM API 调用(Qwen/OpenAI 等)
- 某些云服务(阿里云/腾讯云)
- 第三方服务(如 WeChaty Token)

建议:
- 新手可以使用免费额度
- 小项目用开源方案
- 生产环境考虑付费服务

---

## 平台集成

### Q5: 如何集成微信机器人?

**A**: 有3种主流方案:

**方案1: WeChaty (推荐新手)**
- 优点: 文档完善,社区活跃
- 缺点: 需要购买 Token
- 难度: ⭐⭐

**方案2: iPad 协议**
- 优点: 稳定性好
- 缺点: 需要购买服务
- 难度: ⭐⭐⭐

**方案3: Web 协议**
- 优点: 完全免费
- 缺点: 容易被封号
- 难度: ⭐⭐⭐⭐

详细教程见: README → 对话平台集成 → 微信

---

### Q6: 抖音 API 怎么申请?

**A**: 申请流程:

1. 访问 [抖音开放平台](https://open.douyin.com/)
2. 注册开发者账号
3. 创建应用,选择应用类型
4. 提交资质审核(需要营业执照)
5. 审核通过后获得 API 权限

**注意**:
- 个人开发者权限有限
- 企业认证更容易通过
- 部分 API 需要单独申请

---

### Q7: 小红书有官方 API 吗?

**A**: 小红书的情况比较特殊:

**官方 API**:
- 需要企业认证
- 只对合作伙伴开放
- 申请门槛较高

**替代方案**:
- 使用爬虫(需注意法律风险)
- 第三方服务商
- 浏览器自动化

**建议**:
- 优先尝试官方渠道
- 严格遵守平台规则
- 不要过度爬取数据

---

## 开发问题

### Q8: 中文 LLM 怎么选择?

**A**: 主流选择对比:

| LLM | 优点 | 缺点 | 推荐场景 |
|-----|------|------|----------|
| **通义千问** | 中文能力强,官方支持 | 需要付费 | 生产环境 |
| **ChatGLM** | 可本地部署,开源 | 资源要求高 | 私有化部署 |
| **文心一言** | 百度生态集成好 | 价格较高 | 百度系应用 |
| **GPT-4** | 能力最强 | 贵,中文稍弱 | 高要求场景 |

**建议**:
- 预算充足 → GPT-4
- 中文为主 → 通义千问
- 需要私有化 → ChatGLM
- 百度生态 → 文心一言

---

### Q9: Prompt 怎么写比较好?

**A**: 中文 Prompt 技巧:

**1. 明确角色**
```
你是一位资深的电商客服,拥有5年经验...
```

**2. 提供上下文**
```
当前对话历史:
用户: 我的订单怎么还没发货?
你: [之前的回复]
```

**3. 明确要求**
```
请用友好、专业的语气回复,不超过100字
```

**4. 给出示例**
```
示例:
输入: 订单号是多少?
输出: 请问您的订单号是?我帮您查询一下
```

更多技巧见: README → 提示词库

---

### Q10: 如何处理中文分词?

**A**: 推荐工具:

**jieba** (最流行):
\`\`\`python
import jieba

text = "我想查询订单状态"
words = jieba.cut(text)
print(" / ".join(words))
# 输出: 我 / 想 / 查询 / 订单 / 状态
\`\`\`

**pkuseg** (更准确):
\`\`\`python
import pkuseg

seg = pkuseg.pkuseg()
words = seg.cut("我想查询订单状态")
\`\`\`

**LLM内置分词** (推荐):
- 大部分中文 LLM 自带优化的分词
- 通常不需要手动分词

---

## 部署运维

### Q11: 如何部署到生产环境?

**A**: 推荐方案:

**方案1: Docker (推荐)**
\`\`\`bash
# 构建镜像
docker build -t my-agent .

# 运行容器
docker run -d --env-file .env my-agent
\`\`\`

**方案2: PM2**
\`\`\`bash
# 安装 PM2
npm install -g pm2

# 启动应用
pm2 start app.js --name my-agent

# 设置开机自启
pm2 startup
pm2 save
\`\`\`

**方案3: Serverless**
- 阿里云函数计算
- 腾讯云云函数
- Vercel/Netlify

---

### Q12: 如何监控 Agent 运行状态?

**A**: 监控方案:

**基础监控**:
\`\`\`javascript
// 添加日志
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
\`\`\`

**进阶监控**:
- Prometheus + Grafana (指标监控)
- Sentry (错误追踪)
- ELK Stack (日志分析)

**告警**:
- 钉钉/飞书机器人
- 邮件通知
- 短信告警(阿里云/腾讯云)

---

### Q13: API 调用成本如何优化?

**A**: 省钱技巧:

**1. 缓存结果**
\`\`\`javascript
// 相同问题不重复调用
const cache = new Map();

async function getAnswer(question) {
  if (cache.has(question)) {
    return cache.get(question);
  }

  const answer = await llm.call(question);
  cache.set(question, answer);
  return answer;
}
\`\`\`

**2. 使用更便宜的模型**
- 简单任务用 qwen-turbo
- 复杂任务用 qwen-plus
- 不要总是用最贵的模型

**3. 优化 Prompt**
- 减少不必要的文字
- 合并多个请求
- 使用更短的示例

**4. 批处理**
\`\`\`javascript
// 批量处理而不是逐个处理
const results = await llm.batch(questions);
\`\`\`

---

## 贡献指南

### Q14: 如何贡献资源?

**A**: 贡献步骤:

**方法1: Pull Request (推荐)**
1. Fork 本仓库
2. 创建分支: `git checkout -b add-new-resource`
3. 添加资源到 README.md
4. 提交: `git commit -m "Add: 新资源名称"`
5. 推送: `git push origin add-new-resource`
6. 在 GitHub 创建 Pull Request

**方法2: Issue**
1. 创建 Issue
2. 标题: `[资源推荐] 资源名称`
3. 内容: 资源链接 + 简短描述
4. 等待维护者添加

**方法3: 评论**
- 在 Issue #1 下直接评论
- 格式: `资源名称 | 链接 | 描述`

---

### Q15: 什么样的资源会被收录?

**A**: 收录标准:

**✅ 会被收录**:
- 与 AI Agent 或中文开发相关
- 链接有效且可访问
- 有清晰的文档或说明
- 项目活跃或有价值
- 开源优先

**❌ 不会被收录**:
- 纯商业推广
- 过时或废弃的项目
- 质量低劣
- 与主题无关
- 重复资源

**优先收录**:
- 中文原创项目
- 有实战案例
- 中文文档完善
- 社区活跃

---

### Q16: 发现了错误或过时的信息怎么办?

**A**: 报告方式:

1. **创建 Issue**
   - 标题: `[Bug] 描述问题`
   - 说明: 哪里有错误,正确的是什么

2. **直接修复**
   - Fork 并修复
   - 提交 Pull Request

3. **评论区反馈**
   - 在相关 Issue 下评论

我们会尽快处理!

---

## 📞 更多问题?

- 💬 [GitHub Discussions](https://github.com/happydog-intj/awesome-chinese-ai-agents/discussions)
- 📝 [提交 Issue](https://github.com/happydog-intj/awesome-chinese-ai-agents/issues)
- 📧 邮件: (待添加)
- 微信群: (见主 README)

---

**如果这个 FAQ 对你有帮助,请给项目一个 ⭐!**
