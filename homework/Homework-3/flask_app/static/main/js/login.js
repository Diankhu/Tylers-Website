// Javascript file for login.html
const failure_str = document.querySelector(".failure");
const account_failure_str = document.querySelector(".no_account");
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
        url: "/processlogin",
        data: data_d,
        type: "POST",
        success:function(retruned_data){
              retruned_data = JSON.parse(retruned_data);
              console.log(retruned_data)
              if (retruned_data["Success"] == 1)
              {
                // redirect to the projects home page and reset the failure messages
                failure_str.setAttribute('style','display: none');
                account_failure_str.setAttribute('style','display: none');
                window.location.href = "/projects";
              }
              else if (retruned_data["Account"] == 1)
              {
                // this shows that there is not an account associated with the username
                failure_str.setAttribute('style','display: none');
                account_failure_str.setAttribute('style','display: block');

              }
              else
              {
                // this alerts the user that the username and password is incorrect
                account_failure_str.setAttribute('style','display: none');
                failure_str.setAttribute('style','display: block');
              }

            }
    });
}
// main code /////
// adds click listener to the submit button
submit_button.addEventListener("click", checkCredentials);
