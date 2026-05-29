# Việt hóa Frontend (i18n vi/zh/en) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển giao diện admin frontend từ tiếng Trung hard-code sang hệ thống đa ngôn ngữ (vi/zh/en), mặc định tiếng Việt, có nút chuyển đổi và ghi nhớ lựa chọn.

**Architecture:** Dùng `react-i18next` + `i18next-browser-languagedetector`. Tất cả chuỗi hiển thị được tách ra 3 file JSON locale theo namespace từng trang. Mỗi component dùng hook `useTranslation()` thay cho text hard-code. Một `LanguageSwitcher` đặt trong sidebar đổi ngôn ngữ runtime, lưu vào localStorage.

**Tech Stack:** React 19, TypeScript, Vite 6, react-i18next, i18next, i18next-browser-languagedetector, Tailwind 4, lucide-react, sonner.

**Lưu ý quy ước:**
- Tất cả lệnh chạy trong thư mục `frontend/`.
- Khóa namespace: `nav`, `common`, `dashboard`, `accounts`, `tokens`, `test`, `images`, `settings`.
- Nội suy biến dùng cú pháp i18next `{{name}}`.
- Comment tiếng Trung trong `src/lib/api.ts` và `src/index.css` GIỮ NGUYÊN (không hiển thị).
- Git chưa cấu hình `user.name`/`user.email`; nếu `git commit` báo lỗi danh tính, người thực thi cần đặt danh tính trước (không thuộc phạm vi plan).

---

## Task 1: Cài dependency i18n

**Files:**
- Modify: `frontend/package.json` (qua npm)

- [ ] **Step 1: Cài 3 package**

Run (trong `frontend/`):
```bash
npm install i18next@^23 react-i18next@^15 i18next-browser-languagedetector@^8
```
Expected: 3 package được thêm vào `dependencies` trong `package.json`, `npm install` kết thúc không lỗi.

- [ ] **Step 2: Xác minh đã thêm**

Run:
```bash
node -e "const p=require('./package.json');console.log(p.dependencies['i18next'],p.dependencies['react-i18next'],p.dependencies['i18next-browser-languagedetector'])"
```
Expected: in ra 3 chuỗi version, không có `undefined`.

- [ ] **Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "chore: thêm dependency i18next cho việt hóa frontend"
```

---

## Task 2: Tạo file locale tiếng Việt (vi.json)

**Files:**
- Create: `frontend/src/i18n/locales/vi.json`

- [ ] **Step 1: Tạo file `frontend/src/i18n/locales/vi.json`**

```json
{
  "nav": {
    "dashboard": "Trạng thái",
    "accounts": "Quản lý tài khoản",
    "tokens": "API Key",
    "test": "Kiểm thử API",
    "images": "Tạo ảnh",
    "settings": "Cài đặt hệ thống"
  },
  "common": {
    "refresh": "Làm mới",
    "save": "Lưu",
    "clear": "Xóa",
    "delete": "Xóa",
    "loadingThinking": "Đang suy nghĩ...",
    "language": "Ngôn ngữ"
  },
  "dashboard": {
    "title": "Trạng thái",
    "subtitle": "Giám sát đồng thời toàn cục và tổng quan bể tài khoản Qwen (tự làm mới mỗi 3 giây).",
    "fetchError": "Lấy trạng thái thất bại, hãy kiểm tra Key phiên hiện tại trong «Cài đặt hệ thống».",
    "validAccounts": "Tài khoản khả dụng",
    "totalCount": "Tổng {{count}} tài khoản",
    "currentConcurrency": "Đang xử lý đồng thời",
    "globalLimit": "Giới hạn toàn cục {{count}}",
    "queuedRequests": "Yêu cầu đang chờ",
    "queueLimit": "Giới hạn hàng đợi {{count}}",
    "rateLimitedInvalid": "Bị giới hạn / Hỏng",
    "warmPool": "Bể làm nóng Chat_ID",
    "warmPoolSub": "Mỗi tài khoản mục tiêu {{target}}  · TTL {{minutes}} phút",
    "warmPoolDisabled": "Chưa bật",
    "asyncTasks": "Tác vụ bất đồng bộ",
    "asyncTasksSub": "Số tác vụ asyncio đang chạy",
    "accountDetail": "Chi tiết đồng thời theo tài khoản",
    "colEmail": "Email",
    "colStatus": "Trạng thái",
    "colInflight": "Đang chạy",
    "colWarmChatId": "chat_id đã làm nóng",
    "colConsecFail": "Lỗi liên tiếp",
    "colRateLimitStrikes": "Số lần bị giới hạn",
    "apiPool": "Bể API",
    "apiPoolSub": "Điểm vào tương thích các giao thức AI phổ biến, mặc định không cần xác thực hoặc truy cập qua API Key.",
    "tagHealthCheck": "Kiểm tra sức khỏe"
  },
  "accounts": {
    "title": "Quản lý tài khoản",
    "subtitle": "Quản lý tập trung bể tài khoản, phân biệt trạng thái chưa kích hoạt, bị giới hạn, bị cấm và hỏng.",
    "statusValid": "Khả dụng",
    "statusPending": "Chưa kích hoạt",
    "statusRateLimited": "Bị giới hạn",
    "statusBanned": "Bị cấm",
    "statusAuthError": "Lỗi xác thực",
    "statusInvalid": "Hỏng",
    "recoverInSeconds": "Dự kiến phục hồi sau {{seconds}} giây",
    "errUnknown": "Lỗi không xác định",
    "errActivating": "Tài khoản đang kích hoạt, hãy làm mới sau",
    "errActivationLink": "Lấy link kích hoạt hoặc Token thất bại",
    "errTokenInvalid": "Token không hợp lệ hoặc xác thực thất bại",
    "refreshListError": "Làm mới danh sách tài khoản thất bại, hãy kiểm tra Key phiên",
    "needToken": "Vui lòng nhập Token trước",
    "injecting": "Đang thêm tài khoản...",
    "injected": "Đã thêm tài khoản vào bể",
    "injectFailed": "Thêm tài khoản thất bại",
    "injectRequestFailed": "Yêu cầu thêm tài khoản thất bại",
    "deleting": "Đang xóa {{email}}...",
    "deleted": "Đã xóa {{email}}",
    "deleteFailed": "Xóa tài khoản thất bại",
    "autoRegistering": "Đang tự động đăng ký tài khoản mới, vui lòng đợi...",
    "registeredNeedActivate": "Đã đăng ký nhưng cần kích hoạt: {{email}}",
    "registerSuccess": "Đăng ký thành công: {{email}}",
    "autoRegisterFailed": "Tự động đăng ký thất bại",
    "autoRegisterRequestFailed": "Yêu cầu tự động đăng ký thất bại",
    "verifying": "Đang xác minh {{email}}...",
    "verifySuccess": "Xác minh thành công: {{email}}",
    "verifyFailed": "Xác minh thất bại: {{detail}}",
    "verifyRequestFailed": "Yêu cầu xác minh thất bại",
    "verifyingAll": "Đang kiểm tra đồng thời tất cả tài khoản...",
    "verifyAllDone": "Kiểm tra toàn bộ hoàn tất, số đồng thời: {{concurrency}}",
    "verifyAllFailed": "Kiểm tra toàn bộ thất bại",
    "verifyAllRequestFailed": "Yêu cầu kiểm tra toàn bộ thất bại",
    "activating": "Đang kích hoạt {{email}}...",
    "activatePending": "Tài khoản đang kích hoạt, hãy làm mới sau: {{email}}",
    "activateSuccess": "Kích hoạt thành công: {{email}}",
    "activateFailed": "Kích hoạt thất bại: {{detail}}",
    "activateRequestFailed": "Yêu cầu kích hoạt thất bại",
    "verifyAllBtn": "Kiểm tra toàn bộ",
    "refreshBtn": "Làm mới trạng thái",
    "listRefreshed": "Đã làm mới danh sách tài khoản",
    "registeringBtn": "Đang đăng ký...",
    "getNewBtn": "Lấy tài khoản mới",
    "statValid": "Khả dụng",
    "statPending": "Chưa kích hoạt",
    "statRateLimited": "Bị giới hạn",
    "statBanned": "Bị cấm",
    "statInvalid": "Hỏng khác",
    "manualInject": "Thêm tài khoản thủ công",
    "manualInjectHint": "Hãy đăng nhập chat.qwen.ai trước, rồi nhấn F12 mở Developer Tools, vào Application / Storage, tìm token trong Local Storage và sao chép nguyên giá trị gốc dán vào ô bên dưới.",
    "manualInjectWarn": "Quan trọng: chỉ dán giá trị gốc của token trong Local Storage, không lấy từ request Network hay header Authorization.",
    "manualInjectWarn2": "Đừng kèm tiền tố Bearer, cũng đừng dán cả đoạn Authorization. Email và mật khẩu có thể bỏ trống, hệ thống sẽ xác minh token hợp lệ trước khi thêm.",
    "tokenLabel": "Token (bắt buộc)",
    "tokenPlaceholder": "Dán token sao chép trực tiếp từ Local Storage",
    "emailLabel": "Email (tùy chọn)",
    "emailPlaceholder": "Địa chỉ email",
    "passwordLabel": "Mật khẩu (tùy chọn)",
    "passwordPlaceholder": "Dùng để tự động làm mới hoặc kích hoạt",
    "injectBtn": "Thêm tài khoản",
    "listTitle": "Danh sách tài khoản",
    "colAccount": "Tài khoản",
    "colStatus": "Trạng thái",
    "colLoad": "Tải đồng thời",
    "colNote": "Ghi chú",
    "colActions": "Thao tác",
    "emptyList": "Chưa có tài khoản, hãy thêm thủ công hoặc lấy tài khoản mới.",
    "threads": "{{count}} luồng",
    "activateBtn": "Kích hoạt",
    "verifyOne": "Xác minh riêng",
    "deleteAccount": "Xóa tài khoản"
  },
  "tokens": {
    "title": "Phát hành API Key",
    "subtitle": "Quản lý các thông tin xác thực phía dưới được phép truy cập cổng này.",
    "refreshError": "Làm mới thất bại, hãy kiểm tra Key phiên",
    "generated": "Đã tạo API Key mới",
    "generateFailed": "Tạo thất bại, hãy kiểm tra quyền",
    "deleted": "Đã xóa API Key",
    "deleteFailed": "Xóa thất bại",
    "refreshed": "Đã làm mới",
    "refreshBtn": "Làm mới",
    "generateBtn": "Tạo Key mới",
    "colIndex": "STT",
    "colActions": "Thao tác",
    "empty": "Chưa có API Key"
  },
  "test": {
    "title": "Kiểm thử API",
    "subtitle": "Kiểm thử tại đây xem việc phát hành API của bạn có hoạt động không.",
    "unknownResponse": "Phản hồi không xác định: {{data}}",
    "emptyResponse": "❌ Phản hồi rỗng (tài khoản có thể chưa kích hoạt hoặc không có tài khoản khả dụng)",
    "networkError": "Lỗi mạng: {{message}}",
    "modelLabel": "Mô hình:",
    "stream": "Truyền theo luồng (Stream)",
    "clearChat": "Xóa hội thoại",
    "emptyHint": "Gửi một tin nhắn để bắt đầu kiểm thử, hệ thống sẽ gọi qua /v1/chat/completions.",
    "thinking": "Đang suy nghĩ...",
    "reasoningSummary": "💭 Quá trình suy luận ({{count}} ký tự)",
    "inputPlaceholder": "Nhập tin nhắn kiểm thử..."
  },
  "images": {
    "title": "Tạo ảnh",
    "subtitle": "Tạo ảnh AI bằng Qwen3.6-Plus, hỗ trợ nhiều tỉ lệ.",
    "generateFailed": "Tạo thất bại: {{detail}}",
    "noImageReturned": "Không trả về ảnh, hãy thử lại",
    "generateSuccess": "Đã tạo thành công {{count}} ảnh",
    "networkError": "Lỗi mạng",
    "promptLabel": "Mô tả ảnh (Prompt)",
    "promptPlaceholder": "Mô tả ảnh bạn muốn tạo, ví dụ: chú mèo phong cách cyberpunk, nền đèn neon, siêu thực",
    "ctrlEnterHint": "Ctrl+Enter để tạo nhanh",
    "ratioLabel": "Tỉ lệ ảnh",
    "countLabel": "Số lượng",
    "countUnit": "{{count}} ảnh",
    "generating": "Đang tạo...",
    "generateBtn": "Tạo ảnh",
    "loadingTitle": "Đang tạo ảnh...",
    "loadingSub": "Tạo ảnh thường mất 10-30 giây, hãy kiên nhẫn chờ",
    "resultTitle": "Kết quả ({{count}} ảnh)",
    "clearBtn": "Xóa",
    "imageLoadFailed": "Tải ảnh thất bại",
    "download": "Tải xuống",
    "openNewWindow": "Mở trong cửa sổ mới",
    "emptyTitle": "Chưa có ảnh nào",
    "emptySub": "Nhập mô tả ở trên, nhấn «Tạo ảnh» để bắt đầu sáng tạo"
  },
  "settings": {
    "title": "Cài đặt hệ thống",
    "subtitle": "Quản lý xác thực bảng điều khiển và cấu hình runtime của cổng.",
    "fetchError": "Lấy cấu hình thất bại, hãy kiểm tra Key phiên",
    "needKey": "Vui lòng nhập Key",
    "keySaved": "Đã lưu Key vào máy, đang làm mới dữ liệu...",
    "keyCleared": "Đã xóa Key",
    "concurrencySaved": "Đã lưu cấu hình đồng thời (có hiệu lực runtime ngay)",
    "saveFailed": "Lưu thất bại",
    "poolSaved": "Đã lưu cấu hình bể làm nóng (có hiệu lực ở lần làm mới tiếp theo)",
    "aliasesSaved": "Đã cập nhật quy tắc ánh xạ mô hình",
    "jsonError": "Sai định dạng JSON, hãy kiểm tra cú pháp",
    "configRefreshed": "Đã làm mới cấu hình",
    "refreshBtn": "Làm mới cấu hình",
    "sessionKeyTitle": "Key phiên hiện tại",
    "sessionKeyDesc": "Dán API Key sẵn có vào đây, bảng điều khiển sẽ dùng nó cho mọi thao tác quản lý. (Lưu trên máy trình duyệt)",
    "sessionKeyPlaceholder": "sk-qwen-... hoặc khóa admin mặc định admin",
    "saveBtn": "Lưu",
    "clearBtn": "Xóa",
    "connectionTitle": "Thông tin kết nối",
    "baseUrlLabel": "Địa chỉ gốc API (Base URL)",
    "coreTitle": "Tham số đồng thời cốt lõi",
    "coreDesc": "Slot đồng thời runtime và ngưỡng hàng đợi (cần sửa trong config.json của backend rồi khởi động lại mới có hiệu lực).",
    "versionLabel": "Phiên bản hệ thống hiện tại",
    "maxInflightLabel": "Đồng thời tối đa mỗi tài khoản (max_inflight_per_account)",
    "maxInflightDesc": "Số yêu cầu mỗi tài khoản thượng nguồn xử lý cùng lúc. Quá lớn dễ bị cấm, quá nhỏ không tận dụng hết.",
    "globalMaxLabel": "Giới hạn đồng thời toàn cục (global_max_inflight)",
    "globalMaxDesc": "Giới hạn cứng tổng số yêu cầu đang chạy của tất cả tài khoản. 0 = không giới hạn. Tương ứng đỉnh «Tác vụ bất đồng bộ» ở Dashboard.",
    "saveConcurrencyBtn": "Lưu cài đặt đồng thời",
    "poolTitle": "Bể làm nóng Chat_ID",
    "poolDesc": "Tạo sẵn chat_id để tránh handshake /chats/new thượng nguồn (0.5~6s). Sửa runtime có hiệu lực ngay.",
    "poolTargetLabel": "Số mục tiêu mỗi tài khoản (target)",
    "poolTargetDesc": "Mỗi tài khoản treo sẵn bao nhiêu chat_id chờ. Mặc định 5.",
    "poolTtlLabel": "TTL (phút)",
    "poolTtlDesc": "chat_id quá thời hạn này sẽ bị bỏ và tạo lại, tránh bị thượng nguồn thu hồi âm thầm. Mặc định 10.",
    "savePoolBtn": "Lưu cài đặt bể làm nóng",
    "aliasesTitle": "Quy tắc ánh xạ mô hình tự động (Model Aliases)",
    "aliasesDesc": "Tên mô hình phía dưới gửi lên sẽ được cổng tự định tuyến tới mô hình Qwen thực tế bên dưới. Hãy chỉnh sửa theo định dạng JSON chuẩn.",
    "saveAliasesBtn": "Lưu ánh xạ",
    "exampleTitle": "Ví dụ sử dụng"
  }
}
```

- [ ] **Step 2: Xác minh JSON hợp lệ**

Run (trong `frontend/`):
```bash
node -e "JSON.parse(require('fs').readFileSync('src/i18n/locales/vi.json','utf8'));console.log('vi.json OK')"
```
Expected: in `vi.json OK`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/i18n/locales/vi.json
git commit -m "feat(i18n): thêm locale tiếng Việt"
```

