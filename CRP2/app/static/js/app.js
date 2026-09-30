/* ========================================================= */
/* SHARED STATE + HELPERS                                     */
/* ========================================================= */

const ui = {
    pending: 0,
    nextSender: null,
    nextReceiver: null,
    modifiedBy: null,
    outcome: null,          // { receiver, ok } after Receive & Verify
    everSent: false,
    logCount: 0
};

function $(id) {
    return document.getElementById(id);
}

function escapeHtml(value) {

    const div = document.createElement("div");
    div.textContent = value ?? "";
    return div.innerHTML;
}

function scrollToId(id) {

    const el = $(id);

    if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
    }
}

async function api(method, url, body) {

    const options = { method: method };

    if (body !== undefined) {
        options.headers = { "Content-Type": "application/json" };
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    let data = {};

    try {
        data = await response.json();
    } catch (error) {
        data = { error: "Server returned an unreadable response" };
    }

    return { ok: response.ok, status: response.status, data: data };
}


/* ========================================================= */
/* ACTIVITY LOG                                               */
/* ========================================================= */

function log(kind, title, detail) {

    const list = $("logList");

    if (!list) {
        return;
    }

    const empty = list.querySelector(".log-empty");

    if (empty) {
        empty.remove();
    }

    const item = document.createElement("li");
    item.className = "log-" + kind;

    const time = new Date().toLocaleTimeString();

    item.innerHTML =
        "<strong>" + escapeHtml(title) + "</strong>" +
        (detail ? "<br>" + escapeHtml(detail) : "") +
        "<small>" + escapeHtml(time) + "</small>";

    list.insertBefore(item, list.firstChild);

    ui.logCount += 1;
    $("logCount").textContent = String(ui.logCount);
}

function clearLog() {

    $("logList").innerHTML =
        '<li class="log-empty">Nothing yet. Send a message to begin.</li>';

    ui.logCount = 0;
    $("logCount").textContent = "0";
}

function toggleLog() {

    const panel = $("logPanel");
    const open = panel.classList.contains("hidden");

    panel.classList.toggle("hidden", !open);
    $("logToggle").setAttribute("aria-expanded", String(open));
}


/* ========================================================= */
/* LIVE STATE (status bar, steps, chips, participants)        */
/* ========================================================= */

function setChip(id, cls, text) {

    const el = $(id);

    if (!el) {
        return;
    }

    el.className = "chip " + cls;
    el.textContent = text;
}

function setParticipant(id, cls, text) {

    const el = $(id);

    if (!el) {
        return;
    }

    el.className = "participant-status" + (cls ? " " + cls : "");
    el.textContent = text;
}

function setStep(id, state) {

    const el = $(id);

    if (el) {
        el.className = "lab-step" + (state ? " " + state : "");
    }
}

function renderLiveState() {

    const waiting = ui.pending > 0;

    /* ---- chips ---- */

    setChip(
        "relayChip",
        waiting ? "chip-info" : "chip-idle",
        waiting
            ? "Relay: " + ui.pending + " message" +
              (ui.pending > 1 ? "s" : "") + " in transit"
            : "Relay: empty"
    );

    let integrityClass = "chip-idle";
    let integrityText = "No packet yet";
    let packetClass = "chip-info";
    let packetText = "In transit";

    if (waiting && ui.modifiedBy) {

        integrityClass = packetClass = "chip-warn";
        integrityText = "⚠ Modified in transit (" + ui.modifiedBy + ")";
        packetText = "⚠ Modified in transit";

    } else if (waiting) {

        integrityClass = "chip-ok";
        integrityText = "Packet unmodified";

    } else if (ui.outcome) {

        integrityClass = packetClass = ui.outcome.ok ? "chip-ok" : "chip-bad";
        integrityText = packetText = ui.outcome.ok
            ? "✓ Delivered and verified"
            : "✗ Rejected by " + ui.outcome.receiver;

    } else if (ui.everSent) {

        packetText = "Not in relay";
    }

    setChip("integrityChip", integrityClass, integrityText);
    setChip("packetState", packetClass, packetText);

    /* ---- participants ---- */

    const names = { Alice: "aliceStatus", Bob: "bobStatus" };

    setParticipant("aliceStatus", "", "Ready to send");
    setParticipant("bobStatus", "", "Ready to receive");

    if (waiting && ui.nextSender && ui.nextReceiver) {

        setParticipant(names[ui.nextSender], "state-sending", "Message sent ↗");
        setParticipant(names[ui.nextReceiver], "state-waiting", "Message waiting…");

    } else if (ui.outcome) {

        setParticipant(
            names[ui.outcome.receiver],
            ui.outcome.ok ? "state-ok" : "state-bad",
            ui.outcome.ok ? "Verified ✓" : "Rejected ✗"
        );
    }

    /* ---- steps ---- */

    if (waiting && ui.modifiedBy) {

        setStep("step-send", "done");
        setStep("step-attack", "done");
        setStep("step-receive", "active");

    } else if (waiting) {

        setStep("step-send", "done");
        setStep("step-attack", "active");
        setStep("step-receive", "active");

    } else if (ui.outcome) {

        setStep("step-send", "active");
        setStep("step-attack", "done");
        setStep("step-receive", "done");

    } else {

        setStep("step-send", "active");
        setStep("step-attack", "");
        setStep("step-receive", "");
    }

    /* ---- receive button ---- */

    const receiveButton = $("receiveButton");

    if (receiveButton) {

        receiveButton.disabled = !waiting;
        receiveButton.title = waiting
            ? ""
            : "No message is waiting in the relay. Send one first.";
    }
}

async function refreshStatus() {

    const statusText = $("systemStatus");
    const statusDot = $("statusDot");

    try {

        const { data } = await api("GET", "/api/status");

        ui.pending = data.pending_messages || 0;
        ui.nextSender = data.next_sender || null;
        ui.nextReceiver = data.next_receiver || null;
        ui.modifiedBy = data.modified_by || null;

        if (data.session_established) {

            statusText.textContent = "System Secure";
            statusDot.classList.remove("status-dot-bad");

        } else {

            statusText.textContent = "Session Not Established";
            statusDot.classList.add("status-dot-bad");
        }

        renderLiveState();

        return data;

    } catch (error) {

        statusText.textContent = "Backend Unreachable";
        statusDot.classList.add("status-dot-bad");
    }
}

document.addEventListener("DOMContentLoaded", async function () {

    const data = await refreshStatus();

    /* A page reload keeps the server-side relay: show its packet section */
    if (data && data.pending_messages > 0) {

        $("messageResult").classList.remove("hidden");

        ui.everSent = true;
        renderLiveState();

        log(
            "info",
            "Message already waiting in the relay",
            "Sent before this page was loaded. Packet details are only " +
            "shown for messages sent from this page."
        );
    }
});


/* ========================================================= */
/* RESET SESSION (fresh ML-KEM handshake + new keys)          */
/* ========================================================= */

async function resetSession() {

    const button = $("resetButton");

    button.disabled = true;

    try {

        await api("POST", "/api/reset");

        ["result-tampering", "result-signature", "result-replay",
         "result-wrong-key", "result-interception"].forEach(function (id) {

            const el = $(id);

            if (el) {
                el.className = "attack-result";
                el.textContent = "";
            }
        });

        $("messageResult").classList.add("hidden");

        const receiveResult = $("receiveResult");
        receiveResult.classList.add("hidden");
        receiveResult.innerHTML = "";

        ui.outcome = null;
        ui.everSent = false;

        log("info", "New session", "Fresh ML-KEM-768 handshake, new keys");

        await refreshStatus();

    } catch (error) {

        alert("Could not reset the session: " + error.message);

    } finally {

        button.disabled = false;
    }
}


/* ========================================================= */
/* SEND SECURE MESSAGE                                        */
/* ========================================================= */

async function sendMessage() {

    const sender = $("sender").value;
    const message = $("message").value.trim();
    const status = $("messageStatus");
    const button = $("sendButton");
    const errorBox = $("sendError");

    errorBox.classList.add("hidden");
    errorBox.textContent = "";

    if (!message) {

        status.textContent = "Enter a message";
        status.style.background = "#fee2e2";
        status.style.color = "#b91c1c";
        $("message").focus();
        return;
    }

    status.textContent = "Processing...";
    status.style.background = "#fef3c7";
    status.style.color = "#92400e";

    button.disabled = true;
    button.textContent = "Encrypting...";

    try {

        const { ok, data } = await api("POST", "/api/message", {
            sender: sender,
            message: message
        });

        if (!ok) {
            throw new Error(data.error || "Message could not be sent");
        }

        $("packetSender").textContent = data.sender;
        $("packetReceiver").textContent = data.receiver;
        $("packetMessageId").textContent = data.message_id;
        $("packetTimestamp").textContent = data.timestamp;
        $("packetNonce").textContent = data.nonce;
        $("packetCiphertext").textContent = data.ciphertext;
        $("packetSignature").textContent = data.signature;

        const ciphertextPreview = $("ciphertextPreview");
        const signaturePreview = $("signaturePreview");

        if (ciphertextPreview) {
            ciphertextPreview.textContent =
                createPreview(data.ciphertext, "Encrypted ciphertext");
        }

        if (signaturePreview) {
            signaturePreview.textContent =
                createPreview(data.signature, "ML-DSA-65 signature");
        }

        resetCryptoVisibility();

        $("messageResult").classList.remove("hidden");
        $("messageResult").scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

        const receiveResult = $("receiveResult");
        receiveResult.classList.add("hidden");
        receiveResult.innerHTML = "";

        status.textContent = "Encrypted & Signed";
        status.style.background = "#dcfce7";
        status.style.color = "#15803d";

        $("message").value = "";

        ui.outcome = null;
        ui.everSent = true;

        log(
            "info",
            data.sender + " → " + data.receiver + ": message sent",
            "Encrypted with AES-256-GCM and signed with ML-DSA-65"
        );

        await refreshStatus();

    } catch (error) {

        status.textContent = "Error";
        status.style.background = "#fee2e2";
        status.style.color = "#b91c1c";

        errorBox.textContent = error.message;
        errorBox.classList.remove("hidden");

        log("bad", "Send failed", error.message);

    } finally {

        button.disabled = false;
        button.textContent = "🔒 Send Secure Message";
    }
}


/* ========================================================= */
/* RECEIVE AND VERIFY MESSAGE                                 */
/* ========================================================= */

/* inlineTarget (optional): element that also shows Bob's verdict,
   used by the "Receive & Verify now" button inside attack cards. */

async function receiveMessage(inlineTarget) {

    const result = $("receiveResult");
    const button = $("receiveButton");

    button.disabled = true;

    result.classList.remove("hidden");
    result.style.background = "#eff6ff";
    result.style.color = "#1e3a8a";
    result.style.borderColor = "#dbeafe";
    result.textContent = "🔄 Decrypting and verifying message...";

    let html;
    let ok = false;
    let recorded = true;    // false when Receive did not actually run
    let receiver = ui.nextReceiver || "Receiver";

    try {

        const response = await api("POST", "/api/message/receive");
        const data = response.data;

        if (!response.ok) {

            if (response.status === 404) {
                throw new Error(
                    "No message is waiting in the relay. Send one first."
                );
            }

            const reasonError = new Error(data.error || "Receive failed");
            reasonError.rejected = data.status === "Message rejected";
            throw reasonError;
        }

        ok = true;
        receiver = data.receiver;

        result.style.background = "#dcfce7";
        result.style.color = "#166534";
        result.style.borderColor = "#bbf7d0";

        html =
            "<strong>✓ Message Successfully Verified</strong><br>" +
            "Sender: " + escapeHtml(data.sender) + "<br>" +
            "Receiver: " + escapeHtml(data.receiver) + "<br>" +
            "Message: " + escapeHtml(data.message) + "<br>" +
            "ML-DSA Signature: <strong>VALID</strong>";

        log(
            "ok",
            data.receiver + " accepted the message",
            "AES-GCM authentication and ML-DSA signature both valid"
        );

    } catch (error) {

        result.style.background = "#fee2e2";
        result.style.color = "#991b1b";
        result.style.borderColor = "#fecaca";

        html =
            "<strong>✗ Message Rejected</strong>" +
            "<span class=\"verdict-detail\">" +
            escapeHtml(error.message) + "</span>";

        if (error.rejected) {
            log("bad", receiver + " REJECTED the message", error.message);
        } else {
            recorded = false;
            log("warn", "Receive did not run", error.message);
        }
    }

    result.innerHTML = html;

    if (inlineTarget) {

        inlineTarget.className = "inline-verdict " + (ok ? "ok" : "bad");
        inlineTarget.innerHTML = html;
    }

    if (recorded) {
        ui.outcome = { receiver: receiver, ok: ok };
    }

    await refreshStatus();
}


/* ========================================================= */
/* ATTACK SIMULATION                                          */
/* ========================================================= */

const ATTACK_SUCCESS_STATUSES = new Set([
    "ATTACK DETECTED",
    "INTERCEPTION PROTECTED"
]);

const ATTACK_NEUTRAL_STATUSES = new Set([
    "NO PACKET AVAILABLE",
    "RECEIVE MESSAGE FIRST"
]);

async function runAttack(attackType) {

    const resultElement = $(`result-${attackType}`);
    const button = $(`btn-${attackType}`);

    resultElement.className = "attack-result";
    resultElement.textContent = "Running security test...";

    if (button) {
        button.disabled = true;
    }

    try {

        const { data } = await api("POST", `/api/attack/${attackType}`);

        let body = "";

        if (ATTACK_SUCCESS_STATUSES.has(data.status)) {

            resultElement.classList.add("attack-success");
            body = `<strong>✓ ${escapeHtml(data.status)}</strong><br>` +
                   escapeHtml(data.protection || "");

            log(
                "ok",
                (data.attack || attackType) + ": " + data.status,
                data.protection
            );

        } else if (ATTACK_NEUTRAL_STATUSES.has(data.status)) {

            resultElement.classList.add("attack-neutral");
            body = `<strong>${escapeHtml(data.status)}</strong><br>` +
                   escapeHtml(data.protection || "");

            log("warn", (data.attack || attackType) + ": " + data.status);

        } else {

            resultElement.classList.add("attack-failure");
            body = `<strong>⚠ ${escapeHtml(data.status || "ERROR")}</strong><br>` +
                   escapeHtml(data.protection || data.error || "");

            log(
                "bad",
                (data.attack || attackType) + ": " + (data.status || "ERROR"),
                data.protection || data.error
            );
        }

        if (data.error && ATTACK_SUCCESS_STATUSES.has(data.status)) {
            body += `<span class="attack-detail">Verifier said: ` +
                    `${escapeHtml(data.error)}</span>`;
        }

        if (data.next_step) {
            body += `<span class="attack-next">${escapeHtml(data.next_step)}</span>`;
        }

        resultElement.innerHTML = body;

        /* Active attack on a packet still in transit: offer the verdict here */
        if (data.in_flight) {

            const verdict = document.createElement("div");
            verdict.className = "inline-verdict";
            verdict.style.display = "none";

            const go = document.createElement("button");
            go.className = "inline-receive";
            go.textContent = "🔓 Receive & Verify now";

            go.addEventListener("click", async function () {

                go.disabled = true;
                verdict.style.display = "block";
                verdict.textContent = "Verifying...";

                await receiveMessage(verdict);

                go.remove();
            });

            resultElement.appendChild(document.createElement("br"));
            resultElement.appendChild(go);
            resultElement.appendChild(verdict);
        }

        await refreshStatus();

    } catch (error) {

        resultElement.classList.add("attack-failure");
        resultElement.textContent = error.message;

        log("bad", "Attack request failed", error.message);

    } finally {

        if (button) {
            button.disabled = false;
        }
    }
}


/* ========================================================= */
/* CRYPTOGRAPHIC DATA PREVIEW / SHOW-HIDE / COPY              */
/* ========================================================= */

function createPreview(value, label) {

    if (!value) {
        return `${label}: Not available`;
    }

    const length = value.length;

    if (length <= 72) {
        return `${label}: ${value}`;
    }

    const beginning = value.substring(0, 32);
    const ending = value.substring(value.length - 32);

    return `${label}: ${beginning} ... ${ending} (${length} hex characters)`;
}

function toggleCrypto(elementId, button) {

    const element = $(elementId);

    if (!element) {
        return;
    }

    if (element.classList.contains("visible")) {

        element.classList.remove("visible");
        button.textContent = "Show";

    } else {

        element.classList.add("visible");
        button.textContent = "Hide";
    }
}

function resetCryptoVisibility() {

    ["packetNonce", "packetCiphertext", "packetSignature"].forEach(
        function (elementId) {

            const element = $(elementId);

            if (!element) {
                return;
            }

            element.classList.remove("visible");

            const button = element.parentElement.querySelector(".view-button");

            if (button) {
                button.textContent = "Show";
            }
        }
    );
}

async function copyCrypto(elementId, button) {

    const element = $(elementId);

    if (!element) {
        return;
    }

    const text = element.textContent.trim();

    try {

        await navigator.clipboard.writeText(text);
        button.textContent = "Copied ✓";

    } catch (error) {

        /* clipboard API needs https/localhost: fall back to selection */
        const range = document.createRange();
        range.selectNodeContents(element);

        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        let copied = false;

        try {
            copied = document.execCommand("copy");
        } catch (fallbackError) {
            copied = false;
        }

        selection.removeAllRanges();
        button.textContent = copied ? "Copied ✓" : "Copy failed";
    }

    setTimeout(function () { button.textContent = "Copy"; }, 1400);
}

document.addEventListener("DOMContentLoaded", function () {

    /* add a Copy button next to every Show/Hide button */
    document.querySelectorAll(".crypto-box").forEach(function (box) {

        const view = box.querySelector(".view-button");
        const code = box.querySelector("code");

        if (!view || !code || !code.id) {
            return;
        }

        const copy = document.createElement("button");
        copy.className = "copy-button";
        copy.textContent = "Copy";
        copy.addEventListener("click", function () {
            copyCrypto(code.id, copy);
        });

        view.insertAdjacentElement("afterend", copy);
    });
});


/* ========================================================= */
/* ENTER KEY SUPPORT                                           */
/* ========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const messageInput = $("message");

    if (messageInput) {

        messageInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {
                event.preventDefault();
                sendMessage();
            }
        });
    }
});
