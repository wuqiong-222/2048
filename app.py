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
    touch-action: pan-y pinch-zoom; /* 保留垂直滚动，避免全屏冲突 */
}
</style>

<!-- 引入 Hammer.js 库用于触摸手势 -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>

<script>
    // 等待页面加载完成
    window.addEventListener("load", function() {
        // 寻找游戏区域 (grid-container 的父容器或直接监听 body)
        const container = document.querySelector('.grid-container');
        if (!container) return;
        
        const hammertime = new Hammer(container);
        // 只识别水平/垂直滑动
        hammertime.get('swipe').set({ direction: Hammer.DIRECTION_ALL });
        
        hammertime.on('swipeleft', function(ev) {
            // 触发左滑: 找到 Streamlit 的 left 按钮并点击
            const leftBtn = document.querySelector('button[kind="leftBtn"]');
            if(leftBtn) leftBtn.click();
            else {
                // 备用: 通过 data-testid 查找所有按钮 (更可靠)
                const btns = document.querySelectorAll('button');
                for(let btn of btns) {
                    if(btn.innerText.includes('⬅️') || btn.innerText.includes('左')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
        
        hammertime.on('swiperight', function(ev) {
            const rightBtn = document.querySelector('button[kind="rightBtn"]');
            if(rightBtn) rightBtn.click();
            else {
                const btns = document.querySelectorAll('button');
                for(let btn of btns) {
                    if(btn.innerText.includes('➡️') || btn.innerText.includes('右')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
        
        hammertime.on('swipeup', function(ev) {
            const upBtn = document.querySelector('button[kind="upBtn"]');
            if(upBtn) upBtn.click();
            else {
                const btns = document.querySelectorAll('button');
                for(let btn of btns) {
                    if(btn.innerText.includes('⬆️') || btn.innerText.includes('上')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
        
        hammertime.on('swipedown', function(ev) {
            const downBtn = document.querySelector('button[kind="downBtn"]');
            if(downBtn) downBtn.click();
            else {
                const btns = document.querySelectorAll('button');
                for(let btn of btns) {
                    if(btn.innerText.includes('⬇️') || btn.innerText.includes('下')) {
                        btn.click();
                        break;
                    }
                }
            }
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

# 四个方向控制
def up():
    if st.session_state.game_over:
        return
    st.session_state.board = np.rot90(st.session_state.board)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b, k=3)
    st.session_state.score += s
    add_num()

def down():
    if st.session_state.game_over:
        return
    st.session_state.board = np.rot90(st.session_state.board, k=3)
    b, s = move_left(st.session_state.board)
    st.session_state.board = np.rot90(b)
    st.session_state.score += s
    add_num()

def left():
    if st.session_state.game_over:
        return
    b, s = move_left(st.session_state.board)
    # 检查是否有变化，无变化则不生成新数字
    if not np.array_equal(st.session_state.board, b):
        st.session_state.board = b
        st.session_state.score += s
        add_num()

def right():
    if st.session_state.game_over:
        return
    st.session_state.board = np.fliplr(st.session_state.board)
    b, s = move_left(st.session_state.board)
    new_board = np.fliplr(b)
    if not np.array_equal(st.session_state.board, new_board):
        st.session_state.board = new_board
        st.session_state.score += s
        add_num()

# 随机生成 2 或 4
def add_num():
    empty = [(i, j) for i in range(4) for j in range(4) if st.session_state.board[i][j] == 0]
    if not empty:
        # 检查是否真的无移动可能
        if not any_can_move():
            st.session_state.game_over = True
        return
    i, j = random.choice(empty)
    st.session_state.board[i][j] = 2 if random.random() < 0.9 else 4

def any_can_move():
    """检查是否存在任何合法的移动"""
    for i in range(4):
        for j in range(4):
            if st.session_state.board[i][j] == 0:
                return True
            if j < 3 and st.session_state.board[i][j] == st.session_state.board[i][j+1]:
                return True
            if i < 3 and st.session_state.board[i][j] == st.session_state.board[i+1][j]:
                return True
    return False

# 界面
st.title("🎮 2048 数字游戏")
st.caption("💡 PC端：键盘方向键  |  📱 移动端：手指滑动屏幕")

st.subheader(f"当前分数：{st.session_state.score}")

# 绘制棋盘（添加 id 以方便 JavaScript 绑定）
grid_html = "<div id='swipe-area'><div class='grid-container'>"
for row in st.session_state.board:
    for num in row:
        val = num if num != 0 else ""
        grid_html += f"<div class='grid-item'>{val}</div>"
grid_html += "</div></div>"
st.markdown(grid_html, unsafe_allow_html=True)

# 游戏结束
if st.session_state.game_over:
    st.error("❌ 游戏结束！点击「重新开始」再来一把～")

# 按钮区域，添加 kind 属性便于 JavaScript 定位
col1, col2, col3, col4 = st.columns(4)
with col1: 
    st.button("⬆️ 上", use_container_width=True, on_click=up, key="up_btn", kwargs={"kind": "upBtn"})
with col2: 
    st.button("⬅️ 左", use_container_width=True, on_click=left, key="left_btn", kwargs={"kind": "leftBtn"})
with col3: 
    st.button("➡️ 右", use_container_width=True, on_click=right, key="right_btn", kwargs={"kind": "rightBtn"})
with col4: 
    st.button("⬇️ 下", use_container_width=True, on_click=down, key="down_btn", kwargs={"kind": "downBtn"})

# 重置
if st.button("🔄 重新开始", type="primary"):
    st.session_state.board = np.zeros((4, 4), dtype=int)
    st.session_state.score = 0
    st.session_state.game_over = False
    empty_cells = [(x, y) for x in range(4) for y in range(4)]
    for _ in range(2):
        i, j = random.choice([cell for cell in empty_cells if st.session_state.board[cell[0]][cell[1]] == 0])
        st.session_state.board[i][j] = 2
    st.rerun()

# 键盘事件监听 (通过 JavaScript)
st.markdown("""
<script>
document.addEventListener('keydown', function(event) {
    // 防止页面滚动
    const key = event.key;
    let btn = null;
    
    // 方向键映射
    if (key === 'ArrowUp') {
        btn = document.querySelector('button[kind="upBtn"]');
        event.preventDefault();
    } else if (key === 'ArrowDown') {
        btn = document.querySelector('button[kind="downBtn"]');
        event.preventDefault();
    } else if (key === 'ArrowLeft') {
        btn = document.querySelector('button[kind="leftBtn"]');
        event.preventDefault();
    } else if (key === 'ArrowRight') {
        btn = document.querySelector('button[kind="rightBtn"]');
        event.preventDefault();
    }
    
    if (btn) {
        btn.click();
    }
});
</script>
""", unsafe_allow_html=True)