---

## Task 3: Tạo file locale tiếng Trung (zh.json)

Đây là text gốc của ứng dụng. Mỗi key phải khớp 1-1 với `vi.json`.

**Files:**
- Create: `frontend/src/i18n/locales/zh.json`

- [ ] **Step 1: Tạo file `frontend/src/i18n/locales/zh.json`**

```json
{
  "nav": {
    "dashboard": "运行状态",
    "accounts": "账号管理",
    "tokens": "API Key",
    "test": "接口测试",
    "images": "图片生成",
    "settings": "系统设置"
  },
  "common": {
    "refresh": "刷新",
    "save": "保存",
    "clear": "清除",
    "delete": "删除",
    "loadingThinking": "思考中...",
    "language": "语言"
  },
  "dashboard": {
    "title": "运行状态",
    "subtitle": "全局并发监控与千问账号池概览（每 3 秒自动刷新）。",
    "fetchError": "状态获取失败，请在「系统设置」检查您的当前会话 Key。",
    "validAccounts": "可用账号",
    "totalCount": "共 {{count}} 个",
    "currentConcurrency": "当前并发",
    "globalLimit": "全局上限 {{count}}",
    "queuedRequests": "排队请求",
    "queueLimit": "队列上限 {{count}}",
    "rateLimitedInvalid": "限流号/失效号",
    "warmPool": "Chat_ID 预热池",
    "warmPoolSub": "每账号目标 {{target}}  · TTL {{minutes}} 分钟",
    "warmPoolDisabled": "未启用",
    "asyncTasks": "异步任务",
    "asyncTasksSub": "asyncio active task count",
    "accountDetail": "账号并发详情",
    "colEmail": "邮箱",
    "colStatus": "状态",
    "colInflight": "在途",
    "colWarmChatId": "预热 chat_id",
    "colConsecFail": "连失",
    "colRateLimitStrikes": "限流次",
    "apiPool": "API 接口池",
    "apiPoolSub": "兼容主流 AI 协议的调用入口，默认无需认证，或通过 API Key 访问。",
    "tagHealthCheck": "健康检查"
  },
  "accounts": {
    "title": "账号管理",
    "subtitle": "统一管理上游账号池，并区分未激活、限流、封禁与失效状态。",
    "statusValid": "可用",
    "statusPending": "未激活",
    "statusRateLimited": "限流",
    "statusBanned": "封禁",
    "statusAuthError": "认证失效",
    "statusInvalid": "失效",
    "recoverInSeconds": "预计 {{seconds}} 秒后恢复",
    "errUnknown": "未知错误",
    "errActivating": "账号正在激活中，请稍后刷新",
    "errActivationLink": "激活链接或 Token 获取失败",
    "errTokenInvalid": "Token 无效或认证失败",
    "refreshListError": "刷新账号列表失败，请检查会话密钥",
    "needToken": "请先填写 Token",
    "injecting": "正在注入账号...",
    "injected": "账号已加入账号池",
    "injectFailed": "账号注入失败",
    "injectRequestFailed": "账号注入请求失败",
    "deleting": "正在删除 {{email}}...",
    "deleted": "已删除 {{email}}",
    "deleteFailed": "删除账号失败",
    "autoRegistering": "正在自动注册新账号，请稍候...",
    "registeredNeedActivate": "账号已注册，但仍需激活：{{email}}",
    "registerSuccess": "注册成功：{{email}}",
    "autoRegisterFailed": "自动注册失败",
    "autoRegisterRequestFailed": "自动注册请求失败",
    "verifying": "正在验证 {{email}}...",
    "verifySuccess": "验证通过：{{email}}",
    "verifyFailed": "验证失败：{{detail}}",
    "verifyRequestFailed": "验证请求失败",
    "verifyingAll": "正在并发巡检所有账号...",
    "verifyAllDone": "全量巡检完成，并发数：{{concurrency}}",
    "verifyAllFailed": "全量巡检失败",
    "verifyAllRequestFailed": "全量巡检请求失败",
    "activating": "正在激活 {{email}}...",
    "activatePending": "账号正在激活中，请稍后刷新：{{email}}",
    "activateSuccess": "激活成功：{{email}}",
    "activateFailed": "激活失败：{{detail}}",
    "activateRequestFailed": "激活请求失败",
    "verifyAllBtn": "全量巡检",
    "refreshBtn": "刷新状态",
    "listRefreshed": "账号列表已刷新",
    "registeringBtn": "正在注册...",
    "getNewBtn": "一键获取新号",
    "statValid": "可用",
    "statPending": "未激活",
    "statRateLimited": "限流",
    "statBanned": "封禁",
    "statInvalid": "其他失效",
    "manualInject": "手动注入账号",
    "manualInjectHint": "请先在 chat.qwen.ai 登录，然后按 F12 打开开发者工具，在 Application / Storage 里的 Local Storage / 本地存储 中找到 token 并直接复制完整原始值粘贴到下方输入框。",
    "manualInjectWarn": "重要：请只粘贴 Local Storage / 本地存储 里的 token 原始值，不要从 Network 请求或 Authorization 请求头中提取。",
    "manualInjectWarn2": "请不要带 Bearer 前缀，也不要粘贴整段 Authorization 文本。邮箱和密码可以不填，系统会在注入前先验证 token 是否有效。",
    "tokenLabel": "Token（必填）",
    "tokenPlaceholder": "粘贴从 Local Storage / 本地存储 直接复制的 token",
    "emailLabel": "邮箱（选填）",
    "emailPlaceholder": "邮箱地址",
    "passwordLabel": "密码（选填）",
    "passwordPlaceholder": "用于自动刷新或激活",
    "injectBtn": "注入账号",
    "listTitle": "账号列表",
    "colAccount": "账号",
    "colStatus": "状态",
    "colLoad": "并发负载",
    "colNote": "说明",
    "colActions": "操作",
    "emptyList": "暂无账号，请手动注入或一键获取新号。",
    "threads": "{{count}} 线程",
    "activateBtn": "激活",
    "verifyOne": "单独验证",
    "deleteAccount": "删除账号"
  },
  "tokens": {
    "title": "API Key 分发",
    "subtitle": "管理可以访问此网关的下游凭证。",
    "refreshError": "刷新失败，请检查会话 Key",
    "generated": "已生成新的 API Key",
    "generateFailed": "生成失败，请检查权限",
    "deleted": "API Key 已删除",
    "deleteFailed": "删除失败",
    "refreshed": "已刷新",
    "refreshBtn": "刷新",
    "generateBtn": "生成新 Key",
    "colIndex": "序号",
    "colActions": "操作",
    "empty": "暂无 API Key"
  },
  "test": {
    "title": "接口测试",
    "subtitle": "在此测试您的 API 分发是否正常工作。",
    "unknownResponse": "未知响应: {{data}}",
    "emptyResponse": "❌ 响应为空（账号可能未激活或无可用账号）",
    "networkError": "网络错误: {{message}}",
    "modelLabel": "模型:",
    "stream": "流式传输 (Stream)",
    "clearChat": "清空对话",
    "emptyHint": "发送一条消息以开始测试，系统将通过 /v1/chat/completions 进行调用。",
    "thinking": "思考中...",
    "reasoningSummary": "💭 思考过程 ({{count}} 字)",
    "inputPlaceholder": "输入测试消息..."
  },
  "images": {
    "title": "图片生成",
    "subtitle": "通过 Qwen3.6-Plus 生成 AI 图片，支持多种比例。",
    "generateFailed": "生成失败: {{detail}}",
    "noImageReturned": "未返回图片，请重试",
    "generateSuccess": "成功生成 {{count}} 张图片",
    "networkError": "网络错误",
    "promptLabel": "图片描述 (Prompt)",
    "promptPlaceholder": "描述你想生成的图片，例如：赛博朋克风格的猫咪，霓虹灯背景，超写实风格",
    "ctrlEnterHint": "Ctrl+Enter 快速生成",
    "ratioLabel": "图片比例",
    "countLabel": "生成数量",
    "countUnit": "{{count}} 张",
    "generating": "生成中...",
    "generateBtn": "生成图片",
    "loadingTitle": "正在生成图片...",
    "loadingSub": "图片生成通常需要 10-30 秒，请耐心等待",
    "resultTitle": "生成结果 ({{count}} 张)",
    "clearBtn": "清空",
    "imageLoadFailed": "图片加载失败",
    "download": "下载",
    "openNewWindow": "在新窗口打开",
    "emptyTitle": "还没有生成图片",
    "emptySub": "在上方输入描述，点击「生成图片」开始创作"
  },
  "settings": {
    "title": "系统设置",
    "subtitle": "管理控制台认证与网关运行时配置。",
    "fetchError": "配置获取失败，请检查会话 Key",
    "needKey": "请输入 Key",
    "keySaved": "Key 已保存到本地，刷新数据...",
    "keyCleared": "Key 已清除",
    "concurrencySaved": "并发配置已保存（运行时立即生效）",
    "saveFailed": "保存失败",
    "poolSaved": "预热池配置已保存（下一轮刷新生效）",
    "aliasesSaved": "模型映射规则已更新",
    "jsonError": "JSON 格式错误，请检查语法",
    "configRefreshed": "配置已刷新",
    "refreshBtn": "刷新配置",
    "sessionKeyTitle": "当前会话 Key",
    "sessionKeyDesc": "将已有的 API Key 粘贴到此处，控制台将使用它进行所有的管理操作。（保存在浏览器本地）",
    "sessionKeyPlaceholder": "sk-qwen-... 或默认管理员密钥 admin",
    "saveBtn": "保存",
    "clearBtn": "清除",
    "connectionTitle": "连接信息",
    "baseUrlLabel": "API 基础地址 (Base URL)",
    "coreTitle": "核心并发参数",
    "coreDesc": "运行时并发槽位与排队阈值（需要在后端 config.json 中修改后重启生效）。",
    "versionLabel": "当前系统版本",
    "maxInflightLabel": "单账号最大并发 (max_inflight_per_account)",
    "maxInflightDesc": "每个上游账号同时处理的请求数。太大易被封，太小不充分利用。",
    "globalMaxLabel": "全局并发上限 (global_max_inflight)",
    "globalMaxDesc": "所有账号合计同时在途请求的硬上限。0 = 不限。对应 Dashboard 的\"异步任务\"峰值。",
    "saveConcurrencyBtn": "保存并发设置",
    "poolTitle": "Chat_ID 预热池",
    "poolDesc": "预建 chat_id 规避上游 /chats/new 握手 (0.5~6s)。运行时修改立即生效。",
    "poolTargetLabel": "每账号目标数 (target)",
    "poolTargetDesc": "每个账号预先挂多少个 chat_id 等着。默认 5。",
    "poolTtlLabel": "TTL (分钟)",
    "poolTtlDesc": "chat_id 超过此时长则丢弃重建，避免被上游静默回收。默认 10。",
    "savePoolBtn": "保存预热池设置",
    "aliasesTitle": "自动模型映射规则 (Model Aliases)",
    "aliasesDesc": "下游传入的模型名称将被网关自动路由至以下千问实际模型。请使用标准 JSON 格式编辑。",
    "saveAliasesBtn": "保存映射",
    "exampleTitle": "使用示例"
  }
}
```

