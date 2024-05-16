// Constants to easily refer to pages

// TODO:  On page load, read the path and whether the user has valid credentials:
//        - If they ask for the splash page ("/"), display it
//        - If they ask for the login page ("/login") and don't have credentials, display it
//        - If they ask for the login page ("/login") and have credentials, send them to "/"
//        - If they ask for any other valid page ("/profile" or "/room") and do have credentials,
//          show it to them
//        - If they ask for any other valid page ("/profile" or "/room") and don't have
//          credentials, send them to "/login", but remember where they were trying to go. If they
//          login successfully, send them to their original destination
//        - Hide all other pages

// TODO:  When displaying a page, update the DOM to show the appropriate content for any element
//        that currently contains a {{ }} placeholder. You do not have to parse variable names out
//        of the curly  braces—they are for illustration only. You can just replace the contents
//        of the parent element (and in fact can remove the {{}} from index.html if you want).

// TODO:  Handle clicks on the UI elements.
//        - Send API requests with fetch where appropriate.
//        - Parse the results and update the page.
//        - When the user goes to a new "page" ("/", "/login", "/profile", or "/room"), push it to
//          History

// TODO:  When a user enters a room, start a process that queries for new chat messages every 0.1
//        seconds. When the user leaves the room, cancel that process.
//        (Hint: https://developer.mozilla.org/en-US/docs/Web/API/setInterval#return_value)

const SPLASH = document.querySelector(".splash");
const PROFILE = document.querySelector(".profile");
const LOGIN = document.querySelector(".login");
const ROOM = document.querySelector(".room");

const POST_MESSAGE = '/api/room/post'
const SIGNUP_POINT = '/api/signup';
const SIGNUP_DETAILS_POINT = '/api/signup/details';
const LOGIN_POINT = '/api/login';
const NEW_ROOM_POINT = '/api/rooms/new';
const ALL_MESSAGES_URL = '/api/room/messages';
const ALL_ROOMS = '/api/rooms';
const UPDATE_USERNAME = '/api/update/username';
const UPDATE_PASSWORD = '/api/update/password';
const UPDATE_ROOM = '/api/update/room';
const ERROR = '/api/error';

let rooms = {};
let old_path = '';
let CURRENT_ROOM = 0;

let loginDict = {
  userName: '',
  password: ''
};

let getAllMsgsRequest = {
  room_id: 0
};

let postRequest = {
  room_id: 0,
  body: ''
};

let postUpdateNameRequest = {
  user_name: ''
};

let postUpdatePassRequest = {
  Password: ''
};

let postUpdateRoomRequest = {
  name: '',
  room_id: 0
};

let signUpDetails = {
  userName: '',
  Password: ''
};

// Custom validation on the password reset fields
const passwordField = document.querySelector(".profile input[name=password]");
const repeatPasswordField = document.querySelector(".profile input[name=repeatPassword]");
const repeatPasswordMatches = () => {
  const p = document.querySelector(".profile input[name=password]").value;
  const r = repeatPassword.value;
  return p == r;
};

const checkPasswordRepeat = () => {
  const passwordField = document.querySelector(".profile input[name=password]");
  if(passwordField.value == repeatPasswordField.value) {
    repeatPasswordField.setCustomValidity("");
    return;
  } else {
    repeatPasswordField.setCustomValidity("Password doesn't match");
  }
}

passwordField.addEventListener("input", checkPasswordRepeat);
repeatPasswordField.addEventListener("input", checkPasswordRepeat);


// Helper functions
async function createUrl(endPoint, requestBody, requestHeader, endType){
  let url = endPoint + (Object.keys(requestBody).length > 0 
                        ? ("?" + Object.keys(requestBody).map((key) => key+"="+encodeURIComponent(requestBody[key])).join("&")) 
                        : "");

  let urlHeaders = new Headers();
  urlHeaders.append("Accept", "application/json");
  urlHeaders.append("Content-Type", "application/json");
  urlHeaders.append("Api-Key", localStorage.getItem('API-KEY'));
  urlHeaders.append("User-Id", localStorage.getItem('User-Id'));

  Object.keys(requestHeader).forEach(function(key) {
    urlHeaders.append(key, requestHeader[key]);
  });

  const myInit = {
    method: endType,
    headers: urlHeaders,
  };
  console.log(url);
  data = await fetch(url, myInit);
  jsonForm = await data.json();
  return jsonForm
}

let showOnly = (element) => {
  CURRENT_ROOM = 0;

  SPLASH.classList.add("hide")
  PROFILE.classList.add("hide");
  LOGIN.classList.add("hide");
  ROOM.classList.add("hide");

  element.classList.remove("hide");
}

let showElement = (cls) => {
  document.querySelector(cls).classList.remove("hide");
}

let hideElement = (cls) => {
  document.querySelector(cls).classList.add("hide");
}

