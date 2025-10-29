import asyncio
import json
import os
import random
from pathlib import Path

from nicegui import app, ui

# --- 1. 전역 데이터 및 설정 (모든 사용자에게 동일) ---

SCORE_FILE = Path(__file__).parent / 'backend' / 'scores.json'
APP_DIR = Path(__file__).parent / 'app'
KIMCHI_DIR = APP_DIR / 'src' / 'assets' / '김치'
NON_KIMCHI_DIR = APP_DIR / 'src' / 'assets' / '노김치'

# --- 2. 다국어 지원 (i18n) ---

TRANSLATIONS = {
    'ko': {
        'game_title': '이게 김치일까?',
        'game_subtitle': '플레이할 게임 모드를 선택해주세요!',
        'start_survival': '연속해서 맞추기 (서바이벌)',
        'start_time_attack': '30초 안에 많이 맞추기 (타임어택)',
        'leaderboard': '명예의 전당',
        'loading_cards': '카드를 섞는 중...',
        'score': '점수',
        'time_left': '남은 시간',
        'seconds': '초',
        'instructions': '카드를 보고 아래 버튼을 눌러주세요!',
        'is_kimchi_btn': '김치! 😋',
        'not_kimchi_btn': '김치 아님! 🤔',
        'game_over': '게임 오버!',
        'final_score': '최종 점수',
        'this_was': '이건 "{name}" 이었어요!',
        'submit_score': '점수 등록',
        'enter_nickname': '닉네임을 입력하세요',
        'nickname_empty': '닉네임을 입력해주세요!',
        'try_again': '다시 하기',
        'back_to_menu': '메뉴로 돌아가기',
        'no_scores': '아직 등록된 점수가 없어요!',
        'rank': '순위',
        'nickname': '닉네임',
        'survival_tab': '서바이벌',
        'time_attack_tab': '타임어택',
        'no_images_found': '앗! 이미지 카드를 찾을 수 없어요!',
        'check_assets_folder': '`app/src/assets` 폴더가 있는지 확인해주세요.',
        'wrong_answer_penalty': '오답! -2점 감점! 😭',
    },
    'en': {
        'game_title': 'Is This Kimchi?',
        'game_subtitle': 'Please select a game mode to play!',
        'start_survival': 'Endless Mode (Survival)',
        'start_time_attack': '30-Second Challenge (Time Attack)',
        'leaderboard': 'Leaderboard',
        'loading_cards': 'Shuffling cards...',
        'score': 'Score',
        'time_left': 'Time Left',
        'seconds': 's',
        'instructions': 'Look at the card and press a button below!',
        'is_kimchi_btn': 'Kimchi! 😋',
        'not_kimchi_btn': 'Not Kimchi! 🤔',
        'game_over': 'Game Over!',
        'final_score': 'Final Score',
        'this_was': 'This was "{name}"!',
        'submit_score': 'Submit Score',
        'enter_nickname': 'Enter your nickname',
        'nickname_empty': 'Please enter a nickname!',
        'try_again': 'Try Again',
        'back_to_menu': 'Back to Menu',
        'no_scores': 'No scores registered yet!',
        'rank': 'Rank',
        'nickname': 'Nickname',
        'survival_tab': 'Survival',
        'time_attack_tab': 'Time Attack',
        'no_images_found': 'Oops! Image cards not found!',
        'check_assets_folder': 'Please check if the `app/src/assets` folder exists.',
        'wrong_answer_penalty': 'Wrong! -2 points! 😭',
    }
}

