function loadPreview() {
    const url = document.getElementById("url").value;
    if (!url) return;

    fetch(`/preview?url=${encodeURIComponent(url)}`)
    .then(res => res.json())
    .then(data => {
        if (data.thumbnail) {
            document.getElementById("preview").innerHTML =
                `<h4>${data.title}</h4>
                 <img src="${data.thumbnail}" class="thumbnail">`;
        }
    });
}

function startDownload() {
    const url = document.getElementById("url").value;
    const mode = document.getElementById("mode").value;

    const log = document.getElementById("log");
    log.innerText = "";

    const evtSource = new EventSource(`/download?url=${encodeURIComponent(url)}&mode=${mode}`);

    evtSource.onmessage = function(event) {
        const data = event.data;

        if (data.startsWith("PROGRESS:")) {
            const parts = data.replace("PROGRESS:", "").split("|");

            const percent = parts[0].replace("%","").trim();
            const size = parts[1];
            const speed = parts[2];

            document.getElementById("progress").style.width = percent + "%";
            document.getElementById("stats").innerText =
                `${percent}% | ${size} | ${speed}`;
        }
        else if (data.startsWith("LOG|")) {
            appendLog(data.replace("LOG|",""));
        }
        else if (data === "DONE") {
            log.innerText += "\n✅ Done\n";
            evtSource.close();
            loadHistory();
        }
    };
}

function downloadFile(file) {
    window.open(`/download-file?file=${encodeURIComponent(file)}`, "_blank");
}

function loadHistory() {
    fetch("/history")
    .then(res => res.json())
    .then(data => {
        const list = document.getElementById("history");
        list.innerHTML = "";

        data.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `
                <div><b>${item.file}</b></div>
                <div>${item.time}</div>
            `;

            const btn = document.createElement("button");
            btn.innerText = "⬇ Download";
            btn.onclick = () => downloadFile(item.file);

            li.appendChild(btn);

            list.appendChild(li);
        });
    });
}

function appendLog(text) {
    const log = document.getElementById("log");
    log.innerText += text + "\n";

    // auto scroll to bottom
    log.scrollTop = log.scrollHeight;
}

loadHistory();