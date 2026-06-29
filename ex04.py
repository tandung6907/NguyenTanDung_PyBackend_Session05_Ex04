"""
PHÂN TÍCH & ĐỀ XUẤT ĐA GIẢI PHÁP

1. PHÂN TÍCH INPUT/OUTPUT
Input bài toán:
    - product_id (path parameter, int): id của sản phẩm cần cập nhật
    - Body request gồm: code (str), name (str), price (float), stock (int)

Output thành công:
    - Trả về thông tin sản phẩm sau khi cập nhật (id, code, name, price, stock)

Output thất bại (dùng HTTPException):
    - product_id không tồn tại        -> 404, detail: "Product not found"
    - code bị trùng với sản phẩm khác -> 400, detail: "Product code already exists"
    - name rỗng                        -> 400, detail: "Product name must not be empty"
    - price <= 0                       -> 400, detail: "Price must be greater than 0"
    - stock < 0                        -> 400, detail: "Stock must be greater than or equal to 0"


2. ĐỀ XUẤT TỐI THIỂU 2 GIẢI PHÁP
Giải pháp 1: Duyệt list (linear search)
    - Dùng vòng lặp for (hoặc generator + next()) duyệt qua từng phần
      tử trong products để tìm sản phẩm có "id" == product_id.
    - Khi kiểm tra trùng code, tiếp tục duyệt products một lần nữa,
      so sánh p["code"] == new_code và p["id"] != product_id.
    - Độ phức tạp tìm kiếm: O(n) cho mỗi lần tìm theo id hoặc theo code.

Giải pháp 2: Dùng dict (index theo id)
    - Xây dựng một dict phụ products_index = {p["id"]: p for p in products}
      để tra cứu sản phẩm theo id với độ phức tạp O(1).
    - Để kiểm tra trùng code nhanh, có thể xây thêm dict
      code_index = {p["code"]: p["id"]} ánh xạ code -> id.
    - Khi update, sau khi sửa dữ liệu trong dict, cần đồng bộ lại cả
      list products (hoặc thay thế hoàn toàn list bằng dict làm kho
      lưu trữ chính, bỏ list đi).


PHẦN 2: SO SÁNH & LỰA CHỌN GIẢI PHÁP

Tiêu chí          | Giải pháp 1: Duyệt list          | Giải pháp 2: Dùng dict
------------------|-----------------------------------|--------------------------------------
Tốc độ tìm kiếm   | O(n) - chậm hơn khi dữ liệu lớn    | O(1) - tra cứu theo id/code rất nhanh
Bộ nhớ            | Không tốn thêm bộ nhớ phụ          | Tốn thêm bộ nhớ cho dict index
Dễ hiểu           | Trực quan, dễ đọc với người mới    | Cần hiểu thêm về cấu trúc index phụ
Dễ bảo trì        | Đơn giản, ít rủi ro đồng bộ dữ liệu | Phải đồng bộ dict index mỗi khi
                  |                                     | thêm/sửa/xóa, dễ phát sinh lỗi lệch dữ liệu
Bối cảnh phù hợp  | Dữ liệu nhỏ, ít sản phẩm (như đề    | Dữ liệu lớn, cần tra cứu liên tục,
                  | bài hiện tại chỉ có vài sản phẩm)   | hệ thống production có hàng nghìn bản ghi

Kết luận lựa chọn:
    Với bài toán hiện tại, dữ liệu products chỉ có vài phần tử và được
    cung cấp sẵn dưới dạng list (đúng với cấu trúc dữ liệu ban đầu của
    đề bài), nên chọn Giải pháp 1 - Duyệt list. Lý do: độ phức tạp O(n)
    không ảnh hưởng đáng kể với số lượng sản phẩm nhỏ, code đơn giản,
    dễ đọc, dễ bảo trì và không phải lo việc đồng bộ dữ liệu giữa list
    gốc và dict index phụ. Giải pháp dùng dict sẽ phù hợp hơn nếu hệ
    thống mở rộng lên quy mô lớn với hàng nghìn sản phẩm và cần tối ưu
    tốc độ tra cứu.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

products = [
    {"id": 1, "code": "SP001", "name": "Keyboard", "price": 500000, "stock": 10},
    {"id": 2, "code": "SP002", "name": "Mouse", "price": 300000, "stock": 5}
]


class ProductUpdate(BaseModel):
    code: str
    name: str
    price: float
    stock: int


@app.put("/products/{product_id}")
def update_product(product_id: int, product: ProductUpdate):
    target_product = next((p for p in products if p["id"] == product_id), None)
    if target_product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # Kiểm tra mã sản phẩm có bị trùng với sản phẩm khác không (bẫy 2)
    code_exists = any(
        p["code"] == product.code and p["id"] != product_id
        for p in products
    )
    if code_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product code already exists"
        )

    if not product.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name must not be empty"
        )

    if product.price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Price must be greater than 0"
        )

    if product.stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock must be greater than or equal to 0"
        )

    target_product["code"] = product.code
    target_product["name"] = product.name
    target_product["price"] = product.price
    target_product["stock"] = product.stock

    return target_product