KIMCHI_DATA = {
    '배추김치': {
        'en_name': 'Baechu Kimchi',
        'ko_desc': '한국의 가장 대표적인 김치로, 소금에 절인 배추에 무, 파, 고춧가루, 마늘, 생강 등의 양념을 버무려 만듭니다.',
        'en_desc': 'The most representative kimchi in Korea, made by mixing salted napa cabbage with seasonings such as radish, green onions, red chili powder, garlic, and ginger.',
    },
    '깍두기': {
        'en_name': 'Kkakdugi (Cubed Radish Kimchi)',
        'ko_desc': '무를 깍둑썰기하여 소금에 절인 후 고춧가루, 파, 마늘 등의 양념으로 버무려 만든 김치입니다.',
        'en_desc': 'Kimchi made by dicing radish, salting it, and then mixing it with seasonings like red chili powder, green onions, and garlic.',
    },
    '총각김치': {
        'en_name': 'Chonggak Kimchi (Young Radish Kimchi)',
        'ko_desc': '총각무를 무청째로 담가 아삭한 식감이 일품인 김치입니다.',
        'en_desc': 'This kimchi, made with young radishes including their greens, is known for its excellent crunchy texture.',
    },
    '파김치': {
        'en_name': 'Pa Kimchi (Green Onion Kimchi)',
        'ko_desc': '쪽파를 주재료로 하여 멸치젓과 고춧가루 양념으로 맛을 낸, 독특한 향과 맛이 매력적인 김치입니다.',
        'en_desc': 'A kimchi with a unique aroma and taste, made with green onions as the main ingredient and seasoned with anchovy jeot (fermented seafood) and red chili powder.',
    },
    '오이소박이': {
        'en_name': 'Oi Sobagi (Cucumber Kimchi)',
        'ko_desc': '오이를 세로로 칼집 내어 소를 넣은 김치로, 시원하고 상큼한 맛이 특징입니다.',
        'en_desc': 'A kimchi made by stuffing vertically sliced cucumbers with a filling, characterized by its cool and refreshing taste.',
    },
    '열무김치': {
        'en_name': 'Yeolmu Kimchi (Young Summer Radish Kimchi)',
        'ko_desc': '어린 열무로 담가 여름철에 특히 인기 있는 시원한 물김치입니다.',
        'en_desc': 'A cool water-based kimchi made with young summer radishes, especially popular during the summer.',
    },
    '백김치': {
        'en_name': 'Baek Kimchi (White Kimchi)',
        'ko_desc': '고춧가루를 사용하지 않아 맵지 않고 시원하며 깔끔한 맛이 특징인 김치입니다.',
        'en_desc': 'A non-spicy kimchi known for its cool, clean taste, made without red chili powder.',
    },
    '부추김치': {
        'en_name': 'Buchu Kimchi (Chive Kimchi)',
        'ko_desc': '부추의 독특한 향과 젓갈의 감칠맛이 어우러진 별미 김치입니다.',
        'en_desc': 'A delicacy kimchi where the unique aroma of chives combines with the savory taste of jeot (fermented seafood).',
    },
    '나박김치': {
        'en_name': 'Nabak Kimchi (Water Kimchi)',
        'ko_desc': '무와 배추를 얇게 썰어 국물을 자박하게 부어 만든 물김치의 일종입니다.',
        'en_desc': 'A type of water kimchi made with thinly sliced radish and cabbage in a soupy brine.',
    },
    '갓김치': {
        'en_name': 'Gat Kimchi (Mustard Leaf Kimchi)',
        'ko_desc': '톡 쏘는 맛과 독특한 향이 특징인 갓으로 담근 김치입니다.',
        'en_desc': 'A kimchi made with mustard leaves, characterized by its sharp, pungent taste and unique aroma.',
    }
}