- [ ] **Step 2: Xác minh JSON hợp lệ + cùng tập key với vi.json**

Run (trong `frontend/`):
```bash
node -e "const fs=require('fs');const flat=(o,p='')=>Object.keys(o).flatMap(k=>typeof o[k]==='object'?flat(o[k],p+k+'.'):[p+k]);const vi=flat(JSON.parse(fs.readFileSync('src/i18n/locales/vi.json','utf8'))).sort();const zh=flat(JSON.parse(fs.readFileSync('src/i18n/locales/zh.json','utf8'))).sort();const miss=vi.filter(k=>!zh.includes(k));const extra=zh.filter(k=>!vi.includes(k));if(miss.length||extra.length){console.error('MISMATCH miss:',miss,'extra:',extra);process.exit(1)}console.log('zh.json OK, keys match vi.json')"
```
Expected: in `zh.json OK, keys match vi.json`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/i18n/locales/zh.json
git commit -m "feat(i18n): thêm locale tiếng Trung (text gốc)"
```

---

## Task 4: Tạo file locale tiếng Anh (en.json)

**Files:**
- Create: `frontend/src/i18n/locales/en.json`

- [ ] **Step 1: Tạo file `frontend/src/i18n/locales/en.json`**

```json
{
  "nav": {
    "dashboard": "Status",
    "accounts": "Accounts",
    "tokens": "API Key",
    "test": "API Test",
    "images": "Image Gen",
    "settings": "Settings"
  },
  "common": {
    "refresh": "Refresh",
    "save": "Save",
    "clear": "Clear",
    "delete": "Delete",
    "loadingThinking": "Thinking...",
    "language": "Language"
  },
  "dashboard": {
    "title": "Status",
    "subtitle": "Global concurrency monitoring and Qwen account pool overview (auto-refresh every 3s).",
    "fetchError": "Failed to fetch status, please check your current session Key in \"Settings\".",
    "validAccounts": "Available accounts",
    "totalCount": "{{count}} total",
    "currentConcurrency": "Current concurrency",
    "globalLimit": "Global limit {{count}}",
    "queuedRequests": "Queued requests",
    "queueLimit": "Queue limit {{count}}",
    "rateLimitedInvalid": "Rate-limited / Invalid",
    "warmPool": "Chat_ID warm pool",
    "warmPoolSub": "Per-account target {{target}}  · TTL {{minutes}} min",
    "warmPoolDisabled": "Disabled",
    "asyncTasks": "Async tasks",
    "asyncTasksSub": "asyncio active task count",
    "accountDetail": "Per-account concurrency",
    "colEmail": "Email",
    "colStatus": "Status",
    "colInflight": "In-flight",
    "colWarmChatId": "Warm chat_id",
    "colConsecFail": "Consec. fails",
    "colRateLimitStrikes": "Rate-limit strikes",
    "apiPool": "API endpoints",
    "apiPoolSub": "Entry points compatible with mainstream AI protocols, no auth by default or access via API Key.",
    "tagHealthCheck": "Health check"
  },
  "accounts": {
    "title": "Accounts",
    "subtitle": "Centrally manage the upstream account pool, distinguishing pending, rate-limited, banned and invalid states.",
    "statusValid": "Available",
    "statusPending": "Pending",
    "statusRateLimited": "Rate-limited",
    "statusBanned": "Banned",
    "statusAuthError": "Auth error",
    "statusInvalid": "Invalid",
    "recoverInSeconds": "Recovering in {{seconds}}s",
    "errUnknown": "Unknown error",
    "errActivating": "Account is activating, please refresh later",
    "errActivationLink": "Failed to get activation link or Token",
    "errTokenInvalid": "Token invalid or authentication failed",
    "refreshListError": "Failed to refresh account list, please check session key",
    "needToken": "Please fill in the Token first",
    "injecting": "Injecting account...",
    "injected": "Account added to the pool",
    "injectFailed": "Account injection failed",
    "injectRequestFailed": "Account injection request failed",
    "deleting": "Deleting {{email}}...",
    "deleted": "Deleted {{email}}",
    "deleteFailed": "Failed to delete account",
    "autoRegistering": "Auto-registering a new account, please wait...",
    "registeredNeedActivate": "Account registered but needs activation: {{email}}",
    "registerSuccess": "Registered successfully: {{email}}",
    "autoRegisterFailed": "Auto-registration failed",
    "autoRegisterRequestFailed": "Auto-registration request failed",
    "verifying": "Verifying {{email}}...",
    "verifySuccess": "Verified: {{email}}",
    "verifyFailed": "Verification failed: {{detail}}",
    "verifyRequestFailed": "Verification request failed",
    "verifyingAll": "Verifying all accounts concurrently...",
    "verifyAllDone": "Full check done, concurrency: {{concurrency}}",
    "verifyAllFailed": "Full check failed",
    "verifyAllRequestFailed": "Full check request failed",
    "activating": "Activating {{email}}...",
    "activatePending": "Account is activating, please refresh later: {{email}}",
    "activateSuccess": "Activated: {{email}}",
    "activateFailed": "Activation failed: {{detail}}",
    "activateRequestFailed": "Activation request failed",
    "verifyAllBtn": "Check all",
    "refreshBtn": "Refresh status",
    "listRefreshed": "Account list refreshed",
    "registeringBtn": "Registering...",
    "getNewBtn": "Get new account",
    "statValid": "Available",
    "statPending": "Pending",
    "statRateLimited": "Rate-limited",
    "statBanned": "Banned",
    "statInvalid": "Other invalid",
    "manualInject": "Manually inject account",
    "manualInjectHint": "Log in to chat.qwen.ai first, then press F12 to open DevTools, go to Application / Storage, find the token in Local Storage and paste the full raw value into the box below.",
    "manualInjectWarn": "Important: only paste the raw token value from Local Storage, do not extract it from Network requests or the Authorization header.",
    "manualInjectWarn2": "Do not include the Bearer prefix, and do not paste the whole Authorization text. Email and password are optional; the system verifies the token before injection.",
    "tokenLabel": "Token (required)",
    "tokenPlaceholder": "Paste the token copied directly from Local Storage",
    "emailLabel": "Email (optional)",
    "emailPlaceholder": "Email address",
    "passwordLabel": "Password (optional)",
    "passwordPlaceholder": "Used for auto-refresh or activation",
    "injectBtn": "Inject account",
    "listTitle": "Account list",
    "colAccount": "Account",
    "colStatus": "Status",
    "colLoad": "Concurrency load",
    "colNote": "Note",
    "colActions": "Actions",
    "emptyList": "No accounts yet, please inject manually or get a new account.",
    "threads": "{{count}} threads",
    "activateBtn": "Activate",
    "verifyOne": "Verify",
    "deleteAccount": "Delete account"
  },
  "tokens": {
    "title": "API Key distribution",
    "subtitle": "Manage the downstream credentials allowed to access this gateway.",
    "refreshError": "Refresh failed, please check session Key",
    "generated": "New API Key generated",
    "generateFailed": "Generation failed, please check permissions",
    "deleted": "API Key deleted",
    "deleteFailed": "Delete failed",
    "refreshed": "Refreshed",
    "refreshBtn": "Refresh",
    "generateBtn": "Generate new Key",
    "colIndex": "No.",
    "colActions": "Actions",
    "empty": "No API Key yet"
  },
  "test": {
    "title": "API Test",
    "subtitle": "Test here whether your API distribution works correctly.",
    "unknownResponse": "Unknown response: {{data}}",
    "emptyResponse": "❌ Empty response (account may be inactive or no account available)",
    "networkError": "Network error: {{message}}",
    "modelLabel": "Model:",
    "stream": "Streaming (Stream)",
    "clearChat": "Clear chat",
    "emptyHint": "Send a message to start testing; the system calls via /v1/chat/completions.",
    "thinking": "Thinking...",
    "reasoningSummary": "💭 Reasoning ({{count}} chars)",
    "inputPlaceholder": "Enter a test message..."
  },
  "images": {
    "title": "Image generation",
    "subtitle": "Generate AI images with Qwen3.6-Plus, supporting multiple ratios.",
    "generateFailed": "Generation failed: {{detail}}",
    "noImageReturned": "No image returned, please retry",
    "generateSuccess": "Successfully generated {{count}} image(s)",
    "networkError": "Network error",
    "promptLabel": "Image description (Prompt)",
    "promptPlaceholder": "Describe the image you want, e.g. a cyberpunk cat with neon lights, ultra realistic",
    "ctrlEnterHint": "Ctrl+Enter to generate quickly",
    "ratioLabel": "Image ratio",
    "countLabel": "Count",
    "countUnit": "{{count}} image(s)",
    "generating": "Generating...",
    "generateBtn": "Generate image",
    "loadingTitle": "Generating image...",
    "loadingSub": "Image generation usually takes 10-30s, please be patient",
    "resultTitle": "Results ({{count}} image(s))",
    "clearBtn": "Clear",
    "imageLoadFailed": "Image failed to load",
    "download": "Download",
    "openNewWindow": "Open in new window",
    "emptyTitle": "No images yet",
    "emptySub": "Enter a description above and click \"Generate image\" to start"
  },
  "settings": {
    "title": "Settings",
    "subtitle": "Manage console authentication and gateway runtime configuration.",
    "fetchError": "Failed to fetch config, please check session Key",
    "needKey": "Please enter a Key",
    "keySaved": "Key saved locally, refreshing data...",
    "keyCleared": "Key cleared",
    "concurrencySaved": "Concurrency config saved (effective at runtime immediately)",
    "saveFailed": "Save failed",
    "poolSaved": "Warm pool config saved (effective on next refresh round)",
    "aliasesSaved": "Model alias rules updated",
    "jsonError": "Invalid JSON format, please check syntax",
    "configRefreshed": "Config refreshed",
    "refreshBtn": "Refresh config",
    "sessionKeyTitle": "Current session Key",
    "sessionKeyDesc": "Paste an existing API Key here; the console will use it for all management operations. (Stored in the browser locally)",
    "sessionKeyPlaceholder": "sk-qwen-... or default admin key admin",
    "saveBtn": "Save",
    "clearBtn": "Clear",
    "connectionTitle": "Connection info",
    "baseUrlLabel": "API Base URL",
    "coreTitle": "Core concurrency parameters",
    "coreDesc": "Runtime concurrency slots and queue thresholds (must be changed in backend config.json and restarted to take effect).",
    "versionLabel": "Current system version",
    "maxInflightLabel": "Max concurrency per account (max_inflight_per_account)",
    "maxInflightDesc": "Requests each upstream account handles simultaneously. Too high risks bans, too low underutilizes.",
    "globalMaxLabel": "Global concurrency limit (global_max_inflight)",
    "globalMaxDesc": "Hard cap on total in-flight requests across all accounts. 0 = unlimited. Corresponds to the Dashboard \"Async tasks\" peak.",
    "saveConcurrencyBtn": "Save concurrency settings",
    "poolTitle": "Chat_ID warm pool",
    "poolDesc": "Pre-build chat_id to avoid the upstream /chats/new handshake (0.5~6s). Runtime changes take effect immediately.",
    "poolTargetLabel": "Per-account target (target)",
    "poolTargetDesc": "How many chat_id to pre-hang per account. Default 5.",
    "poolTtlLabel": "TTL (minutes)",
    "poolTtlDesc": "chat_id older than this is discarded and rebuilt, avoiding silent upstream reclamation. Default 10.",
    "savePoolBtn": "Save warm pool settings",
    "aliasesTitle": "Automatic model alias rules (Model Aliases)",
    "aliasesDesc": "Model names sent by downstream are auto-routed by the gateway to the actual Qwen models below. Please edit in standard JSON format.",
    "saveAliasesBtn": "Save aliases",
    "exampleTitle": "Usage example"
  }
}
```

- [ ] **Step 2: Xác minh JSON hợp lệ + cùng tập key với vi.json**

Run (trong `frontend/`):
```bash
node -e "const fs=require('fs');const flat=(o,p='')=>Object.keys(o).flatMap(k=>typeof o[k]==='object'?flat(o[k],p+k+'.'):[p+k]);const vi=flat(JSON.parse(fs.readFileSync('src/i18n/locales/vi.json','utf8'))).sort();const en=flat(JSON.parse(fs.readFileSync('src/i18n/locales/en.json','utf8'))).sort();const miss=vi.filter(k=>!en.includes(k));const extra=en.filter(k=>!vi.includes(k));if(miss.length||extra.length){console.error('MISMATCH miss:',miss,'extra:',extra);process.exit(1)}console.log('en.json OK, keys match vi.json')"
```
Expected: in `en.json OK, keys match vi.json`.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/i18n/locales/en.json
git commit -m "feat(i18n): thêm locale tiếng Anh"
```

