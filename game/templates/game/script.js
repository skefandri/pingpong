const canvas = document.getElementById('pongCanvas');
const ctx = canvas.getContext('2d');

// Game settings
const paddleWidth = 10;
const paddleHeight = 75;
const ballRadius = 10;

let paddle1Y = (canvas.height - paddleHeight) / 2;
let paddle2Y = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 2;
let ballSpeedY = 2;

function drawPaddle(x, y) {
    ctx.beginPath();
    ctx.rect(x, y, paddleWidth, paddleHeight);
    ctx.fillStyle = "#0095DD";
    ctx.fill();
    ctx.closePath();
}

function drawBall() {
    ctx.beginPath();
    ctx.arc(ballX, ballY, ballRadius, 0, Math.PI * 2);
    ctx.fillStyle = "#0095DD";
    ctx.fill();
    ctx.closePath();
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawPaddle(0, paddle1Y);
    drawPaddle(canvas.width - paddleWidth, paddle2Y);
    drawBall();

    ballX += ballSpeedX;
    ballY += ballSpeedY;

    // Ball collision with top and bottom
    if(ballY + ballSpeedY > canvas.height - ballRadius || ballY + ballSpeedY < ballRadius) {
        ballSpeedY = -ballSpeedY;
    }

    // Ball collision with paddles
    if(ballX + ballSpeedX > canvas.width - ballRadius - paddleWidth) {
        if(ballY > paddle2Y && ballY < paddle2Y + paddleHeight) {
            ballSpeedX = -ballSpeedX;
        } else {
            resetBall();
            return "Player 1";
        }
    } else if(ballX + ballSpeedX < ballRadius + paddleWidth) {
        if(ballY > paddle1Y && ballY < paddle1Y + paddleHeight) {
            ballSpeedX = -ballSpeedX;
        } else {
            resetBall();
            return "Player 2";
        }
    }
}

function resetBall() {
    ballX = canvas.width / 2;
    ballY = canvas.height / 2;
    ballSpeedX = -ballSpeedX;
}

async function playMatch(player1, player2) {
    // Reset paddles
    paddle1Y = (canvas.height - paddleHeight) / 2;
    paddle2Y = (canvas.height - paddleHeight) / 2;

    alert(`Match starting: ${player1} vs ${player2}`);
    return new Promise((resolve) => {
        requestAnimationFrame(function gameLoop() {
            const winner = draw();
            if (winner) {
                resolve(winner === "Player 1" ? player1 : player2);
            } else {
                requestAnimationFrame(gameLoop);
            }
        });
    });
}

async function startTournament() {
    const players = [];
    for (let i = 1; i <= 4; i++) {
        const player = document.getElementById(`player${i}`).value.trim();
        if (player) {
            players.push(player);
        }
    }

    if (players.length < 4) {
        alert("Please enter all four player names.");
        return;
    }

    const shuffledPlayers = players.sort(() => 0.5 - Math.random());
    let resultsHTML = "<h2>Tournament Results</h2>";

    // Play semi-finals
    const winner1 = await playMatch(shuffledPlayers[0], shuffledPlayers[1]);
    const loser1 = winner1 === shuffledPlayers[0] ? shuffledPlayers[1] : shuffledPlayers[0];
    const winner2 = await playMatch(shuffledPlayers[2], shuffledPlayers[3]);
    const loser2 = winner2 === shuffledPlayers[2] ? shuffledPlayers[3] : shuffledPlayers[2];

    resultsHTML += `<p>Semi-final 1: ${shuffledPlayers[0]} vs ${shuffledPlayers[1]} - Winner: ${winner1}</p>`;
    resultsHTML += `<p>Semi-final 2: ${shuffledPlayers[2]} vs ${shuffledPlayers[3]} - Winner: ${winner2}</p>`;

    // Play classification match
    const thirdPlaceWinner = await playMatch(loser1, loser2);
    resultsHTML += `<p>Classification (3rd place): ${loser1} vs ${loser2} - Winner: ${thirdPlaceWinner}</p>`;

    // Play final
    const tournamentWinner = await playMatch(winner1, winner2);
    resultsHTML += `<p>Final: ${winner1} vs ${winner2} - Winner: ${tournamentWinner}</p>`;

    document.getElementById('results').innerHTML = resultsHTML;
}

document.getElementById('startTournament').addEventListener('click', startTournament);