function postLoggedIn(){
  hideElement(".loginHeader .loggedOut");
  hideElement(".signup");
  showElement(".loginHeader .loggedIn");
  showElement(".create");

  
  let usernameSpan = document.getElementsByClassName('username');
  for(var i=0; i < usernameSpan.length; i++){
    if(usernameSpan[i].innerHTML.includes("Welcome")){
      usernameSpan[i].innerHTML = 'Welcome back, <a onclick="updateDetails()" style="text-decoration: underline; cursor: pointer; color: blue;">' + localStorage.getItem('User-Name') + 
      '</a>! <a class="logout" onclick="logoutUser()" style="text-decoration: underline; cursor: pointer;">(logout)</a>'; 
    }
    else {
      usernameSpan[i].innerHTML = '<a onclick="updateDetails()" style="text-decoration: underline; cursor: pointer; color: blue;">' + localStorage.getItem('User-Name') + 
      '</a>! <a class="logout" onclick="logoutUser()" style="text-decoration: underline; cursor: pointer;">(logout)</a>'; 
    }
  }
  var usernameInput = document.querySelector('input[name="username"]');
  usernameInput.value = localStorage.getItem('User-Name');
}

function postLoggedOut(){
  hideElement(".loginHeader .loggedIn");
  hideElement(".create");
  showElement(".loginHeader .loggedOut");
  showElement(".signup");
}

function defaultHide(){
  document.querySelector('.editRoomName').classList.add('hide');
  document.querySelector('.displayRoomName').classList.remove('hide');
}

function hideUnhidableByHideCls(){
  document.querySelector('.login .failed').setAttribute("style", "display: none");
}

function setUrlAndLoad(url){
  window.history.pushState(null, null, '/' + url);
  router();
}






// Identity management
async function signUpUser() {
  postMsg = await createUrl(SIGNUP_POINT, {}, {}, 'POST');
  localStorage.setItem('API-KEY', postMsg.api_key);
  localStorage.setItem('User-Id', postMsg.user_id);
  localStorage.setItem('User-Name', postMsg.user_name);
  setUrlAndLoad('');
}

async function signUpUserWithDetails() {
  signUpDetails.userName = document.getElementById('username').value;
  signUpDetails.Password = document.getElementById('password').value;
  postMsg = await createUrl(SIGNUP_DETAILS_POINT, {}, signUpDetails, 'POST');
  localStorage.setItem('API-KEY', postMsg.api_key);
  localStorage.setItem('User-Id', postMsg.user_id);
  localStorage.setItem('User-Name', postMsg.user_name);
  setUrlAndLoad('');
}

function logoutUser(){
  localStorage.removeItem('API-KEY');
  rooms = {};
  let messagesDiv = document.body.querySelector(".roomList");
  let child = messagesDiv.lastElementChild;
  while (child) {
    messagesDiv.removeChild(child);
    child = messagesDiv.lastElementChild;
  }
  document.querySelector('.noRooms').setAttribute("style", "display: block");
  setUrlAndLoad('');
}

async function loginUser(){
  loginDict.userName = document.getElementById('username').value;
  loginDict.password = document.getElementById('password').value;
  document.getElementById('username').value = '';
  document.getElementById('password').value = '';
  let loginUsr = await createUrl(LOGIN_POINT, {}, loginDict, 'POST');
  if(loginUsr.api_key.length > 0){
    localStorage.setItem('API-KEY', loginUsr.api_key);
    localStorage.setItem('User-Id', loginUsr.user_id);
    localStorage.setItem('User-Name', loginUsr.user_name);
    setUrlAndLoad(old_path.length > 0 ? old_path : '');
  } else {
    document.querySelector('.login .failed').setAttribute("style", "display: flex");
  }
  return;
}

async function updateUsername(){
  postUpdateNameRequest.user_name = document.querySelector('input[name="username"]').value;
  postMsg = await createUrl(UPDATE_USERNAME, postUpdateNameRequest, {}, 'POST');
  localStorage.setItem('User-Name', postMsg['name']);
  postLoggedIn();
}

async function updatePassword(){
  let pass1 = document.querySelector('input[name="password"]').value;
  let pass2 = document.querySelector('input[name="repeatPassword"]').value;

  if(pass1 == pass2){
    postUpdatePassRequest.Password = pass1;
    postMsg = await createUrl(UPDATE_PASSWORD, {}, postUpdatePassRequest, 'POST');
  }
  postLoggedIn();
}





// Room functions
async function createNewRoom(){
  let newRoom = await createUrl(NEW_ROOM_POINT, {}, {}, 'POST');
  setUrlAndLoad('room/' + newRoom['room_id']);
}

async function postMessage(body) {
  postRequest.room_id = CURRENT_ROOM;
  postRequest.body = body;
  postMsg = await createUrl(POST_MESSAGE, postRequest, {}, 'POST')
  document.getElementById("commentTA").value = '';
}