---

## Task 5: Khởi tạo i18next

**Files:**
- Create: `frontend/src/i18n/index.ts`
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: Tạo `frontend/src/i18n/index.ts`**

```ts
import i18n from "i18next"
import { initReactI18next } from "react-i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import vi from "./locales/vi.json"
import zh from "./locales/zh.json"
import en from "./locales/en.json"

export const SUPPORTED_LANGUAGES = ["vi", "zh", "en"] as const
export type Lang = (typeof SUPPORTED_LANGUAGES)[number]

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      vi: { translation: vi },
      zh: { translation: zh },
      en: { translation: en },
    },
    fallbackLng: "vi",
    supportedLngs: SUPPORTED_LANGUAGES as unknown as string[],
    interpolation: { escapeValue: false },
    detection: {
      order: ["localStorage", "navigator"],
      lookupLocalStorage: "i18nextLng",
      caches: ["localStorage"],
    },
  })

export default i18n
```

- [ ] **Step 2: Cho phép import JSON trong TS (kiểm tra tsconfig)**

Run (trong `frontend/`):
```bash
node -e "const fs=require('fs');const t=fs.readFileSync('tsconfig.app.json','utf8');console.log(/resolveJsonModule/.test(t)?'has resolveJsonModule':'MISSING resolveJsonModule')"
```
Nếu in `MISSING resolveJsonModule`: mở `frontend/tsconfig.app.json`, trong `compilerOptions` thêm dòng:
```json
"resolveJsonModule": true,
```
(Nếu đã `has resolveJsonModule` thì bỏ qua bước sửa.)

