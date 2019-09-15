
const eloScale = 3000;

export const startingFen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

export const gameStatus = {
  starting: [0, 'New Game', 'info'],
  active: [1, 'Active Game', 'primary'],
  whiteWon: [2, 'White won', 'danger'],
  blackWon: [3, 'Black won', 'danger'],
  draw: [4, 'Draw', 'warning'],
};

const pieceLetters = 'pnbrqk';

export const invertLetters = fen => {
  const tempLetter = 'T';
  var fenInvert = fen;
  for (var letter of pieceLetters){
    const upper = letter.toUpperCase();
    fenInvert = fenInvert.replace(new RegExp(letter, 'g'), tempLetter);
    fenInvert = fenInvert.replace(new RegExp(upper, 'g'), letter);
    fenInvert = fenInvert.replace(new RegExp(tempLetter, 'g'), upper);
  }
  return fenInvert;
};

export const invertFen = fen => {

  const parts = fen.split(' ');
  const positionPart = parts[0];
  const colorPart = parts[1];

  if (colorPart == 'w') {
    return fen;
  }

  const castlePart = parts[2];

  const fenInvertLetters = invertLetters(positionPart);
  const fenSplit = fenInvertLetters.split('/');

  const positionPartInvert = fenSplit.reverse().join('/');
  const castlePartInvert = invertLetters(castlePart);

  const full = positionPartInvert + ' w ' + castlePartInvert + ' ' + parts.slice(3).join(' ');

  console.log(full);
  return full;
};

export const fillFen = fen => {
  var fenFill = fen;
  for (var i=1; i<=8; i++){
    fenFill = fenFill.replace(new RegExp('' + i, 'g'), 'E'.repeat(i));
  }
  return fenFill.replace(new RegExp('/', 'g'), '');
};

const allPieces = 'pPnNbBrRqQkK';
const castlingValues = 'kKqQ';

export const getFeatures = fen => {
  const fenFilled = fillFen(fen);
  var features = [];
  for (var val of fenFilled){
    for (var piece of allPieces){
      features.push(1.0 * (val == piece));
    }
  }
  return features;
};

export const getCastleFeatures = castleString => {
  var features = [];
  for (var s of castlingValues){
    features.push(castleString.includes(s) * 1.0);
  }
  return features;
};

export const getUrl = (fen, elo_white, elo_black, totalTime, timeLeft) => {
  const fenClean = fen.replace(/ /g, '+').replace(/\//g, 'S');

  var url = 'https://chessinsights.org/human_api/fen=' + fenClean;
  url = url + '/totaltime=' + totalTime;
  url = url + '/increment=0';
  url = url + '/time=' + timeLeft;
  url = url + '/ratingwhite=' + elo_white + '/ratingblack=' + elo_black;
  return url;

}

export async function getPrediction(fen, elo, isWhite, totalTime, timeLeft) {
  const url = getUrl(fen, elo, isWhite, totalTime, timeLeft);
  const response = await fetch(url);
  const data = await response.json();
  return data;
}
