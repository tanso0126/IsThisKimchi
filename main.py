import asyncio
import json
import os
import random
from pathlib import Path

from nicegui import app, ui

# --- 1. 데이터 및 에셋 로직 ---

SCORE_FILE = Path(__file__).parent / 'backend' / 'scores.json'
APP_DIR = Path(__file__).parent / 'app'
KIMCHI_DIR = APP_DIR / 'src' / 'assets' / '김치'
NON_KIMCHI_DIR = APP_DIR / 'src' / 'assets' / '노김치'

kimchi_descriptions = {
    '배추김치': '한국의 가장 대표적인 김치로, 소금에 절인 배추에 무, 파, 고춧가루, 마늘, 생강 등의 양념을 버무려 만듭니다.',
    '깍두기': '무를 깍둑썰기하여 소금에 절인 후 고춧가루, 파, 마늘 등의 양념으로 버무려 만든 김치입니다.',
    '총각김치': '총각무를 무청째로 담가 아삭한 식감이 일품인 김치입니다.',
    '파김치': '쪽파를 주재료로 하여 멸치젓과 고춧가루 양념으로 맛을 낸, 독특한 향과 맛이 매력적인 김치입니다.',
    '오이소박이': '오이를 세로로 칼집 내어 소를 넣은 김치로, 시원하고 상큼한 맛이 특징입니다.',
    '열무김치': '어린 열무로 담가 여름철에 특히 인기 있는 시원한 물김치입니다.',
    '백김치': '고춧가루를 사용하지 않아 맵지 않고 시원하며 깔끔한 맛이 특징인 김치입니다.',
    '부추김치': '부추의 독특한 향과 젓갈의 감칠맛이 어우러진 별미 김치입니다.',
    '나박김치': '무와 배추를 얇게 썰어 국물을 자박하게 부어 만든 물김치의 일종입니다.',
    '갓김치': '톡 쏘는 맛과 독특한 향이 특징인 갓으로 담근 김치입니다.',
}

def get_asset_path(full_path: Path) -> str:
    return str(full_path.relative_to(Path(__file__).parent).as_posix())

def create_shuffled_deck():
    all_kimchi_data = []
    if KIMCHI_DIR.exists():
        for kimchi_type_dir in KIMCHI_DIR.iterdir():
            if kimchi_type_dir.is_dir():
                kimchi_name = kimchi_type_dir.name
                for image_path in kimchi_type_dir.glob('*.*'):
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                        all_kimchi_data.append({
                            'id': str(image_path), 'name': kimchi_name, 'is_kimchi': True,
                            'url': get_asset_path(image_path),
                            'description': kimchi_descriptions.get(kimchi_name, '맛있는 김치입니다!'),
                        })

    all_non_kimchi_data = []
    if NON_KIMCHI_DIR.exists():
        for non_kimchi_type_dir in NON_KIMCHI_DIR.iterdir():
            if non_kimchi_type_dir.is_dir():
                non_kimchi_name = non_kimchi_type_dir.name
                for image_path in non_kimchi_type_dir.glob('*.*'):
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                        all_non_kimchi_data.append({
                            'id': str(image_path), 'name': non_kimchi_name, 'is_kimchi': False,
                            'url': get_asset_path(image_path),
                            'description': f'이것은 김치가 아닌 "{non_kimchi_name}"입니다.',
                        })

    session_kimchi = []
    if all_kimchi_data:
        k = min(len(all_kimchi_data), 40)
        session_kimchi = random.sample(all_kimchi_data, k)

    session_non_kimchi = []
    if all_non_kimchi_data:
        k = min(len(all_non_kimchi_data), 40)
        session_non_kimchi = random.sample(all_non_kimchi_data, k)

    final_deck = session_kimchi + session_non_kimchi
    random.shuffle(final_deck)
    return final_deck

# --- 2. 백엔드 로직 ---

DEFAULT_SCORES = {'survival': [], 'time_attack': []}

def load_scores():
    if not SCORE_FILE.exists():
        return DEFAULT_SCORES
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'survival' in data and 'time_attack' in data:
                return data
            elif isinstance(data, list): # 이전 버전 호환
                return {'survival': data, 'time_attack': []}
            else:
                return DEFAULT_SCORES
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_SCORES

def save_scores(scores):
    with open(SCORE_FILE, 'w', encoding='utf-8') as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

