<template>
  <Alert v-show="isAlertShown" :text="alertText"></Alert>

  <div class="parent">
    <div class="left-side-container child">
      <div class="score-container" style="height: 200px; ">
        <div class="score" id="current-score">
          <Score title="Score" :score=currentScore></Score>
        </div>
        <div class="score" id="personal-best" style="margin-top: 20px;">
          <Score title="Personal Best" :score="personalBest"></Score>
        </div>
      </div>
      <div class="instruction-container">Instructions:<div v-for="(instruction, index) in instuctions"> {{ index + 1 }}.
          {{
            instruction
          }}
        </div>
      </div>

    </div>


    <div class="child game-container">
      <canvas width="500" height="500" id="game"></canvas>
    </div>
    <div class="leaderboard-container child">
      <table id="leaderboard">
        <thead>
          <tr>
            <th>Username</th>
            <th>Score</th>
            <th>Scored At</th>
            <th>Time Taken</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(score, index) in topScores" :class="{ 'champion': index === 0 }">
            <td :class="{ 'no-bottom': index === topScores.length - 1 }">
              <div style="display: flex; align-items: center;">
                <img src="/crown.svg" width="25px" v-if="index === 0">
                <div width="20px" v-else style="width: 20px;"></div>

                <div>{{ truncateText(score.username) }}</div>
                <!-- <div>ssdddddddddddddddddds</div> -->
              </div>
            </td>
            <td :class="{ 'no-bottom': index === topScores.length - 1 }">{{ score.score }}</td>
            <td :class="{ 'no-bottom': index === topScores.length - 1 }">{{ new
              Date(score.scoredAt).toLocaleString('en-US', { dateStyle: 'short', timeStyle: 'short' }) }}</td>
            <td :class="{ 'no-bottom': index === topScores.length - 1 }">{{ formatTime(score.timeTakenSeconds) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, computed } from "vue";
import ScoreService from "./services/ScoreService";
import Score from './components/Score.vue'
import Alert from "./components/Alert.vue";


const instuctions = ref(["Move with arrow keys/WASD/IJKL", "Eat the 404", "Don't touch your tail", "Pause/Unpause with Esc"])

function truncateText(text) {
  const maxLength = 10
  if (text.length > maxLength) {
    return text.substring(0, maxLength - 3) + '...';
  } else {
    return text;
  }
}

const time_counter_seconds = ref(0);

setInterval(() => { time_counter_seconds + 1 }, 1000);

const game_start_time_seconds = ref(0)

const topScores = ref([]);

const personalBest = ref(0);

const currentScore = ref(0);

function formatTime(totalSeconds) {
  // const hours = Math.floor(timeTaken / 3600);
  // const minutes = Math.floor((timeTaken % 3600) / 60);
  // const seconds = timeTaken % 60;

  // return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

  let minutes = Math.floor(totalSeconds / 60);
  let seconds = Math.round(totalSeconds % 60);

  return `${minutes}m ${seconds}s`;
}


const updateHighscoresEvent = new CustomEvent('updateHighscores', {
  bubbles: false, // prevent event from bubbling up the DOM
  cancelable: true // allow event to be cancelled
});


// Listen for the updateHighscores event
window.addEventListener('updateHighscores', async (event) => {
  topScores.value = await ScoreService.getScores();
});

async function setupScores() {
  personalBest.value = localStorage.getItem("personal_best") ?? 0;

  window.dispatchEvent(updateHighscoresEvent);
  setInterval(async () => {
    window.dispatchEvent(updateHighscoresEvent);
  }, 5000);
}

function calculateScore(length) {
  return (length - SNAKE_INITIAL_LENGTH) * 1;
}

// let currentScore = ref(0);

let context;
let canvas;

function initialize_canvas() {
  canvas = document.getElementById("game");
  context = canvas.getContext("2d");
}

let snake;
let apple;

onMounted(async () => {
  // Initialize Canvas
  initialize_canvas();

  // setup scores
  setupScores();

  // start the game
  requestAnimationFrame(loop);


  snake = new Snake(160, 160, grid);
  apple = new Apple(320, 320);
});




const SNAKE_BODY_GRADIENT = { start: [24, 87, 39], end: [15, 54, 24] };
const SNAKE_INITIAL_LENGTH = 4;
// const SNAKE_EAT_SOUND = new Audio("gulp.mp3");

// the canvas width & height, snake x & y, and the apple x & y, all need to be a multiples of the grid size in order for collision detection to work
// (e.g. 16 * 25 = 400)
var grid = 20;

// var personal_best_score = ref(0);

var username = localStorage.getItem("username");
if (username === "" || username === null) {
  username = prompt("Enter your username:");
  console.log("Username: " + username);
  localStorage.setItem("username", username);
}
function pause_game() {
  game_paused = true;
}

function unpause_game() {
  game_paused = false;
  requestAnimationFrame(loop);
}

var game_paused = false;

class Snake {
  constructor(x, y, grid) {
    this.x = x;
    this.y = y;
    this.dx = grid;
    this.dy = 0;
    this.dxToApply = grid;
    this.dyToApply = 0;
    this.cells = [];
    this.maxCells = SNAKE_INITIAL_LENGTH;
    this.autoplay = false;
    this.birthDatetime = new Date()
  }

  queue_turn_left() {
    this.dxToApply = -grid;
    this.dyToApply = 0;
  }
  queue_turn_right() {
    this.dxToApply = grid;
    this.dyToApply = 0;
  }
  queue_turn_up() {
    this.dyToApply = -grid;
    this.dxToApply = 0;
  }
  queue_turn_down() {
    this.dyToApply = grid;
    this.dxToApply = 0;
  }

  move() {
    this.x += this.dx;
    this.y += this.dy;
  }

  flush_queued_move() {
    this.dx = this.dxToApply;
    this.dy = this.dyToApply;
  }

  increase_length() {
    this.maxCells++;
    currentScore.value += 1
  }

  calculateGradient(i, firstColor, secondColor) {
    const step = i / (this.maxCells - 1);
    const r = Math.round(
      firstColor[0] + (secondColor[0] - firstColor[0]) * step
    );
    const g = Math.round(
      firstColor[1] + (secondColor[1] - firstColor[1]) * step
    );
    const b = Math.round(
      firstColor[2] + (secondColor[2] - firstColor[2]) * step
    );

    return `rgba(${r}, ${g}, ${b}, 1)`;
  }

  doOptimalMove(x, y) {
    x = x / grid;
    y = y / grid;
    console.log(x, "   ", y);

    if (y === 0) {
      if (this.dy === -20) {
        this.queue_turn_right();
      } else if (this.dx === -20) {
        this.queue_turn_down();
      } else {
        this.queue_turn_down();
      }
    } else if (y === 25 - 1) {
      if (this.dx === -20) {
        this.queue_turn_up();
      } else if (this.dy === 20) {
        this.queue_turn_right();
      } else {
        this.queue_turn_up();
      }
    } else if (this.dx === 20) {
      this.queue_turn_down();
    }
  }
}

class Apple {
  constructor(x, y) {
    this.x = x;
    this.y = y;
  }
}



// get random whole numbers in a specific range
// @see https://stackoverflow.com/a/1527820/2124254
function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min)) + min;
}

