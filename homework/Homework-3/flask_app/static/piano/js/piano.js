/* javascript.js*/

// DOCUMENT VARIABLES
// grabs every element with the key class description
const keys = document.querySelectorAll(".key");
// grabs every element that has a code class description
const codes = document.querySelectorAll(".code");
// this is the div that contains all the keys
const piano = document.querySelector(".all_keys");
const base = document.querySelector(".great_old_one");
const piano_description = document.querySelector("#piano_description");
// NON DOCUMENT VARIABLES
const keypresses = [87,69,84,89,85,79,80,65,83,68,70,71,72,74,75,76,59];
// contains the mapping of keydown codes to their respective sound
const sounds = {65:"http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
                87:"http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
                83:"http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
                69:"http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
                68:"http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
                70:"http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
                84:"http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
                71:"http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
                89:"http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
                72:"http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
                85:"http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
                74:"http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
                75:"http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
                79:"http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
                76:"http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
                80:"http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
                59:"http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"};
// sound for when the great old one appears
const scary = "https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1";
// contains mapping keydown codes and their respective objects
var key_map = {}
// contains the secret code that reveals the great old one
const secret = [87,69,83,69,69,89,79,85];
// keeps track of how many correct keys have been pressed for the secret code
let count = 0;
// boolean that shows if the keys are playable right now
let playable = true;

// FUNCTIONS
// function that reveals the codes for the piano keys
function reveal()
{

  // for each element that has a code, change the display and reveal the code
  codes.forEach(code => {
    code.setAttribute('style','opacity: 1');
  });
}
// function handles the hiding of the key codes
function hide()
{
  // after a short timeout, go through each element with a code and hide the code again
  setTimeout(function(){
    codes.forEach(code => {
      // changes the display back to none to hide the code once again
      code.setAttribute('style','opacity: 0');
    });
    // 150 ms for the timeout
  },150);
}

// when the key goes up, bring it back to full size
function keyuplog(e){
  // after a short timeout, bring the key to full size
  setTimeout(function(){

    key_map[e].style.transform = 'scale(1)';
    // 450 ms for the timeout
  },450);
}

// function that handles the event for key presses
function keylog(e) {
  // saves the current keycode
  let keycode = e.keyCode;
  if( playable === true)
  {
    // trys the current keypress to see if it matches with one of the codes in the key map
    try
    {

        // if it matches, change the scale like the key has been pressed
        key_map[keycode].style.transform = 'scale(.95)';
        keySound= new Audio(sounds[keycode]);
    }
    catch(error)
    {
      // keep the value at 0 if its not a viable piano press
      keycode = 0;
    }

    // only resets if the key was actually pressed aka keycode is non 0
    if(keycode !== 0)
    {
      // this handles the audio for the key, when it ready to play, it will play
      keySound.addEventListener("canplaythrough", event => {
        // this makes it so that when a key is held down, the sound is played only once
        if (!e.repeat)
        {

          keySound.play();
        }
        });
      // this makes it so that the string does not count when a key is held down
      if (!e.repeat)
      {
        // if the codes match up then add a count
        if (keycode === secret[count])
        {
          count += 1;

        }
        else
        {
          count = 0;
        }
        if (count === 8)
        {
          // if they got all 8 characters correct then make the image appear
          piano.setAttribute('style','display:none');
          base.setAttribute('style', 'opacity: 1');

          // makes the piano no longer respond to key presses
          playable = false;
          piano_description.textContent = "I have awoken.";
          keySound = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1");
          // play the scary sound

          keySound.addEventListener("canplaythrough", event => {
            // this makes it so that when a key is held down, the sound is played only once

              keySound.play();
          });
        }
      }

      key_map[keycode].addEventListener("keyup", keyuplog(keycode));


    }
    else if (keycode === 0)
    {
      count = 0;
    }
  }

};


// MAIN code
// maps all the key objects with their correct keydown code
for (let i = 0; i < keys.length;i++)
{
  key_map[keypresses[i]] = keys[i];
}

// this goes through each key on the piano and gives it a mouse over event listener
keys.forEach(key => {
    // when a mouse over even occurs it calls the reveal function
    key.addEventListener("mouseover", reveal);
});
// when the mouse leaves the div containing the all the keys, it calls the hide function
piano.addEventListener("mouseleave",hide);
// calls the keylog function whenever a keydown event occurs
document.addEventListener('keydown', keylog);
