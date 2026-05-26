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

# 自定义CSS - 包含触摸滑动
st.markdown("""
<style>
/* 主容器样式 */
.main-header {
    text-align: center;
    margin-bottom: 20px;
}

/* 棋盘容器 - 支持触摸滑动 */
.game-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
    touch-action: none;
}

.grid-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    background: #bbada0;
    padding: 15px;
    border-radius: 12px;
    max-width: 450px;
    width: 100%;
    cursor: pointer;
    touch-action: none;
    user-select: none;
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
.num-0 { background: #cdc1b4; color: #776e65; }
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

.button-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin: 20px 0;
}
</style>

<!-- 触摸滑动脚本 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>

<script>
(function() {
    // 等待DOM加载完成
    function initTouch() {
        const gridContainer = document.querySelector('.grid-container');
        if (!gridContainer) {
            setTimeout(initTouch, 100);
            return;
        }
        
        console.log("触摸滑动已初始化");
        
        // 创建Hammer实例
        const hammer = new Hammer(gridContainer);
        hammer.get('swipe').set({
            direction: Hammer.DIRECTION_ALL,
            threshold: 20,
            velocity: 0.3
        });
        
        // 滑动回调
        hammer.on('swipeleft', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("左滑触发");
            const btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.innerText.includes('左') || b.innerText.includes('⬅️')
            );
            if (btn) btn.click();
        });
        
        hammer.on('swiperight', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("右滑触发");
            const btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.innerText.includes('右') || b.innerText.includes('➡️')
            );
            if (btn) btn.click();
        });
        
        hammer.on('swipeup', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("上滑触发");
            const btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.innerText.includes('上') || b.innerText.includes('⬆️')
            );
            if (btn) btn.click();
        });
        
        hammer.on('swipedown', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log("下滑触发");
            const btn = Array.from(document.querySelectorAll('button')).find(b => 
                b.innerText.includes('下') || b.innerText.includes('⬇️')
            );
            if (btn) btn.click();
        });
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTouch);
    } else {
        initTouch();
    }
})();
</script>
""", unsafe_allow_html=True)

# UI界面
st.title("🎮 2048 数字游戏")
st.markdown("<p style='text-align: center; color: #666;'>💡 PC端：键盘方向键 | 📱 移动端：在棋盘上滑动手指</p>", unsafe_allow_html=True)

# 分数显示
col1, col2, col3 = st.columns([1, 1, 1])
col2.metric("🏆 当前分数", st.session_state.score)

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
    st.error("💀 游戏结束！点击下方按钮重新开始")

# 控制按钮
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.button("⬆️ 上", use_container_width=True, on_click=action_up, key="up")
with col2:
    st.button("⬅️ 左", use_container_width=True, on_click=action_left, key="left")
with col3:
    st.button("➡️ 右", use_container_width=True, on_click=action_right, key="right")
with col4:
    st.button("⬇️ 下", use_container_width=True, on_click=action_down, key="down")

# 重置按钮
if st.button("🔄 重新开始", use_container_width=True, type="primary"):
    reset_game()
    st.rerun()

# 键盘监听（PC端）
st.markdown("""
<script>
document.addEventListener('keydown', function(event) {
    const key = event.key;
    let buttonText = null;
    
    if (key === 'ArrowUp') {
        buttonText = '上';
        event.preventDefault();
    } else if (key === 'ArrowDown') {
        buttonText = '下';
        event.preventDefault();
    } else if (key === 'ArrowLeft') {
        buttonText = '左';
        event.preventDefault();
    } else if (key === 'ArrowRight') {
        buttonText = '右';
        event.preventDefault();
    }
    
    if (buttonText) {
        const buttons = document.querySelectorAll('button');
        for (let btn of buttons) {
            if (btn.innerText.includes(buttonText)) {
                btn.click();
                break;
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)
