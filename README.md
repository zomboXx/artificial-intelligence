# Học phần: Trí Tuệ Nhân Tạo (Artificial Intelligence)

Repository học tập của tôi cho học phần **Trí Tuệ Nhân Tạo / Artificial Intelligence**.

## Thông tin sinh viên

- **Sinh viên thực hiện**: Nguyễn Đức Phát
- **Mã số sinh viên**: 24110296
- **Trường**: Đại học Sư phạm Kỹ thuật Thành phố Hồ Chí Minh (HCM-UTE)
- **Mục đích**: Lưu trữ bài tập về nhà, báo cáo notebook, source code mô phỏng và phiên bản web trực quan hóa các thuật toán AI đã học.

## Cách chạy phiên bản Web

Ứng dụng web được xây dựng bằng **Streamlit**.

```powershell
pip install -r requirements.txt
streamlit run src/main.py
```

Phiên bản web có bốn module chính:

- **Search Algorithms**: 8-Puzzle, Grid Pathfinding và 8-Queens.
- **Vacuum Agent**: Simple Reflex Agent và Model-Based Agent.
- **CSP Lab**: Map Coloring và 8-Puzzle dưới dạng CSP.
- **Adversarial Search**: Tic-Tac-Toe với debugger từng bước.

## Thuật toán trong phiên bản Web

### Tìm kiếm không có thông tin

- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- IDS (Iterative Deepening Search)
- UCS (Uniform Cost Search)

### Tìm kiếm có thông tin

- Greedy Best-First Search
- A* Search
- IDA* Search
- Manhattan Distance và Misplaced Tiles

### Local Search và Meta-heuristic

- Simple Hill Climbing
- Steepest-Ascent Hill Climbing
- Stochastic Hill Climbing
- Hill Climbing with Sideways Moves
- Random-Restart Hill Climbing
- Local Beam Search, `k = 2`, chọn trạng thái tốt hơn
- Local Beam Search, `k = 2`, chọn trạng thái tốt nhất
- Simulated Annealing

### Tìm kiếm trong môi trường phức tạp

- Sensorless / Belief State Search
- Partial Observation Search
- AND-OR Graph Search

### Constraint Satisfaction Problem

- Backtracking
- Forward Checking
- Arc Consistency với AC-3
- Min-Conflicts

### Tìm kiếm đối kháng

- Minimax
- Alpha-Beta Pruning
- Expectimax

## Nội dung theo buổi học

- **Buổi 4**: Vacuum Agent với Simple Reflex Agent và Model-Based Agent.
- **Buổi 5**: 8-Puzzle với BFS và DFS.
- **Buổi 6**: 8-Puzzle với IDS theo cơ chế tìm kiếm sâu dần.
- **Buổi 7**: 8-Puzzle với UCS và cấu hình step cost.
- **Buổi 8**: Greedy Best-First Search và A* Search với heuristic.
- **Buổi 9**: IDA* và Hill Climbing.
- **Buổi 10**: Steepest-Ascent, Stochastic, Sideways Moves, Random-Restart và Local Beam Search.
- **Buổi 11**: Simulated Annealing và Belief State.
- **Buổi 12**: Sensorless Search, Partial Observation và AND-OR Graph Search.
- **Buổi 13**: CSP với Backtracking, Forward Checking, AC-3 và Min-Conflicts trên Map Coloring và 8-Puzzle CSP.
- **Buổi 14**: Minimax, Alpha-Beta Pruning và Expectimax trên Tic-Tac-Toe.

## Cấu trúc thư mục chính

```text
.
├── Buổi 4..14/                 # Notebook BTVN theo từng buổi
├── src/
│   ├── main.py                 # Entry point Streamlit
│   ├── search/                 # Generic search core và thuật toán Buổi 5-12
│   ├── problems/               # 8-Puzzle, Pathfinding, 8-Queens và renderer
│   ├── csp/                    # CSP models và solver Buổi 13
│   ├── adversarial/            # Game search và debugger Buổi 14
│   ├── core/                   # Vacuum Agent logic
│   ├── views/                  # Giao diện Streamlit theo module
│   └── styles/                 # Theme giao diện
├── docs/                       # Tài liệu kiến trúc
├── requirements.txt
└── README.md
```

## Nguyên tắc triển khai

- Notebook giữ vai trò báo cáo học thuật và demo Tkinter độc lập.
- Web app dùng source Python trong `src/`, không nạp thuật toán trực tiếp từ notebook.
- Các thuật toán sinh trạng thái trung gian để giao diện có thể chạy từng bước, tự động chạy và debug.
- Mỗi nhóm bài toán có renderer phù hợp với trạng thái và metric riêng.
