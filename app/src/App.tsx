import React, { useState, useEffect, useCallback } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import axios from 'axios';
import './App.css';

// --- API 기본 URL ---
const API_URL = 'http://localhost:3000';

// --- 데이터 타입 정의 ---
interface Image {
  id: string;
  name: string;
  url: string;
  isKimchi: boolean;
  description: string;
  importFunc?: () => Promise<ImageModule>;
}

interface ImageModule {
  default: string;
}

interface Score {
  nickname: string;
  score: number;
}

// --- Helper function for proper shuffling (Fisher-Yates Algorithm) ---
function shuffleArray<T>(array: T[]): T[] {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
}

// --- 데이터 로딩 및 처리 ---
const kimchiModules = import.meta.glob('/src/assets/김치/**/*.{[jJ][pP][gG],[jJ][pP][eE][gG],[pP][nN][gG],[gG][iI][fF]}') as Record<string, () => Promise<ImageModule>>;
const nonKimchiModules = import.meta.glob('/src/assets/노김치/**/*.{[jJ][pP][gG],[jJ][pP][eE][gG],[pP][nN][gG],[gG][iI][fF]}') as Record<string, () => Promise<ImageModule>>;

const kimchiDescriptions: Record<string, string> = {
  '배추김치': '한국의 가장 대표적인 김치로, 소금에 절인 배추에 무, 파, 고춧가루, 마늘, 생강 등의 양념을 버무려 만듭니다.',
  '깍두기': '무를 깍둑썰기하여 소금에 절인 후 고춧가루, 파, 마늘 등의 양념으로 버무려 만든 김치입니다.',
  '총각김치': '총각무를 무청째로 담가 아삭한 식감이 일품인 김치입니다.',
  '파김치': '쪽파를 주재료로 하여 멸치젓과 고춧가루 양념으로 맛을 낸, 독특한 향과 맛이 매력적인 김치입니다.',
  '오이소박이': '오이를 세로로 칼집 내어 소를 넣은 김치로, 시원하고 상큼한 맛이 특징입니다.',
  '열무김치': '어린 열무로 담가 여름철에 특히 인기 있는 시원한 물김치입니다.',
  '백김치': '고춧가루를 사용하지 않아 맵지 않고 시원하며 깔끔한 맛이 특징인 김치입니다.',
  '부추김치': '부추의 독특한 향과 젓갈의 감칠맛이 어우러진 별미 김치입니다.',
  '나박김치': '무와 배추를 얇게 썰어 국물을 자박하게 부어 만든 물김치의 일종입니다.',
};

const createShuffledDeck = () => {
  const allKimchiData = Object.keys(kimchiModules).map(path => {
    const pathParts = path.split('/');
    const name = pathParts[pathParts.length - 2];
    return {
      id: path,
      name,
      isKimchi: true,
      description: kimchiDescriptions[name] || '맛있는 김치입니다!',
      importFunc: kimchiModules[path],
    };
  });

  const allNonKimchiData = Object.keys(nonKimchiModules).map(path => {
    const pathParts = path.split('/');
    const categoryName = pathParts[pathParts.length - 2];
    return {
      id: path,
      name: categoryName,
      isKimchi: false,
      description: `이것은 김치가 아닌 "${categoryName}"입니다.`,
      importFunc: nonKimchiModules[path],
    };
  });

  const shuffledKimchi = shuffleArray(allKimchiData);
  const sessionKimchi = shuffledKimchi.slice(0, 20);

  const shuffledNonKimchi = shuffleArray(allNonKimchiData);
  const sessionNonKimchi: (typeof allNonKimchiData[0])[] = [];
  if (shuffledNonKimchi.length > 0) {
      for (let i = 0; i < 20; i++) {
        sessionNonKimchi.push({ ...shuffledNonKimchi[i % shuffledNonKimchi.length], id: `non-kimchi-session-${i}` });
      }
  }

  const finalDeck = [...sessionKimchi, ...sessionNonKimchi];
  return shuffleArray(finalDeck);
};

