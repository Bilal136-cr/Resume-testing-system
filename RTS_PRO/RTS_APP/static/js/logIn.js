document.getElementById('loginForm').onsubmit = function (e) {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    if (username === "" || password === "") {
        e.preventDefault();
        alert("Both fields are required!");
    }
};