var count = 0;

// game loop
function loop() {
  if (!game_paused) {
    requestAnimationFrame(loop);
  }

  // console.log("dfsfs", localStorage.getItem("lastname"));

  // slow game loop to 15 fps instead of 60 (60/15 = 4)
  if (++count < 4) {
    return;
  }

  count = 0;
  if (snake.autoplay) {
    snake.doOptimalMove(snake.x, snake.y);
  }
  snake.flush_queued_move();

  context.clearRect(0, 0, canvas.width, canvas.height);

  // move snake by it's velocity
  snake.move();

  // wrap snake position horizontally on edge of screen
  if (snake.x < 0) {
    snake.x = canvas.width - grid;
  } else if (snake.x >= canvas.width) {
    snake.x = 0;
  }

  // wrap snake position vertically on edge of screen
  if (snake.y < 0) {
    snake.y = canvas.height - grid;
  } else if (snake.y >= canvas.height) {
    snake.y = 0;
  }

  // keep track of where snake has been. front of the array is always the head
  snake.cells.unshift({ x: snake.x, y: snake.y });

  //   remove cells as we move away from them
  if (snake.cells.length > snake.maxCells) {
    snake.cells.pop();
  }

  // context.fillStyle = "lightgreen";
  // for (let i = 0; i < 25; i++) {
  //   for (let j = 0; j < 25; j++) {
  //     // context.fillRect(i * grid, j * grid, grid - 2, grid - 2);
  //     context.rect(i * grid, j * grid, grid - 1, grid - 1);

  //   }
  // }

  // DEBUG: CELL ID
  // context.fillStyle = "red";
  // for (let i = 0; i < 25; i++) {
  //   for (let j = 0; j < 25; j++) {
  //     // context.fillStyle = "lightgreen";
  //     // context.fillRect(i * grid, j * grid, grid - 2, grid - 2);
  //     // context.rect(i * grid, j * grid, grid - 1, grid - 1);

  //     context.font = `8px arial`;
  //     context.fillText(`${i}:${j}`, i * grid + 2, j * grid + 11.5);
  //   }
  // }
  // context.fill();

  // draw apple
  context.fillStyle = "#ffcb74";
  context.fillRect(apple.x, apple.y, grid - 1, grid - 1);

  // console.log("width", canvas.width);
  context.fillStyle = "#373636";
  // context.fillStyle = "red";
  context.font = `${grid * 0.5}px arial`;
  // context.fillRect(apple.x, apple.y, 3, 3);
  context.fillText("404", apple.x, apple.y + grid / 1.5);

  // draw snake one cell at a time
  context.fillStyle = "#185727";
  snake.cells.forEach(function (cell, index) {
    // drawing 1 px smaller than the grid creates a grid effect in the snake body so you can see how long it is

    //   if (index == 0) {
    //     context.fillStyle = "red";
    //     context.fillRect(cell.x, cell.y, grid - 1, grid - 1);
    //   } else {
    //     context.fillStyle = "#185727";
    //     context.fillRect(cell.x, cell.y, grid - 1, grid - 1);
    //   }
    context.fillStyle = snake.calculateGradient(
      index,
      SNAKE_BODY_GRADIENT.end,
      SNAKE_BODY_GRADIENT.start
    );
    context.fillRect(cell.x, cell.y, grid - 1, grid - 1);

    // Draw eyes
    if (index === 0) {
      // context.fillStyle = "red";
      // context.fillRect(cell.x, cell.y, grid - 1, grid - 1);

      // Draw the white dots for the eyes
      context.fillStyle = "white";

      // console.log(snake);
      const eyeRadius = 2;

      // left
      if (snake.dx === 20) {
        context.beginPath();
        context.arc(cell.x + 15, cell.y + 6, eyeRadius, 0, 2 * Math.PI);
        context.fill();

        context.beginPath();
        context.arc(cell.x + 15, cell.y + 14, eyeRadius, 0, 2 * Math.PI);
        context.fill();
      }

      //Right
      else if (snake.dx === -20) {
        context.beginPath();
        context.arc(cell.x + 5, cell.y + 6, eyeRadius, 0, 2 * Math.PI);
        context.fill();

        context.beginPath();
        context.arc(cell.x + 5, cell.y + 14, eyeRadius, 0, 2 * Math.PI);
        context.fill();
      }

      // down
      else if (snake.dy === 20) {
        context.beginPath();
        context.arc(cell.x + 6, cell.y + 15, eyeRadius, 0, 2 * Math.PI);
        context.fill();

        context.beginPath();
        context.arc(cell.x + 14, cell.y + 15, eyeRadius, 0, 2 * Math.PI);
        context.fill();
      }

      // up
      else if (snake.dy === -20) {
        context.beginPath();
        context.arc(cell.x + 6, cell.y + 5, eyeRadius, 0, 2 * Math.PI);
        context.fill();

        context.beginPath();
        context.arc(cell.x + 14, cell.y + 5, eyeRadius, 0, 2 * Math.PI);
        context.fill();
      }
    }

    // snake ate apple
    if (cell.x === apple.x && cell.y === apple.y) {
      // snake.maxCells++;
      // SNAKE_EAT_SOUND.play();
      snake.increase_length();

      // canvas is 400x400 which is 25x25 grids
      // apple.x = getRandomInt(0, 25) * grid;
      // apple.y = getRandomInt(0, 25) * grid;
      apple = new Apple(getRandomInt(0, 25) * grid, getRandomInt(0, 25) * grid);

      // console.log("eaating apple", snake.score, "  ", highscore);

      if (currentScore.value > personalBest.value) {
        personalBest.value = currentScore.value;
        localStorage.setItem("personal_best", personalBest.value);
      }
    }

    // check collision with all cells after this one (modified bubble sort)
    for (var i = index + 1; i < snake.cells.length; i++) {
      // snake occupies same space as a body part. reset game
      // Death
      if (cell.x === snake.cells[i].x && cell.y === snake.cells[i].y) {
        let timeTakenSeconds = (new Date().getTime() - snake.birthDatetime.getTime()) / 1000;
        ScoreService.saveScore(username, currentScore.value, timeTakenSeconds);
        currentScore.value = 0;
        window.dispatchEvent(updateHighscoresEvent);

        snake = new Snake(160, 160, grid);

        apple.x = getRandomInt(0, 25) * grid;
        apple.y = getRandomInt(0, 25) * grid;
      }
    }
  });

  // // Draw score
  // context.font = "50px serif";
  // context.fillStyle = "#ffcb74";
  // context.fillText(currentScore.value, 400, 40);

  // // Draw highscore
  // context.font = "50px serif";
  // context.fillStyle = "#ffcb74";
  // // context.fillText(
  // //   personal_best_score ? personal_best_score : 0,
  // //   450,
  // //   40
  // // );
  // context.fillText(personalBest.value, 450, 40);
}

