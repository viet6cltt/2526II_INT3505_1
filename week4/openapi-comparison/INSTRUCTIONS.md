# INSTRUCTIONS

## Mục tiêu
So sánh OpenAPI với các công cụ:
- API Blueprint
- RAML
- TypeSpec
- TypeAPI

---------------

## Nội dung so sánh

Các tiêu chí:
- Cách viết (YAML, Markdown, DSL, JSON)
- Mục đích sử dụng
- Tool hỗ trợ (UI, generate code)
- Mức độ phổ biến

---------------

## Cách làm

1. Viết cùng 1 API (Book API) bằng các format
2. Render UI:
   - OpenAPI → Swagger
   - API Blueprint → Aglio
   - RAML → HTML
   - TypeSpec → OpenAPI → Swagger
   - TypeAPI → TypeAPI Viewer
3. So sánh kết quả

---

## So sánh 

- OpenAPI: Dạng yaml, có cấu trúc lồng nhau rất sâu, yêu cầu khai báo tỉ mỉ từng thuộc tính dữ liệu. Có tài liệu tham khảo nhiều.
- API Blueprint: Dạng Markdown, sử dụng các ký hiệu #, +, - để định nghĩa, thân thiện với người không chuyên kỹ thuật, dễ đọc như Markdown.
- RAML: dạng yaml, có cấu trúc rõ ràng hơn OpenAPI, hỗ trợ tái sử dụng tốt(types, traits), thiết kế theo hướng design-first, ít phổ biến hơn OpenAPI.
- TypeSpec: Dạng DSL(giống TypeScript), cho phép định nghĩa model và API một cách gọn gàng, viết API bằng tư duy lập trình thay vì khai báo dữ liệu.
- TypeAPI: dạng JSON, tuy nhiên lại không phổ biến nhiều.

## Kết luận

- OpenAPI: có hệ sinh thái khổng lồ, tài liệu hỗ trợ cực lớn.
- API Blueprint: thiên về documentation, là cầu nối tốt giữa Developer và các bên không chuyên.
- RAML: Tốt ưu nhất cho thiết kế, có khả năng quản lý project lớn tốt nhờ tính module hóa cao.
- TypeSpec: Năng suất cao nhất, rất mạnh trong việc tái sử dụng Model, 1 dòng TypeSpec có thể sinh ra 5-10 dòng OpenAPI (ở trên, file docs viết bằng TypeSpec ~150, OpenAPI ~550 dòng.)
- TypeAPI: hỗ trợ viết API gọn nhẹ, hiện đại.