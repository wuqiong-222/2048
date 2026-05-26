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
    empty = [(i, j) for i in range(4) for j in range(4)]
    for _ in range(2):
        i, j = random.choice([(x, y) for x, y in empty if st.session_state.board[x][y] == 0])
        st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 样式美化 + 触屏滑动支持 (Hammer.js)
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
.grid-container {display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 20px auto; max-width: 400px;}
.grid-item {
    width: 90px; height: 90px; border-radius: 8px; display: flex; align-items: center;
    justify-content: center; font-size: 24px; font-weight: bold; color: #333;
    background: #eee; border: 2px solid #ccc;
}
/* 让游戏区域支持触摸滑动 */
#swipe-area {
    touch-action: pan-y pinch-zoom;
}
</style>

<!-- 引入 Hammer.js 库用于触摸手势 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>

<script>
    // 等待页面加载完成
    window.addEventListener("load", function() {
        // 寻找游戏区域
        const container = document.querySelector('.grid-container');
        if (!container) return;
        
        const hammertime = new Hammer(container);
        hammertime.get('swipe').set({ direction: Hammer.DIRECTION_ALL });
        
        // 辅助函数：查找按钮并点击
        function clickButton(emoji) {
            const btns = document.querySelectorAll('button');
            for(let btn of btns) {
                if(btn.innerText.includes(emoji)) {
                    btn.click();
                    break;
                }
            }
        }
        
        hammertime.on('swipeleft', function(ev) {
            clickButton('⬅️');
        });
        
        hammertime.on('swiperight', function(ev) {
            clickButton('➡️');
        });
        
        hammertime.on('swipeup', function(ev) {
            clickButton('⬆️');
        });
        
        hammertime.on('swipedown', function(ev) {
            clickButton('⬇️');
        });
    });
</script>
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

# 检查是否有合法移动
def can_move():
    board = st.session_state.board
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return True
            if j < 3 and board[i][j] == board[i][j+1]:
                return True
            if i < 3 and board[i][j] == board[i+1][j]:
                return True
    return False

# 随机生成 2 或 4
def add_num():
    empty = [(i, j) for i in range(4) for j in range(4) if st.session_state.board[i][j] == 0]
    if not empty:
        if not can_move():
            st.session_state.game_over = True
        return
    i, j = random.choice(empty)
    st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 四个方向控制
def up():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    st.session_state.board = np.rot90(st.session_state.board)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b, k=3)
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def down():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    st.session_state.board = np.rot90(st.session_state.board, k=3)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b)
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def left():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    b, s = move_left(st.session_state.board)
    st.session_state.board = b
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def right():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    flipped = np.fliplr(st.session_state.board)
    b, s = move_left(flipped)
    st.session_state.board = np.fliplr(b)
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

# 重置游戏
def reset_game():
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    empty = [(i, j) for i in range(4) for j in range(4)]
    for _ in range(2):
        i, j = random.choice(empty)
        st.session_state.board[i][j] = 2
        empty.remove((i, j))

# 界面
st.title("🎮 2048 数字游戏")
st.caption("💡 PC端：键盘方向键  |  📱 移动端：手指滑动屏幕")

score_col, _ = st.columns([1, 3])
score_col.subheader(f"当前分数：{st.session_state.score}")

# 绘制棋盘
grid_html = "<div id='swipe-area'><div class='grid-container'>"
for row in st.session_state.board:
    for num in row:
        val = num if num != 0 else ""
        # 根据数字大小设置不同背景色
        color_class = ""
        grid_html += f"<div class='grid-item'>{val}</div>"
grid_html += "</div></div>"
st.markdown(grid_html, unsafe_allow_html=True)

# 游戏结束提示
if st.session_state.game_over:
    st.error("❌ 游戏结束！点击「重新开始」再来一把～")

# 按钮区域
col1, col2, col3, col4 = st.columns(4)
with col1: 
    st.button("⬆️ 上", use_container_width=True, on_click=up)
with col2: 
    st.button("⬅️ 左", use_container_width=True, on_click=left)
with col3: 
    st.button("➡️ 右", use_container_width=True, on_click=right)
with col4: 
    st.button("⬇️ 下", use_container_width=True, on_click=down)

# 重置按钮
if st.button("🔄 重新开始", type="primary", use_container_width=True):
    reset_game()
    st.rerun()

# 键盘事件监听
st.markdown("""
<script>
document.addEventListener('keydown', function(event) {
    const key = event.key;
    let emoji = null;
    
    if (key === 'ArrowUp') {
        emoji = '⬆️';
        event.preventDefault();
    } else if (key === 'ArrowDown') {
        emoji = '⬇️';
        event.preventDefault();
    } else if (key === 'ArrowLeft') {
        emoji = '⬅️';
        event.preventDefault();
    } else if (key === 'ArrowRight') {
        emoji = '➡️';
        event.preventDefault();
    }
    
    if (emoji) {
        const btns = document.querySelectorAll('button');
        for(let btn of btns) {
            if(btn.innerText.includes(emoji)) {
                btn.click();
                break;
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)
