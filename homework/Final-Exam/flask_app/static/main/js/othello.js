const gridItem = document.querySelectorAll(".grid_item");
const gameStart = document.querySelector(".start_button");
const difficulty_label = document.querySelector(".difficulty_label");
const endGame = document.querySelector(".end_button");
var activePlayer = "black";


function start()
{
    const difficulty = document.querySelector(".difficulty");
    if(difficulty.value !== "")
    {


        // saves the difficulty to the browsers session variable
        var data = {'difficulty':difficulty.value};
        // SEND DATA TO SERVER VIA jQuery.ajax({})
        jQuery.ajax({
        url: "/processgamestart",
        data: data,
        type: "POST",
        success:function(returned_data) {

        }});
        // perform multiple tasks to start game like creating starting board, disabling start game form
        // making end game button appear instead
        difficulty.style.display = "none";
        gameStart.style.display = "none";
        difficulty_label.style.display = "none";
        endGame.style.display = "block";
        for (let item = 0; item < gridItem.length; item++)
        {
            if(gridItem[item].getAttribute("data-value") === "33")
            {
                gridItem[item].children[0].classList.add("white_player");
                gridItem[item].classList.add("white");
            }
            else if(gridItem[item].getAttribute("data-value") === "34")
            {
                gridItem[item].children[0].classList.add("black_player");
                gridItem[item].classList.add("black");
            }
            else if(gridItem[item].getAttribute("data-value") === "43")
            {
                gridItem[item].children[0].classList.add("black_player");
                gridItem[item].classList.add("black");
            }
            else if(gridItem[item].getAttribute("data-value") === "44")
            {
                gridItem[item].children[0].classList.add("white_player");
                gridItem[item].classList.add("white");
            }
        }
    //     move to normal find next move function
        activePlayer = "black";
        possibleMoves("black");

    }


}
function take()
{
    let clicked_square = 0;
    let added_class = "";
    let removed_class = "";
    // find index in grid that equates to current click
    for (let item = 0; item < gridItem.length; item++)
    {
        if(gridItem[item] === this)
        {
            clicked_square = item;
        }
    }
    // see what players turn it is rn
    var currentPlayer = "";
    var otherplayer = "";
    if (activePlayer === "black")
    {
        currentPlayer = "black";
        otherplayer = "white";
        added_class = "black_player";
        removed_class = "white_player";
    }
    else
    {
        currentPlayer = "white";
        otherplayer = "black";
        added_class = "white_player";
        removed_class = "black_player";
    }
    let possibleFirstMoves = [-8,-7,1,9,8,7,-1,-9];
    for (let x = 0; x < possibleFirstMoves.length; x++)
    {
        var moveIsPossible = false;
        var spotsTaken=[];
        let currentsquare = Number(clicked_square) + possibleFirstMoves[x];
        // keep iterating until it sees the end of the board, its, empty spot, or its own color chip
        while(true)
        {

            // this shows if the spot is blank
            if(gridItem[currentsquare].classList.contains(currentPlayer)===false
                && gridItem[currentsquare].classList.contains(otherplayer)=== false )
            {
                break;
            }
            // if the spot is the same color, then it is not valid move
            else if(gridItem[currentsquare].classList.contains(currentPlayer)===true)
            {

                if(moveIsPossible === true)
                {
                    // take control of opponents chips
                    for (let y = 0; y < spotsTaken.length; y++)
                    {

                        gridItem[spotsTaken[y]].children[0].classList.remove(removed_class);
                        gridItem[spotsTaken[y]].classList.remove(otherplayer);
                        gridItem[spotsTaken[y]].children[0].classList.add(added_class);
                        gridItem[spotsTaken[y]].classList.add(currentPlayer);

                        break;
                    }
                    break;
                }
                else
                {
                    break;
                }
            }
            // if the square is the other players, the move can be valid, must explore to make sure there is ana available spot to place in
            else if(gridItem[currentsquare].classList.contains(otherplayer)=== true)
            {
                moveIsPossible = true;
                spotsTaken.push(currentsquare);
                currentsquare += possibleFirstMoves[x];
            }
            else if (gridItem[currentsquare] === undefined)
            {
                break;
            }
        }

    }
    this.children[0].classList.add(added_class);
    this.classList.add(currentPlayer);

    // remove all div's with possible class and remove this event listeners so it can change to other players turn
    const possibleTakes = document.querySelectorAll(".possible");
    for (let x = 0; x < possibleTakes.length; x++)
    {
        possibleTakes[x].classList.remove("possible");
        possibleTakes[x].parentElement.removeEventListener("click",take);
    }
}

function possibleMoves(player)
{
    // see what players turn it is rn
    var currentPlayer = "";
    var otherplayer = "";
    if (player === "black")
    {
        currentPlayer = "black";
        otherplayer = "white";
    }
    else
    {
        currentPlayer = "white";
        otherplayer = "black";
    }
    console.log(currentPlayer);
    // iterate through current players potential moves and highlight them for the player to see
    // highlights them by adding a class that gives the space a blue circle and adds eventlistener to players click
    console.log(gridItem);
    for (let item = 0; item < gridItem.length; item++)
    {
        if (gridItem[item].classList.contains(currentPlayer)=== true)
        {
        //     validate if this players chip can be
        //     possible moves are diagonals and vertical/horizontal
            console.log(gridItem[item].classList.contains(currentPlayer));
            console.log(gridItem[item].getAttribute("data-value"));
            let possibleFirstMoves = [-8,-7,1,9,8,7,-1,-9];
            for (let x = 0; x < possibleFirstMoves.length; x++)
            {
                var moveIsPossible = false;
                var spotsTaken=[];
                let currentsquare = Number(item) + possibleFirstMoves[x];
                // keep iterating until it sees the end of the board, its, empty spot, or its own color chip
                while(true)
                {

                    // this shows if the spot is blank
                    if(gridItem[currentsquare].classList.contains(currentPlayer)===false
                        && gridItem[currentsquare].classList.contains(otherplayer)=== false )
                    {
                        // if it possible, make the square interactable
                        if(moveIsPossible === true)
                        {
                            gridItem[currentsquare].children[0].classList.add("possible");
                            gridItem[currentsquare].addEventListener("click",take);
                            break;
                        }
                        else
                        {
                            break;
                        }
                    }
                    // if the spot is the same color, then it is not valid move
                    else if(gridItem[currentsquare].classList.contains(currentPlayer)===true)
                        {
                            break;
                        }
                    // if the square is the other players, the move can be valid, must explore to make sure there is ana available spot to place in
                    else if(gridItem[currentsquare].classList.contains(otherplayer)=== true)
                    {
                        moveIsPossible = true;
                        spotsTaken.push(currentsquare);
                        currentsquare += possibleFirstMoves[x];


                    }
                    else if (gridItem[currentsquare] === undefined)
                    {
                        break;
                    }
                }

            }



        }

    }



}


//main

gameStart.addEventListener("click",start)

//initialize the grid
var grid = Array.apply(null, Array(8)).map(function () {});
for (let item = 0; item < grid.length; item++)
{
    grid[item] = Array(8);
}
var counter = 0;
var current_row=0;
//put the grid divs into the grid
for (let item = 0; item < gridItem.length; item++)
{
    if(counter >= 8)
    {
        counter = 0;
        current_row += 1;
    }
    grid[current_row][counter] = gridItem[item];
    counter += 1;
}
