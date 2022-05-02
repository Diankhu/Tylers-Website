// wordle.js document
// https://www.w3schools.com/jsref/event_onclick.asp used for virtual keyboad onclick function
// https://flaviocopes.com/how-to-remove-last-char-string-js/ for string slice method
// https://www.w3schools.com/css/css3_transitions.asp for transitions of the colors
// https://www.techiedelight.com/measure-execution-time-method-javascript/ measuring time
// DOCUMENT VARIABLES
// grabs every element with the keyboard_button class description
const keys = document.querySelectorAll(".keyboard_button");
const gridRow = document.querySelectorAll(".grid_row");
const gridColumn = document.querySelectorAll(".grid_box");
// gets the length of the correct hidden word by finding the count of grid rows in the grid since they will be the same
const correctWordLength = gridRow.length;
const guess_failure = document.querySelector(".guess_fail");
const not_enough = document.querySelector(".too_few");
// handles the exit button for the instructions
const exit_button = document.querySelector(".exit_button");
const instruction_prompt = document.querySelector(".instruction_prompt");
// contains mapping keydown codes and their respective objects
var keyMap = {}
var currentWordLength = 0;
var currentWordGuess = ""
var currentGuessRow = 0;
var currentGuessColumn = 0;
var currentGridBox = 0;
var real_word = false
var guessCount = 0;
// keyboard starts off because user must exit out of the instruction prompt first for it to be turned on
var keyboardOn = false;
// this is the key return values
const keyPresses = [81,87,69,82,84,89,85,73,79,80,65,83,68,70,71,72,74,75,76,13,90,88,67,86,66,78,77,8];
// timer variables
var startTime;
var totalTime;
var timerStart = false;

// game over VARIABLES
var victory = false;

// handles the end of the game
function gameover()
{
  // leaderboard infortmation for styling

  const scoreboard = document.querySelector(".scoreboard");
  var data = {};
  // SEND DATA TO SERVER VIA jQuery.ajax({})
  jQuery.ajax({
      url: "/retrieverankings",
      data: data,
      type: "POST",
      success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // use the information in returned data to add information to the popup leaderboard
            document.querySelector(".correct_word").textContent = returned_data['word'];
            scoreboard.style.display = 'block';
            if (1 in returned_data)
            {
                document.querySelector(".rank_1").textContent = returned_data[1][0] + " in " + returned_data[1][1] + " seconds";
            }
            if (2 in returned_data)
            {
                document.querySelector(".rank_2").textContent = returned_data[2][0] + " in " + returned_data[2][1] + " seconds";
            }
            if (3 in returned_data)
            {
                document.querySelector(".rank_3").textContent = returned_data[3][0] + " in " + returned_data[3][1] + " seconds";
            }
            if (4 in returned_data)
            {
                document.querySelector(".rank_4").textContent = returned_data[4][0] + " in " + returned_data[4][1] + " seconds";
            }
            if (5 in returned_data)
            {
                document.querySelector(".rank_5").textContent = returned_data[5][0] + " in " + returned_data[5][1] + " seconds";
            }




            if (victory === true)
            {
                document.querySelector(".status").textContent = "Congratulations! You guessed the Word of the Day.";
            }
            else if (victory === false)
            {
              document.querySelector(".status").textContent = "Good luck next time!";
            }

          }
  });
}
// colors the squares of
function colorsquares(e)
{

  var start_index = currentGuessRow * correctWordLength;


  var isSame = true;
  // iterate through the keys and color them
  for (key in e)
  {

    if (key !== "Success")
    {
        // this gives the coloring a smooth transition
        gridColumn[start_index].style.transition = "background-color 1s ease-out";
        var correct_key = "";
        // find the virtual key object that is the same as the character in this index of the grid
        for (let i = 0; i < keys.length;i++)
        {
          if (keys[i].textContent === gridColumn[start_index].textContent)
          {
            // break when the correct key object is found
            correct_key = keys[i];
            break;
          }
        }
        // this gives the coloring a smooth transition
        correct_key.style.transition = "background-color 1s ease-out";
        if(e[key] === 0)
        {
          gridColumn[start_index].style.backgroundColor = "#BBBBBB";

          // the other colors have priority over this color
          if (correct_key.style.backgroundColor !== "rgb(248, 203, 46)" && correct_key.style.backgroundColor !== "rgb(78, 148, 79)")
          {
            correct_key.style.backgroundColor = "#BBBBBB";
          }
          // this is to track if the words are the same
          isSame = false;
        }
        if(e[key] === 1)
        {
          gridColumn[start_index].style.backgroundColor = "#F8CB2E";
          // only green has priority over yellow, if the color is anything but green, color it yellow
          if (correct_key.style.backgroundColor !== "rgb(78, 148, 79)")
          {
              correct_key.style.backgroundColor = "#F8CB2E";
          }
          // this is to track if the words are the same
          isSame = false;
        }
        if(e[key] === 2)
        {
          // green has highest priority and can color over anything
          gridColumn[start_index].style.backgroundColor = "#4E944F";
          correct_key.style.backgroundColor = "#4E944F";
        }
        start_index += 1;
    }
  }

  // if isSame is still true after iterating through the dictionary of color codes, then that means the inputted word
  // is the same as the correct word. So shut off all keyboard usage
  if (isSame === true)
  {
    keyboardOn = false;
    // the user has won, stop the timer
    var end = Date.now();
    // convert ms to seconds
    totalTime = (end - startTime)/1000;

    // user has beat the game
    victory = true;
    // make a jquery call to routes to communicate the victory and store the user information
    var data = {'time':totalTime};

    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processvictory",
        data: data,
        type: "POST",
        success:function(returned_data){
              returned_data = JSON.parse(returned_data);
              // if success is 1, then the inputted word is a valid word, the returned data will contain a dictionary of color codes for the grid row
              // use the dictionary information to properly color the the grid row and then move onto the next row for another inputted word
              if (returned_data["Success"] === 1)
              {
                gameover();
              }

            }
    });
  }
}
// taken from piano.js
// when the key goes up, bring it back to full size
function keyuplog(e){
  // after a short timeout, bring the key to full size
  setTimeout(function(){

    e.style.transform = 'scale(1)';
    // 450 ms for the timeout
  },250);
}

