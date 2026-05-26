import streamlit as st
import random

# 页面配置（必须置顶）
st.set_page_config(
    page_title="2048",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 全局样式 + 精准尺寸适配（修复尺寸问题）
st.markdown("""
<style>
/* 整体页面约束，防止溢出 */
.main {
    max-width: 480px;
    margin: 0 auto;
    padding: 10px;
}
/* 棋盘外层容器 */
.game-board-wrap {
    width: 100%;
    background-color: #bbada0;
    padding: 12px;
    border-radius: 12px;
    box-sizing: border-box;
    margin: 15px 0;
}
/* 4*4 标准网格，固定等宽列 */
.game-board {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    width: 100%;
}
/* 格子：强制正方形，PC/手机统一比例 */
.cell {
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    font-weight: bold;
    box-sizing: border-box;
}
/* 字体自适应：大屏大字体，小屏自动缩小 */
@media (min-width: 400px) {
    .cell { font-size: 30px; }
}
@media (max-width: 399px) {
    .cell { font-size: 22px; }
}

/* 数字对应配色 */
.cell-0 { background: #cdc1b4; color: transparent; }
.cell-2 { background: #eee4da; color: #776e65; }
.cell-4 { background: #ede0c8; color: #776e65; }
.cell-8 { background: #f2b179; color: #ffffff; }
.cell-16 { background: #f59563; color: #ffffff; }
.cell-32 { background: #f67c5f; color: #ffffff; }
.cell-64 { background: #f65e3b; color: #ffffff; }
.cell-128 { background: #edcf72; color: #ffffff; }
.cell-256 { background: #edcc61; color: #ffffff; }
.cell-512 { background: #ecc850; color: #ffffff; }
.cell-1024 { background: #edc22e; color: #ffffff; }
.cell-2048 { background: #3c3a32; color: #ffffff; }

/* 操作按钮样式，适配触屏 */
.stButton > button {
    font-size: 16px !important;
    padding: 10px 0 !important;
    border-radius: 8px !important;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ===================== 游戏核心逻辑 =====================
def init_board():
    board = [[0 for _ in range(4)] for _ in range(4)]
    add_random_tile(board)
    add_random_tile(board)
    return board

def add_random_tile(board):
    empty_cells = [(r, c) for r in range(4) for c in range(4) if board[r][c] == 0]
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r][c] = 2 if random.random() < 0.9 else 4

def compress(row):
    new_row = [num for num in row if num != 0]
    new_row += [0] * (4 - len(new_row))
    return new_row

def merge(row):
    row = compress(row)
    for i in range(3):
        if row[i] == row[i+1] and row[i] != 0:
            row[i] *= 2
            row[i+1] = 0
    return compress(row)

def move_left(board):
    new_board = [merge(row) for row in board]
    return new_board if new_board != board else None

def rotate_board(b):
    return [list(col)[::-1] for col in zip(*b)]

def move_right(board):
    new_board = [merge(row[::-1])[::-1] for row in board]
    return new_board if new_board != board else None

def move_up(board):
    rotated = rotate_board(board)
    new_rot = [merge(row) for row in rotated]
    new_board = rotate_board(rotate_board(rotate_board(new_rot)))
    return new_board if new_board != board else None

def move_down(board):
    rotated = rotate_board(rotate_board(rotate_board(board)))
    new_rot = [merge(row) for row in rotated]
    new_board = rotate_board(new_rot)
    return new_board if new_board != board else None

def check_win(board):
    return any(2048 in row for row in board)

def check_game_over(board):
    if any(0 in row for row in board):
        return False
    for r in range(4):
        for c in range(4):
            curr = board[r][c]
            if c < 3 and board[r][c+1] == curr:
                return False
            if r < 3 and board[r+1][c] == curr:
                return False
    return True

# ===================== 会话状态初始化 =====================
if "board" not in st.session_state:
    st.session_state.board = init_board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "is_win" not in st.session_state:
    st.session_state.is_win = False
if "operate" not in st.session_state:
    st.session_state.operate = ""

# ===================== 触屏滑动 + 键盘监听 JS =====================
st.markdown("""
<script>
// 键盘方向键监听
document.addEventListener("keydown", function(e) {
    let dir = "";
    if(e.key === "ArrowUp") dir = "up";
    if(e.key === "ArrowDown") dir = "down";
    if(e.key === "ArrowLeft") dir = "left";
    if(e.key === "ArrowRight") dir = "right";
    if(dir) {
        window.streamlitDir = dir;
        document.body.click();
        e.preventDefault();
    }
});

// 手机触屏滑动监听
let startX = 0, startY = 0;
document.addEventListener("touchstart", function(e) {
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
});
document.addEventListener("touchend", function(e) {
    let endX = e.changedTouches[0].clientX;
    let endY = e.changedTouches[0].clientY;
    let dx = endX - startX;
    let dy = endY - startY;
    let dir = "";
    const threshold = 40;

    if(Math.abs(dx) > Math.abs(dy)) {
        dir = dx > threshold ? "right" : dx < -threshold ? "left" : "";
    } else {
        dir = dy > threshold ? "down" : dy < -threshold ? "up" : "";
    }
    if(dir) {
        window.streamlitDir = dir;
        document.body.click();
    }
});
</script>
""", unsafe_allow_html=True)

# 执行移动逻辑
def run_move(direction):
    if st.session_state.game_over:
        return
    b = st.session_state.board
    new_b = None
    if direction == "left":
        new_b = move_left(b)
    elif direction == "right":
        new_b = move_right(b)
    elif direction == "up":
        new_b = move_up(b)
    elif direction == "down":
        new_b = move_down(b)

    if new_b:
        st.session_state.board = new_b
        add_random_tile(st.session_state.board)
        if check_win(st.session_state.board):
            st.session_state.is_win = True
            st.session_state.game_over = True
        elif check_game_over(st.session_state.board):
            st.session_state.game_over = True

# 接收JS传来的操作指令
if "streamlitDir" in globals() and streamlitDir:
    run_move(streamlitDir)
    streamlitDir = ""

# ===================== 页面渲染 =====================
st.title("🎮 2048")
st.caption("电脑：方向键 ↑↓←→ | 手机：屏幕滑动 / 点击按钮")

# 控制按钮区
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("👆 上"):
        run_move("up")
with b2:
    if st.button("👇 下"):
        run_move("down")
with b3:
    if st.button("👈 左"):
        run_move("left")
with b4:
    if st.button("👉 右"):
        run_move("right")

if st.button("🔄 重新开局"):
    st.session_state.board = init_board()
    st.session_state.game_over = False
    st.session_state.is_win = False

# 游戏状态提示
if st.session_state.is_win:
    st.success("🎉 恭喜！成功合成 2048，游戏胜利！")
elif st.session_state.game_over:
    st.error("💥 格子已满，游戏结束！")

# 渲染棋盘（严格4*4，尺寸统一）
board_html = '<div class="game-board-wrap"><div class="game-board">'
for row in st.session_state.board:
    for num in row:
        board_html += f'<div class="cell cell-{num}">{num if num != 0 else ""}</div>'
board_html += '</div></div>'
st.markdown(board_html, unsafe_allow_html=True)
