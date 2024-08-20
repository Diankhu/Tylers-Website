const back = document.querySelector(".back_button");
const card_delete = document.querySelectorAll(".delete");
const study = document.querySelector(".study_start");

function onclick()
{
    window.location.href = "/Flashcard";

}

function deleteWord()
{
    const number = this.parentElement.children[0].innerText
    const card_id = {"number":number}

    jQuery.ajax({
      url: "/processworddelete",
      data: card_id,
      type: "POST",
      success:function(returned_data){
            window.location.href = "/Deck";

          }
  });
}

function start()
{
    window.location.href = "/Study";

}



back.addEventListener("click", onclick);
try {
  card_delete.addEventListener("click",deleteWord)
} catch (error) {

}
card_delete.forEach(card => {
    try {
  card.addEventListener("click",deleteWord)
        } catch (error) {

}
});
study.addEventListener("click",start);