// this function handles clicks on the on screen keyboard
function keyboardclick()
{
  // only allow this functionality to occur when the keyboard on variable is true, this allows for the keyboard to be shut off
  if (keyboardOn === true)
  {
    // this gives the virtual keyboard the effect of being pressed when clicked
    this.style.transform = "scale(.95)";
    this.addEventListener("keyup", keyuplog(this));
    // calculates what the current grid box that will be filled
    currentGridBox = currentGuessRow * correctWordLength + currentGuessColumn;
    if (this.textContent === "Enter")
    {
      // if the current inputted word is the same length as the correct word, then send the word to verfied
      if(correctWordLength === currentWordLength)
      {
        var data_d = {'word':currentWordGuess};

        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
            url: "/wordvalidation",
            data: data_d,
            type: "POST",
            success:function(returned_data){
                  returned_data = JSON.parse(returned_data);
                  // if success is 1, then the inputted word is a valid word, the returned data will contain a dictionary of color codes for the grid row
                  // use the dictionary information to properly color the the grid row and then move onto the next row for another inputted word
                  if (returned_data["Success"] === 1)
                  {
                    // colors the current grid row before resetting and incrementing the grid information
                    colorsquares(returned_data);
                    // resets the column index and the current word length
                    currentGuessRow += 1;
                    currentGuessColumn = 0;
                    currentWordLength = 0;
                    currentWordGuess = "";
                    // resets the guest failure message
                    guess_failure.style.display = "none";
                    // increments the guess count
                    guessCount += 1;
                    // if the user has reached their max amount of guesses, which is the same as the size of the correct word, then turn off the keyboards functionality
                    if (guessCount === correctWordLength)
                    {
                      keyboardOn = false;
                      // the user has failed, stop the timer
                      var end = Date.now();
                      // convert ms to seconds
                      totalTime = (end - startTime)/1000;
                      console.log(totalTime);
                      if (victory !== true)
                      {
                        gameover()
                      }
                    }
                  }
                  else
                  {
                    // if success is not 1, then the word is not valid and alert the user that the word is not valid
                    guess_failure.style.display = "flex";
                  }
                }
        });
      }
      else
      {
        // alerts the user that the inputted word does not have enough characters
        not_enough.style.display = "flex";
      }

    }
    // handles backspace key press
    else if (this.textContent === "Backspace")
    {

      if (currentWordLength !== 0)
      {
        //  removes the last entered key by eliminating the text in the last grid box used
        gridColumn[currentGridBox-1].textContent = "";
        // decrements the word length and the column
        currentWordLength -= 1;
        currentGuessColumn -= 1;
        currentWordGuess = currentWordGuess.slice(0,-1);
        // resets the failure messages
        guess_failure.style.display = "none";
        not_enough.style.display = "none";
      }

    }
    // handles the rest of the viable keyboard character keypresses
    else
    {
      // this will continue filling in the grid until the current word length is equal to the correct word length
      if (currentWordLength < correctWordLength)
      {

        // tracks the time from the first user input,this only occurs when the timer has not been started
        if(currentGridBox === 0 && timerStart === false)
        {

          startTime = Date.now();

          timerStart = true;
        }
        // fills the current grid box with the text content associated with the keypress
        gridColumn[currentGridBox].textContent = this.textContent;
        currentWordLength += 1;
        currentGuessColumn += 1;
        currentWordGuess += this.textContent;
        // removes the failure element if the user had inputted a non valid guess and then backspace to correct it
        guess_failure.style.display = "none";
        not_enough.style.display = "none";
      }
    }
  }

}


