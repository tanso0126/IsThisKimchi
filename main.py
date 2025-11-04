import asyncio
import json
import os
import random
from pathlib import Path

from nicegui import app, ui
from dotenv import load_dotenv

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
        'rank': '순위',
        'nickname': '닉네임',
        'survival_tab': '서바이벌',
        'time_attack_tab': '타임어택',
        'try_again': '다시 하기',
        'back_to_menu': '메뉴로 돌아가기',
        'no_scores': '아직 등록된 점수가 없어요.',
        'how_to_make_kimchi_btn': '김치 만드는 법 🥬',
        'how_to_make_kimchi_title': '김치, 어떻게 만들까?',
        'how_to_make_btn': '{kimchi_name} 만드는 법 🥬',
        'recipe_배추김치': '''🥬 배추김치 레시피\n\n📌 재료\n- 배추: 5포기  \n- 무: 2개  \n- 물: 10컵  \n- 굵은 소금: 2컵  \n- 미나리: 800g  \n- 갓: 500g  \n- 쪽파: 800g  \n- 생강: 100g  \n- 마늘: 10통  \n- 새우젓: 4컵  \n- 굴: 2컵  \n- 찹쌀풀: 4컵  \n- 고춧가루: 4컵  \n- 밤: 10개  \n- 통깨: 약간  \n- 소금: 적당량  \n- 설탕: 적당량  \n\n🥣 담그는 방법\n\n1. 배추 손질 및 절이기  \n   - 배추의 겉잎을 떼고 반으로 자른 후, 소금물에 절인다.  \n   - 절인 배추를 깨끗이 씻어 물기를 빼고 밑동을 잘라낸다.\n\n2. 야채 준비  \n   - 무는 4cm 길이로 채 썬다.  \n   - 미나리, 갓, 쪽파는 다듬어서 4cm 길이로 자른다.  \n   - 굴은 소금물에 흔들어 씻은 후 물기를 제거한다.\n\n3. 양념 만들기  \n   - 고춧가루는 따뜻한 물에 불려둔다.  \n   - 새우젓은 곱게 다지고, 마늘과 생강도 곱게 다진다.\n\n4. 속재료 섞기  \n   - 무채에 불린 고춧가루를 넣고 고루 버무린다.  \n   - 미나리, 쪽파, 갓, 다진 마늘과 생강, 새우젓, 설탕을 넣고 섞는다.  \n   - 소금으로 간을 맞추고 굴을 넣어 가볍게 버무린다.\n\n5. 배추에 양념 넣기  \n   - 절인 배추 잎 사이사이에 양념소를 넣고 겉잎으로 싸준다.\n\n6. 항아리에 담기  \n   - 양념을 넣은 배추를 항아리에 꼭꼭 눌러 담는다.  \n   - 우거지를 위에 덮고 돌로 눌러준다.''',
        'recipe_깍두기': '''🥬 깍두기 레시피\n\n📌 재료\n- 무: 2개  \n- 굴: 1컵 반  \n- 고춧가루: 1컵  \n- 새우젓: 반 컵  \n- 쪽파: 100g  \n- 마늘: 4통  \n- 생강: 30g  \n- 소금: 약간  \n- 통깨: 약간  \n\n🥣 담그는 방법\n1. 무는 2cm 크기의 네모로 썬다.  \n2. 굴은 엷은 소금물에 씻어 자게미를 제거한 후 물기를 뺀다.  \n3. 고춧가루는 따뜻한 물에 불린다.  \n4. 쪽파는 깨끗이 씻어 2.5cm 길이로 썰고, 새우젓은 곱게 다진다.  \n   마늘과 생강도 곱게 다져 놓는다.  \n5. 무에 불린 고춧가루를 넣고 고루 버무려 물을 들인다.  \n6. 갓, 파, 생강, 마늘, 통깨, 새우젓, 소금을 넣어 버무린다.  \n7. 마지막으로 굴을 넣어 다시 버무린 후 항아리에 담는다.''',
        'recipe_파김치': '''🥬 파김치 레시피\n\n📌 재료\n- 쪽파: 2단  \n- 멸치젓: 1컵  \n- 고춧가루: 1컵  \n- 마늘: 2통  \n- 생강: 1톨  \n- 설탕: 1큰술  \n- 통깨: 2큰술  \n- 소금: 약간  \n\n🥣 담그는 방법\n1. 쪽파는 다듬어 씻은 후 물기를 뺀다.  \n2. 멸치젓에 같은 양의 물을 넣어 끓인 후 면보에 걸러 국물을 낸다.  \n3. 파에 멸치젓국을 부어 1시간 정도 절인 뒤 국물을 따른다.  \n4. 따라낸 멸치젓국에 고춧가루, 마늘, 생강, 찹쌀풀, 소금을 넣어 양념을 만든다.  \n5. 절여진 파에 고춧가루, 마늘, 생강, 설탕, 통깨를 넣어 버무린 후 소금으로 간을 맞춘다.  \n6. 파를 몇 가닥씩 모아 묶어 항아리에 차곡차곡 담는다.''',
        'recipe_백김치': '''🥬 백김치 레시피\n\n📌 재료\n- 배추: 5포기  \n- 무: 1개  \n- 물: 10컵  \n- 굵은 소금: 2컵  \n- 미나리: ½단  \n- 갓: ½단  \n- 실파: ½단  \n- 배: 1개  \n- 밤: 5개  \n- 대추: 5개  \n- 실고추: 약간  \n- 표고버섯: 5장  \n- 석이버섯: 5장  \n- 잣: 2큰술  \n- 소금: 2큰술  \n- 설탕: 1컵  \n- 대파: 3통  \n- 마늘: 1톨  \n- 국물용 배: 1개  \n- 국물용 물: 5컵  \n- 국물용 소금: ½컵  \n\n🥣 담그는 방법\n1. 배추를 반으로 자르고 소금물에 5~6시간 절인 후 씻어 밑동을 자른다.  \n2. 무는 4cm 길이로 채 썬다.  \n3. 실파, 미나리, 갓은 4cm로 썬다.  \n4. 배, 밤, 대추는 채 썰고 실고추는 짧게 자른다.  \n5. 표고와 석이버섯은 불려 채 썬다.  \n6. 대파는 어슷썰고 마늘과 생강은 다진다.  \n7. 무, 배, 밤, 대추채에 실고추를 넣어 버무린 후 미나리, 실파, 갓, 버섯류, 잣, 대파, 마늘, 생강, 설탕을 넣고 소금으로 간한다.  \n8. 배춧잎 사이에 속을 넣고 겉잎으로 싸서 항아리에 담는다.  \n9. 배즙과 물, 소금을 섞어 국물을 만들어 붓는다.''',
        'recipe_총각김치': '''🥬 총각김치 레시피\n\n📌 재료\n- 알타리무: 2단  \n- 굵은 소금: 1컵  \n- 고춧가루: 1컵  \n- 멸치젓: ½컵  \n- 새우젓: ½컵  \n- 찹쌀풀: 1컵  \n- 대파: 2대  \n- 마늘: 3통  \n- 생강: 2톨  \n- 설탕: 1큰술  \n\n🥣 담그는 방법\n1. 총각무는 잔털을 떼고 다듬어 씻은 후 소금을 뿌려 2시간 절인다.  \n2. 절인 무를 씻어 물기를 뺀다.  \n3. 대파는 어슷썰고, 마늘과 생강은 다진다.  \n4. 멸치젓에 같은 양의 물을 넣고 끓여 체에 거른다.  \n5. 새우젓은 다지고, 물 1컵에 찹쌀가루 1큰술을 넣어 끓인다.  \n6. 멸치젓국에 고춧가루를 섞고, 대파·마늘·생강·새우젓·설탕을 넣는다.  \n7. 절여진 무에 양념을 넣어 버무리고 몇 가닥씩 모아 항아리에 담는다.''',
        'recipe_갓김치': '''🥬 갓김치 레시피\n\n📌 재료\n- 갓: 1kg  \n- 실파: 500g  \n- 굵은 소금: ½컵  \n- 고춧가루: 2컵  \n- 멸치젓: 1컵 반  \n- 마늘: 2통  \n- 생강: 1통  \n- 통깨: 2큰술  \n- 실고추: 약간  \n\n🥣 담그는 방법\n1. 갓은 줄기가 연한 것으로 골라 다듬고 소금을 뿌려 30분 절인다.  \n2. 실파를 다듬어 씻고 마늘과 생강은 다진다.  \n3. 멸치젓에 같은 양의 물을 넣어 끓인 후 걸러 국물을 만든다.  \n4. 그 국물에 고춧가루를 불려 마늘, 생강, 통깨, 실고추를 넣어 양념을 만든다.  \n5. 절인 갓을 씻어 물기를 뺀 뒤 양념으로 버무려 항아리에 담는다.  \n6. 우거지를 덮고 돌로 눌러 뚜껑을 덮는다.''',
        'recipe_부추김치': '''🥬 부추김치 레시피\n\n📌 재료\n- 부추: 1kg  \n- 멸치젓: ½컵  \n- 고춧가루: 1컵  \n- 마늘: 1통  \n- 생강: 1톨  \n- 설탕: 1큰술  \n- 통깨: 약간  \n\n🥣 담그는 방법\n1. 부추는 깨끗이 다듬어 씻어 물기를 뺀다.  \n2. 부추를 반으로 자르고 달인 멸치젓국을 켜켜로 뿌려 20분 절인다.  \n3. 중간에 위아래를 뒤집어준다.  \n4. 마늘과 생강은 다지고, 불린 고춧가루에 다진 마늘, 생강, 설탕, 통깨를 섞는다.  \n5. 절인 부추에 양념을 넣어 살살 버무린 후 항아리에 담는다.''',
        'recipe_나박김치': '''🥬 나박김치 레시피\n\n📌 재료\n- 배추: 1포기  \n- 무: 1개  \n- 대파: 1대  \n- 마늘: 5쪽  \n- 생강: 1쪽  \n- 붉은 고추: 2개  \n- 풋고추: 2개  \n- 소금: 3큰술  \n- 설탕: 1큰술  \n- 물: 10컵  \n\n🥣 담그는 방법\n1. 배추는 먹기 좋은 크기로 썰고 무는 얇게 썬다.  \n2. 대파는 어슷썰고 고추는 어슷하게 썬다.  \n3. 마늘과 생강은 얇게 저민다.  \n4. 물에 소금과 설탕을 넣고 녹여 김치국물을 만든다.  \n5. 준비한 재료를 김치통에 넣고 국물을 붓는다.  \n6. 상온에서 하루 숙성시킨 뒤 냉장 보관한다.''',
        'recipe_무생채': '''🥬 무생채 레시피\n\n📌 재료\n- 무: 1개  \n- 고춧가루: 3큰술  \n- 식초: 2큰술  \n- 설탕: 1큰술  \n- 소금: 1작은술  \n- 다진 마늘: 1큰술  \n- 통깨: 약간  \n\n🥣 담그는 방법\n1. 무는 껍질을 벗기고 가늘게 채 썬다.  \n2. 채 썬 무에 소금을 넣고 10분 정도 절인다.  \n3. 절인 무의 물기를 가볍게 짜고, 고춧가루, 식초, 설탕, 다진 마늘을 넣고 버무린다.  \n4. 통깨를 넣고 마지막으로 간을 맞춘다.  \n5. 바로 먹거나 하루 정도 냉장 숙성해도 좋다.''',
        'recipe_열무김치': '''🥬 열무김치 레시피\n\n📌 재료\n- 열무: 2단  \n- 굵은 소금: 1컵  \n- 고춧가루: 1컵  \n- 새우젓: 4큰술  \n- 마늘: 5쪽  \n- 생강: 1쪽  \n- 쪽파: 100g  \n- 설탕: 1큰술  \n- 통깨: 약간  \n\n🥣 담그는 방법\n1. 열무는 깨끗이 다듬어 씻고, 소금을 뿌려 1시간 정도 절인다.  \n2. 절인 열무를 씻어 물기를 뺀다.  \n3. 마늘과 생강을 다지고, 새우젓, 고춧가루, 설탕을 섞어 양념을 만든다.  \n4. 쪽파를 썰어 넣고 열무와 함께 버무린다.  \n5. 항아리나 김치통에 담고 실온에서 하루 숙성 후 냉장 보관한다.''',
        'recipe_오이소박이': '''🥬 오이소박이 레시피\n\n📌 재료\n- 오이: 5개  \n- 굵은 소금: 3큰술  \n- 부추: 200g  \n- 당근: ½개  \n- 쪽파: 50g  \n- 마늘: 5쪽  \n- 생강: 1쪽  \n- 고춧가루: 5큰술  \n- 새우젓: 2큰술  \n- 설탕: 1큰술  \n- 통깨: 약간  \n\n🥣 담그는 방법\n1. 오이는 깨끗이 씻어 길게 4등분으로 칼집을 낸다.  \n2. 굵은 소금을 뿌려 30분 정도 절인 후 헹구어 물기를 뺀다.  \n3. 부추와 당근, 쪽파는 4cm 길이로 썬다.  \n4. 마늘과 생강은 다지고, 고춧가루, 새우젓, 설탕을 섞어 양념을 만든다.  \n5. 부추, 당근, 쪽파를 양념에 버무린 후 오이 속에 채워 넣는다.  \n6. 항아리나 김치통에 담아 하루 숙성 후 냉장 보관한다.''',
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
        'rank': 'Rank',
        'nickname': 'Nickname',
        'survival_tab': 'Survival',
        'time_attack_tab': 'Time Attack',
        'try_again': 'Try Again',
        'back_to_menu': 'Back to Menu',
        'no_scores': 'No scores yet.',
        'no_images_found': 'Oops! Image cards not found!',
        'check_assets_folder': 'Please check if the `app/src/assets` folder exists.',
        'wrong_answer_penalty': 'Wrong! -2 points! 😭',
        'how_to_make_kimchi_title': 'How to Make Kimchi',
        'how_to_make_btn': 'How to make {kimchi_name} 🥬',
        'recipe_배추김치': '''🇺🇸 Baechu Kimchi Recipe (Napa Cabbage Kimchi)\n\n📌 Ingredients\n- Napa cabbage: 5 heads  \n- Korean radish: 2 pieces  \n- Water: 10 cups  \n- Coarse salt: 2 cups  \n- Water dropwort (Minari): 800g  \n- Mustard leaves: 500g  \n- Green onions: 800g  \n- Ginger: 100g  \n- Garlic: 10 bulbs  \n- Salted shrimp (Saeujeot): 4 cups  \n- Oysters: 2 cups  \n- Glutinous rice paste: 4 cups  \n- Red pepper powder: 4 cups  \n- Chestnuts: 10  \n- Sesame seeds: a little  \n- Salt: to taste  \n- Sugar: to taste  \n\n🥣 Instructions\n\n1. Prepare and brine the cabbage  \n   - Remove the outer leaves of the cabbage, cut in half, and soak in salt water.  \n   - Rinse the cabbage thoroughly, drain the water, and cut off the root ends.\n\n2. Prepare the vegetables  \n   - Julienne the radish into 4 cm long strips.  \n   - Trim and cut water dropwort, mustard leaves, and green onions into 4 cm lengths.  \n   - Rinse the oysters in salt water and drain.\n\n3. Make the seasoning  \n   - Soak the red pepper powder in warm water.  \n   - Mince the salted shrimp, garlic, and ginger.\n\n4. Mix the stuffing ingredients  \n   - Mix the soaked red pepper powder with the julienned radish.  \n   - Add water dropwort, green onions, mustard leaves, minced garlic and ginger, salted shrimp, and sugar.  \n   - Season with salt and gently mix in the oysters.\n\n5. Stuff the cabbage  \n   - Place the seasoning between each layer of cabbage leaves, and wrap the cabbage with its outer leaves.\n\n6. Ferment the kimchi  \n   - Pack the stuffed cabbages tightly into a container or jar.  \n   - Cover with cabbage leaves (ugeoji), press down with a weight or stone.''',
        'recipe_깍두기': '''🇺🇸 Kkakdugi (Cubed Radish Kimchi)\n\n📌 Ingredients\n- Radish: 2 pieces  \n- Oysters: 1½ cups  \n- Red pepper powder: 1 cup  \n- Salted shrimp: ½ cup  \n- Green onions: 100g  \n- Garlic: 4 cloves  \n- Ginger: 30g  \n- Salt: to taste  \n- Sesame seeds: a little  \n\n🥣 Instructions\n1. Cut the radish into 2cm cubes.  \n2. Rinse the oysters lightly in salt water, remove impurities, and drain.  \n3. Soak red pepper powder in warm water.  \n4. Chop the green onions into 2.5cm pieces. Mince salted shrimp, garlic, and ginger.  \n5. Mix the soaked red pepper powder with the cubed radish evenly.  \n6. Add green onions, garlic, ginger, sesame seeds, salted shrimp, and salt, then mix well.  \n7. Add oysters last, mix gently, and store in a jar.''',
        'recipe_파김치': '''🇺🇸 Pa Kimchi (Green Onion Kimchi)\n\n📌 Ingredients\n- Green onions: 2 bunches  \n- Anchovy sauce: 1 cup  \n- Red pepper powder: 1 cup  \n- Garlic: 2 cloves  \n- Ginger: 1 piece  \n- Sugar: 1 tbsp  \n- Sesame seeds: 2 tbsp  \n- Salt: to taste  \n\n🥣 Instructions\n1. Trim and wash green onions, then drain.  \n2. Boil anchovy sauce with equal water and strain through cloth.  \n3. Pour over green onions to brine for 1 hour, then drain.  \n4. Mix anchovy broth with red pepper powder, garlic, ginger, and salt to make seasoning.  \n5. Mix brined onions with seasoning, sugar, and sesame seeds.  \n6. Tie in small bundles and pack in a jar.''',
        'recipe_백김치': '''🇺🇸 Baek Kimchi (White Kimchi)\n\n📌 Ingredients\n- Napa cabbage: 5 heads  \n- Radish: 1  \n- Water: 10 cups  \n- Coarse salt: 2 cups  \n- Water dropwort: ½ bunch  \n- Mustard leaves: ½ bunch  \n- Green onions: ½ bunch  \n- Pear: 1  \n- Chestnuts: 5  \n- Jujubes: 5  \n- Red chili threads: a little  \n- Shiitake mushrooms: 5  \n- Black mushrooms: 5  \n- Pine nuts: 2 tbsp  \n- Salt: 2 tbsp  \n- Sugar: 1 cup  \n- Leeks: 3 stalks  \n- Garlic: 1 clove  \n- For brine: 1 pear, 5 cups water, ½ cup salt  \n\n🥣 Instructions\n1. Cut cabbage in half and brine in salt water for 5–6 hours. Rinse and trim roots.  \n2. Slice radish into 4cm strips.  \n3. Cut greens into 4cm lengths.  \n4. Julienne pear, chestnuts, and jujubes.  \n5. Soak and slice mushrooms.  \n6. Slice leeks diagonally; mince garlic and ginger.  \n7. Mix all filling ingredients with salt and sugar.  \n8. Stuff between cabbage leaves and wrap with outer leaves.  \n9. Combine pear juice, water, and salt for brine and pour over kimchi.''',
        'recipe_총각김치': '''🇺🇸 Chonggak Kimchi (Young Radish Kimchi)\n\n📌 Ingredients\n- Young radishes: 2 bunches  \n- Coarse salt: 1 cup  \n- Red pepper powder: 1 cup  \n- Anchovy sauce: ½ cup  \n- Salted shrimp: ½ cup  \n- Glutinous rice paste: 1 cup  \n- Leeks: 2  \n- Garlic: 3 cloves  \n- Ginger: 2 pieces  \n- Sugar: 1 tbsp  \n\n🥣 Instructions\n1. Clean and trim young radishes, remove root hairs, and brine with salt for 2 hours.  \n2. Rinse and drain.  \n3. Slice leeks; mince garlic and ginger.  \n4. Boil anchovy sauce with equal water and strain.  \n5. Mince salted shrimp; make glutinous rice paste.  \n6. Mix anchovy broth with red pepper powder, garlic, ginger, shrimp, and sugar.  \n7. Combine with radishes, roll into small bundles, and store in a jar.''',
        'recipe_갓김치': '''🇺🇸 Gat Kimchi (Mustard Leaf Kimchi)\n\n📌 Ingredients\n- Mustard leaves: 1kg  \n- Green onions: 500g  \n- Coarse salt: ½ cup  \n- Red pepper powder: 2 cups  \n- Anchovy sauce: 1½ cups  \n- Garlic: 2 cloves  \n- Ginger: 1 piece  \n- Sesame seeds: 2 tbsp  \n- Red chili threads: a little  \n\n🥣 Instructions\n1. Trim mustard leaves, sprinkle salt, and brine for 30 minutes.  \n2. Prepare and wash green onions; mince garlic and ginger.  \n3. Boil anchovy sauce with equal water, strain, and soak red pepper powder in it.  \n4. Add garlic, ginger, sesame seeds, and red chili threads to make seasoning.  \n5. Rinse mustard leaves, drain, mix with seasoning, and pack in a jar.  \n6. Cover with outer leaves, press down with a stone, and close the lid.''',
        'recipe_부추김치': '''🇺🇸 Buchu Kimchi (Chive Kimchi)\n\n📌 Ingredients\n- Chives: 1kg  \n- Anchovy sauce: ½ cup  \n- Red pepper powder: 1 cup  \n- Garlic: 1 bulb  \n- Ginger: 1 piece  \n- Sugar: 1 tbsp  \n- Sesame seeds: a little  \n\n🥣 Instructions\n1. Clean and drain chives.  \n2. Cut in half, layer with boiled anchovy broth, and brine for 20 minutes.  \n3. Turn occasionally while brining.  \n4. Mince garlic and ginger. Mix with soaked red pepper powder, sugar, and sesame seeds.  \n5. Gently mix the seasoned paste with chives and pack into a jar to ferment.''',
        'recipe_나박김치': '''🇺🇸 Nabak Kimchi (Water Kimchi with Radish and Cabbage)\n\n📌 Ingredients\n- Napa cabbage: 1 head  \n- Radish: 1  \n- Green onion: 1 stalk  \n- Garlic: 5 cloves  \n- Ginger: 1 piece  \n- Red chili peppers: 2  \n- Green chili peppers: 2  \n- Salt: 3 tbsp  \n- Sugar: 1 tbsp  \n- Water: 10 cups  \n\n🥣 Instructions\n1. Cut cabbage into bite-size pieces and slice radish thinly.  \n2. Slice green onions and peppers diagonally.  \n3. Slice garlic and ginger thinly.  \n4. Dissolve salt and sugar in water to make brine.  \n5. Combine all ingredients in a jar and pour in the brine.  \n6. Ferment at room temperature for a day, then refrigerate.''',
        'recipe_무생채': '''🇺🇸 Mu Saengchae (Seasoned Radish Salad)\n\n📌 Ingredients\n- Radish: 1  \n- Red pepper powder: 3 tbsp  \n- Vinegar: 2 tbsp  \n- Sugar: 1 tbsp  \n- Salt: 1 tsp  \n- Minced garlic: 1 tbsp  \n- Sesame seeds: a little  \n\n🥣 Instructions\n1. Peel and julienne the radish thinly.  \n2. Sprinkle salt and let sit for 10 minutes.  \n3. Squeeze out excess water and mix with red pepper powder, vinegar, sugar, and garlic.  \n4. Add sesame seeds and adjust seasoning.  \n5. Serve fresh or chill for a day before serving.''',
        'recipe_열무김치': '''🇺🇸 Yeolmu Kimchi (Young Summer Radish Kimchi)\n\n📌 Ingredients\n- Young radish greens: 2 bunches  \n- Coarse salt: 1 cup  \n- Red pepper powder: 1 cup  \n- Salted shrimp: 4 tbsp  \n- Garlic: 5 cloves  \n- Ginger: 1 piece  \n- Green onions: 100g  \n- Sugar: 1 tbsp  \n- Sesame seeds: a little  \n\n🥣 Instructions\n1. Clean and trim young radish greens. Sprinkle salt and let sit for 1 hour.  \n2. Rinse and drain.  \n3. Mince garlic and ginger, then mix with red pepper powder, salted shrimp, and sugar.  \n4. Add chopped green onions and mix with the radish greens.  \n5. Store in a jar, ferment for a day at room temperature, then refrigerate.''',
        'recipe_오이소박이': '''🇺🇸 Oi Sobagi (Stuffed Cucumber Kimchi)\n\n📌 Ingredients\n- Cucumbers: 5  \n- Coarse salt: 3 tbsp  \n- Chives: 200g  \n- Carrot: ½  \n- Green onions: 50g  \n- Garlic: 5 cloves  \n- Ginger: 1 piece  \n- Red pepper powder: 5 tbsp  \n- Salted shrimp: 2 tbsp  \n- Sugar: 1 tbsp  \n- Sesame seeds: a little  \n\n🥣 Instructions\n1. Wash cucumbers and make 4 lengthwise slits, keeping one end intact.  \n2. Sprinkle salt and brine for 30 minutes, then rinse and drain.  \n3. Cut chives, carrot, and green onions into 4cm pieces.  \n4. Mince garlic and ginger, then mix with red pepper powder, salted shrimp, and sugar.  \n5. Combine the vegetables with seasoning and stuff into the cucumbers.  \n6. Store in a container and ferment for one day before refrigerating.''',
    }
}

