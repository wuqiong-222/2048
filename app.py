import streamlit as st
import numpy as np
import random

# 页面配置
st.set_page_config(
    page_title="2048 游戏",
    page_icon="🎮",
    layout="centered"
)

# 初始化游戏状态
if "board" not in st.session_state:
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    # 开局生成2个数字
    add_new = lambda b: random.choice([(i, j) for i in range(4) for j in range(4) if b[i][j] == 0])
    for _ in range(2):
        i, j = add_new(st.session_state.board)
        st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 样式美化
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
.grid-container {display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px auto; max-width: 400px;}
.grid-item {
    width: 90px; height: 90px; border-radius: 8px; display: flex; align-items: center;
    justify-content: center; font-size: 24px; font-weight: bold; color: #333;
    background: #eee; border: 2px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# 核心逻辑：左滑（上下右都是左滑+翻转矩阵）
def move_left(board):
    new_board = np.zeros_like(board)
    score = 0
    for i in range(4):
        row = board[i][board[i] != 0]
        merged = []
        skip = False
        for j in range(len(row)):
            if skip:
                skip = False
                continue
            if j + 1 < len(row) and row[j] == row[j+1]:
                merged.append(row[j] * 2)
                score += row[j] * 2
                skip = True
            else:
                merged.append(row[j])
        new_board[i, :len(merged)] = merged
    return new_board, score

# 四个方向控制
def up():
    st.session_state.board = np.rot90(st.session_state.board)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b, k=3)
    st.session_state.score += s
    add_num()

def down():
    st.session_state.board = np.rot90(st.session_state.board, k=3)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b)
    st.session_state.score += s
    add_num()

def left():
    b, s = move_left(st.session_state.board)
    st.session_state.board = b
    st.session_state.score += s
    add_num()

def right():
    st.session_state.board = np.fliplr(st.session_state.board)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.fliplr(b)
    st.session_state.score += s
    add_num()

# 随机生成 2 或 4
def add_num():
    empty = [(i, j) for i in range(4) for j in range(4) if st.session_state.board[i][j] == 0]
    if not empty:
        st.session_state.game_over = True
        return
    i, j = random.choice(empty)
    st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 界面
st.title("🎮 2048 数字游戏")
st.subheader(f"当前分数：{st.session_state.score}")

# 绘制棋盘
grid_html = "<div class='grid-container'>"
for row in st.session_state.board:
    for num in row:
        val = num if num != 0 else ""
        grid_html += f"<div class='grid-item'>{val}</div>"
grid_html += "</div>"
st.markdown(grid_html, unsafe_allow_html=True)

# 游戏结束
if st.session_state.game_over:
    st.error("❌ 游戏结束！点击「重新开始」再来一把～")

# 按钮
col1, col2, col3, col4 = st.columns(4)
with col1: st.button("⬆️ 上", use_container_width=True, on_click=up)
with col2: st.button("⬅️ 左", use_container_width=True, on_click=left)
with col3: st.button("➡️ 右", use_container_width=True, on_click=right)
with col4: st.button("⬇️ 下", use_container_width=True, on_click=down)

# 重置
if st.button("🔄 重新开始", type="primary"):
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    for _ in range(2):
        i, j = random.choice([(x, y) for x in range(4) for y in range(4) if st.session_state.board[x][y] == 0])
        st.session_state.board[i][j] = 2
    st.rerun()