
///variables and constants
const back = document.querySelector(".back_button");
const confirmation_boxes = document.querySelectorAll(".confirmation");
const correct_box = document.querySelector(".correct");
const wrong_box = document.querySelector(".wrong");
const restart_button = document.querySelector(".restart_outer");
const check =  document.querySelectorAll(".check");
var cards = 'Empty';
var card_deck = [];
var deck_index = 0;

/// functions
function onclick()
{
    window.location.href = "/Deck";

}

function cardRetrieval()
{


    jQuery.ajax({
      url: "/retrievecards",
      type: "POST",
      success:function(returned_data){
          returned_data = JSON.parse(returned_data);
            cards = returned_data;
            // cards format is card_id,deck_id, front
            document.querySelector(".front_card").innerHTML = cards[0]["front"];
            document.querySelector(".back_card").innerHTML = cards[0]["back"];
            // puts the cards into an array object that will get iterated as the user studies
            for (let i = 0; i < cards.length; i++) {
                var card = [];
                card[0]= cards[i]["front"];
                card[1]= cards[i]["back"];
                card[2]= "No";
                card_deck.push(card);
            }
            console.log(card_deck);
          }
  });
}
// this function ends the study session and prompts user to restart the deck and start again
function end()
{
    check.forEach(box => {

        box.style.display = "none";

    });

    restart_button.style.display = "flex";
}
// this function finds the next card that has not been correctly answered
function next()
{
    // resets the deck index when it is too large
    if(deck_index >= card_deck.length)
    {
        deck_index = 0;
        console.log("shuffled");
        shuffle(card_deck);
        console.log(card_deck);

    }

    // if the new index is not greater than the deck length, then iterate to the next card's info
    if (deck_index < card_deck.length)
    {
        // this will count how many cards its checked, when cards checked = length,then all been checked and restart
        let count = 0;
        // check if the user has already correctly remembered the new card before showing it
        // if the new card has been remembered before, iterate to the next one, if there are none left, skip to end
        while(true)
        {

            if(count >= card_deck.length)
            {
                end();
                break;

            }
            if(deck_index >= card_deck.length)
            {
                deck_index = 0;
                console.log("shuffled");
                shuffle(card_deck);
                console.log(card_deck);

            }
            else if(card_deck[deck_index][2] === "Yes")
            {
                console.log("yes");
                deck_index += 1;
                count += 1;
            }
            else
            {
                console.log("no");
                document.querySelector(".front_card").innerHTML = card_deck[deck_index][0];
                document.querySelector(".back_card").innerHTML = card_deck[deck_index][1];
                break;
            }
        }
    }

}
function confirmation()
{

    if(this.id === "correct")
    {
        let current_front = document.querySelector(".front_card").innerHTML;
        for (let k = 0; k < card_deck.length; k++) {
            if(card_deck[k][0] === current_front)
            {
                card_deck[k][2] = "Yes";
            }
        }
    }
    deck_index += 1;
    console.log(deck_index);
    next()
}
// shuffle function cited from https://stackoverflow.com/questions/2450954/how-to-randomize-shuffle-a-javascript-array
function shuffle(array) {
  let currentIndex = array.length,  randomIndex;

  // While there remain elements to shuffle.
  while (currentIndex > 0) {

    // Pick a remaining element.
    randomIndex = Math.floor(Math.random() * currentIndex);
    currentIndex--;

    // And swap it with the current element.
    [array[currentIndex], array[randomIndex]] = [
      array[randomIndex], array[currentIndex]];
  }

  return array;
}
function restart()
{
    for (let k = 0; k < card_deck.length; k++)
    {
        card_deck[k][2] = "no";
    }
    console.log("restarted");
    restart_button.style.display = "none";
    check.forEach(box => {

        box.style.display = "flex";

    });
    shuffle(card_deck);
    deck_index = 0;
    next();

}


///main code
back.addEventListener("click", onclick);
cardRetrieval();

confirmation_boxes.forEach(box => {

  box.addEventListener("click",confirmation)

});
restart_button.addEventListener("click", restart);