// --- 컴포넌트 정의 ---

const ItemTypes = { CARD: 'card' };

const KimchiCard = ({ image }: { image: Image }) => {
  const [, drag] = useDrag(() => ({
    type: ItemTypes.CARD,
    item: image,
  }));

  return (
    <div ref={drag} style={{ backgroundImage: `url(${image.url})` }} className={'card'}>
       <h3>{image.name}</h3>
    </div>
  );
};

const DropZone = ({ onDrop, isKimchiZone }: { onDrop: (item: Image) => void; isKimchiZone: boolean }) => {
  const [, drop] = useDrop(() => ({
    accept: ItemTypes.CARD,
    drop: (item: Image) => onDrop(item),
  }));

  return (
    <div ref={drop} className={`dropZone ${isKimchiZone ? 'rightZone' : 'leftZone'}`}>
      {isKimchiZone ? '김치! 😋' : '김치 아님! 🤔'}
    </div>
  );
};

// --- 메인 앱 컴포넌트 ---
function App() {
  const [view, setView] = useState('menu');
  const [gameDeck, setGameDeck] = useState<Image[]>([]);
  const [activeCards, setActiveCards] = useState<Image[]>([]);
  const [deckIndex, setDeckIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [timer, setTimer] = useState(5);
  const [isLoading, setIsLoading] = useState(false);
  const [gameOverImage, setGameOverImage] = useState<Image | null>(null);
  const [nickname, setNickname] = useState('');
  const [leaderboard, setLeaderboard] = useState<Score[]>([]);

  const startGame = useCallback(async () => {
    setIsLoading(true);
    setView('game');
    setScore(0);
    setGameOverImage(null);
    
    const newDeck = createShuffledDeck();
    setGameDeck(newDeck);

    const initialLoadCount = 10;
    const cardPromises: Promise<Image>[] = [];
    for (let i = 0; i < Math.min(initialLoadCount, newDeck.length); i++) {
        const cardData = newDeck[i];
        if (cardData.importFunc) {
            cardPromises.push(
                cardData.importFunc().then(module => ({
                    ...cardData,
                    url: module.default,
                }))
            );
        }
    }
    const initialCards = await Promise.all(cardPromises);
    setActiveCards(initialCards);
    setDeckIndex(initialLoadCount);

    setIsLoading(false);
    setTimer(5);
  }, []);

  useEffect(() => {
    if (view !== 'game' || isLoading || activeCards.length === 0) return;

    const interval = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          setGameOverImage(activeCards[0]);
          setView('gameover');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [view, isLoading, activeCards]);

  const handleDrop = useCallback((item: Image, zoneIsKimchi: boolean) => {
    const isCorrect = item.isKimchi === zoneIsKimchi;

    if (!isCorrect) {
      setGameOverImage(item);
      setView('gameover');
      return;
    }

    setScore(prevScore => prevScore + 1);
    setTimer(5);

    // 상태 업데이트가 꼬이지 않도록 함수형 업데이트를 사용해요!
    setDeckIndex(prevDeckIndex => {
        const newDeckIndex = prevDeckIndex + 1;

        setGameDeck(prevGameDeck => {
            let updatedDeck = prevGameDeck;
            // 덱의 끝에 가까워지면 새로운 카드를 뒤에 추가해요.
            if (newDeckIndex >= updatedDeck.length - 5) {
                updatedDeck = [...updatedDeck, ...createShuffledDeck()];
            }

            const nextCardData = updatedDeck[prevDeckIndex]; // 이전 인덱스를 사용해 정확한 다음 카드를 가져와요.
            if (nextCardData?.importFunc) {
                nextCardData.importFunc().then(module => {
                    const newCard: Image = { ...nextCardData, url: module.default };
                    setActiveCards(prevActiveCards => [...prevActiveCards.slice(1), newCard]);
                });
            } else {
                setActiveCards(prevActiveCards => prevActiveCards.slice(1));
            }
            return updatedDeck;
        });

        return newDeckIndex;
    });
}, []);

  const handleScoreSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (nickname.trim() === '') {
      alert('닉네임을 입력해주세요!');
      return;
    }
    try {
      const response = await axios.post(`${API_URL}/api/submit`, { nickname, score });
      setLeaderboard(response.data.scores);
      setView('leaderboard');
    } catch (error) {
      console.error('점수 등록에 실패했습니다:', error);
      alert('점수 등록 중 오류가 발생했습니다.');
    }
  };

  const showLeaderboard = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/leaderboard`);
      setLeaderboard(response.data);
      setView('leaderboard');
    } catch (error) {
      console.error('리더보드 로딩에 실패했습니다:', error);
      alert('리더보드를 불러오는 중 오류가 발생했습니다.');
    }
  };

  if (view === 'menu') {
    return (
      <div className="gameContainer">
        <h1>이게 김치일까?</h1>
        <p className="infoText" style={{margin: '20px'}}>K-푸드의 대표주자, 김치를 맞혀보세요!</p>
        <button onClick={startGame}>게임 시작</button>
        <button onClick={showLeaderboard} style={{marginTop: '10px'}}>명예의 전당</button>
      </div>
    )
  }

  if (isLoading) {
    return <div className="gameContainer"><h1>카드를 섞는 중...</h1></div>;
  }

  if (view === 'gameover' && gameOverImage) {
    return (
      <div className="gameContainer">
        <h1>게임 오버!</h1>
        <h2>최종 점수: {score}</h2>
        <div className='card' style={{backgroundImage: `url(${gameOverImage.url})`, position: 'relative', marginBottom: '20px'}}>
          <h3>이건 "{gameOverImage.name}" 이었어요!</h3>
        </div>
        <p style={{maxWidth: '350px'}}>{gameOverImage.description}</p>
        
        <form onSubmit={handleScoreSubmit} style={{marginTop: '20px'}}>
          <input 
            type="text" 
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="닉네임을 입력하세요" 
            style={{marginRight: '10px'}}
          />
          <button type="submit">점수 등록</button>
        </form>

        <button onClick={startGame} style={{marginTop: '10px'}}>다시 하기</button>
      </div>
    );
  }

  if (view === 'leaderboard') {
    return (
      <div className="gameContainer">
        <h1>명예의 전당</h1>
        <div className="leaderboardContainer">
          {leaderboard.map((entry, index) => (
            <div key={index} className="leaderboardEntry">
              <span>{index + 1}. {entry.nickname}</span>
              <span>{entry.score}점</span>
            </div>
          ))}
        </div>
        <button onClick={() => setView('menu')} style={{marginTop: '20px'}}>메뉴로 돌아가기</button>
      </div>
    )
  }

  return (
    <>
      {view === 'game' && (
        <div className="dropZoneContainer">
          <DropZone onDrop={(item) => handleDrop(item, false)} isKimchiZone={false} />
          <DropZone onDrop={(item) => handleDrop(item, true)} isKimchiZone={true} />
        </div>
      )}
      <div className="gameContainer">
        <div style={{position: 'absolute', top: '20px', right: '20px'}}>
            <button onClick={showLeaderboard}>🏆</button>
        </div>
        <h1>이게 김치일까?</h1>
        <h2>점수: {score}</h2>
        <div className="timer">남은 시간: {timer}초</div>
        <div className='cardContainer'>
          {activeCards.length > 0 ? (
            <KimchiCard 
              key={activeCards[0].id}
              image={activeCards[0]} 
            />
          ) : (
            <div>
              <h1>잠시만요...</h1>
              <h2>새로운 카드를 섞고 있어요!</h2>
            </div>
          )}
        </div>
        <p className="infoText">
          카드를 끌어서 왼쪽(김치 아님) 또는 오른쪽(김치) 구역으로 옮겨주세요!
        </p>
      </div>
    </>
  );
}

export default App;