NON_KIMCHI_DATA = {
    '가지볶음': {
        'en_name': 'Gaji-bokkeum (Stir-fried Eggplant)',
        'ko_desc': '가지를 먹기 좋게 썰어 간장과 마늘 등으로 양념하여 볶은 한국의 흔한 밑반찬입니다.',
        'en_desc': 'A common Korean side dish made by stir-frying sliced eggplant with soy sauce and garlic.'
    },
    '고사리나물': {
        'en_name': 'Gosari-namul (Bracken Fern Side Dish)',
        'ko_desc': '삶은 고사리를 간장, 마늘, 참기름 등으로 양념하여 볶거나 무친 나물입니다.',
        'en_desc': 'A side dish made by seasoning boiled bracken fern with soy sauce, garlic, and sesame oil.'
    },
    '꽈리고추무침': {
        'en_name': 'Kkwarigochu-muchim (Seasoned Shishito Peppers)',
        'ko_desc': '꽈리고추를 쪄서 간장, 고춧가루, 액젓 등으로 양념한 매콤짭짤한 밑반찬입니다.',
        'en_desc': 'A spicy and savory side dish made by steaming shishito peppers and seasoning them with soy sauce, chili powder, and fish sauce.'
    },
    '도라지무침': {
        'en_name': 'Doraji-muchim (Seasoned Bellflower Roots)',
        'ko_desc': '쓴맛을 제거한 도라지를 고추장, 식초, 설탕 등으로 새콤달콤하게 무친 요리입니다.',
        'en_desc': 'A dish made by seasoning bitterless bellflower roots with a sweet and sour sauce of gochujang, vinegar, and sugar.'
    },
    '도토리묵': {
        'en_name': 'Dotori-muk (Acorn Jelly)',
        'ko_desc': '도토리 녹말로 만든 묵을 썰어 간장 양념과 함께 먹는 음식입니다. 탱글탱글한 식감이 특징입니다.',
        'en_desc': 'Acorn jelly, cut into pieces and served with a soy sauce-based dressing. It has a jiggly, smooth texture.'
    },
    '미역줄기볶음': {
        'en_name': 'Miyeok-julgi-bokkeum (Stir-fried Seaweed Stems)',
        'ko_desc': '염장된 미역줄기를 볶아 만든 밑반찬으로, 꼬들꼬들한 식감이 특징입니다.',
        'en_desc': 'A side dish made by stir-frying salted seaweed stems, known for its chewy and crunchy texture.'
    },
    '숙주나물': {
        'en_name': 'Sukju-namul (Mung Bean Sprout Salad)',
        'ko_desc': '숙주를 데쳐 소금, 참기름, 다진 마늘 등으로 무친 담백하고 아삭한 나물입니다.',
        'en_desc': 'A light and crunchy side dish made by blanching mung bean sprouts and seasoning them with salt, sesame oil, and minced garlic.'
    },
    '시금치나물': {
        'en_name': 'Sigeumchi-namul (Seasoned Spinach)',
        'ko_desc': '데친 시금치를 간장이나 소금, 참기름 등으로 조물조물 무쳐 만든 대표적인 나물 반찬입니다.',
        'en_desc': 'A classic Korean side dish made by seasoning blanched spinach with soy sauce or salt and sesame oil.'
    },
    '애호박볶음': {
        'en_name': 'Aehobak-bokkeum (Stir-fried Zucchini)',
        'ko_desc': '애호박을 채 썰어 새우젓이나 소금으로 간을 하여 볶은, 달큰하고 부드러운 맛의 반찬입니다.',
        'en_desc': 'A sweet and soft side dish made by stir-frying julienned zucchini seasoned with salted shrimp or salt.'
    },
    '약과': {
        'en_name': 'Yakgwa (Honey Cookie)',
        'ko_desc': '밀가루를 꿀, 참기름 등으로 반죽하여 기름에 튀겨 만든 한국의 전통 과자입니다.',
        'en_desc': 'A traditional Korean confectionery made by deep-frying dough made of flour, honey, and sesame oil.'
    },
    '약식': {
        'en_name': 'Yaksik (Sweet Rice Dessert)',
        'ko_desc': '찹쌀에 밤, 대추, 잣 등을 섞어 찐 후 간장, 꿀, 참기름으로 양념한 달콤한 영양 간식입니다.',
        'en_desc': 'A sweet and nutritious snack made by steaming glutinous rice with chestnuts, jujubes, and pine nuts, then seasoning with soy sauce, honey, and sesame oil.'
    },
    '잡채': {
        'en_name': 'Japchae (Glass Noodle Stir Fry)',
        'ko_desc': '당면과 여러 가지 채소, 고기 등을 간장 양념으로 볶아 만든 한국의 잔치 음식입니다.',
        'en_desc': 'A festive Korean dish made by stir-frying glass noodles with various vegetables and meat in a soy sauce seasoning.'
    },
    '콩나물무침': {
        'en_name': 'Kongnamul-muchim (Seasoned Soybean Sprouts)',
        'ko_desc': '삶은 콩나물을 소금, 고춧가루, 참기름 등으로 무친, 한국인이 가장 사랑하는 밑반찬 중 하나입니다.',
        'en_desc': 'One of the most beloved Korean side dishes, made by seasoning boiled soybean sprouts with salt, chili powder, and sesame oil.'
    },
    '한과': {
        'en_name': 'Hangwa (Traditional Korean Confectionery)',
        'ko_desc': '곡물 가루나 꿀, 엿, 과일 등을 주재료로 하여 만든 한국의 전통 과자를 총칭하는 말입니다.',
        'en_desc': 'A general term for traditional Korean confections made with grain flour, honey, yeot (Korean taffy), and fruits.'
    },
    '홍어무침': {
        'en_name': 'Hongeo-muchim (Seasoned Fermented Skate)',
        'ko_desc': '삭힌 홍어를 막걸리 식초, 고추장, 채소 등과 함께 새콤달콤하게 무친 요리입니다. 톡 쏘는 맛이 특징입니다.',
        'en_desc': 'A dish made by seasoning fermented skate with makgeolli vinegar, gochujang, and vegetables for a sweet and sour taste, known for its strong, ammonia-like aroma.'
    },
    '회무침': {
        'en_name': 'Hoe-muchim (Spicy Raw Fish Salad)',
        'ko_desc': '신선한 생선회를 채소와 함께 초고추장 양념으로 새콤달콤하게 무쳐낸 요리입니다.',
        'en_desc': 'A dish made by mixing fresh raw fish with vegetables in a sweet, sour, and spicy gochujang-based sauce.'
    }
}

