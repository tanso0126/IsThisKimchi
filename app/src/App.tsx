import React, { useState, useEffect, useCallback } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import './App.css';

// --- 데이터 타입 정의 ---
interface Image {
  id: string;
  name: string;
  url: string;
  isKimchi: boolean;
  description: string;
}

interface ImageModule {
  default: string;
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
    const fileName = pathParts[pathParts.length - 1];
    const name = fileName.substring(0, fileName.lastIndexOf('.'));
    return {
      id: path,
      name: name,
      isKimchi: false,
      description: '이것은 김치가 아닙니다.',
      importFunc: nonKimchiModules[path],
    };
  });

  // 50% 비율을 위해 세션 덱 생성
  const shuffledKimchi = allKimchiData.sort(() => Math.random() - 0.5);
  const sessionKimchi = shuffledKimchi.slice(0, 20);

  const sessionNonKimchi: (typeof allNonKimchiData[0])[] = [];
  if (allNonKimchiData.length > 0) {
      for (let i = 0; i < 20; i++) {
        sessionNonKimchi.push({ ...allNonKimchiData[i % allNonKimchiData.length], id: `non-kimchi-session-${i}` });
      }
  }

  const finalDeck = [...sessionKimchi, ...sessionNonKimchi];
  return finalDeck.sort(() => Math.random() - 0.5);
};

const gameDeck = createShuffledDeck();

// --- 컴포넌트 정의 ---

const ItemTypes = { CARD: 'card' };

const KimchiCard = ({ image, setIsDragging }: { image: Image, setIsDragging: (isDragging: boolean) => void }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.CARD,
    item: image,
    collect: (monitor) => ({ isDragging: !!monitor.isDragging() }),
  }));

  useEffect(() => {
    setIsDragging(isDragging);
  }, [isDragging, setIsDragging]);

  return (
    <div ref={drag} style={{ backgroundImage: `url(${image.url})` }} className={'card'} />
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

function App() {
  const [activeCards, setActiveCards] = useState<Image[]>([]);
  const [deckIndex, setDeckIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState<Image | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [timer, setTimer] = useState(5);
  const [isLoading, setIsLoading] = useState(true);

  const loadInitialCards = useCallback(async () => {
    setIsLoading(true);
    const initialLoadCount = 10;
    const cardPromises: Promise<Image>[] = [];

    for (let i = 0; i < Math.min(initialLoadCount, gameDeck.length); i++) {
      const cardData = gameDeck[i];
      if ('importFunc' in cardData) {
        cardPromises.push(
          (cardData.importFunc as () => Promise<ImageModule>)().then(module => ({
            ...(cardData as Omit<typeof cardData, 'importFunc'>),
            url: module.default,
          }))
        );
      } else {
        cardPromises.push(Promise.resolve(cardData as Image));
      }
    }

    const initialCards = await Promise.all(cardPromises);
    setActiveCards(initialCards);
    setDeckIndex(initialLoadCount);
    setIsLoading(false);
    setTimer(5);
  }, []);

  useEffect(() => {
    loadInitialCards();
  }, [loadInitialCards]);

  useEffect(() => {
    if (isLoading || gameOver || activeCards.length === 0) return;

    const interval = setInterval(() => {
      setTimer((prev) => {
        if (prev <= 1) {
          setGameOver(activeCards[0]);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [isLoading, gameOver, activeCards]);

  const handleDrop = useCallback((item: Image, zoneIsKimchi: boolean) => {
    const isCorrect = item.isKimchi === zoneIsKimchi;

    if (!isCorrect) {
      setGameOver(item);
      setActiveCards(prev => prev.slice(1));
      return;
    }

    setScore(prevScore => prevScore + 1);
    setTimer(5);

    setDeckIndex(currentIndex => {
      const nextIndex = currentIndex + 1;
      if (currentIndex < gameDeck.length) {
        const nextCardData = gameDeck[currentIndex];
        const loadAndSet = async () => {
          let newCard: Image;
          if ('importFunc' in nextCardData) {
            const module = await (nextCardData.importFunc as () => Promise<ImageModule>)();
            newCard = { ...(nextCardData as any), url: module.default };
          } else {
            newCard = nextCardData as Image;
          }
          setActiveCards(prev => [...prev.slice(1), newCard]);
        };
        loadAndSet();
      } else {
        setActiveCards(prev => prev.slice(1));
      }
      return nextIndex;
    });
  }, []);

  const restartGame = () => {
    window.location.reload();
  };

  if (isLoading) {
    return <div>게임을 불러오는 중...</div>;
  }

  if (gameOver) {
    return (
      <div className="gameContainer">
        <h1>게임 오버!</h1>
        <h2>최종 점수: {score}</h2>
        <div className='card' style={{backgroundImage: `url(${gameOver.url})`, position: 'relative', marginBottom: '20px'}}></div>
        <h3>이건 "{gameOver.name}" 이었어요!</h3>
        <p style={{maxWidth: '350px'}}>{gameOver.description}</p>
        <button onClick={restartGame} style={{marginTop: '20px'}}>새로운 게임 시작하기</button>
      </div>
    );
  }

  return (
    <>
      <div className={`dropZoneContainer ${isDragging ? 'visible' : ''}`}>
        <DropZone onDrop={(item) => handleDrop(item, false)} isKimchiZone={false} />
        <DropZone onDrop={(item) => handleDrop(item, true)} isKimchiZone={true} />
      </div>
      <div className="gameContainer">
        <h1>이게 김치일까?</h1>
        <h2>점수: {score}</h2>
        <div className="timer">남은 시간: {timer}초</div>
        <div className='cardContainer'>
          {activeCards.length > 0 ? (
            activeCards.map((card, index) => (
              index === 0 && <KimchiCard 
                key={card.id}
                image={card} 
                setIsDragging={setIsDragging}
              />
            )).reverse()
          ) : (
            <div>
              <h1>축하합니다!</h1>
              <h2>모든 문제를 다 맞혔어요!</h2>
              <h3>최종 점수: {score}</h3>
              <button onClick={restartGame} style={{marginTop: '20px'}}>새로운 게임 시작하기</button>
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
