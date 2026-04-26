function loadPreview() {
    const url = document.getElementById("url").value;
    if (!url) return;

    document.getElementById("preview").innerHTML = "";
    document.getElementById("previewLoader").classList.remove("hidden");

    fetch(`/preview?url=${encodeURIComponent(url)}`)
    .then(res => res.json())
    .then(data => {
        document.getElementById("previewLoader").classList.add("hidden");

        if (data.thumbnail) {
            document.getElementById("preview").innerHTML =
                `<h4>${data.title}</h4>
                 <img src="${data.thumbnail}" class="thumbnail">`;
        }
    })
    .catch(() => {
        document.getElementById("previewLoader").classList.add("hidden");
    });
}

function startDownload() {
    const url = document.getElementById("url").value;
    const mode = document.getElementById("mode").value;

    const log = document.getElementById("log");
    log.innerText = "";

    const btn = document.getElementById("downloadBtn");

    btn.disabled = true;
    document.getElementById("btnLoader").classList.remove("hidden");
    document.getElementById("btnText").innerText = "Downloading...";
    
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
            stopButtonLoader();

            document.getElementById("btnLoader").classList.add("hidden");
            document.getElementById("btnText").innerText = "⬇ Start Download";

            showToast("Download Complete ✅");
        }
        else if (data === "ERROR") {
            stopButtonLoader();
            showToast("Download Failed ❌");
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

    let span = document.createElement("div");

    if (text.toLowerCase().includes("error")) {
        span.className = "log-error";
    } else if (text.toLowerCase().includes("downloaded") || text.toLowerCase().includes("%")) {
        span.className = "log-success";
    } else {
        span.className = "log-info";
    }

    span.innerText = text;
    log.appendChild(span);

    log.scrollTop = log.scrollHeight;
}

function showToast(message) {
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.classList.remove("hidden");

    setTimeout(() => {
        toast.classList.add("hidden");
    }, 3000);
}

function stopButtonLoader() {
    const btn = document.getElementById("downloadBtn");
    btn.disabled = false;

    document.getElementById("btnLoader").classList.add("hidden");
    document.getElementById("btnText").innerText = "⬇ Start Download";
}

loadHistory();