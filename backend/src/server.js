import express from "express";
import fs from "fs";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

const FILE = "scores.json";

// 파일에서 점수 불러오기
function loadScores() {
  if (!fs.existsSync(FILE)) return [];
  return JSON.parse(fs.readFileSync(FILE, "utf8"));
}

// 점수 저장하기
function saveScores(scores) {
  fs.writeFileSync(FILE, JSON.stringify(scores, null, 2));
}

// 점수 제출 API
app.post("/api/submit", (req, res) => {
  const { nickname, score } = req.body;
  if (!nickname || typeof score !== "number") {
    return res.status(400).json({ error: "Invalid data" });
  }

  const scores = loadScores();

  // 이미 있으면 갱신, 없으면 추가
  const existing = scores.find((s) => s.nickname === nickname);
  if (existing) existing.score = Math.max(existing.score, score);
  else scores.push({ nickname, score });

  // 점수순 정렬 (내림차순)
  scores.sort((a, b) => b.score - a.score);

  saveScores(scores);
  res.json({ message: "Score saved", scores });
});

// 전체 랭킹 조회 API
app.get("/api/leaderboard", (req, res) => {
  const scores = loadScores();
  res.json(scores);
});

// 서버 실행
app.listen(3000, () => console.log("🚀 Server running on http://localhost:3000"));
