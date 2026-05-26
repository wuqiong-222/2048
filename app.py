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
    positions = [(i, j) for i in range(4) for j in range(4)]
    for _ in range(2):
        empty = [p for p in positions if st.session_state.board[p[0]][p[1]] == 0]
        if empty:
            i, j = random.choice(empty)
            st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

# 核心游戏逻辑
def compress(board):
    """压缩行，去掉0"""
    new_board = np.zeros_like(board)
    for i in range(4):
        pos = 0
        for j in range(4):
            if board[i][j] != 0:
                new_board[i][pos] = board[i][j]
                pos += 1
    return new_board

def merge(board):
    """合并相邻相同数字"""
    score = 0
    for i in range(4):
        for j in range(3):
            if board[i][j] == board[i][j+1] and board[i][j] != 0:
                board[i][j] *= 2
                score += board[i][j]
                board[i][j+1] = 0
    return board, score

def move_left(board):
    """左移主逻辑"""
    new_board = compress(board)
    new_board, score = merge(new_board)
    new_board = compress(new_board)
    return new_board, score

def move_right(board):
    """右移"""
    flipped = np.fliplr(board)
    flipped, score = move_left(flipped)
    return np.fliplr(flipped), score

def move_up(board):
    """上移"""
    rotated = np.rot90(board)
    rotated, score = move_left(rotated)
    return np.rot90(rotated, k=-1), score

def move_down(board):
    """下移"""
    rotated = np.rot90(board, k=-1)
    rotated, score = move_left(rotated)
    return np.rot90(rotated), score

def add_new_number():
    """添加新数字（2或4）"""
    empty = [(i, j) for i in range(4) for j in range(4) if st.session_state.board[i][j] == 0]
    if empty:
        i, j = random.choice(empty)
        st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4
        
        # 检查游戏是否结束
        if not any_move_possible():
            st.session_state.game_over = True

def any_move_possible():
    """检查是否还有合法移动"""
    board = st.session_state.board
    # 检查是否有空格
    if 0 in board:
        return True
    # 检查是否有相邻相同数字
    for i in range(4):
        for j in range(4):
            if j < 3 and board[i][j] == board[i][j+1]:
                return True
            if i < 3 and board[i][j] == board[i+1][j]:
                return True
    return False

# 移动操作（带状态更新）
def perform_move(move_func):
    if st.session_state.game_over:
        return False
    
    old_board = st.session_state.board.copy()
    new_board, score_gain = move_func(st.session_state.board)
    
    if not np.array_equal(old_board, new_board):
        st.session_state.board = new_board
        st.session_state.score += score_gain
        add_new_number()
        return True
    return False

def action_up():
    perform_move(move_up)

def action_down():
    perform_move(move_down)

def action_left():
    perform_move(move_left)

def action_right():
    perform_move(move_right)

def reset_game():
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    positions = [(i, j) for i in range(4) for j in range(4)]
    for _ in range(2):
        empty = [p for p in positions if st.session_state.board[p[0]][p[1]] == 0]
        if empty:
            i, j = random.choice(empty)
            st.session_state.board[i][j] = 2

