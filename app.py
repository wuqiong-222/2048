import streamlit as st
import random
import json

# ------------------- 页面配置（必须放最顶部）-------------------
st.set_page_config(
    page_title="2048",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------- 样式：电脑+手机双端适配 -------------------
st.markdown("""
<style>
/* 全局适配 */
html, body {
    overflow-x: hidden;
    max-width: 100vw;
    margin: 0 auto;
}

/* 棋盘容器：自动居中、自动缩放 */
.board-container {
    width: 90vw;
    max-width: 420px;
    margin: 10px auto;
    touch-action: manipulation;
}

/* 4×4 网格 */
.board {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    background: #bbada0;
    padding: 10px;
    border-radius: 10px;
}

/* 格子：正方形、自适应 */
.cell {
    aspect-ratio: 1 / 1;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: clamp(20px, 6vw, 32px);
    font-weight: bold;
    border-radius: 6px;
    background: #cdc1b4;
    color: #776e65;
}

/* 数字颜色 */
.c2 { background:#eee4da; }
.c4 { background:#ede0c8; }
.c8 { background:#f2b179; color:white; }
.c16 { background:#f59563; color:white; }
.c32 { background:#f67c5f; color:white; }
.c64 { background:#f65e3b; color:white; }
.c128 { background:#edcf72; color:white; }
.c256 { background:#edcc61; color:white; }
.c512 { background:#ecc850; color:white; }
.c1024 { background:#edc22e; color:white; }
.c2048 { background:#3c3a32; color:white; }

/* 按钮放大，手机好按 */
.stButton button {
    font-size: 18px !important;
    padding: 12px !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------- 游戏核心逻辑 -------------------
def init_board():
    board = [[0]*4 for _ in range(4)]
    add_random(board)
    add_random(board)
    return board

def add_random(board):
    empty = [(r,c) for r in range(4) for c in range(4) if board[r][c]==0]
    if empty:
        r,c = random.choice(empty)
        board[r][c] = 2 if random.random()<0.9 else 4

def flatten(row):
    nums = [x for x in row if x != 0]
    for i in range(len(nums)-1):
        if nums[i]==nums[i+1]:
            nums[i] *= 2
            nums[i+1] = 0
    nums = [x for x in nums if x != 0]
    return nums + [0]*(4-len(nums))

def move_left(board):
    new = [flatten(row) for row in board]
    return new if new != board else None

def rotate(board):
    return [list(x) for x in zip(*board[::-1])]

def move_right(board):
    b = [row[::-1] for row in board]
    b = move_left(b)
    return [row[::-1] for row in b] if b else None

def move_up(board):
    b = rotate(rotate(rotate(board)))
    b = move_left(b)
    return rotate(b) if b else None

def move_down(board):
    b = rotate(board)
    b = move_left(b)
    return rotate(rotate(rotate(b))) if b else None

def is_win(board):
    return any(2048 in row for row in board)

def is_lose(board):
    if any(0 in row for row in board):
        return False
    for r in range(4):
        for c in range(4):
            v = board[r][c]
            if r<3 and board[r+1][c]==v: return False
            if c<3 and board[r][c+1]==v: return False
    return True

# ------------------- 状态初始化 -------------------
if "board" not in st.session_state:
    st.session_state.board = init_board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "win" not in st.session_state:
    st.session_state.win = False

# ------------------- 键盘/滑动 支持 -------------------
if "key" not in st.session_state:
    st.session_state.key = ""

# JS 监听键盘 + 触屏滑动
st.markdown("""
<script>
// 键盘 ↑ ↓ ← →
document.addEventListener('keydown', function(e) {
    let key = '';
    if(e.key==='ArrowUp') key='up';
    if(e.key==='ArrowDown') key='down';
    if(e.key==='ArrowLeft') key='left';
    if(e.key==='ArrowRight') key='right';
    if(key) {
        window.parent.postMessage({type: 'key', data: key}, '*');
        e.preventDefault();
    }
});

// 手机触屏滑动
let touchX, touchY;
document.addEventListener('touchstart', e=>{touchX=e.touches[0].clientX; touchY=e.touches[0].clientY});
document.addEventListener('touchend', e=>{
    if(!touchX||!touchY) return;
    let dx = e.changedTouches[0].clientX - touchX;
    let dy = e.changedTouches[0].clientY - touchY;
    let res='';
    if(Math.abs(dx)>Math.abs(dy)){
        if(dx>30) res='right';
        if(dx<-30) res='left';
    }else{
        if(dy>30) res='down';
        if(dy<-30) res='up';
    }
    if(res) window.parent.postMessage({type:'swipe',data:res},'*');
});

// 接收消息发给Streamlit
window.addEventListener('message', e=>{
    if(e.data.type==='key'||e.data.type==='swipe'){
        window.stKey = e.data.data;
        document.body.click();
    }
});
</script>
""", unsafe_allow_html=True)

# ------------------- 执行操作 -------------------
def do_move(func):
    if st.session_state.game_over:
        return
    new_board = func(st.session_state.board)
    if new_board:
        st.session_state.board = new_board
        add_random(st.session_state.board)
        if is_win(st.session_state.board):
            st.session_state.win = True
            st.session_state.game_over = True
        elif is_lose(st.session_state.board):
            st.session_state.game_over = True

# 从JS获取按键
if "stKey" in globals() and stKey:
    if stKey == "up": do_move(move_up)
    if stKey == "down": do_move(move_down)
    if stKey == "left": do_move(move_left)
    if stKey == "right": do_move(move_right)
    stKey = ""

# ------------------- 界面渲染 -------------------
st.title("🎮 2048 游戏")
st.subheader("电脑：键盘 ↑ ↓ ← →  手机：滑动屏幕")

# 按钮
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("👆 上"): do_move(move_up)
with col2:
    if st.button("👇 下"): do_move(move_down)
with col3:
    if st.button("👈 左"): do_move(move_left)
with col4:
    if st.button("👉 右"): do_move(move_right)

if st.button("🔄 重新开始"):
    st.session_state.board = init_board()
    st.session_state.game_over = False
    st.session_state.win = False

# 状态
if st.session_state.win:
    st.success("🎉 恭喜你，合成 2048 成功！")
elif st.session_state.game_over:
    st.error("💥 游戏结束，再来一局吧！")

# 棋盘
st.markdown('<div class="board-container"><div class="board">', unsafe_allow_html=True)
for row in st.session_state.board:
    for num in row:
        cls = f"cell c{num}" if num != 0 else "cell"
        txt = str(num) if num != 0 else ""
        st.markdown(f'<div class="{cls}">{txt}</div>', unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)
