# Học phần: Nhập môn Trí tuệ Nhân tạo (252ARIN330585_07)

Repository học tập của tôi cho học phần **Trí Tuệ Nhân Tạo / Artificial Intelligence**.

## Thông tin sinh viên

- **Sinh viên thực hiện**: Nguyễn Đức Phát
- **Mã số sinh viên**: 24110296
- **Lớp học phần**: 252ARIN330585_07
- **Trường**: Đại học Công Nghệ Kỹ thuật Thành phố Hồ Chí Minh (HCM-UTE)
- **Mục đích**: Lưu trữ bài tập về nhà, báo cáo notebook, source code mô phỏng và phiên bản web trực quan hóa các thuật toán AI đã học.

## Phiên bản Web

- **Deployment target**: Streamlit Community Cloud.
- **URL public đề xuất**: [https://artificial-intelligence-btvn.streamlit.app](https://artificial-intelligence-btvn.streamlit.app)
- **Repository**: [https://github.com/ducphat1509-beep/artificial-intelligence](https://github.com/ducphat1509-beep/artificial-intelligence)
- **Branch**: `main`
- **Entry point**: `src/main.py`

*Lưu ý: Ứng dụng web được xây dựng bằng Streamlit, chạy trực tiếp trên Streamlit Community Cloud bằng cách tự động cài đặt các thư viện trong `requirements.txt` và tự động cập nhật khi có commit mới trên branch `main`.*

## Cách chạy phiên bản Web ở local

Để chạy ứng dụng ở máy local, bạn nên tạo một môi trường ảo (virtual environment) để tránh xung đột thư viện:

1. **Khởi tạo môi trường ảo (venv)**:
   ```powershell
   python -m venv .venv
   ```

2. **Kích hoạt môi trường ảo**:
   - Trên **Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - Trên **Windows (Command Prompt)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - Trên **macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

3. **Cài đặt các thư viện**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Khởi chạy web app**:
   ```bash
   streamlit run src/main.py
   ```

Sau khi khởi chạy thành công, trình duyệt sẽ tự động mở hoặc bạn có thể truy cập thủ công địa chỉ:
```text
http://localhost:8501
```

## Cách deploy lên Streamlit Community Cloud

Tài liệu chính thức của Streamlit Community Cloud:
- [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)

Các bước deploy cơ bản:
1. Đảm bảo mã nguồn mới nhất đã được đẩy lên GitHub:
   ```bash
   git push origin main
   ```
2. Truy cập [https://share.streamlit.io](https://share.streamlit.io) và đăng nhập bằng tài khoản GitHub chứa repository này.
3. Nhấp vào nút **Create app** (hoặc **Deploy an app**) và cấu hình như sau:
   - **Repository**: `ducphat1509-beep/artificial-intelligence`
   - **Branch**: `main`
   - **Main file path**: `src/main.py`
   - **App URL**: `artificial-intelligence-btvn`
4. Chọn **Deploy**. Sau khi cài đặt môi trường thành công, ứng dụng sẽ hoạt động tại URL đã đăng ký.

*Mẹo: Nếu URL mong muốn đã bị trùng, hãy đổi **App URL** sang một tên khác (ví dụ: `ai-btvn-24110296`) rồi cập nhật lại liên kết trong file README này.*

## Tổng quan các Module trong phiên bản Web

Ứng dụng trực quan hóa gồm 4 module chính tương ứng với các chủ đề bài học:

1. **Search Algorithms** (Module Tìm kiếm): Trực quan hóa đường đi trên Grid Pathfinding, giải 8-Puzzle và xếp 8 quân hậu (8-Queens).
2. **Vacuum Agent** (Module Tác tử hút bụi): Mô phỏng hoạt động của Simple Reflex Agent và Model-Based Agent trong phòng 4x4.
3. **CSP Lab** (Module Thỏa mãn ràng buộc): Giải bài toán Tô màu bản đồ Úc (Map Coloring) và xếp 8-Puzzle dưới dạng CSP.
4. **Adversarial Search** (Module Tìm kiếm đối kháng): Debug trực quan từng bước đệ quy của thuật toán trong trò chơi Tic-Tac-Toe.

---

## Chi tiết Thuật toán & Phương pháp Trực quan

### 1. Tìm kiếm không có thông tin (Uninformed Search)
- **BFS** (Breadth-First Search)
- **DFS** (Depth-First Search)
- **IDS** (Iterative Deepening Search)
- **UCS** (Uniform Cost Search)

### 2. Tìm kiếm có thông tin (Informed Search)
- **Greedy Best-First Search**
- **A* Search**
- **IDA* Search**
- *Hàm Heuristic tích hợp*: Manhattan Distance (Khoảng cách Manhattan) và Misplaced Tiles (Số ô sai vị trí) áp dụng cho 8-Puzzle và Grid Pathfinding.

### 3. Tìm kiếm cục bộ & Tối ưu hóa (Local Search & Meta-heuristic)
- **Simple Hill Climbing** (Leo đồi đơn giản)
- **Steepest-Ascent Hill Climbing** (Leo đồi dốc nhất)
- **Stochastic Hill Climbing** (Leo đồi ngẫu nhiên)
- **Hill Climbing with Sideways Moves** (Leo đồi cho phép đi ngang)
- **Random-Restart Hill Climbing** (Leo đồi khởi động lại ngẫu nhiên)
- **Local Beam Search** (`k = 2`, chọn trạng thái tốt hơn)
- **Local Beam Search** (`k = 2`, chọn trạng thái tốt nhất)
- **Simulated Annealing** (Mô phỏng luyện kim)

### 4. Tìm kiếm trong môi trường phức tạp (Complex Environments)
- **Sensorless / Belief State Search** (Tìm kiếm không cảm biến)
- **Partial Observation Search** (Tìm kiếm quan sát một phần)
- **AND-OR Graph Search** (Tìm kiếm trên đồ thị AND-OR)

### 5. Bài toán thỏa mãn ràng buộc (CSP - Constraint Satisfaction Problem)
- **Backtracking** (Quay lui cơ bản)
- **Forward Checking** (Kiểm tra trước)
- **AC-3 Algorithm + Backtracking** (Thuật toán Arc Consistency 3 kết hợp quay lui)
- **Min-Conflicts** (Thuật toán tối thiểu xung đột)

### 6. Tìm kiếm đối kháng (Adversarial Search)
- **Minimax**
- **Alpha-Beta Pruning** (Cắt tỉa Alpha-Beta)
- **Expectimax**

---

## Nội dung theo buổi học

- **Buổi 4**: Tác tử hút bụi (Vacuum Agent - Simple Reflex & Model-Based Agent).
- **Buổi 5**: Giải 8-Puzzle bằng BFS và DFS.
- **Buổi 6**: Giải 8-Puzzle bằng thuật toán tìm kiếm sâu dần (IDS).
- **Buổi 7**: Giải 8-Puzzle bằng tìm kiếm chi phí đồng nhất (UCS) với tùy chỉnh Step Cost.
- **Buổi 8**: Greedy Best-First Search và A* Search trên 8-Puzzle & Pathfinding.
- **Buổi 9**: Thuật toán IDA* và Hill Climbing.
- **Buổi 10**: Các biến thể nâng cao của Hill Climbing (Steepest-Ascent, Stochastic, Sideways Moves, Random-Restart) và Local Beam Search.
- **Buổi 11**: Simulated Annealing và Belief State.
- **Buổi 12**: Sensorless Search, Partial Observation và AND-OR Graph Search.
- **Buổi 13**: CSP Lab với Backtracking, Forward Checking, AC-3 và Min-Conflicts trên Map Coloring & 8-Puzzle CSP.
- **Buổi 14**: Minimax, Alpha-Beta Pruning và Expectimax trên Tic-Tac-Toe (kèm trình gỡ lỗi đệ quy chi tiết).

---

## Cấu trúc thư mục dự án

```text
.
├── Buổi 4..14/                 # File Notebook (.ipynb) báo cáo BTVN theo từng buổi học
├── src/
│   ├── main.py                 # File entry point khởi chạy Streamlit Web App
│   ├── search/                 # Nhân (core) thuật toán tìm kiếm độc lập và thuật toán từ Buổi 5-12
│   ├── problems/               # Cấu trúc các bài toán (8-Puzzle, Pathfinding, 8-Queens) và bộ sinh HTML tương ứng
│   ├── csp/                    # Mô hình CSP và các thuật toán giải bài toán CSP (Buổi 13)
│   ├── adversarial/            # Trực quan hóa thuật toán Game Search đối kháng (Buổi 14)
│   ├── core/                   # Logic mô phỏng tác tử hút bụi (Vacuum Agent)
│   ├── views/                  # Các giao diện (views) Streamlit tương ứng với từng module
│   └── styles/                 # Cài đặt theme, màu sắc tân cổ điển (neobrutalism style)
├── docs/                       # Tài liệu thiết kế hệ thống và kiến trúc phần mềm
│   └── ARCHITECTURE.md         # Chi tiết kiến trúc phân tách giữa Problem - Algorithm - UI
├── requirements.txt            # Danh sách các thư viện cần cài đặt
└── README.md                   # Hướng dẫn sử dụng và tài liệu tổng quan dự án
```

## Nguyên tắc triển khai dự án

1. **Phân tách trách nhiệm rõ ràng**:
   - File Jupyter Notebook đóng vai trò báo cáo học thuật và chạy thử nghiệm cục bộ độc lập (sử dụng Tkinter hoặc CLI).
   - Ứng dụng Web sử dụng mã nguồn chuẩn hóa hoàn toàn bằng Python thuần trong thư mục `src/`, tuyệt đối không phụ thuộc hay tải trực tiếp từ notebook.
2. **Thiết kế thuật toán tương thích hoạt động từng bước (Step-based)**:
   - Các thuật toán tìm kiếm/CSP/đối kháng được thiết kế dưới dạng Generator (`yield`) hoặc lưu giữ vết trạng thái trung gian (`SearchStep`, `CSPStep`, Game Events). Nhờ đó, giao diện Web có thể điều khiển chạy từng bước (Step-by-step), tự động chạy với tốc độ tùy chỉnh (Autoplay) và hiển thị trực quan các cấu trúc dữ liệu như Frontier, Explored Set hay cây đệ quy.
3. **Bộ sinh giao diện tách biệt (Problem Renderers)**:
   - Mỗi bài toán tự định nghĩa cách hiển thị trạng thái của nó (dạng bảng cho 8-Puzzle, đồ thị mạng lưới cho Pathfinding, bản đồ SVG cho Map Coloring) mà không làm ảnh hưởng đến lõi thuật toán tìm kiếm chung.
