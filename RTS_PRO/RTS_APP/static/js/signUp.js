document.getElementById('signupForm').onsubmit = function (e) {
    var username = document.getElementById('username').value;
    var email = document.getElementById('email').value;
    var password1 = document.getElementById('password1').value;
    var password2 = document.getElementById('password2').value;
    if (username === "" || email === "" || password1 === "" || password2 === "") {
        e.preventDefault();
        alert("All fields are required!")
    }
};