function loadRoom(roomId, roomName) {
  setUrlAndLoad("room/" + roomId);
}

function toggleEditMode(){
  document.querySelector('.displayRoomName').classList.add('hide');
  document.querySelector('.editRoomName').classList.remove('hide');
}

async function populateRooms(){
  rooms = await createUrl(ALL_ROOMS, {}, {}, 'GET')
  let messagesDiv = document.body.querySelector(".roomList");
  let child = messagesDiv.lastElementChild;
  while (child) {
    messagesDiv.removeChild(child);
    child = messagesDiv.lastElementChild;
  }

  if(Object.keys(rooms).length > 0){
    document.querySelector('.noRooms').setAttribute("style", "display: none");
  } else {
    document.querySelector('.noRooms').setAttribute("style", "display: block");
  }

  Object.keys(rooms).forEach(key => {
    let message = document.createElement("a");
    message.setAttribute("style", "cursor: pointer;")
    message.setAttribute("onclick", "loadRoom(" + key + ', "' + rooms[key]['name'] + '")');
    message.innerHTML = key + ': <strong>' + rooms[key]['name'] + "</strong>";
    messagesDiv.append(message);
  });
}

async function saveRoomName() {
  postUpdateRoomRequest.name = document.querySelector('#roomNameInput').value;
  postUpdateRoomRequest.room_id = CURRENT_ROOM;
  var response = await createUrl(UPDATE_ROOM, postUpdateRoomRequest, {}, 'POST');
  document.querySelector('.displayRoomName strong').innerHTML = postUpdateRoomRequest.name;
  document.querySelector('.editRoomName').classList.add('hide');
  document.querySelector('.displayRoomName').classList.remove('hide');
}




// Profile load

async function updateDetails(){
  setUrlAndLoad('profile');
}




// Show me a new "page"
let router = async () => {
  let path = window.location.pathname;
  if(localStorage.getItem('API-KEY') == null){
    postLoggedOut();

    // There is no point of splash screen if we point every request to login screen if user isn't loggedin.
    // Hence, we will redirect all the requests other than home to login screen
    if(path != "/" && path.length > 1){
      splitted = path.split('/');
      old_path = splitted[1];
      for(var j = 2; j < splitted.length; j++){
        old_path += '/' + splitted[j];
      }
      window.history.pushState(null, null, '/login');
      path = '/login';
    }
  }
  else{
    postLoggedIn();

    if(path == "/login"){
      window.history.pushState(null, null, '/');
      path = '/';
    }
  }
  defaultHide();
  hideUnhidableByHideCls();

  // We dont know what to do with /room so redirecitng it to home
  if(path == "/" || path == "/room") {
    document.title = 'Home';
    showOnly(SPLASH);
    if(localStorage.getItem('API-KEY') != null){
      await populateRooms();
    }
  }
  else if(path == "/profile"){
    document.title = 'Signup and Update';
    showOnly(PROFILE);
  }
  else if(path.startsWith("/room/")) {
    document.title = 'Rooms';
    showOnly(ROOM);

    CURRENT_ROOM = path.split('/')[2];
    document.title = 'Room ' + CURRENT_ROOM;
    // if(Object.keys(rooms).length == 0){
    await populateRooms();
    document.querySelector('.displayRoomName strong').innerHTML = rooms[CURRENT_ROOM]['name'];
    document.querySelector('#roomNameInput').value = rooms[CURRENT_ROOM]['name'];
    document.querySelector('.roomDetail #roomId').innerHTML = '/rooms/' + CURRENT_ROOM;

  }
  else if(path == "/login") {
    document.title = 'Login';
    showOnly(LOGIN);
  } 
  else {
    await createUrl(ERROR, {}, {}, 'POST');
    console.log("I don't know how we got to "+path+", but something has gone wrong");
  }
}

window.addEventListener("DOMContentLoaded", router);
window.addEventListener("popstate", router);




// Message polling
async function startMessagePolling() {
  setInterval(async () => {
    if (CURRENT_ROOM == 0) return;

    console.log(CURRENT_ROOM);
    getAllMsgsRequest.room_id = CURRENT_ROOM;
    let messages = await createUrl(ALL_MESSAGES_URL, getAllMsgsRequest, {}, 'GET')
    let messagesDiv = document.body.querySelector(".messages");
    let child = messagesDiv.lastElementChild;
    while (child) {
      messagesDiv.removeChild(child);
      child = messagesDiv.lastElementChild;
    }

    Object.keys(messages).forEach(key => {
      let message = document.createElement("message");
      let author = document.createElement("author");
      author.innerHTML = messages[key].name;
      let content = document.createElement("content");
      content.innerHTML = messages[key].body;
      message.appendChild(author);
      message.appendChild(content);
      messagesDiv.append(message);
    });
  }, 500);
  return;
}