def submit_score(nickname, score, game_mode):
    scores = load_scores()
    mode_scores = scores.get(game_mode, [])
    
    existing_score = next((s for s in mode_scores if s['nickname'] == nickname), None)

    if existing_score:
        existing_score['score'] = max(existing_score.get('score', 0), score)
    else:
        mode_scores.append({'nickname': nickname, 'score': score})

    mode_scores.sort(key=lambda s: s.get('score', 0), reverse=True)
    scores[game_mode] = mode_scores
    save_scores(scores)

# --- 3. UI 상태 및 로직 ---
state = {
    'view': 'menu',
    'game_mode': None,
    'deck': [],
    'score': 0,
    'timer_value': 30,
    'game_over_image': None,
}

# --- 4. UI 레이아웃 ---

@ui.page('/')
def main_page():
    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            body {
                font-family: 'Noto Sans KR', sans-serif;
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            .q-card {
                box-shadow: 0px 18px 40px -12px rgba(0, 0, 0, 0.8) !important;
                border-radius: 20px !important;
            }
        </style>
    ''')
    ui.dark_mode().enable()

    view_container = ui.column().classes('w-full items-center justify-center')
    game_timer = ui.timer(1.0, lambda: handle_timer_tick(), active=False)

    def build_menu():
        with view_container.classes('gap-4 text-center'):
            ui.label('이게 김치일까?').classes('text-5xl font-bold text-red-500 mb-4')
            ui.label('플레이할 게임 모드를 선택해주세요!').classes('text-lg text-gray-400 mb-8')
            ui.button('연속해서 맞추기 (서바이벌)', on_click=lambda: start_game('survival')).classes('px-7 py-2 text-lg')
            ui.button('30초 안에 많이 맞추기 (타임어택)', on_click=lambda: start_game('time_attack')).classes('px-7 py-2 text-lg')
            ui.button('명예의 전당', on_click=show_leaderboard).classes('px-7 py-2 text-lg mt-4')

    def build_game():
        with view_container.classes('w-full items-center justify-center gap-2'):
            with ui.row().classes('absolute top-5 right-5 items-center'):
                ui.button('🏆', on_click=show_leaderboard, color='yellow').classes('text-2xl')

            ui.label('이게 김치일까?').classes('text-5xl font-bold text-red-500 mb-2')
            score_label = ui.label().classes('text-3xl mb-2').bind_text_from(state, 'score', lambda s: f'점수: {s}')
            timer_label = ui.label().classes('text-4xl font-bold mb-4')
            
            if state['game_mode'] == 'survival':
                timer_label.bind_text_from(state, 'timer_value', lambda t: f'남은 시간: {t}초')
            else:
                timer_label.bind_text_from(state, 'timer_value', lambda t: f'남은 시간: {t}초')

            with ui.card().classes('w-[350px] h-[500px] p-0 overflow-hidden relative'):
                if state['deck']:
                    current_card = state['deck'][0]
                    ui.image(current_card['url']).classes('w-full h-full object-cover')
                else:
                    ui.spinner(size='lg').classes('w-full h-full flex items-center justify-center')

            ui.label('카드를 보고 아래 버튼을 눌러주세요!').classes('text-lg text-gray-400 mt-4')
            
            with ui.row():
                ui.button('김치 아님! 🤔', on_click=lambda: handle_choice(False), color='blue').classes('p-4 text-xl')
                ui.button('김치! 😋', on_click=lambda: handle_choice(True), color='red').classes('p-4 text-xl')

    def build_game_over():
        img = state['game_over_image']
        with view_container.classes('gap-4 text-center'):
            ui.label('게임 오버!').classes('text-6xl font-bold text-red-600')
            ui.label(f"최종 점수: {state['score']}").classes('text-4xl')

            if img and state['game_mode'] == 'survival':
                with ui.card().classes('w-[350px] h-fit'):
                    ui.image(img['url'])
                    with ui.card_section():
                        ui.label(f'이건 "{img["name"]}" 이었어요!').classes('text-2xl font-bold')
                        ui.label(img['description']).classes('text-md mt-2')

            with ui.row().classes('items-center'):
                nickname_input = ui.input(placeholder='닉네임을 입력하세요').classes('w-48')
                ui.button('점수 등록', on_click=lambda: handle_score_submit(nickname_input.value, state['game_mode'])).classes('text-lg')
            
            ui.button('다시 하기', on_click=lambda: start_game(state['game_mode'])).classes('px-7 py-2 text-lg')
            ui.button('메뉴로', on_click=show_menu).classes('px-7 py-2 text-lg mt-2')

    def build_leaderboard():
        with view_container.classes('gap-4 w-full items-center'):
            ui.label('명예의 전당').classes('text-5xl font-bold text-yellow-500')
            scores = load_scores()
            with ui.tabs().classes('w-96') as tabs:
                survival_tab = ui.tab('서바이벌')
                time_attack_tab = ui.tab('타임어택')
            with ui.tab_panels(tabs, value=survival_tab).classes('w-96 bg-transparent'):
                with ui.tab_panel(survival_tab):
                    if not scores.get('survival'):
                        ui.label('아직 등록된 점수가 없어요!').classes('p-4 text-center')
                    else:
                        with ui.grid(columns=3).classes('w-full p-4 gap-y-2'):
                            ui.label('순위').classes('font-bold')
                            ui.label('닉네임').classes('font-bold')
                            ui.label('점수').classes('font-bold place-self-end')
                            for i, s in enumerate(scores['survival'][:20]):
                                ui.label(f'{i+1}.')
                                ui.label(s.get('nickname', ''))
                                ui.label(s.get('score', '')).classes('place-self-end')
                with ui.tab_panel(time_attack_tab):
                    if not scores.get('time_attack'):
                        ui.label('아직 등록된 점수가 없어요!').classes('p-4 text-center')
                    else:
                        with ui.grid(columns=3).classes('w-full p-4 gap-y-2'):
                            ui.label('순위').classes('font-bold')
                            ui.label('닉네임').classes('font-bold')
                            ui.label('점수').classes('font-bold place-self-end')
                            for i, s in enumerate(scores['time_attack'][:20]):
                                ui.label(f'{i+1}.')
                                ui.label(s.get('nickname', ''))
                                ui.label(s.get('score', '')).classes('place-self-end')
            ui.button('메뉴로 돌아가기', on_click=show_menu).classes('mt-4 px-7 py-2 text-lg')

    def update_view():
        view = state['view']
        view_container.clear()
        if view == 'menu':
            build_menu()
        elif view == 'game':
            build_game()
        elif view == 'gameover':
            build_game_over()
        elif view == 'leaderboard':
            build_leaderboard()

    async def start_game(mode: str):
        view_container.clear()
        with view_container:
            ui.spinner(size='lg')
            ui.label('카드를 섞는 중...').classes('text-3xl')
        
        await asyncio.sleep(0.1)
        state['game_mode'] = mode
        state['score'] = 0
        state['timer_value'] = 5 if mode == 'survival' else 30
        state['game_over_image'] = None
        state['deck'] = create_shuffled_deck()

        if not state['deck']:
            view_container.clear()
            with view_container:
                ui.label('앗! 이미지 카드를 찾을 수 없어요!').classes('text-2xl text-red-500')
                ui.label('`app/src/assets` 폴더가 있는지 확인해주세요.').classes('text-lg')
                ui.button('메뉴로 돌아가기', on_click=show_menu)
            return

        state['view'] = 'game'
        update_view()
        game_timer.activate()

    def handle_choice(is_kimchi_choice: bool):
        if not state['deck']: return
        card = state['deck'][0]
        is_correct = (card['is_kimchi'] == is_kimchi_choice)

        if is_correct:
            state['score'] += 1
            if state['game_mode'] == 'survival':
                state['timer_value'] = 5
        else:  # 오답
            if state['game_mode'] == 'survival':
                game_over()
                return
            elif state['game_mode'] == 'time_attack':
                state['score'] = max(0, state['score'] - 2)
                ui.notify('오답! -2점 감점! 😭', color='negative')

        # 다음 카드로 이동
        state['deck'].pop(0)
        if len(state['deck']) < 5:
            state['deck'].extend(create_shuffled_deck())
        
        if state['view'] == 'game':
            update_view()

    def game_over():
        game_timer.deactivate()
        if state['deck']:
            state['game_over_image'] = state['deck'][0]
        state['view'] = 'gameover'
        update_view()

    def handle_timer_tick():
        state['timer_value'] -= 1
        if state['timer_value'] < 0:
            state['timer_value'] = 0
            game_over()
    
    def show_leaderboard():
        game_timer.deactivate()
        state['view'] = 'leaderboard'
        update_view()

    def show_menu():
        game_timer.deactivate()
        state['view'] = 'menu'
        update_view()
    
    async def handle_score_submit(nickname: str, game_mode: str):
        if not nickname.strip():
            ui.notify('닉네임을 입력해주세요!', color='negative')
            return
        submit_score(nickname, state['score'], game_mode)
        await asyncio.sleep(0.1)
        show_leaderboard()

    update_view()

app.add_static_files('/app', str(APP_DIR))

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get('PORT', 8080))
    ui.run(title='이게 김치일까?', language='ko', reload=False, port=port, host='0.0.0.0')