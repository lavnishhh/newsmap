var sig

const sleep = ms => new Promise(r => setTimeout(r, ms));
function handleCredentialResponse(response) {
    const data = response.credential.split('.');
    var payload = JSON.parse(atob(data[1]));
    const ID = payload.sub
    document.getElementById('googleSignInButton').children[1].style.display = 'none';
    document.getElementById('profile-picture').src = payload.picture
    document.getElementById('profile-picture').style.display = 'block';
    document.getElementById("account-name").textContent = payload.name;
    document.getElementById('logout').style.color = "#FF0000";
    const logoutListener = document.getElementById('logout').addEventListener('click', (event) => {
        signOut();
        event.target.disabled = true;
        document.getElementById('logout').removeEventListener('click', logoutListener);
        document.getElementById('logout').style.color = "#666666";
    })
  }


async function createSignIn() {
    return true;
    google.accounts.id.initialize({
        client_id: "235879741882-7jnpbc2mhv8nrpdcoch40bk1h8cnvn1p.apps.googleusercontent.com",
        callback: handleCredentialResponse
    });
    document.getElementById('profile-picture').style.display= "none";
}

function signOut(){
    google.accounts.id.disableAutoSelect()
    document.getElementById('googleSignInButton').children[1].style.display = 'block';
    document.getElementById('profile-picture').src = "https://cdn-icons-png.flaticon.com/128/8141/8141083.png"
    document.getElementById('profile-picture').style.display = 'none';
    document.getElementById("account-name").textContent = "User"
}

document.getElementById('loc-search').addEventListener('focusin',() => {
    document.getElementById('loc-search-menu').style.display = 'block';
    document.getElementById('loc-search-menu').style.opacity = 1;
});

document.getElementById('loc-search').addEventListener('focusout', () => {
    document.getElementById('loc-search-menu').style.opacity = 0;
    sleep(200).then(() => {
        document.getElementById('loc-search-menu').style.display = 'none';
    })
});


document.getElementById('source-search').addEventListener('focusin',() => {
    document.getElementById('source-search-menu').style.display = 'block';
    document.getElementById('source-search-menu').style.opacity = 1;
});

document.getElementById('source-search').addEventListener('focusout', () => {
    document.getElementById('source-search-menu').style.opacity = 0;
    sleep(200).then(() => {
        document.getElementById('source-search-menu').style.display = 'none';
    })
});

document.getElementById('menu-button').addEventListener('focusin',() => {
    console.log('hello')
    document.getElementById('settings-menu').style.display = 'block';
    document.getElementById('settings-menu').style.opacity = 1;
});

document.getElementById('menu-button').addEventListener('focusout', () => {
    document.getElementById('settings-menu').style.opacity = 0;
    sleep(200).then(() => {
        document.getElementById('settings-menu').style.display = 'none';
    })
});
//query = '?source=' + source + '&loc='  + place.toLowerCase()
// var newurl = window.location.origin + window.location.pathname + query;
//           window.history.pushState({path:newurl},'',newurl);