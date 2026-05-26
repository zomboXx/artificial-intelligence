# Học phần: Trí Tuệ Nhân Tạo (Artificial Intelligence)

Chào mừng bạn đến với kho lưu trữ (repository) học tập của tôi!

## 📌 Giới thiệu bản thân & Repository
- **Sinh viên thực hiện**: Nguyễn Đức Phát
- **Mã số sinh viên**: 24110296
- **Trường**: Đại học Công Nghệ Kỹ thuật Thành phố Hồ Chí Minh (HCM-UTE)
- **Mục đích**: Repository này được tạo ra nhằm lưu trữ toàn bộ mã nguồn, tài liệu, bài tập về nhà và các dự án nhỏ trong suốt quá trình học tập và thực hành học phần **Trí Tuệ Nhân Tạo** (ARIN330585).

---

## 📚 Các chủ đề và Bài toán tiêu biểu trong học phần Trí Tuệ Nhân Tạo
Học phần Nhập môn / Cơ sở Trí Tuệ Nhân Tạo thường trang bị các kiến thức nền tảng và các dạng bài toán kinh điển sau:

### 1. Tìm kiếm không gian trạng thái (State Space Search)
Đây là kỹ thuật giải quyết vấn đề bằng cách duyệt qua các trạng thái từ Start đến Goal.
- **Tìm kiếm mù (Uninformed Search)**: Duyệt cây/đồ thị mà không có thông tin đánh giá khoảng cách đến đích.
  - *Thuật toán*: Tìm kiếm theo chiều rộng (BFS), Tìm kiếm theo chiều sâu (DFS), Tìm kiếm chi phí đồng nhất (UCS).
  - *Bài toán ứng dụng*: **8-Puzzle** (Trò chơi trượt số), Đong nước (Water Jug), Mê cung (Maze Solving).
- **Tìm kiếm có thông tin / Heuristic (Informed Search)**: Sử dụng hàm đánh giá Heuristic để tối ưu hướng đi.
  - *Thuật toán*: Greedy Best-First Search, Giải thuật tìm kiếm A*.
  - *Bài toán ứng dụng*: Tìm đường đi ngắn nhất trên bản đồ (Pathfinding), 8-Puzzle tối ưu (dùng Heuristic khoảng cách Manhattan).

### 2. Tìm kiếm đối kháng (Adversarial Search)
Ứng dụng trong việc xây dựng các Agent tự động chơi game chiến thuật 2 người.
- *Thuật toán*: Giải thuật cực tiểu cực đại (Minimax), Cắt tỉa Alpha-Beta (Alpha-Beta Pruning).
- *Bài toán ứng dụng*: Cờ Caro (Tic-Tac-Toe), Cờ gánh, Cờ vua (Chess), Cờ vây (Go).

### 3. Bài toán thỏa mãn ràng buộc (Constraint Satisfaction Problems - CSP)
Giải quyết các bài toán bằng cách gán giá trị cho các biến sao cho thỏa mãn tập các ràng buộc đặt ra.
- *Thuật toán*: Tìm kiếm quay lui (Backtracking Search), Lan truyền ràng buộc (Constraint Propagation - AC-3), Forward Checking.
- *Bài toán ứng dụng*: Tô màu bản đồ (Map Coloring), Xếp lịch thi, Trò chơi Sudoku, Bài toán 8 quân hậu (8-Queens).

### 4. Biểu diễn tri thức và Suy diễn logic (Knowledge Representation & Logic)
Giúp hệ thống máy tính có khả năng tư duy suy luận từ những tri thức sẵn có.
- *Thuật toán*: Logic mệnh đề (Propositional Logic), Logic vị từ bậc một (First-Order Logic), thuật toán Phân giải (Resolution), Lan truyền tiến (Forward Chaining), Lan truyền lùi (Backward Chaining).
- *Bài toán ứng dụng*: Trò chơi thế giới Wumpus (Wumpus World), Hệ thống chuyên gia chuẩn đoán y khoa.

### 5. Học máy cơ bản (Introduction to Machine Learning)
Các giải thuật giúp máy tính học hỏi từ dữ liệu quá khứ để đưa ra quyết định mà không cần lập trình chi tiết từng bước.
- **Học có giám sát (Supervised Learning)**:
  - *Thuật toán*: K-Láng giềng gần nhất (KNN), Cây quyết định (Decision Tree), Naive Bayes, Hồi quy tuyến tính (Linear Regression).
- **Học không giám sát (Unsupervised Learning)**:
  - *Thuật toán*: Phân cụm K-Means (K-Means Clustering).

### 6. Tối ưu hóa Meta-heuristic
Các phương pháp tìm kiếm lời giải xấp xỉ tối ưu cho các bài toán NP-khó.
- *Thuật toán*: Tìm kiếm leo đồi (Hill Climbing), Tìm kiếm luyện kim (Simulated Annealing), Thuật toán di truyền (Genetic Algorithm - GA).
- *Bài toán ứng dụng*: Người bán hàng du lịch (Traveling Salesperson Problem - TSP), Bài toán xếp balo (Knapsack).

---

## 🛠️ Trạng thái thực hành hiện tại
- **Buổi 4**: Đã hoàn thành giải bài toán **Vacuum Agent** (Robot hút bụi thông minh) theo 2 hướng simple reflex và model-based agent.
- **Buổi 5**: Đã hoàn thành giải bài toán **8-Puzzle** sử dụng thuật toán **BFS** và **DFS** kèm giao diện mô phỏng thời gian thực bằng **Tkinter** dưới dạng Incremental Search.
- **Buổi 6**: Đã hoàn thành giải bài toán **8-Puzzle** sử dụng thuật toán **IDS (Iterative Deepening Search - Tìm kiếm sâu dần)** với thứ tự ưu tiên duyệt **LRUD** và trực quan hóa thời gian thực (Real-time).
- **Buổi 7**: Đã hoàn thành giải bài toán **8-Puzzle** sử dụng giải thuật **UCS (Uniform Cost Search)** chuẩn hóa chi phí đường đi thực tế $f(n) = g(n)$. Để phân biệt bản chất với BFS, trọng số của mỗi bước đi (Step Cost) được cấu hình tùy biến bằng *giá trị của ô số vừa được hoán đổi*, giúp kiểm chứng trực quan cơ chế sắp xếp Frontier của hàng đợi ưu tiên.
- **Buổi 8**: Đã hoàn thành tích hợp bộ đôi thuật toán tìm kiếm có thông tin (Informed Search) gồm **Greedy Best-First Search** ($f(n) = h(n)$) và **A\* Search** ($f(n) = g(n) + h(n)$) sử dụng hàm Heuristic Khoảng cách Manhattan. Chương trình được tối ưu hóa với thanh lựa chọn **Dropdown Combobox** trên giao diện Tkinter, cho phép người dùng chuyển đổi linh hoạt giữa hai thuật toán để so sánh sự khác biệt trong việc đánh giá và tối ưu hóa chi phí.

*Repository đang liên tục được cập nhật theo tiến độ học tập trên lớp.*