import React, { useState, useEffect, useCallback } from 'react';
import { useDrag, useDrop } from 'react-dnd';
import './App.css';

const ItemTypes = { CARD: 'card' };

type KimchiImage = { id: number; name: string; url: string; isKimchi: boolean; };

const db: KimchiImage[] = [
    { id: 1, name: '배추김치', url: 'https://picsum.photos/350/500?random=1', isKimchi: true },
    { id: 2, name: '총각김치', url: 'https://picsum.photos/350/500?random=2', isKimchi: true },
    { id: 3, name: '파김치', url: 'https://picsum.photos/350/500?random=3', isKimchi: true },
    { id: 4, name: '깍두기', url: 'https://picsum.photos/350/500?random=4', isKimchi: true },
    { id: 5, name: '피자', url: 'https://picsum.photos/350/500?random=5', isKimchi: false },
    { id: 6, name: '스테이크', url: 'https://picsum.photos/350/500?random=6', isKimchi: false },
    { id: 7, name: '초밥', url: 'https://picsum.photos/350/500?random=7', isKimchi: false },
    { id: 8, name: '치킨', url: 'https://picsum.photos/350/500?random=8', isKimchi: false },
    { id: 9, name: '파스타', url: 'https://picsum.photos/350/500?random=9', isKimchi: false },
];

const getShuffledDb = () => [...db].sort(() => Math.random() - 0.5);

const KimchiCard = ({ image, setIsDragging }: { image: KimchiImage, setIsDragging: (isDragging: boolean) => void }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.CARD,
    item: { id: image.id, isKimchi: image.isKimchi },
    collect: (monitor) => ({ isDragging: !!monitor.isDragging() }),
  }));

  useEffect(() => {
    setIsDragging(isDragging);
  }, [isDragging, setIsDragging]);

  return (
    <div ref={drag} style={{ backgroundImage: `url(${image.url})` }} className={'card'}>
      <h3>{image.name}</h3>
    </div>
  );
};

const DropZone = ({ onDrop, isKimchiZone }: { onDrop: (isKimchi: boolean) => void; isKimchiZone: boolean }) => {
  const [, drop] = useDrop(() => ({
    accept: ItemTypes.CARD,
    drop: (item: { isKimchi: boolean }) => onDrop(item.isKimchi),
  }));

  return (
    <div ref={drop} className={`dropZone ${isKimchiZone ? 'rightZone' : 'leftZone'}`}>
      {isKimchiZone ? '김치! 😋' : '김치 아님! 🤔'}
    </div>
  );
};

function App() {
  const [images, setImages] = useState(getShuffledDb);
  const [score, setScore] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [timer, setTimer] = useState(5);

  useEffect(() => {
    if (images.length === 0 || gameOver) return;
    const interval = setInterval(() => {
      setTimer((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [images, gameOver]);

  useEffect(() => {
    if (timer === 0) {
      setGameOver(true);
    }
  }, [timer]);

  const handleDrop = useCallback((cardIsKimchi: boolean, zoneIsKimchi: boolean) => {
    const isCorrect = cardIsKimchi === zoneIsKimchi;

    if (isCorrect) {
      setScore(prevScore => prevScore + 1);
    } else {
      setGameOver(true);
    }
    setImages(prevImages => prevImages.slice(1));
    setTimer(5);
  }, []);

  const restartGame = () => {
    setImages(getShuffledDb());
    setScore(0);
    setGameOver(false);
    setTimer(5);
  };

  if (gameOver) {
    return (
      <div className="gameContainer">
        <h1>게임 오버!</h1>
        <h2>최종 점수: {score}</h2>
        <button onClick={restartGame}>다시 시작하기</button>
      </div>
    );
  }

  return (
    <>
      <div className={`dropZoneContainer ${isDragging ? 'visible' : ''}`}>
        <DropZone onDrop={(isKimchi) => handleDrop(isKimchi, false)} isKimchiZone={false} />
        <DropZone onDrop={(isKimchi) => handleDrop(isKimchi, true)} isKimchiZone={true} />
      </div>
      <div className="gameContainer">
        <h1>이게 김치일까?</h1>
        <h2>점수: {score}</h2>
        <div className="timer">남은 시간: {timer}초</div>
        <div className='cardContainer'>
          {images.length > 0 ? (
            <KimchiCard image={images[0]} setIsDragging={setIsDragging} />
          ) : (
            <div>모든 카드를 확인했어요! 최종 점수: {score}</div>
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