def get_asset_path(full_path: Path) -> str:
    return str(full_path.relative_to(Path(__file__).parent).as_posix())

def create_shuffled_deck():
    all_kimchi_data = []
    if KIMCHI_DIR.exists():
        for kimchi_type_dir in KIMCHI_DIR.iterdir():
            if kimchi_type_dir.is_dir() and kimchi_type_dir.name in KIMCHI_DATA:
                for image_path in kimchi_type_dir.glob('*.*'):
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                        all_kimchi_data.append({
                            'id': str(image_path), 'name': kimchi_type_dir.name, 'is_kimchi': True,
                            'url': get_asset_path(image_path)
                        })

    all_non_kimchi_data = []
    if NON_KIMCHI_DIR.exists():
        for non_kimchi_type_dir in NON_KIMCHI_DIR.iterdir():
            if non_kimchi_type_dir.is_dir() and non_kimchi_type_dir.name in NON_KIMCHI_DATA:
                for image_path in non_kimchi_type_dir.glob('*.*'):
                    if image_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
                        all_non_kimchi_data.append({
                            'id': str(image_path), 'name': non_kimchi_type_dir.name, 'is_kimchi': False,
                            'url': get_asset_path(image_path)
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

# --- 3. 백엔드 로직 ---

DEFAULT_SCORES = {'survival': [], 'time_attack': []}

def load_scores():
    if not SCORE_FILE.exists():
        return DEFAULT_SCORES
    try:
        with open(SCORE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'survival' in data and 'time_attack' in data:
                return data
            elif isinstance(data, list):
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

# --- 4. UI 페이지 ---

@ui.page('/')
def main_page():
    # 각 사용자 세션(브라우저 탭)을 위한 로컬 상태
    state = {
        'view': 'menu',
        'language': 'ko',
        'game_mode': None,
        'deck': [],
        'score': 0,
        'timer_value': 30,
        'game_over_image': None,
    }

    def T(key: str) -> str:
        return TRANSLATIONS[state['language']].get(key, key)

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
    
    # 타이머는 게임 화면이 만들어질 때 설정됩니다.
    game_timer = ui.timer(1.0, lambda: None, active=False)

    def build_menu():
        with view_container.classes('gap-4 text-center'):
            with ui.row().classes('absolute top-5 right-5'):
                ui.button('🇰🇷', on_click=lambda: set_language('ko'), color='white' if state['language'] != 'ko' else 'blue').props('flat')
                ui.button('🇺🇸', on_click=lambda: set_language('en'), color='white' if state['language'] != 'en' else 'blue').props('flat')

            ui.label(T('game_title')).classes('text-5xl font-bold text-red-500 mb-4')
            ui.label(T('game_subtitle')).classes('text-lg text-gray-400 mb-8')
            ui.button(T('start_survival'), on_click=lambda: start_game('survival')).classes('px-7 py-2 text-lg')
            ui.button(T('start_time_attack'), on_click=lambda: start_game('time_attack')).classes('px-7 py-2 text-lg')
            ui.button(T('leaderboard'), on_click=show_leaderboard).classes('px-7 py-2 text-lg mt-4')

    def build_game():
        score_label = None
        timer_label = None

        def handle_timer_tick_local():
            state['timer_value'] -= 1
            if timer_label:
                timer_label.text = f"{T('time_left')}: {state['timer_value']}{T('seconds')}"
            if state['timer_value'] <= 0:
                game_over()

        game_timer.callback = handle_timer_tick_local

        with view_container.classes('w-full items-center justify-center gap-2'):
            with ui.row().classes('absolute top-5 right-5 items-center'):
                ui.button('🏆', on_click=show_leaderboard, color='yellow').classes('text-2xl')

            ui.label(T('game_title')).classes('text-5xl font-bold text-red-500 mb-2')
            score_label = ui.label(f"{T('score')}: {state['score']}").classes('text-3xl mb-2')
            timer_label = ui.label(f"{T('time_left')}: {state['timer_value']}{T('seconds')}").classes('text-4xl font-bold mb-4')

            with ui.card().classes('w-[350px] h-[500px] p-0 overflow-hidden relative'):
                if state['deck']:
                    ui.image(state['deck'][0]['url']).classes('w-full h-full object-cover')
                else:
                    ui.spinner(size='lg').classes('w-full h-full flex items-center justify-center')

            ui.label(T('instructions')).classes('text-lg text-gray-400 mt-4')
            
            with ui.row():
                ui.button(T('not_kimchi_btn'), on_click=lambda: handle_choice(False), color='blue').classes('p-4 text-xl')
                ui.button(T('is_kimchi_btn'), on_click=lambda: handle_choice(True), color='red').classes('p-4 text-xl')

    def build_game_over():
        img = state['game_over_image']
        with view_container.classes('gap-4 text-center'):
            ui.label(T('game_over')).classes('text-6xl font-bold text-red-600')
            ui.label(f"{T('final_score')}: {state['score']}").classes('text-4xl')

            if img and state['game_mode'] == 'survival':
                with ui.card().classes('w-[350px] h-fit'):
                    ui.image(img['url'])
                    with ui.card_section():
                        name_key = img['name']
                        is_kimchi = img['is_kimchi']
                        
                        data_source = KIMCHI_DATA if is_kimchi else NON_KIMCHI_DATA
                        food_info = data_source.get(name_key, {})

                        if state['language'] == 'en':
                            display_name = food_info.get('en_name', name_key)
                            display_desc = food_info.get('en_desc', '')
                        else:
                            display_name = name_key
                            display_desc = food_info.get('ko_desc', '')

                        ui.label(T('this_was').format(name=display_name)).classes('text-2xl font-bold')
                        ui.label(display_desc).classes('text-md mt-2')

            with ui.row().classes('items-center'):
                nickname_input = ui.input(placeholder=T('enter_nickname')).classes('w-48')
                ui.button(T('submit_score'), on_click=lambda: handle_score_submit(nickname_input.value, state['game_mode'])).classes('text-lg')
            
            ui.button(T('try_again'), on_click=lambda: start_game(state['game_mode'])).classes('px-7 py-2 text-lg')
            ui.button(T('back_to_menu'), on_click=show_menu).classes('px-7 py-2 text-lg mt-2')

    def build_leaderboard():
        with view_container.classes('gap-4 w-full items-center'):
            ui.label(T('leaderboard')).classes('text-5xl font-bold text-yellow-500')
            scores = load_scores()
            with ui.tabs().classes('w-96') as tabs:
                survival_tab = ui.tab(T('survival_tab'))
                time_attack_tab = ui.tab(T('time_attack_tab'))
            with ui.tab_panels(tabs, value=survival_tab).classes('w-96 bg-transparent'):
                with ui.tab_panel(survival_tab):
                    if not scores.get('survival'):
                        ui.label(T('no_scores')).classes('p-4 text-center')
                    else:
                        with ui.grid(columns=3).classes('w-full p-4 gap-y-2'):
                            ui.label(T('rank')).classes('font-bold'); ui.label(T('nickname')).classes('font-bold'); ui.label(T('score')).classes('font-bold place-self-end')
                            for i, s in enumerate(scores['survival'][:20]):
                                ui.label(f'{i+1}.'); ui.label(s.get('nickname', '')); ui.label(s.get('score', '')).classes('place-self-end')
                with ui.tab_panel(time_attack_tab):
                    if not scores.get('time_attack'):
                        ui.label(T('no_scores')).classes('p-4 text-center')
                    else:
                        with ui.grid(columns=3).classes('w-full p-4 gap-y-2'):
                            ui.label(T('rank')).classes('font-bold'); ui.label(T('nickname')).classes('font-bold'); ui.label(T('score')).classes('font-bold place-self-end')
                            for i, s in enumerate(scores['time_attack'][:20]):
                                ui.label(f'{i+1}.'); ui.label(s.get('nickname', '')); ui.label(s.get('score', '')).classes('place-self-end')
            ui.button(T('back_to_menu'), on_click=show_menu).classes('mt-4 px-7 py-2 text-lg')

    def update_view():
        view = state['view']
        view_container.clear()
        if view == 'menu': build_menu()
        elif view == 'game': build_game()
        elif view == 'gameover': build_game_over()
        elif view == 'leaderboard': build_leaderboard()

    async def start_game(mode: str):
        view_container.clear()
        with view_container:
            ui.spinner(size='lg')
            ui.label(T('loading_cards')).classes('text-3xl')
        
        await asyncio.sleep(0.1)
        state['game_mode'] = mode
        state['score'] = 0
        state['timer_value'] = 5 if mode == 'survival' else 30
        state['game_over_image'] = None
        state['deck'] = create_shuffled_deck()

        if not state['deck']:
            view_container.clear()
            with view_container:
                ui.label(T('no_images_found')).classes('text-2xl text-red-500')
                ui.label(T('check_assets_folder')).classes('text-lg')
                ui.button(T('back_to_menu'), on_click=show_menu)
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
        else:
            if state['game_mode'] == 'survival':
                game_over()
                return
            elif state['game_mode'] == 'time_attack':
                state['score'] = max(0, state['score'] - 2)
                ui.notify(T('wrong_answer_penalty'), color='negative')

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
        if state['timer_value'] <= 0:
            game_over()
        else:
            update_view() # This will re-render the game view, updating the timer label

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
            ui.notify(T('nickname_empty'), color='negative')
            return
        submit_score(nickname, state['score'], game_mode)
        await asyncio.sleep(0.1)
        show_leaderboard()
        
    def set_language(lang: str):
        state['language'] = lang
        update_view()

    update_view()

app.add_static_files('/app', str(APP_DIR))

if __name__ in {"__main__", "__mp_main__"}:
    # NOTE: 실제 프로덕션 환경에서는 이 비밀 키를 꼭 변경해야 해요!
    # 터미널에서 python3 -c "import secrets; print(secrets.token_hex(32))" 명령어로 안전한 키를 생성할 수 있어요.
    storage_secret = os.environ.get('STORAGE_SECRET', 'THIS_IS_A_SECRET_KEY_CHANGE_ME')
    port = int(os.environ.get('PORT', 8080))
    ui.run(title='이게 김치일까?', language='ko', reload=False, port=port, host='0.0.0.0', storage_secret=storage_secret)