# 注入JavaScript（键盘+触摸）
st.markdown("""
<style>
/* 棋盘样式 */
.game-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    background: #bbada0;
    padding: 15px;
    border-radius: 12px;
    max-width: 450px;
    width: 100%;
    cursor: pointer;
    touch-action: none;
}

.grid-item {
    aspect-ratio: 1 / 1;
    background: #cdc1b4;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    transition: all 0.1s ease;
}

/* 数字颜色 */
.num-0 { background: #cdc1b4; }
.num-2 { background: #eee4da; color: #776e65; }
.num-4 { background: #ede0c8; color: #776e65; }
.num-8 { background: #f2b179; color: #f9f6f2; }
.num-16 { background: #f59563; color: #f9f6f2; }
.num-32 { background: #f67c5f; color: #f9f6f2; }
.num-64 { background: #f65e3b; color: #f9f6f2; }
.num-128 { background: #edcf72; color: #f9f6f2; font-size: 28px; }
.num-256 { background: #edcc61; color: #f9f6f2; font-size: 28px; }
.num-512 { background: #edc850; color: #f9f6f2; font-size: 28px; }
.num-1024 { background: #edc53f; color: #f9f6f2; font-size: 24px; }
.num-2048 { background: #edc22e; color: #f9f6f2; font-size: 24px; }

/* 移动端优化 */
@media (max-width: 600px) {
    .grid-item {
        font-size: 24px;
    }
}
</style>

<script>
// 键盘控制
document.addEventListener('keydown', function(event) {
    const key = event.key;
    let direction = null;
    
    if (key === 'ArrowUp') {
        direction = '上';
        event.preventDefault();
    } else if (key === 'ArrowDown') {
        direction = '下';
        event.preventDefault();
    } else if (key === 'ArrowLeft') {
        direction = '左';
        event.preventDefault();
    } else if (key === 'ArrowRight') {
        direction = '右';
        event.preventDefault();
    }
    
    if (direction) {
        // 找到对应的Streamlit按钮并点击
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.textContent.includes(direction)) {
                btn.click();
                console.log('键盘触发:', direction);
                break;
            }
        }
    }
});

// 触摸滑动控制
(function() {
    let touchStartX = 0;
    let touchStartY = 0;
    
    function findGridContainer() {
        const container = document.querySelector('.grid-container');
        if (container) {
            console.log('找到棋盘容器，启用触摸滑动');
            setupTouchEvents(container);
        } else {
            console.log('等待棋盘容器加载...');
            setTimeout(findGridContainer, 500);
        }
    }
    
    function setupTouchEvents(element) {
        element.addEventListener('touchstart', function(e) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: false });
        
        element.addEventListener('touchend', function(e) {
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            
            const deltaX = touchEndX - touchStartX;
            const deltaY = touchEndY - touchStartY;
            
            // 最小滑动距离30px
            if (Math.abs(deltaX) < 30 && Math.abs(deltaY) < 30) {
                return;
            }
            
            let direction = null;
            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                // 水平滑动
                if (deltaX > 0) {
                    direction = '右';
                } else {
                    direction = '左';
                }
            } else {
                // 垂直滑动
                if (deltaY > 0) {
                    direction = '下';
                } else {
                    direction = '上';
                }
            }
            
            if (direction) {
                console.log('触摸滑动:', direction);
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.textContent.includes(direction)) {
                        btn.click();
                        break;
                    }
                }
            }
            
            e.preventDefault();
        }, { passive: false });
    }
    
    // 启动
    findGridContainer();
})();
</script>
""", unsafe_allow_html=True)

# UI界面
st.title("🎮 2048 游戏")
st.markdown("<p style='text-align: center; color: #666;'>💻 键盘方向键 | 📱 手指滑动棋盘</p>", unsafe_allow_html=True)

# 分数显示
col1, col2, col3 = st.columns([1, 1, 1])
col2.metric("🏆 分数", st.session_state.score)

# 显示棋盘
grid_html = '<div class="game-container"><div class="grid-container">'
for i in range(4):
    for j in range(4):
        val = st.session_state.board[i][j]
        num_class = f"num-{val}" if val in [0,2,4,8,16,32,64,128,256,512,1024,2048] else "num-0"
        display_text = str(val) if val != 0 else ""
        grid_html += f'<div class="grid-item {num_class}">{display_text}</div>'
grid_html += '</div></div>'
st.markdown(grid_html, unsafe_allow_html=True)

# 游戏结束提示
if st.session_state.game_over:
    st.error("💀 游戏结束！")

# 控制按钮
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button("⬆️ 上", use_container_width=True, on_click=action_up, key="up_btn")
with col2:
    st.button("⬅️ 左", use_container_width=True, on_click=action_left, key="left_btn")
with col3:
    st.button("➡️ 右", use_container_width=True, on_click=action_right, key="right_btn")
with col4:
    st.button("⬇️ 下", use_container_width=True, on_click=action_down, key="down_btn")

# 重置按钮
if st.button("🔄 重新开始", use_container_width=True, type="primary"):
    reset_game()
    st.rerun()
