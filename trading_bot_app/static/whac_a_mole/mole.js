let currMoleTile;
let currPlantTile;
let score = 0;
let gameOver = false;
let totalClicks = 0;
let hits = 0;
let misses = 0;
let startTime;
let endTime;

window.onload = function() {
    setGame();
    startTime = new Date().getTime();
}

function setGame() {
    for (let i = 0; i < 9; i++) {
        let tile = document.createElement("div");
        tile.id = i.toString();
        tile.addEventListener("click", selectTile);
        document.getElementById("board").appendChild(tile);
    }
    setInterval(setMole, 1000);
    setInterval(setPlant, 2000);
}

function getRandomTile() {
    let num = Math.floor(Math.random() * 9);
    return num.toString();
}

function setMole() {
    if (gameOver) {
        return;
    }
    if (currMoleTile) {
        currMoleTile.innerHTML = "";
    }
    let mole = document.createElement("img");
    mole.src = "/static/whac_a_mole/elmo.png";

    let num = getRandomTile();
    if (currPlantTile && currPlantTile.id == num) {
        return;
    }
    currMoleTile = document.getElementById(num);
    currMoleTile.appendChild(mole);
}

function setPlant() {
    if (gameOver) {
        return;
    }
    if (currPlantTile) {
        currPlantTile.innerHTML = "";
    }
    let plant = document.createElement("img");
    plant.src = "/static/whac_a_mole/piranha-plant.png";

    let num = getRandomTile();
    if (currMoleTile && currMoleTile.id == num) {
        return;
    }
    currPlantTile = document.getElementById(num);
    currPlantTile.appendChild(plant);
}

function displayPopup() {
    let popup = document.getElementById('popup');
    popup.style.display = 'block';
}

function selectTile() {
    if (gameOver) {
        displayPopup();
        return;
    }
    totalClicks++;
    if (this == currMoleTile) {
        score += 10;
        hits++;
        document.getElementById("score").innerText = score.toString();
    } else if (this == currPlantTile) {
        document.getElementById("score").innerText = "GAME OVER: " + score.toString();
        gameOver = true;
        endTime = new Date().getTime();
        sendGameData();
    } else {
        misses++;
    }
}

function sendGameData() {
    let timePlayed = (endTime - startTime) / 1000; // Time played in seconds
    let gameData = {
        timePlayed: timePlayed,
        totalClicks: totalClicks,
        hits: hits,
        misses: misses,
        score: score
    };

    fetch('/submit_game_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(gameData),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        alert('Game data submitted successfully: ' + JSON.stringify(data));
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}