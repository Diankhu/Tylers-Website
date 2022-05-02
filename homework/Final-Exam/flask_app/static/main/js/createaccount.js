// Javascript file for createaccount.html

const failure_str = document.querySelector(".failure");
const submit_button = document.querySelector(".submit");

function checkCredentials() {
    // grab the inputted username and password
    const username = document.querySelector('.username').value;
    const password = document.querySelector('.password').value;
    // package data in a JSON object
    var data_d = {'email': username, 'password': password}

    console.log(data_d)
    // SEND DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/processcreation",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              console.log(retruned_data)
              if (retruned_data["Success"] == 1)
              {
                // redirect to login when successful
                failure_str.setAttribute('style','display: none');
                window.location.href = "/login";
              }
              else
              {
                // alerts the user that there is already an account associated with that username
                failure_str.setAttribute('style','display: block');
              }

            }
    });
}


// main code /////
// adds click listener to the submit button
submit_button.addEventListener("click", checkCredentials);
