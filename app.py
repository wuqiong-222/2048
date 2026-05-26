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

# 样式美化 + 触屏滑动支持
st.markdown("""
<style>
.block-container {padding-top: 1rem;}
.grid-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin: 20px auto;
    max-width: 400px;
    background: #bbada0;
    padding: 15px;
    border-radius: 12px;
    cursor: pointer;
    touch-action: none;  /* 完全禁止浏览器手势，让滑动更灵敏 */
}
.grid-item {
    aspect-ratio: 1 / 1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: bold;
    color: #776e65;
    background: #cdc1b4;
    transition: all 0.1s ease;
}
/* 不同数字的背景色 */
.grid-item:contains("2") { background: #eee4da; }
.grid-item:contains("4") { background: #ede0c8; }
.grid-item:contains("8") { background: #f2b179; color: white; }
.grid-item:contains("16") { background: #f59563; color: white; }
.grid-item:contains("32") { background: #f67c5f; color: white; }
.grid-item:contains("64") { background: #f65e3b; color: white; }
.grid-item:contains("128") { background: #edcf72; color: white; }
.grid-item:contains("256") { background: #edcc61; color: white; }
.grid-item:contains("512") { background: #edc850; color: white; }
.grid-item:contains("1024") { background: #edc53f; color: white; }
.grid-item:contains("2048") { background: #edc22e; color: white; }
</style>

<script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>

<script>
// 等待页面完全加载
(function() {
    function initSwipe() {
        const container = document.querySelector('.grid-container');
        if (!container) {
            setTimeout(initSwipe, 100);
            return;
        }
        
        // 创建 Hammer 实例，专门监听滑动
        const hammertime = new Hammer(container);
        hammertime.get('swipe').set({
            direction: Hammer.DIRECTION_ALL,
            threshold: 10,     // 滑动10px就触发
            velocity: 0.1      // 速度阈值降低，更容易触发
        });
        
        // 辅助函数：点击对应的方向按钮
        function swipeDirection(direction) {
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                const text = btn.innerText || btn.textContent;
                if (direction === 'left' && (text.includes('⬅️') || text.includes('左'))) {
                    btn.click();
                    console.log('触发左滑');
                    break;
                } else if (direction === 'right' && (text.includes('➡️') || text.includes('右'))) {
                    btn.click();
                    console.log('触发右滑');
                    break;
                } else if (direction === 'up' && (text.includes('⬆️') || text.includes('上'))) {
                    btn.click();
                    console.log('触发上滑');
                    break;
                } else if (direction === 'down' && (text.includes('⬇️') || text.includes('下'))) {
                    btn.click();
                    console.log('触发下滑');
                    break;
                }
            }
        }
        
        // 绑定滑动事件
        hammertime.on('swipeleft', function(e) {
            e.preventDefault();
            swipeDirection('left');
        });
        
        hammertime.on('swiperight', function(e) {
            e.preventDefault();
            swipeDirection('right');
        });
        
        hammertime.on('swipeup', function(e) {
            e.preventDefault();
            swipeDirection('up');
        });
        
        hammertime.on('swipedown', function(e) {
            e.preventDefault();
            swipeDirection('down');
        });
        
        console.log('触摸滑动已启用！');
    }
    
    // 确保 DOM 加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSwipe);
    } else {
        initSwipe();
    }
})();
</script>
""", unsafe_allow_html=True)

# 核心逻辑：左滑
def move_left(board):
    new_board = np.zeros_like(board)
    score = 0
    for i in range(4):
        # 去掉0
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
        # 补0
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

# 随机生成新数字
def add_num():
    empty = [(i, j) for i in range(4) for j in range(4) if st.session_state.board[i][j] == 0]
    if not empty:
        if not can_move():
            st.session_state.game_over = True
        return
    i, j = random.choice(empty)
    st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 四个方向控制
def move_up():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    st.session_state.board = np.rot90(st.session_state.board)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b, k=3)
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def move_down():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    st.session_state.board = np.rot90(st.session_state.board, k=3)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b)
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def move_left():
    if st.session_state.game_over:
        return
    old_board = st.session_state.board.copy()
    b, s = move_left(st.session_state.board)
    st.session_state.board = b
    if not np.array_equal(old_board, st.session_state.board):
        st.session_state.score += s
        add_num()

def move_right():
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

# ========== UI 界面 ==========
st.title("🎮 2048 数字游戏")
st.caption("💡 PC端：按键盘方向键（↑↓←→）| 📱 移动端：在棋盘上滑动手指")

# 显示分数
col1, col2, col3 = st.columns([1, 2, 1])
col1.metric("当前分数", st.session_state.score)

# 绘制棋盘（带颜色）
grid_html = "<div class='grid-container'>"
for i in range(4):
    for j in range(4):
        num = st.session_state.board[i][j]
        val = str(num) if num != 0 else ""
        # 内联样式给数字背景色
        bg_color = "#cdc1b4"
        text_color = "#776e65"
        if num == 2: bg_color = "#eee4da"
        elif num == 4: bg_color = "#ede0c8"
        elif num == 8: bg_color = "#f2b179"; text_color = "white"
        elif num == 16: bg_color = "#f59563"; text_color = "white"
        elif num == 32: bg_color = "#f67c5f"; text_color = "white"
        elif num == 64: bg_color = "#f65e3b"; text_color = "white"
        elif num >= 128: bg_color = "#edcf72"; text_color = "white"
        
        grid_html += f"<div class='grid-item' style='background: {bg_color}; color: {text_color};'>{val}</div>"
grid_html += "</div>"
st.markdown(grid_html, unsafe_allow_html=True)

# 游戏结束提示
if st.session_state.game_over:
    st.error("❌ 游戏结束！点击下方按钮重新开始")

# 方向按钮（作为备用和移动端回调）
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.button("⬆️ 上", use_container_width=True, on_click=move_up)
with c2:
    st.button("⬅️ 左", use_container_width=True, on_click=move_left)
with c3:
    st.button("➡️ 右", use_container_width=True, on_click=move_right)
with c4:
    st.button("⬇️ 下", use_container_width=True, on_click=move_down)

# 重置按钮
if st.button("🔄 重新开始", type="primary", use_container_width=True):
    reset_game()
    st.rerun()

# 键盘监听（PC端）
st.markdown("""
<script>
document.addEventListener('keydown', function(event) {
    const key = event.key;
    let btnText = null;
    
    // 映射方向键
    if (key === 'ArrowUp') {
        btnText = '⬆️';
        event.preventDefault();
    } else if (key === 'ArrowDown') {
        btnText = '⬇️';
        event.preventDefault();
    } else if (key === 'ArrowLeft') {
        btnText = '⬅️';
        event.preventDefault();
    } else if (key === 'ArrowRight') {
        btnText = '➡️';
        event.preventDefault();
    }
    
    if (btnText) {
        // 查找对应的按钮并点击
        const btns = document.querySelectorAll('button');
        for (let btn of btns) {
            if (btn.innerText.includes(btnText)) {
                btn.click();
                break;
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)