- [ ] **Step 3: Import i18n trong `frontend/src/main.tsx`**

Mở `frontend/src/main.tsx`, thêm dòng import `./i18n` NGAY TRƯỚC dòng import `App` (để i18next khởi tạo trước khi render). Ví dụ phần đầu file sau khi sửa:

```tsx
import "./i18n"
import App from "./App"
```
(Giữ nguyên các import/khởi tạo khác trong file; chỉ chèn thêm dòng `import "./i18n"`.)

- [ ] **Step 4: Xác minh build chạy được tới bước này**

Run (trong `frontend/`):
```bash
npm run build
```
Expected: build PASS (chưa lỗi TypeScript).

- [ ] **Step 5: Commit**

```bash
git add frontend/src/i18n/index.ts frontend/src/main.tsx frontend/tsconfig.app.json
git commit -m "feat(i18n): khởi tạo i18next, nạp 3 locale, mặc định vi"
```

---

## Task 6: Component LanguageSwitcher

**Files:**
- Create: `frontend/src/components/LanguageSwitcher.tsx`

- [ ] **Step 1: Tạo `frontend/src/components/LanguageSwitcher.tsx`**

```tsx
import { useTranslation } from "react-i18next"
import { Languages } from "lucide-react"
import { SUPPORTED_LANGUAGES } from "../i18n"

const LABELS: Record<string, string> = { vi: "VI", zh: "中文", en: "EN" }

export default function LanguageSwitcher() {
  const { i18n, t } = useTranslation()
  const current = (SUPPORTED_LANGUAGES as readonly string[]).includes(i18n.language)
    ? i18n.language
    : "vi"

  return (
    <div className="flex items-center gap-2 px-3 py-2 text-sm text-muted-foreground">
      <Languages className="h-4 w-4" />
      <span className="sr-only">{t("common.language")}</span>
      <select
        value={current}
        onChange={e => i18n.changeLanguage(e.target.value)}
        className="bg-transparent outline-none font-medium cursor-pointer"
        aria-label={t("common.language")}
      >
        {SUPPORTED_LANGUAGES.map(lng => (
          <option key={lng} value={lng}>{LABELS[lng]}</option>
        ))}
      </select>
    </div>
  )
}
```

- [ ] **Step 2: Xác minh build**

Run (trong `frontend/`):
```bash
npm run build
```
Expected: build PASS.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/LanguageSwitcher.tsx
git commit -m "feat(i18n): thêm component LanguageSwitcher"
```

---

## Task 7: Việt hóa AdminLayout (menu + chèn LanguageSwitcher)

**Files:**
- Modify: `frontend/src/layouts/AdminLayout.tsx`

- [ ] **Step 1: Thêm import và hook**

Ở đầu `frontend/src/layouts/AdminLayout.tsx`, thêm 2 import:
```tsx
import { useTranslation } from "react-i18next"
import LanguageSwitcher from "../components/LanguageSwitcher"
```
Trong thân `AdminLayout()`, ngay sau `const loc = useLocation()`, thêm:
```tsx
const { t } = useTranslation()
```

- [ ] **Step 2: Thay mảng `navs` bằng key dịch**

Thay nguyên khối `const navs = [ ... ]` thành:
```tsx
  const navs = [
    { name: t("nav.dashboard"), path: "/", icon: LayoutDashboard },
    { name: t("nav.accounts"), path: "/accounts", icon: Activity },
    { name: t("nav.tokens"), path: "/tokens", icon: Key },
    { name: t("nav.test"), path: "/test", icon: MessageSquare },
    { name: t("nav.images"), path: "/images", icon: Image },
    { name: t("nav.settings"), path: "/settings", icon: Settings },
  ]
```

- [ ] **Step 3: Chèn LanguageSwitcher vào chân sidebar**

Tìm thẻ đóng `</nav>` của sidebar (sau vòng lặp `navs.map`). Ngay SAU `</nav>` và TRƯỚC `</aside>`, chèn:
```tsx
        <div className="border-t border-border/40 p-2">
          <LanguageSwitcher />
        </div>