const alertText = ref("")
const isAlertShown = ref(false)
function showAlert(text) {
  console.log("shwoing alert")
  alertText.value = text
  isAlertShown.value = true

  setTimeout(() => {
    isAlertShown.value = false
  }, 2000);
}


const CHEATING_ALERT_TEXT = "Autoplay enabled"
const CHEATING_ALERT_DISABLED_TEXT = "Autoplay enabled"
const autoplayCheat = 'aspirine'.split('');
let autoplayCheatPointer = 0

// listen to keyboard events to move the snake
document.addEventListener("keydown", function (e) {

  if (game_paused) {
    console.log("unpausing");
    unpause_game();
  }

  // p key
  else if (e.key === "Escape") {
    console.log("pause called", game_paused);
    pause_game();
  }

  if (e.key === autoplayCheat[autoplayCheatPointer]) {
    autoplayCheatPointer += 1
    if (autoplayCheatPointer === autoplayCheat.length) {
      snake.autoplay = true;
      showAlert(CHEATING_ALERT_TEXT)
      return
    }
  } else {
    autoplayCheatPointer = 0
  }

  // left arrow key
  if ((e.key === "ArrowLeft" || e.key === "a" || e.key === "j") && snake.dx === 0) {
    snake.autoplay = false;
    snake.queue_turn_left();
  }
  // up arrow key
  else if ((e.key === "ArrowUp" || e.key === "w" || e.key === "i") && snake.dy === 0) {
    snake.autoplay = false;
    snake.queue_turn_up();
  }
  // right arrow key
  else if ((e.key === "ArrowRight" || e.key === "d" || e.key === "l") && snake.dx === 0) {
    snake.autoplay = false;
    snake.queue_turn_right();
  }
  // down arrow key
  else if ((e.key === "ArrowDown" || e.key === "s" || e.key === "k") && snake.dy === 0) {
    snake.autoplay = false;
    snake.queue_turn_down();
  }
  // // c key
  // else if (e.key === "c") {
  //   snake.autoplay = !snake.autoplay;

  //   console.log("Cheating: autoplay toggled");
  // }
});
</script>