// Adapted from piano.js
// function that handles the event for key presses
function keylog(e) {

  // only allow this functionality to occur when the keyboard on variable is true, this allows for the keyboard to be shut off
  if (keyboardOn === true)
  {
    // saves the current keycode
    let keycode = e.keyCode;

    currentGridBox = currentGuessRow * correctWordLength + currentGuessColumn;
    // trys the current keypress to see if it matches with one of the codes in the key map
    try
    {
        // tests if the right key is being pressed
        // if it matches, change the scale like the key has been pressed
        keyMap[keycode].style.transform = 'scale(1)';

    }
    catch(error)
    {
      // keep the value at 0 if its not a viable piano press
      keycode = 0;
    }
    if(keycode !== 0)
    {
      // handles enter key press
      if (keycode === 13)
      {
        // if the inputted word is the same length as the correct word, then it send ajax query to validate the word
        if(correctWordLength === currentWordLength)
        {
          var data_d = {'word':currentWordGuess};

          // SEND DATA TO SERVER VIA jQuery.ajax({})
          jQuery.ajax({
              url: "/wordvalidation",
              data: data_d,
              type: "POST",
              success:function(returned_data){
                    returned_data = JSON.parse(returned_data);
                    if (returned_data["Success"] === 1)
                    {
                      colorsquares(returned_data);
                      // resets the column index and the current word length
                      currentGuessRow += 1;
                      currentGuessColumn = 0;
                      currentWordLength = 0;
                      // resets the current word string
                      currentWordGuess = "";
                      // if success was returned then the word was valid, reset the invalid guess message
                      guess_failure.style.display = "none";
                      // increment the count of user guesses
                      guessCount += 1;
                      // if the guess amount is the same as the length of the correct word, then the user has no more guesses available
                      // shut off keyboard functionality
                      if (guessCount === correctWordLength)
                      {
                        keyboardOn = false;
                        // stop the timer, the user has lost
                        var end = Date.now();
                        // convert ms to seconds
                        totalTime = (end - startTime)/1000;

                        // if the user did not win with this last guess, call the gameover function
                        if (victory !== true)
                        {
                          gameover()
                        }
                      }
                    }
                    else
                    {
                      // if success is not 1, then the inputted word was not valid, alert the user that the word is not valid
                      guess_failure.style.display = "flex";
                    }
                  }
          });
        }
        else
        {
          // alert the user that the word does not have enough characters
          not_enough.style.display = "flex";
        }
      }
      // handles backspace key press
      else if (keycode === 8)
      {
        // cannot erase past 0 since 0 is the last character in the grid
        if (currentWordLength !== 0)
        {
          //  removes the last entered key by eliminating the text in the last grid box used
          gridColumn[currentGridBox-1].textContent = "";
          // decrements the word length and the column
          currentWordLength -= 1;
          currentGuessColumn -= 1;
          currentWordGuess = currentWordGuess.slice(0,-1);
          // resets the failure strings
          guess_failure.style.display = "none";
          not_enough.style.display = "none";
        }

      }
      // handles the rest of the viable keyboard character keypresses
      else
      {
        // this will continue filling in the grid until the current word length is equal to the correct word length
        if (currentWordLength < correctWordLength )
        {

          if(currentGridBox === 0 && timerStart === false)
          {

            startTime = Date.now();

            timerStart = true;
          }
          // fills the current grid box with the text content associated with the keypress
          gridColumn[currentGridBox].textContent = keyMap[keycode].textContent;
          currentWordLength += 1;
          currentGuessColumn += 1;
          // adds the inputted character to the current guess
          currentWordGuess += keyMap[keycode].textContent;
          // resets the not enough characters user warning
          not_enough.style.display = "none";
        }
      }
    }
  }

};
// this function hides the instruction prompt when the x is clicked and then turns on the keyboard so the user can play the game
function hide()
{
  instruction_prompt.style.display = "none";
  keyboardOn = true;
}
// MAIN code
// maps all the key objects with their correct keydown code
for (let i = 0; i < keys.length;i++)
{
  keyMap[keyPresses[i]] = keys[i];

}
// this goes through each key on the virtual keyboard and gives it a click event listener
keys.forEach(key => {
    // when a mouse over even occurs it calls the reveal function
    key.addEventListener("click", keyboardclick);
});
// calls the keylog function whenever a keydown event occurs
document.addEventListener('keydown', keylog);
// adds click listener to the exit button
exit_button.addEventListener("click", hide);
