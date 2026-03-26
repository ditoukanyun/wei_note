---
type: wiki
tags:
  - Chrome
  - 开发工具
  - 调试
---

# Chrome 开发调试

## 禁用 Web 安全策略

用于本地开发调试，禁用同源策略（CORS）限制：

```bash
open -n /Applications/Google\ Chrome.app/ --args --disable-web-security --user-data-dir=/Users/chenwei/MyChromeDevUserData/
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `--disable-web-security` | 禁用 Web 安全策略，允许跨域请求 |
| `--user-data-dir` | 指定用户数据目录，避免污染默认配置 |
| `-n` | 打开新实例，不影响正在运行的 Chrome |

### 注意事项

- 仅用于本地开发调试，**切勿用于正常浏览**
- 建议配合独立的用户数据目录，避免影响日常使用的 Chrome
- 关闭后重新打开普通 Chrome 即可恢复正常安全策略