<style>
/* html,
body {
  height: 100%;
  margin: 0;
}

body {
  background: #373636;
  display: flex;
  align-items: center;
  justify-content: center;
} */

canvas {
  border: 1px solid #ccc;
}




.parent {
  width: 100%;
  padding-left: 0;
  margin-left: 0;
  margin-right: 0;
  box-sizing: border-box;
  display: flex;
  /* width: 100%; */
  justify-content: space-between;
  /* border: 1px green solid; */

  align-items: center;
  /* width: 100vw; */
  /* height: 100vh;
  margin-left: 0;
  margin-right: 0;
  padding-left: 0; */
}

.child {
  /* Child 1 takes up 40% of the space */
  /* margin: 0 10px; */
  margin: 10px;
  /* add some margin to create a gap between the child elements */
}

.game-container {

  /* margin-top: 4%; */
  width: 500px;
  top: 100px
}

.left-side-container {

  /* border: red 1px solid; */
  width: 250px;
}

.score-container {
  /* border: green 1 px solid; */
  margin-bottom: 100px;

}

.instruction-container {
  /* border: yellow 1px solid; */

  /* border: 1px solid #ccc;
  border-radius: 10px;
  padding: 10px; */
  font-family: 'Fantasy';

  color: #ccc;
}

.leaderboard-container {

  /* border: green 1px solid; */
  width: 450px;
}



#leaderboard {
  font-family: Arial, sans-serif;
  font-size: 14px;
  width: 450px;
  /* margin-right: 2%; */
  /* margin-left: 0; */
  /* margin: 0 auto; */
  /* padding: 20px; */
  border: 1px solid #ccc;
  border-radius: 10px;
  /* box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); */
}

#leaderboard th {
  /* background-color: #f0f0f0; */
  color: white;
  padding: 10px;
  border-bottom: 1px solid #ccc;

}


#leaderboard td {
  padding: 10px;
  border-bottom: 1px solid #ccc;
}

#leaderboard .no-bottom {
  /* padding: 10px; */
  border-bottom: 0px solid #ccc;
}

/* #leaderboard tr:hover {
        background-color: #f2f2f2;
      } */

#leaderboard th,
#leaderboard td {
  text-align: left;
}

#leaderboard th:first-child,
#leaderboard td:first-child {
  width: 10%;
}

#leaderboard th:nth-child(2),
#leaderboard td:nth-child(2) {
  width: 20%;
}

#leaderboard th:nth-child(3),
#leaderboard td:nth-child(3) {
  width: 35%;
}

#leaderboard th:nth-child(4),
#leaderboard td:nth-child(4) {
  width: 25%;
}


.champion {
  color: #ffcb74;
}

/* 
TODO:
1. Fix score  
2. Favicon ------------------ Done
3. Instructions
4. Cheats - properly -------------Done
5. Cheat notification
*/
</style>
