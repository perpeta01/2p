document.getElementById("start-button").onclick = function() {
    fetch('/start', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            console.log(data.status);
            document.getElementById("bet-button").style.display = "inline"; // Mostra o botão de apostas
        });
};

document.getElementById("bet-button").onclick = function() {
    fetch('/start_betting', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data.status));
};

document.getElementById("stop-button").onclick = function() {
    fetch('/stop_betting', { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data.status));
};