KIMCHI_DATA = {    '배추김치': {
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
    SCORE_FILE.parent.mkdir(parents=True, exist_ok=True) 
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


# --- 4. UI 뷰 정의 ---

@ui.page('/')
async def main_page():
    # 앱의 전역 저장소를 사용하여 상태 관리
    app.storage.general.setdefault('language', 'ko')

    state = {
        'view': 'menu',
        'game_mode': None,
        'deck': [],
        'score': 0,
        'timer_value': 0,
        'game_over_image': None,
    }

    game_card_ui_element = None
    score_label_ui_element = None
    timer_label_ui_element = None

    def T(key: str) -> str:
        return TRANSLATIONS[app.storage.general['language']].get(key, key)

    def set_language(lang: str):
        if lang in ['ko', 'en']:
            app.storage.general['language'] = lang
            update_view()

    async def load_language_and_update():
        # 이 함수는 이제 필요 없지만, 혹시 모를 다른 용도를 위해 남겨둘 수 있습니다.
        # 현재는 set_language를 통해 상태가 즉시 반영되므로 비워둡니다.
        pass
    async def handle_timer_tick_callback():
        """게임 타이머 콜백: 시간 감소 및 UI 업데이트."""
        nonlocal timer_label_ui_element
        if state['view'] == 'game': # 게임 화면일 때만 타이머 작동
            state['timer_value'] -= 1
            if timer_label_ui_element: # 엘리먼트가 존재하면 업데이트
                timer_label_ui_element.text = f"{T('time_left')}: {state['timer_value']}{T('seconds')}"
            
            if state['timer_value'] <= 0:
                game_timer.deactivate() # 타이머 즉시 정지
                await game_over() # 게임 오버 처리 (async)    
    
    game_timer = ui.timer(1.0, handle_timer_tick_callback, active=False)

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

    def build_menu():
        view_container.clear()
        with view_container.classes('gap-4 text-center'):
            with ui.row().classes('absolute top-5 right-5'):
                ui.button('🇰🇷', on_click=lambda: set_language('ko'), color='white' if app.storage.general['language'] != 'ko' else 'blue').props('flat') # type: ignore
                ui.button('🇺🇸', on_click=lambda: set_language('en'), color='white' if app.storage.general['language'] != 'en' else 'blue').props('flat') # type: ignore

            ui.label(T('game_title')).classes('text-5xl font-bold text-red-500 mb-4')
            ui.label(T('game_subtitle')).classes('text-lg text-gray-400 mb-8')
            ui.button(T('start_survival'), on_click=lambda: start_game('survival')).classes('px-7 py-2 text-lg')
            ui.button(T('start_time_attack'), on_click=lambda: start_game('time_attack')).classes('px-7 py-2 text-lg')
            ui.button(T('leaderboard'), on_click=show_leaderboard).classes('px-7 py-2 text-lg mt-4')

    def build_game():
        nonlocal game_card_ui_element, score_label_ui_element, timer_label_ui_element
        view_container.clear() # 이전 뷰 클리어
        with view_container.classes('w-full items-center justify-center gap-2'):
            with ui.row().classes('absolute top-5 right-5 items-center'):
                ui.button('🏆', on_click=show_leaderboard, color='yellow').classes('text-2xl')

            ui.label(T('game_title')).classes('text-5xl font-bold text-red-500 mb-2')
            # 레이블 엘리먼트 생성
            score_label_ui_element = ui.label(f"{T('score')}: {state['score']}").classes('text-3xl mb-2')
            timer_label_ui_element = ui.label(f"{T('time_left')}: {state['timer_value']}{T('seconds')}").classes('text-4xl font-bold mb-4')

            with ui.card().classes('w-[350px] h-[500px] p-0 overflow-hidden relative'):
                if state['deck']:
                    # 이미지 엘리먼트 생성
                    game_card_ui_element = ui.image(state['deck'][0]['url']).classes('w-full h-full object-cover')
                else:
                    # 덱이 비었을 경우 스피너 표시
                    game_card_ui_element = ui.spinner(size='lg').classes('w-full h-full flex items-center justify-center')
            
            ui.label(T('instructions')).classes('text-lg text-gray-400 mt-4')
            
            with ui.row():
                ui.button(T('not_kimchi_btn'), on_click=lambda: handle_choice(False), color='blue').classes('p-4 text-xl')
                ui.button(T('is_kimchi_btn'), on_click=lambda: handle_choice(True), color='red').classes('p-4 text-xl')

    async def handle_choice(is_kimchi_choice: bool):
        nonlocal game_card_ui_element, score_label_ui_element, timer_label_ui_element # nonlocal 선언 추가
        if not state['deck']: return

        card = state['deck'][0]
        is_correct = (card['is_kimchi'] == is_kimchi_choice)

        if is_correct:
            state['score'] += 1
            if state['game_mode'] == 'survival':
                state['timer_value'] = 5 # 서바이벌 모드에서 정답 시 타이머 리셋
        else:
            if state['game_mode'] == 'survival':
                await game_over() # 서바이벌 모드에서 오답 시 게임 오버
                return
            elif state['game_mode'] == 'time_attack':
                state['score'] = max(0, state['score'] - 2) # 타임어택 모드에서 오답 시 -2점
                ui.notify(T('wrong_answer_penalty'), color='negative')

        # 점수 UI 업데이트
        if score_label_ui_element:
            score_label_ui_element.text = f"{T('score')}: {state['score']}"

        state['deck'].pop(0) # 현재 카드 제거

        if len(state['deck']) < 5:
            state['deck'].extend(create_shuffled_deck()) # 덱이 부족하면 카드 추가
        
        # 다음 카드 이미지 업데이트
        if state['deck'] and game_card_ui_element:
            if isinstance(game_card_ui_element, ui.image): # 현재 엘리먼트가 ui.image 일 경우
                game_card_ui_element.set_source(state['deck'][0]['url']) # type: ignore
            
        # 서바이벌 모드에서 타이머값 변경 시 UI 업데이트
        if state['game_mode'] == 'survival' and timer_label_ui_element:
            timer_label_ui_element.text = f"{T('time_left')}: {state['timer_value']}{T('seconds')}"

    async def game_over():
        game_timer.deactivate()
        if state['deck']:
            state['game_over_image'] = state['deck'][0] # 게임 오버 화면에 표시할 마지막 카드 정보 저장
        state['view'] = 'gameover'
        update_view() # 게임 오버 화면으로 전환

    def build_game_over():
        view_container.clear()
        img = state['game_over_image']
        with view_container.classes('gap-4 text-center'):
            ui.label(T('game_over')).classes('text-6xl font-bold text-red-600')
            ui.label(f"{T('final_score')}: {state['score']}").classes('text-4xl') 

            if img and state['game_mode'] == 'survival': # 서바이벌 모드에서만 오답 이미지 설명
                with ui.card().classes('w-[350px] h-fit'):
                    ui.image(img['url'])
                    with ui.card_section():
                        name_key = img['name']
                        is_kimchi = img['is_kimchi']
                        
                        data_source = KIMCHI_DATA if is_kimchi else NON_KIMCHI_DATA
                        food_info = data_source.get(name_key, {})

                        if app.storage.general['language'] == 'en':
                            display_name = food_info.get('en_name', name_key)
                            display_desc = food_info.get('en_desc', '')
                        else:
                            display_name = name_key
                            display_desc = food_info.get('ko_desc', '')

                        ui.label(T('this_was').format(name=display_name)).classes('text-2xl font-bold')
                        ui.label(display_desc).classes('text-md mt-2')

            with ui.row().classes('items-center'):
                nickname_input = ui.input(placeholder=T('enter_nickname')).classes('w-48')
                ui.button(T('submit_score'), on_click=lambda: handle_score_submit(nickname_input.value)).classes('text-lg')
            
            ui.button(T('try_again'), on_click=lambda: start_game(state['game_mode'])).classes('px-7 py-2 text-lg')
            # 김치 만드는 법 버튼 (김치일 경우에만 표시)
            if img and img['is_kimchi']:
                kimchi_name_ko = img['name']
                
                if app.storage.general['language'] == 'en':
                    kimchi_display_name = KIMCHI_DATA.get(kimchi_name_ko, {}).get('en_name', kimchi_name_ko)
                else:
                    kimchi_display_name = kimchi_name_ko

                button_text = T('how_to_make_btn').format(kimchi_name=kimchi_display_name)
                ui.button(button_text, on_click=lambda k=kimchi_name_ko: ui.navigate.to(f'/how-to-make-kimchi/{k}')).classes('px-7 py-2 text-lg mt-2 bg-green-500')
            ui.button(T('back_to_menu'), on_click=show_menu).classes('px-7 py-2 text-lg mt-2')

    def build_leaderboard():
        view_container.clear()
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
        # state['view']에 따라 현재 뷰 컨테이너를 지우고 새로운 뷰를 그리기
        # view_container.clear()는 각 build_xxx 함수에서 호출(혹은 직접 처리)되므로, 여기서 중복 호출하지 않음
        if state['view'] == 'menu': build_menu()
        elif state['view'] == 'game': build_game()
        elif state['view'] == 'gameover': build_game_over()
        elif state['view'] == 'leaderboard': build_leaderboard()

    async def start_game(mode: str):
        view_container.clear()
        with view_container:
            ui.spinner(size='lg') # type: ignore
            ui.label(T('loading_cards')).classes('text-3xl')
        
        await asyncio.sleep(0.1) # 스피너 보이게 딜레이
        state['game_mode'] = mode
        state['score'] = 0
        state['timer_value'] = 5 if mode == 'survival' else 30 # 게임 모드에 따라 타이머 초기화
        state['game_over_image'] = None # 게임 오버 이미지 초기화
        state['deck'] = create_shuffled_deck() # 새로운 카드 덱 생성

        if not state['deck']:
            # 이미지 파일을 찾지 못했을 경우 
            view_container.clear()
            with view_container:
                ui.label(T('no_images_found')).classes('text-2xl text-red-500')
                ui.label(T('check_assets_folder')).classes('text-lg')
                ui.button(T('back_to_menu'), on_click=show_menu)
            return

        state['view'] = 'game'
        update_view() # 게임 뷰 그리기
        game_timer.activate() # 타이머 활성화

    async def handle_score_submit(nickname: str):
        if not nickname.strip():
            ui.notify(T('nickname_empty'), color='negative')
            return
        submit_score(nickname, state['score'], state['game_mode'])
        await asyncio.sleep(0.1) # 점수 저장 딜레이
        show_leaderboard()

    def show_leaderboard():
        game_timer.deactivate()
        state['view'] = 'leaderboard'
        update_view()

    def show_menu():
        game_timer.deactivate()
        state['view'] = 'menu'
        update_view()

    update_view()


# --- 5. 김치 만드는 법 페이지 ---

@ui.page('/how-to-make-kimchi/{kimchi_name}')
async def how_to_make_kimchi_page(kimchi_name: str):
    app.storage.general.setdefault('language', 'ko')

    def T(key: str) -> str:
        return TRANSLATIONS[app.storage.general['language']].get(key, key)
        
    def set_language(lang: str):
        if lang in ['ko', 'en']:
            app.storage.general['language'] = lang
        page_content.clear()
        build_recipe_page()

    ui.add_head_html('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            body {
                font-family: 'Noto Sans KR', sans-serif;
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
        </style>
    ''')
    ui.dark_mode().enable()

    page_content = ui.column().classes('w-full items-center justify-center p-8')

    def build_recipe_page():
        with page_content:
            with ui.row().classes('absolute top-5 right-5'):
                ui.button('🇰🇷', on_click=lambda: set_language('ko'), color='white' if app.storage.general['language'] != 'ko' else 'blue').props('flat')
                ui.button('🇺🇸', on_click=lambda: set_language('en'), color='white' if app.storage.general['language'] != 'en' else 'blue').props('flat')

            if app.storage.general['language'] == 'en':
                kimchi_display_name = KIMCHI_DATA.get(kimchi_name, {}).get('en_name', kimchi_name)
            else:
                kimchi_display_name = kimchi_name
            
            ui.label(T('how_to_make_kimchi_title').format(kimchi_name=kimchi_display_name)).classes('text-5xl font-bold text-green-500 mb-8')
            
            recipe_key = f"recipe_{kimchi_name}"
            recipe_content = T(recipe_key) if recipe_key in TRANSLATIONS[app.storage.general['language']] else "Recipe not found for this kimchi."

            with ui.card().classes('w-full max-w-4xl bg-white/5'):
                with ui.card_section():
                    ui.markdown(recipe_content).classes('text-gray-300 text-left')

            ui.button(T('back_to_menu'), on_click=lambda: ui.navigate.to('/')).classes('mt-8 px-7 py-2 text-lg')
            
    build_recipe_page()


# --- 6. 앱 전역 설정 ---

app.add_static_files('/app', str(APP_DIR))

if __name__ in {"__main__", "__mp_main__"}:
    load_dotenv()
    # .env 파일에서 키를 로드
    storage_secret = os.environ.get('STORAGE_SECRET')
    if not storage_secret:
        raise ValueError("STORAGE_SECRET이 .env 파일에 설정되지 않았습니다!")
    port = int(os.environ.get('PORT', 8080))
    ui.run(title='이게 김치일까?', language='ko', reload=False, port=port, host='0.0.0.0', storage_secret=storage_secret)