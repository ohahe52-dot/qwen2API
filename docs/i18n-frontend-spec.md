# Việt hóa giao diện frontend (đa ngôn ngữ i18n)

Ngày: 2026-05-29

## Mục tiêu

Việt hóa giao diện admin của repo `qwen2API`. Giao diện hiện đang dùng tiếng Trung
hard-code trong JSX. Thay vì dịch cứng, dựng hệ thống đa ngôn ngữ (i18n) hỗ trợ
**3 ngôn ngữ: Việt (vi), Trung (zh), Anh (en)**, mặc định **tiếng Việt**, có nút
chuyển đổi và ghi nhớ lựa chọn của người dùng.

## Bối cảnh

- Frontend: React 19 + TypeScript + Vite 6 + Tailwind 4 + react-router 7 + sonner (toast).
- Text hiển thị nằm trong 7 file:
  - `src/layouts/AdminLayout.tsx` (menu điều hướng)
  - `src/pages/Dashboard.tsx`
  - `src/pages/AccountsPage.tsx`
  - `src/pages/TokensPage.tsx`
  - `src/pages/TestPage.tsx`
  - `src/pages/ImagePage.tsx`
  - `src/pages/SettingsPage.tsx`
- Tổng ~219 đoạn text tiếng Trung. Nhiều chuỗi có nội suy biến
  (vd: `共 ${acc.total} 个`, `全局上限 ${...}`).
- Tiếng Trung trong `src/lib/api.ts` và `src/index.css` chỉ là **comment** trong code,
  KHÔNG phải text hiển thị → giữ nguyên, không dịch.

## Phương án lõi i18n (đã chọn)

Dùng **`react-i18next`** (`i18next` + `react-i18next`):
- Xử lý sẵn nội suy biến `t('key', { count })`.
- Tự lưu/đọc lựa chọn ngôn ngữ qua localStorage (`i18nextLng`) bằng
  `i18next-browser-languagedetector`.
- Là chuẩn phổ biến của hệ sinh thái React; đáng tin với khối lượng chuỗi nội suy lớn.

Thêm dependency: `i18next`, `react-i18next`, `i18next-browser-languagedetector`.

## Kiến trúc & cấu trúc file

```
frontend/src/
  i18n/
    index.ts                 # khởi tạo i18next: default 'vi', fallback 'vi',
                             # detect order: localStorage → mặc định 'vi'
    locales/
      vi.json                # tiếng Việt (mặc định)
      zh.json                # tiếng Trung (giữ nguyên text gốc)
      en.json                # tiếng Anh
  components/
    LanguageSwitcher.tsx     # dropdown chuyển VI / 中文 / EN
```

- `src/main.tsx`: `import './i18n'` trước khi render `<App />`.
- Mỗi file locale là object JSON gom theo namespace:
  `nav`, `common`, `dashboard`, `accounts`, `tokens`, `test`, `images`, `settings`.
- Ngôn ngữ mặc định **vi**; lựa chọn người dùng lưu localStorage, giữ sau reload.

## Thay đổi trong từng file

- **7 file giao diện**: text tiếng Trung hard-code → `t('namespace.key')`.
  Mỗi component dùng hook `useTranslation()`.
- **Nội suy biến**: `共 ${acc.total} 个` → `t('dashboard.totalCount', { count: acc.total })`,
  giá trị trong JSON dạng `"共 {{count}} 个"` (zh) / `"Tổng {{count}} tài khoản"` (vi) /
  `"{{count}} total"` (en).
- **toast.error/success**: dùng `t(...)` (vd thông báo lỗi `Dashboard.tsx:52`).
- **`AdminLayout.tsx`**: mảng `navs` dùng `t('nav.*')`; chèn `<LanguageSwitcher>`
  vào chân sidebar và header mobile.
- **Comment tiếng Trung** trong `api.ts`, `index.css`: giữ nguyên.
- **`<title>` / document title**: mặc định để `qwen2API` (không bắt buộc i18n).

## LanguageSwitcher

- Dropdown nhỏ gọn, icon `Languages` từ `lucide-react` (đã có sẵn).
- 3 lựa chọn: `VI` / `中文` / `EN`.
- Khi chọn: gọi `i18n.changeLanguage(lng)`, tự lưu localStorage qua language-detector.
- Vị trí: chân sidebar (không phá layout hiện tại), và truy cập được trên mobile.

## Kiểm thử & xác minh

- `npm run build` pass (TypeScript + Vite).
- `npm run lint` không phát sinh lỗi mới.
- Quét lại: không còn ký tự tiếng Trung trong JSX của 7 file
  (chỉ còn trong `zh.json` và comment code).
- Thủ công: `npm run dev`, đổi qua 3 ngôn ngữ, xác nhận text đổi đúng,
  layout không vỡ, lựa chọn ngôn ngữ giữ sau reload.

## Ngoài phạm vi (YAGNI)

- Không dịch comment trong code.
- Không i18n cho phần backend.
- Không thêm ngôn ngữ ngoài vi/zh/en.
- Không tách chuỗi của thư viện bên thứ ba (sonner, lucide).
