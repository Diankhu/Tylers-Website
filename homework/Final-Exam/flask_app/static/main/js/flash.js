const decks = document.querySelectorAll(".deck");




function onclick()
{
    var deck_id = {"number": this.children[0].innerText};
    console.log(deck_id);

    jQuery.ajax({
      url: "/processdeckclick",
      data: deck_id,
      type: "POST",
      success:function(returned_data){
            window.location.href = "/Deck";

          }
  });

}


// main code
//gives each deck an event listener
decks.forEach(deck => {
    // when a mouse over even occurs it calls the reveal function
    deck.addEventListener("click", onclick);
});