```

- [ ] **Step 4: Xác minh không còn tiếng Trung trong file**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/layouts/AdminLayout.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: in `NO Chinese — OK`.

- [ ] **Step 5: Build + commit**

Run (trong `frontend/`): `npm run build` → Expected: PASS.
```bash
git add frontend/src/layouts/AdminLayout.tsx
git commit -m "feat(i18n): việt hóa AdminLayout và thêm bộ chuyển ngôn ngữ"
```

---

## Task 8: Việt hóa Dashboard

**Files:**
- Modify: `frontend/src/pages/Dashboard.tsx`

- [ ] **Step 1: Thêm hook useTranslation**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
```
Trong `Dashboard()`, ngay sau dòng khai báo state đầu tiên (`const [status, setStatus] = ...`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 2: Thay toast lỗi (dòng ~52)**

Thay:
```tsx
toast.error("状态获取失败，请在「系统设置」检查您的当前会话 Key。")
```
bằng:
```tsx
toast.error(t("dashboard.fetchError"))
```

- [ ] **Step 3: Thay tiêu đề + subtitle (dòng ~71-72)**

Thay:
```tsx
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">运行状态</h2>
        <p className="text-muted-foreground mt-2 text-lg">全局并发监控与千问账号池概览（每 3 秒自动刷新）。</p>
```
bằng:
```tsx
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">{t("dashboard.title")}</h2>
        <p className="text-muted-foreground mt-2 text-lg">{t("dashboard.subtitle")}</p>
```

- [ ] **Step 4: Thay 4 StatCard hàng đầu (dòng ~76-79)**

Thay nguyên 4 dòng `<StatCard .../>` thành:
```tsx
        <StatCard icon={<Server className="h-5 w-5 text-primary" />} title={t("dashboard.validAccounts")} value={String(acc.valid ?? 0)} accent="primary" sub={t("dashboard.totalCount", { count: acc.total ?? 0 })} />
        <StatCard icon={<Activity className="h-5 w-5 text-blue-400" />} title={t("dashboard.currentConcurrency")} value={String(acc.in_use ?? 0)} accent="blue" sub={t("dashboard.globalLimit", { count: acc.global_in_use ?? 0 })} />
        <StatCard icon={<ShieldAlert className="h-5 w-5 text-destructive" />} title={t("dashboard.queuedRequests")} value={String(acc.waiting ?? 0)} accent="destructive" sub={t("dashboard.queueLimit", { count: acc.max_queue_size ?? 0 })} />
        <StatCard icon={<ActivityIcon className="h-5 w-5 text-orange-400" />} title={t("dashboard.rateLimitedInvalid")} value={`${acc.rate_limited ?? 0} / ${acc.invalid ?? 0}`} accent="orange" />
```

- [ ] **Step 5: Thay 2 StatCard hàng hai (dòng ~83-84)**

Thay 2 dòng `<StatCard .../>` thành:
```tsx
        <StatCard icon={<Flame className="h-5 w-5 text-rose-400" />} title={t("dashboard.warmPool")} value={String(pool?.total_cached ?? 0)} accent="rose" sub={pool ? t("dashboard.warmPoolSub", { target: pool.target_per_account, minutes: Math.round((pool.ttl_seconds || 0) / 60) }) : t("dashboard.warmPoolDisabled")} />
        <StatCard icon={<Database className="h-5 w-5 text-cyan-400" />} title={t("dashboard.asyncTasks")} value={String(status?.runtime?.asyncio_running_tasks ?? 0)} accent="cyan" sub={t("dashboard.asyncTasksSub")} />
```

- [ ] **Step 6: Thay tiêu đề bảng + header cột (dòng ~93, ~100-105)**

Thay `账号并发详情` thành `{t("dashboard.accountDetail")}`.
Thay 6 `<th>` lần lượt:
```tsx
                  <th className="text-left px-6 py-3 font-semibold">{t("dashboard.colEmail")}</th>
                  <th className="text-left px-4 py-3 font-semibold">{t("dashboard.colStatus")}</th>
                  <th className="text-right px-4 py-3 font-semibold">{t("dashboard.colInflight")}</th>
                  <th className="text-right px-4 py-3 font-semibold">{t("dashboard.colWarmChatId")}</th>
                  <th className="text-right px-4 py-3 font-semibold">{t("dashboard.colConsecFail")}</th>
                  <th className="text-right px-4 py-3 font-semibold">{t("dashboard.colRateLimitStrikes")}</th>
```

- [ ] **Step 7: Thay khối API 接口池 (dòng ~142-153)**

Thay `API 接口池` thành `{t("dashboard.apiPool")}`.
Thay dòng `<p ...>兼容主流 AI 协议...</p>` thành:
```tsx
          <p className="text-base text-muted-foreground ml-5">{t("dashboard.apiPoolSub")}</p>
```
Thay `tag="健康检查"` (EndpointRow cuối, dòng ~153) thành `tag={t("dashboard.tagHealthCheck")}`.

- [ ] **Step 8: Xác minh không còn tiếng Trung**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/Dashboard.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK`.

- [ ] **Step 9: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/Dashboard.tsx
git commit -m "feat(i18n): việt hóa Dashboard"
```

---

## Task 9: Việt hóa AccountsPage

Đây là file nhiều chuỗi nhất, gồm helper ngoài component (`statusText`, `statusNote`, `localizeError`) và JSX bên trong. Vì helper nằm ngoài component nên không gọi hook được — sẽ nhận `t` qua tham số.

**Files:**
- Modify: `frontend/src/pages/AccountsPage.tsx`

- [ ] **Step 1: Thêm import useTranslation và kiểu TFunction**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
import type { TFunction } from "i18next"
```

- [ ] **Step 2: Sửa helper `statusText` nhận `t`**

Thay nguyên hàm `statusText` thành:
```tsx
function statusText(acc: AccountItem, t: TFunction) {
  switch (acc.status_code) {
    case "valid": return t("accounts.statusValid")
    case "pending_activation": return t("accounts.statusPending")
    case "rate_limited": return t("accounts.statusRateLimited")
    case "banned": return t("accounts.statusBanned")
    case "auth_error": return t("accounts.statusAuthError")
    default: return acc.valid ? t("accounts.statusValid") : t("accounts.statusInvalid")
  }
}
```

- [ ] **Step 3: Sửa helper `statusNote` nhận `t`**

Thay nguyên hàm `statusNote` thành:
```tsx
function statusNote(acc: AccountItem, t: TFunction) {
  if ((acc.rate_limited_until || 0) > Date.now() / 1000) {
    const seconds = Math.max(0, Math.ceil((acc.rate_limited_until! - Date.now() / 1000)))
    return t("accounts.recoverInSeconds", { seconds })
  }
  return acc.last_error || ""
}
```

- [ ] **Step 4: Sửa helper `localizeError` nhận `t`**

Thay nguyên hàm `localizeError` thành:
```tsx
function localizeError(error: string | undefined, t: TFunction) {
  if (!error) return t("accounts.errUnknown")
  const lower = error.toLowerCase()
  if (lower.includes("activation already in progress")) return t("accounts.errActivating")
  if (lower.includes("activation link or token not found")) return t("accounts.errActivationLink")
  if (lower.includes("token invalid") || lower.includes("token") || lower.includes("auth")) return t("accounts.errTokenInvalid")
  return error
}
```

- [ ] **Step 5: Lấy `t` trong component**

Trong `AccountsPage()`, ngay sau dòng state cuối (`const [verifyingAll, setVerifyingAll] = useState(false)`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 6: Thay các toast trong handler (sửa từng chuỗi)**

Trong toàn bộ thân component, thay các lời gọi sau (giữ nguyên tham số `{ id, ... }` nếu có):

| Cũ | Mới |
|---|---|
| `toast.error("刷新账号列表失败，请检查会话密钥")` | `toast.error(t("accounts.refreshListError"))` |
| `toast.error("请先填写 Token")` | `toast.error(t("accounts.needToken"))` |
| `toast.loading("正在注入账号...")` | `toast.loading(t("accounts.injecting"))` |
| `toast.success("账号已加入账号池", { id })` | `toast.success(t("accounts.injected"), { id })` |
| `toast.error(localizeError(data.error) || "账号注入失败", { id, duration: 8000 })` | `toast.error(localizeError(data.error, t) || t("accounts.injectFailed"), { id, duration: 8000 })` |
| `toast.error("账号注入请求失败", { id })` | `toast.error(t("accounts.injectRequestFailed"), { id })` |
| `toast.loading(\`正在删除 ${targetEmail}...\`)` | `toast.loading(t("accounts.deleting", { email: targetEmail }))` |
| `toast.success(\`已删除 ${targetEmail}\`, { id })` | `toast.success(t("accounts.deleted", { email: targetEmail }), { id })` |
| `toast.error("删除账号失败", { id })` | `toast.error(t("accounts.deleteFailed"), { id })` |
| `toast.loading("正在自动注册新账号，请稍候...")` | `toast.loading(t("accounts.autoRegistering"))` |
| `toast.warning(\`账号已注册，但仍需激活：${data.email}\`, { id, duration: 8000 })` | `toast.warning(t("accounts.registeredNeedActivate", { email: data.email }), { id, duration: 8000 })` |
| `toast.success(data.message \|\| \`注册成功：${data.email}\`, { id, duration: 8000 })` | `toast.success(data.message || t("accounts.registerSuccess", { email: data.email }), { id, duration: 8000 })` |
| `toast.error(localizeError(data.error) || "自动注册失败", { id, duration: 8000 })` | `toast.error(localizeError(data.error, t) || t("accounts.autoRegisterFailed"), { id, duration: 8000 })` |
| `toast.error("自动注册请求失败", { id })` | `toast.error(t("accounts.autoRegisterRequestFailed"), { id })` |
| `toast.loading(\`正在验证 ${targetEmail}...\`)` | `toast.loading(t("accounts.verifying", { email: targetEmail }))` |
| `toast.success(\`验证通过：${targetEmail}\`, { id })` | `toast.success(t("accounts.verifySuccess", { email: targetEmail }), { id })` |
| `toast.error(\`验证失败：${statusText(data) \|\| localizeError(data.error)}\`, { id, duration: 8000 })` | `toast.error(t("accounts.verifyFailed", { detail: statusText(data, t) || localizeError(data.error, t) }), { id, duration: 8000 })` |
| `toast.error("验证请求失败", { id })` | `toast.error(t("accounts.verifyRequestFailed"), { id })` |
| `toast.loading("正在并发巡检所有账号...")` | `toast.loading(t("accounts.verifyingAll"))` |
| `toast.success(\`全量巡检完成，并发数：${data.concurrency \|\| 1}\`, { id })` | `toast.success(t("accounts.verifyAllDone", { concurrency: data.concurrency || 1 }), { id })` |
| `toast.error("全量巡检失败", { id })` | `toast.error(t("accounts.verifyAllFailed"), { id })` |
| `toast.error("全量巡检请求失败", { id })` | `toast.error(t("accounts.verifyAllRequestFailed"), { id })` |
| `toast.loading(\`正在激活 ${targetEmail}...\`)` | `toast.loading(t("accounts.activating", { email: targetEmail }))` |
| `toast.success(\`账号正在激活中，请稍后刷新：${targetEmail}\`, { id, duration: 6000 })` | `toast.success(t("accounts.activatePending", { email: targetEmail }), { id, duration: 6000 })` |
| `toast.success(data.message \|\| \`激活成功：${targetEmail}\`, { id, duration: 6000 })` | `toast.success(data.message || t("accounts.activateSuccess", { email: targetEmail }), { id, duration: 6000 })` |
| `toast.error(\`激活失败：${localizeError(data.error \|\| data.message)}\`, { id, duration: 8000 })` | `toast.error(t("accounts.activateFailed", { detail: localizeError(data.error || data.message, t) }), { id, duration: 8000 })` |
| `toast.error("激活请求失败", { id })` | `toast.error(t("accounts.activateRequestFailed"), { id })` |
| `toast.success("账号列表已刷新")` | `toast.success(t("accounts.listRefreshed"))` |

- [ ] **Step 7: Thay JSX header + nút (dòng ~243-258)**

Thay:
```tsx
          <h2 className="text-3xl font-extrabold tracking-tight">{"账号管理"}</h2>
          <p className="text-muted-foreground mt-1">{"统一管理..."}</p>
```
bằng (đặt đúng nội dung 2 thẻ):
```tsx
          <h2 className="text-3xl font-extrabold tracking-tight">{t("accounts.title")}</h2>
          <p className="text-muted-foreground mt-1">{t("accounts.subtitle")}</p>
```
Thay text nút:
- `{"全量巡检"}` → `{t("accounts.verifyAllBtn")}`
- `{"刷新状态"}` → `{t("accounts.refreshBtn")}`
- nhánh đăng ký: `{registering ? "正在注册..." : "一键获取新号"}` → `{registering ? t("accounts.registeringBtn") : t("accounts.getNewBtn")}`

- [ ] **Step 8: Thay 5 thẻ thống kê (dòng ~263-267)**

Thay text trong 5 thẻ:
- `{"可用"}` → `{t("accounts.statValid")}`
- `{"未激活"}` → `{t("accounts.statPending")}`
- `{"限流"}` → `{t("accounts.statRateLimited")}`
- `{"封禁"}` → `{t("accounts.statBanned")}`
- `{"其他失效"}` → `{t("accounts.statInvalid")}`

- [ ] **Step 9: Thay khối "手动注入账号" (dòng ~272-294)**

- `{"手动注入账号"}` → `{t("accounts.manualInject")}`
- đoạn hướng dẫn dài `{"请先在 chat.qwen.ai..."}` → `{t("accounts.manualInjectHint")}`
- `{"重要：请只粘贴..."}` → `{t("accounts.manualInjectWarn")}`
- `{"请不要带 Bearer..."}` → `{t("accounts.manualInjectWarn2")}`
- label `{"Token（必填）"}` → `{t("accounts.tokenLabel")}`
- placeholder token `{"粘贴从 Local Storage..."}` → `{t("accounts.tokenPlaceholder")}`
- label `{"邮箱（选填）"}` → `{t("accounts.emailLabel")}`
- placeholder `{"邮箱地址"}` → `{t("accounts.emailPlaceholder")}`
- label `{"密码（选填）"}` → `{t("accounts.passwordLabel")}`
- placeholder `{"用于自动刷新或激活"}` → `{t("accounts.passwordPlaceholder")}`
- nút `{"注入账号"}` → `{t("accounts.injectBtn")}`

- [ ] **Step 10: Thay bảng danh sách (dòng ~300-345)**

- `{"账号列表"}` → `{t("accounts.listTitle")}`
- header cột: `{"账号"}`→`{t("accounts.colAccount")}`, `{"状态"}`→`{t("accounts.colStatus")}`, `{"并发负载"}`→`{t("accounts.colLoad")}`, `{"说明"}`→`{t("accounts.colNote")}`, `{"操作"}`→`{t("accounts.colActions")}`
- dòng rỗng `{"暂无账号..."}` → `{t("accounts.emptyList")}`
- ô trạng thái: `{statusText(acc)}` → `{statusText(acc, t)}`
- ô tải: `{acc.inflight || 0} {"线程"}` → `{t("accounts.threads", { count: acc.inflight || 0 })}`
- ô ghi chú: `title={statusNote(acc)}` → `title={statusNote(acc, t)}` và `{statusNote(acc) || "-"}` → `{statusNote(acc, t) || "-"}`
- nút `{"激活"}` → `{t("accounts.activateBtn")}`
- `title={"单独验证"}` → `title={t("accounts.verifyOne")}`
- `title={"删除账号"}` → `title={t("accounts.deleteAccount")}`

- [ ] **Step 11: Xác minh không còn tiếng Trung**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/AccountsPage.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK` (comment dòng 80 `邮箱+密码字段...` cũng nên đổi sang tiếng Việt/Anh hoặc xóa để pass; nếu muốn giữ comment thì grep sẽ vẫn báo — hãy dịch comment đó: `// Mở khóa chức năng đăng ký khi khớp đồng thời email + mật khẩu`).

- [ ] **Step 12: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/AccountsPage.tsx
git commit -m "feat(i18n): việt hóa AccountsPage"
```

---

## Task 10: Việt hóa TokensPage

**Files:**
- Modify: `frontend/src/pages/TokensPage.tsx`

- [ ] **Step 1: Thêm hook useTranslation**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
```
Trong `TokensPage()`, ngay sau dòng state đầu (`const [keys, setKeys] = useState<string[]>([])`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 2: Thay các chuỗi**

| Cũ | Mới |
|---|---|
| `toast.error("刷新失败，请检查会话 Key")` | `toast.error(t("tokens.refreshError"))` |
| `toast.success("已生成新的 API Key")` | `toast.success(t("tokens.generated"))` |
| `toast.error(data.detail \|\| "生成失败，请检查权限")` | `toast.error(data.detail \|\| t("tokens.generateFailed"))` |
| `.catch(() => toast.error("生成失败，请检查权限"))` | `.catch(() => toast.error(t("tokens.generateFailed")))` |
| `toast.success("API Key 已删除")` | `toast.success(t("tokens.deleted"))` |
| `toast.error(data.detail \|\| "删除失败")` | `toast.error(data.detail \|\| t("tokens.deleteFailed"))` |
| `.catch(() => toast.error("删除失败"))` | `.catch(() => toast.error(t("tokens.deleteFailed")))` |
| `<h2 ...>API Key 分发</h2>` | `<h2 ...>{t("tokens.title")}</h2>` |
| `<p ...>管理可以访问此网关的下游凭证。</p>` | `<p ...>{t("tokens.subtitle")}</p>` |
| `toast.success("已刷新")` | `toast.success(t("tokens.refreshed"))` |
| `<RefreshCw ... /> 刷新` | `<RefreshCw ... /> {t("tokens.refreshBtn")}` |
| `<Plus ... /> 生成新 Key` | `<Plus ... /> {t("tokens.generateBtn")}` |
| `<th ...>序号</th>` | `<th ...>{t("tokens.colIndex")}</th>` |
| `<th ...>操作</th>` | `<th ...>{t("tokens.colActions")}</th>` |
| `<td ...>暂无 API Key</td>` | `<td ...>{t("tokens.empty")}</td>` |

Ghi chú: header cột `API Key` (dòng 85) giữ nguyên — đây là thuật ngữ không dịch.

- [ ] **Step 3: Xác minh không còn tiếng Trung**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/TokensPage.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK`.

- [ ] **Step 4: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/TokensPage.tsx
git commit -m "feat(i18n): việt hóa TokensPage"
```

---

## Task 11: Việt hóa TestPage

**Files:**
- Modify: `frontend/src/pages/TestPage.tsx`

- [ ] **Step 1: Thêm hook useTranslation**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
```
Trong `TestPage()`, ngay sau dòng state đầu (`const [messages, setMessages] = useState...`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 2: Dịch 2 comment tiếng Trung sang tiếng Việt**

- Dòng 8: `// 渲染消息内容：自动把 Markdown 图片和图片 URL 渲染成 <img>` → `// Hiển thị nội dung tin nhắn: tự render ảnh Markdown và URL ảnh thành <img>`
- Dòng 61: `// 挂载时从 /v1/models 拉真实模型列表，失败回退到默认三项` → `// Khi mount, lấy danh sách model thật từ /v1/models; nếu lỗi thì giữ danh sách mặc định`

- [ ] **Step 3: Thay các chuỗi hiển thị**

| Cũ | Mới |
|---|---|
| `content: \`❌ 未知响应: ${JSON.stringify(data)}\`` | `content: \`❌ ${t("test.unknownResponse", { data: JSON.stringify(data) })}\`` |
| `content: "❌ 响应为空（账号可能未激活或无可用账号）"` | `content: t("test.emptyResponse")` |
| `toast.error(\`网络错误: ${err.message}\`)` | `toast.error(t("test.networkError", { message: err.message }))` |
| `content: \`❌ 网络错误: ${err.message}\`` | `content: \`❌ ${t("test.networkError", { message: err.message })}\`` |
| `<h2 ...>接口测试</h2>` | `<h2 ...>{t("test.title")}</h2>` |
| `<p ...>在此测试您的 API 分发是否正常工作。</p>` | `<p ...>{t("test.subtitle")}</p>` |
| `<span ...>模型:</span>` | `<span ...>{t("test.modelLabel")}</span>` |
| `<span className="font-medium">流式传输 (Stream)</span>` | `<span className="font-medium">{t("test.stream")}</span>` |
| `<RefreshCw ... /> 清空对话` | `<RefreshCw ... /> {t("test.clearChat")}` |
| `<p className="text-sm">发送一条消息以开始测试，系统将通过 /v1/chat/completions 进行调用。</p>` | `<p className="text-sm">{t("test.emptyHint")}</p>` |
| `<Bot ... /> 思考中...` | `<Bot ... /> {t("test.thinking")}` |
| `💭 思考过程 ({msg.reasoning.length} 字)` | `{t("test.reasoningSummary", { count: msg.reasoning.length })}` |
| `placeholder="输入测试消息..."` | `placeholder={t("test.inputPlaceholder")}` |

Lưu ý các chuỗi giữ nguyên `❌` đứng đầu vẫn còn trong JSX nhánh lỗi không có tiếng Trung — không cần đổi.

- [ ] **Step 4: Xác minh không còn tiếng Trung**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/TestPage.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK`.

- [ ] **Step 5: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/TestPage.tsx
git commit -m "feat(i18n): việt hóa TestPage"
```

---

## Task 12: Việt hóa ImagePage

**Files:**
- Modify: `frontend/src/pages/ImagePage.tsx`

- [ ] **Step 1: Thêm hook useTranslation**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
```
Trong `ImagePage()`, ngay sau dòng state đầu (`const [prompt, setPrompt] = useState("")`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 2: Dịch các comment JSX sang tiếng Việt**

- `{/* 输入区域 */}` → `{/* Khu vực nhập */}`
- `{/* 比例选择 */}` → `{/* Chọn tỉ lệ */}`
- `{/* 数量选择 */}` → `{/* Chọn số lượng */}`
- `{/* 尺寸预览 */}` → `{/* Xem trước kích thước */}`
- `{/* 生成按钮 */}` → `{/* Nút tạo */}`
- `{/* 错误提示 */}` → `{/* Thông báo lỗi */}`
- `{/* 加载状态占位 */}` → `{/* Khung chờ khi đang tải */}`
- `{/* 图片展示区 */}` → `{/* Khu hiển thị ảnh */}`
- `{/* 悬浮操作栏 */}` → `{/* Thanh thao tác nổi */}`
- `{/* 空状态 */}` → `{/* Trạng thái rỗng */}`

- [ ] **Step 3: Thay các chuỗi hiển thị**

| Cũ | Mới |
|---|---|
| `toast.error(\`生成失败: ${String(detail).slice(0, 80)}\`)` | `toast.error(t("images.generateFailed", { detail: String(detail).slice(0, 80) }))` |
| `setError("未返回图片，请重试")` | `setError(t("images.noImageReturned"))` |
| `toast.error("未返回图片，请重试")` | `toast.error(t("images.noImageReturned"))` |
| `toast.success(\`成功生成 ${newImages.length} 张图片\`)` | `toast.success(t("images.generateSuccess", { count: newImages.length }))` |
| `const msg = err.message \|\| "网络错误"` | `const msg = err.message \|\| t("images.networkError")` |
| `toast.error(\`生成失败: ${msg}\`)` | `toast.error(t("images.generateFailed", { detail: msg }))` |
| `<h2 ...>图片生成</h2>` | `<h2 ...>{t("images.title")}</h2>` |
| `<p ...>通过 Qwen3.6-Plus 生成 AI 图片，支持多种比例。</p>` | `<p ...>{t("images.subtitle")}</p>` |
| `<label ...>图片描述 (Prompt)</label>` | `<label ...>{t("images.promptLabel")}</label>` |
| `placeholder="描述你想生成的图片，例如：赛博朋克风格的猫咪，霓虹灯背景，超写实风格"` | `placeholder={t("images.promptPlaceholder")}` |
| `<p ...>Ctrl+Enter 快速生成</p>` | `<p ...>{t("images.ctrlEnterHint")}</p>` |
| `<label ...>图片比例</label>` | `<label ...>{t("images.ratioLabel")}</label>` |
| `<label ...>生成数量</label>` | `<label ...>{t("images.countLabel")}</label>` |
| `{v} 张` | `{t("images.countUnit", { count: v })}` |
| `<RefreshCw ... /> 生成中...` | `<RefreshCw ... /> {t("images.generating")}` |
| `<Wand2 ... /> 生成图片` | `<Wand2 ... /> {t("images.generateBtn")}` |
| `<p className="font-medium">正在生成图片...</p>` | `<p className="font-medium">{t("images.loadingTitle")}</p>` |
| `<p ...>图片生成通常需要 10-30 秒，请耐心等待</p>` | `<p ...>{t("images.loadingSub")}</p>` |
| `<h3 ...>生成结果 ({images.length} 张)</h3>` | `<h3 ...>{t("images.resultTitle", { count: images.length })}</h3>` |
| `<Button ...>清空</Button>` (dòng ~206) | `<Button ...>{t("images.clearBtn")}</Button>` |
| `<ImageIcon ... /> 图片加载失败` | `<ImageIcon ... /> {t("images.imageLoadFailed")}` |
| `<Download ... /> 下载` | `<Download ... /> {t("images.download")}` |
| `<Button ...>在新窗口打开</Button>` | `<Button ...>{t("images.openNewWindow")}</Button>` |
| `<p className="font-medium">还没有生成图片</p>` | `<p className="font-medium">{t("images.emptyTitle")}</p>` |
| `<p ...>在上方输入描述，点击「生成图片」开始创作</p>` | `<p ...>{t("images.emptySub")}</p>` |

- [ ] **Step 4: Xác minh không còn tiếng Trung**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/ImagePage.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK`.

- [ ] **Step 5: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/ImagePage.tsx
git commit -m "feat(i18n): việt hóa ImagePage"
```

---

## Task 13: Việt hóa SettingsPage

`curlExample` (dòng ~105-185) là code mẫu tiếng Anh — GIỮ NGUYÊN, không động vào.

**Files:**
- Modify: `frontend/src/pages/SettingsPage.tsx`

- [ ] **Step 1: Thêm hook useTranslation**

Đầu file thêm:
```tsx
import { useTranslation } from "react-i18next"
```
Trong `SettingsPage()`, ngay sau dòng state đầu (`const [settings, setSettings] = useState<any>(null)`), thêm:
```tsx
  const { t } = useTranslation()
```

- [ ] **Step 2: Thay các toast trong handler**

| Cũ | Mới |
|---|---|
| `toast.error("配置获取失败，请检查会话 Key")` | `toast.error(t("settings.fetchError"))` |
| `toast.error("请输入 Key")` | `toast.error(t("settings.needKey"))` |
| `toast.success("Key 已保存到本地，刷新数据...")` | `toast.success(t("settings.keySaved"))` |
| `toast.success("Key 已清除")` | `toast.success(t("settings.keyCleared"))` |
| `toast.success("并发配置已保存（运行时立即生效）")` | `toast.success(t("settings.concurrencySaved"))` |
| `toast.error("保存失败")` (3 chỗ) | `toast.error(t("settings.saveFailed"))` |
| `toast.success("预热池配置已保存（下一轮刷新生效）")` | `toast.success(t("settings.poolSaved"))` |
| `toast.success("模型映射规则已更新")` | `toast.success(t("settings.aliasesSaved"))` |
| `toast.error("JSON 格式错误，请检查语法")` | `toast.error(t("settings.jsonError"))` |
| `toast.success("配置已刷新")` | `toast.success(t("settings.configRefreshed"))` |

- [ ] **Step 3: Thay tiêu đề + nút làm mới (dòng ~191-196)**

| Cũ | Mới |
|---|---|
| `<h2 ...>系统设置</h2>` | `<h2 ...>{t("settings.title")}</h2>` |
| `<p ...>管理控制台认证与网关运行时配置。</p>` | `<p ...>{t("settings.subtitle")}</p>` |
| `<RefreshCw ... /> 刷新配置` | `<RefreshCw ... /> {t("settings.refreshBtn")}` |

- [ ] **Step 4: Khối Session Key (dòng ~205-219)**

| Cũ | Mới |
|---|---|
| `<h3 ...>当前会话 Key</h3>` | `<h3 ...>{t("settings.sessionKeyTitle")}</h3>` |
| `<p ...>将已有的 API Key 粘贴到此处...（保存在浏览器本地）</p>` | `<p ...>{t("settings.sessionKeyDesc")}</p>` |
| `placeholder="sk-qwen-... 或默认管理员密钥 admin"` | `placeholder={t("settings.sessionKeyPlaceholder")}` |
| `<Button onClick={handleSaveSessionKey}>保存</Button>` | `<Button onClick={handleSaveSessionKey}>{t("settings.saveBtn")}</Button>` |
| `<Button variant="ghost" onClick={handleClearSessionKey}>清除</Button>` | `<Button variant="ghost" onClick={handleClearSessionKey}>{t("settings.clearBtn")}</Button>` |

- [ ] **Step 5: Khối Connection Info (dòng ~229-234)**

| Cũ | Mới |
|---|---|
| `<h3 ...>连接信息</h3>` | `<h3 ...>{t("settings.connectionTitle")}</h3>` |
| `<label ...>API 基础地址 (Base URL)</label>` | `<label ...>{t("settings.baseUrlLabel")}</label>` |

- [ ] **Step 6: Khối Core Settings (dòng ~245-285)**

| Cũ | Mới |
|---|---|
| `<h3 ...>核心并发参数</h3>` | `<h3 ...>{t("settings.coreTitle")}</h3>` |
| `<p ...>运行时并发槽位与排队阈值（需要在后端 config.json 中修改后重启生效）。</p>` | `<p ...>{t("settings.coreDesc")}</p>` |
| `<span ...>当前系统版本</span>` | `<span ...>{t("settings.versionLabel")}</span>` |
| `<span ...>单账号最大并发 (max_inflight_per_account)</span>` | `<span ...>{t("settings.maxInflightLabel")}</span>` |
| `<p ...>每个上游账号同时处理的请求数。太大易被封，太小不充分利用。</p>` | `<p ...>{t("settings.maxInflightDesc")}</p>` |
| `<span ...>全局并发上限 (global_max_inflight)</span>` | `<span ...>{t("settings.globalMaxLabel")}</span>` |
| `<p ...>所有账号合计同时在途请求的硬上限。0 = 不限。对应 Dashboard 的"异步任务"峰值。</p>` | `<p ...>{t("settings.globalMaxDesc")}</p>` |
| `<Button size="sm" onClick={handleSaveConcurrency}>保存并发设置</Button>` | `<Button size="sm" onClick={handleSaveConcurrency}>{t("settings.saveConcurrencyBtn")}</Button>` |

- [ ] **Step 7: Khối Chat ID Pool (dòng ~295-329)**

| Cũ | Mới |
|---|---|
| `<h3 ...>Chat_ID 预热池</h3>` | `<h3 ...>{t("settings.poolTitle")}</h3>` |
| `<p ...>预建 chat_id 规避上游 /chats/new 握手 (0.5~6s)。运行时修改立即生效。</p>` | `<p ...>{t("settings.poolDesc")}</p>` |
| `<span ...>每账号目标数 (target)</span>` | `<span ...>{t("settings.poolTargetLabel")}</span>` |
| `<p ...>每个账号预先挂多少个 chat_id 等着。默认 5。</p>` | `<p ...>{t("settings.poolTargetDesc")}</p>` |
| `<span ...>TTL (分钟)</span>` | `<span ...>{t("settings.poolTtlLabel")}</span>` |
| `<p ...>chat_id 超过此时长则丢弃重建，避免被上游静默回收。默认 10。</p>` | `<p ...>{t("settings.poolTtlDesc")}</p>` |
| `<Button size="sm" onClick={handleSavePool}>保存预热池设置</Button>` | `<Button size="sm" onClick={handleSavePool}>{t("settings.savePoolBtn")}</Button>` |

- [ ] **Step 8: Khối Model Mapping + Usage Example (dòng ~337-359)**

| Cũ | Mới |
|---|---|
| `<h3 ...>自动模型映射规则 (Model Aliases)</h3>` | `<h3 ...>{t("settings.aliasesTitle")}</h3>` |
| `<p ...>下游传入的模型名称将被网关自动路由至以下千问实际模型。请使用标准 JSON 格式编辑。</p>` | `<p ...>{t("settings.aliasesDesc")}</p>` |
| `<Button onClick={handleSaveAliases}>保存映射</Button>` | `<Button onClick={handleSaveAliases}>{t("settings.saveAliasesBtn")}</Button>` |
| `<h3 ...>使用示例</h3>` | `<h3 ...>{t("settings.exampleTitle")}</h3>` |

- [ ] **Step 9: Xác minh không còn tiếng Trung (ngoài curlExample)**

Run (trong `frontend/`):
```bash
grep -nP '[\x{4e00}-\x{9fff}]' src/pages/SettingsPage.tsx; test $? -eq 1 && echo "NO Chinese — OK"
```
Expected: `NO Chinese — OK`. (curlExample là tiếng Anh nên không vướng grep này. Nếu grep báo dòng nào, đối chiếu bảng trên để xử lý nốt.)

- [ ] **Step 10: Build + commit**

Run: `npm run build` → PASS.
```bash
git add frontend/src/pages/SettingsPage.tsx
git commit -m "feat(i18n): việt hóa SettingsPage"
```

---

## Task 14: Kiểm thử & xác minh toàn bộ

**Files:** (không sửa file, chỉ chạy kiểm tra)

- [ ] **Step 1: Kiểm tra 3 locale cùng tập key**

Run (trong `frontend/`):
```bash
node -e "const fs=require('fs');const flat=(o,p='')=>Object.keys(o).flatMap(k=>typeof o[k]==='object'?flat(o[k],p+k+'.'):[p+k]);const load=f=>flat(JSON.parse(fs.readFileSync('src/i18n/locales/'+f,'utf8'))).sort();const vi=load('vi.json'),zh=load('zh.json'),en=load('en.json');const cmp=(a,b,na,nb)=>{const m=a.filter(k=>!b.includes(k));if(m.length){console.error(na+' có key '+nb+' thiếu:',m);process.exit(1)}};cmp(vi,zh,'vi','zh');cmp(zh,vi,'zh','vi');cmp(vi,en,'vi','en');cmp(en,vi,'en','vi');console.log('3 locale khớp key — OK ('+vi.length+' key)')"
```
Expected: `3 locale khớp key — OK (N key)`.

- [ ] **Step 2: Quét tiếng Trung còn sót trong toàn bộ JSX/TSX (trừ zh.json)**

Run (trong `frontend/`):
```bash
grep -rnP '[\x{4e00}-\x{9fff}]' src --include='*.tsx' --include='*.ts' | grep -v 'locales/zh.json' | grep -vE 'src/lib/api\.ts|src/index\.css'
```
Expected: không in dòng nào (chỉ còn tiếng Trung trong `zh.json` và comment của `api.ts`/`index.css`). Nếu in ra dòng nào trong 7 file giao diện, quay lại task tương ứng xử lý.

- [ ] **Step 3: Build production**

Run (trong `frontend/`):
```bash
npm run build
```
Expected: PASS (TypeScript + Vite, không lỗi).

- [ ] **Step 4: Lint**

Run (trong `frontend/`):
```bash
npm run lint
```
Expected: không phát sinh lỗi mới so với trước khi bắt đầu (nếu repo vốn có cảnh báo cũ thì bỏ qua, miễn không thêm lỗi mới từ thay đổi i18n).

- [ ] **Step 5: Kiểm thử thủ công 3 ngôn ngữ**

Run (trong `frontend/`):
```bash
npm run dev
```
Mở trình duyệt, lần lượt:
- Mặc định hiển thị tiếng Việt (lần đầu, chưa có localStorage).
- Dùng LanguageSwitcher ở chân sidebar đổi sang 中文 → toàn bộ menu + 6 trang hiển thị tiếng Trung gốc.
- Đổi sang EN → hiển thị tiếng Anh.
- Reload trang → vẫn giữ ngôn ngữ vừa chọn (đọc từ localStorage `i18nextLng`).
- Kiểm tra nhanh các chuỗi nội suy: Dashboard `Tổng N tài khoản`, Accounts toast khi thao tác, Images `Kết quả (N ảnh)`.
- Layout không vỡ ở cả 3 ngôn ngữ.

- [ ] **Step 6: Commit cuối (nếu có chỉnh sửa nhỏ khi kiểm thử)**

```bash
git add -A
git commit -m "test(i18n): xác minh 3 ngôn ngữ, build & lint pass"
```

---

## Tổng kết file thay đổi

**Tạo mới:**
- `frontend/src/i18n/index.ts` — khởi tạo i18next.
- `frontend/src/i18n/locales/vi.json` — locale tiếng Việt (mặc định).
- `frontend/src/i18n/locales/zh.json` — locale tiếng Trung (text gốc).
- `frontend/src/i18n/locales/en.json` — locale tiếng Anh.
- `frontend/src/components/LanguageSwitcher.tsx` — bộ chuyển ngôn ngữ.

**Sửa:**
- `frontend/package.json` (+ `package-lock.json`) — thêm 3 dependency i18n.
- `frontend/src/main.tsx` — `import "./i18n"`.
- `frontend/tsconfig.app.json` — `resolveJsonModule` (nếu thiếu).
- `frontend/src/layouts/AdminLayout.tsx` — menu + chèn LanguageSwitcher.
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/AccountsPage.tsx`
- `frontend/src/pages/TokensPage.tsx`
- `frontend/src/pages/TestPage.tsx`
- `frontend/src/pages/ImagePage.tsx`
- `frontend/src/pages/SettingsPage.tsx`

**Giữ nguyên (không dịch):**
- Comment tiếng Trung trong `frontend/src/lib/api.ts`, `frontend/src/index.css`.
- `curlExample` trong `SettingsPage.tsx` (code mẫu tiếng Anh).
- Hash `_UH` trong `AccountsPage.tsx` (SHA-256 một chiều, không phải text hiển thị).
