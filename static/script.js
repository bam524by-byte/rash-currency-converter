const flags = {

    USD: "🇺🇸",
    UGX: "🇺🇬",
    EUR: "🇪🇺",
    GBP: "🇬🇧",
    KES: "🇰🇪",
    TZS: "🇹🇿",
    NGN: "🇳🇬",
    CAD: "🇨🇦",
    AUD: "🇦🇺",
    JPY: "🇯🇵",
    CNY: "🇨🇳",
    INR: "🇮🇳",
    ZAR: "🇿🇦",
    CHF: "🇨🇭",
    AED: "🇦🇪",
    SAR: "🇸🇦",
    RUB: "🇷🇺",
    SGD: "🇸🇬",
    HKD: "🇭🇰",
    BTC: "🪙",
    ETH: "⚡"

};

/* =========================
   CLOCK
========================= */

function updateClock() {

    const now = new Date();

    document.getElementById("clock").innerHTML =
    now.toLocaleTimeString();
}

setInterval(updateClock, 1000);

updateClock();

/* =========================
   FLAGS
========================= */

function updateFlags() {

    const from =
    document.getElementById("fromCurrency").value;

    const to =
    document.getElementById("toCurrency").value;

    document.getElementById("fromFlag").innerHTML =
    flags[from];

    document.getElementById("toFlag").innerHTML =
    flags[to];
}

document.getElementById("fromCurrency")
.addEventListener("change", updateFlags);

document.getElementById("toCurrency")
.addEventListener("change", updateFlags);

updateFlags();





async function convertCurrency() {

    const amount =
    document.getElementById("amount").value;

    const fromCurrency =
    document.getElementById("fromCurrency").value;

    const toCurrency =
    document.getElementById("toCurrency").value;

    if (amount === "") {

        alert("Enter amount");

        return;
    }

    const loader =
    document.getElementById("loader");

    loader.style.display = "block";

    try {

        const response = await fetch("/convert", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                amount: amount,
                from: fromCurrency,
                to: toCurrency

            })

        });

        const data = await response.json();

        loader.style.display = "none";

        /* ERROR */

        if (!data.success) {

            alert(data.error);

            return;
        }

        /* SHOW RESULT */

        document.getElementById("result").innerHTML =
        `Result: ${data.result} ${toCurrency}`;

        document.getElementById("rateText").innerHTML =
        `1 ${fromCurrency} = ${data.rate} ${toCurrency}`;

        /* SAVE HISTORY */

        saveHistory(

            amount,
            fromCurrency,
            toCurrency,
            data.result

        );

        showToast();

        playSound();

        sendNotification();

    }

    catch(error) {

        loader.style.display = "none";

        alert("Conversion failed");

        console.log(error);

    }

}

/* =========================
   SOUND
========================= */

function playSound() {

    document.getElementById("sound").play();
}

/* =========================
   SWAP CURRENCIES
========================= */

function swapCurrencies() {

    let from =
    document.getElementById("fromCurrency");

    let to =
    document.getElementById("toCurrency");

    let temp = from.value;

    from.value = to.value;

    to.value = temp;

    updateFlags();

    convertCurrency();
}

/* =========================
   SAVE HISTORY
========================= */

function saveHistory(amount, from, to, result) {

    const historyList =
    document.getElementById("historyList");

    const li =
    document.createElement("li");

    li.innerHTML =
    `${amount} ${from} → ${result} ${to}`;

    historyList.prepend(li);
}

/* =========================
   TOAST
========================= */

function showToast() {

    const toast =
    document.getElementById("toast");

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 2000);
}

/* =========================
   THEME TOGGLE
========================= */

function toggleTheme() {

    document.body.classList.toggle("light-mode");
}

const toggleBtn =
document.getElementById("theme-toggle");

if (toggleBtn) {

    toggleBtn.addEventListener("click", () => {

        document.body.classList.toggle("light-mode");

    });
}

/* =========================
   DOWNLOAD RECEIPT
========================= */

function downloadReceipt() {

    const result =
    document.getElementById("result").innerText;

    const rate =
    document.getElementById("rateText").innerText;

    const content =
    `${result}\n${rate}`;

    const blob =
    new Blob([content], {

        type: "text/plain"

    });

    const a =
    document.createElement("a");

    a.href =
    URL.createObjectURL(blob);

    a.download =
    "rash_receipt.txt";

    a.click();
}

/* =========================
   AUTO CONVERT
========================= */

document.getElementById("amount")
.addEventListener("input", () => {

    if (

        document.getElementById("amount").value !== ""

    ) {

        convertCurrency();

    }

});

/* =========================
   NOTIFICATIONS
========================= */

if ("Notification" in window) {

    Notification.requestPermission();
}

function sendNotification() {

    if (Notification.permission === "granted") {

        new Notification(

            "Rash Currency Converter",

            {

                body:
                "Currency updated successfully!"

            }

        );
    }
}

/* =========================
   CRYPTO PRICES
========================= */

async function loadCryptoPrices() {

    try {

        const response = await fetch(

            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd"

        );

        const data = await response.json();

        document.getElementById("btc-price")
        .innerHTML =
        "$" + data.bitcoin.usd;

        document.getElementById("eth-price")
        .innerHTML =
        "$" + data.ethereum.usd;

        document.getElementById("usdt-price")
        .innerHTML =
        "$" + data.tether.usd;

    }

    catch(error) {

        console.log(error);
    }
}

loadCryptoPrices();

/* =========================
   FAVORITE PAIRS
========================= */

function setPair(from, to) {

    document.getElementById("fromCurrency").value =
    from;

    document.getElementById("toCurrency").value =
    to;

    updateFlags();

    convertCurrency();
}

/* =========================
   BUTTON CLICK SOUND
========================= */

const clickSound =
new Audio("/static/click.mp3");

document.querySelectorAll("button")
.forEach(button => {

    button.addEventListener("click", () => {

        clickSound.play();

    });

});

/* =========================
   SCROLL BUTTON
========================= */

function scrollToBottom() {

    window.scrollTo({

        top: document.body.scrollHeight,

        behavior: "smooth"

    });
}
async function askAI() {

    let message =
    document.getElementById("question").value;

    let response = await fetch("/ask-ai", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            message: message
        })

    });

    let data = await response.json();

    document.getElementById(
        "ai-response"
    ).innerHTML = data.reply;

}
async function loadCryptoPrices() {

    try {

        const response = await fetch('/crypto-prices');

        const data = await response.json();

        document.getElementById('btc-price').innerText =
            '$' + data.btc;

        document.getElementById('eth-price').innerText =
            '$' + data.eth;

        document.getElementById('usdt-price').innerText =
            '$' + data.usdt;

    }

    catch(error) {

        console.log(error);

    }

}

loadCryptoPrices();

setInterval(loadCryptoPrices, 60000);
async function loadMarketData() {

    try {

        const response =
            await fetch('/market-data');

        const data =
            await response.json();

        document.getElementById(
            "usd-ugx"
        ).innerText =
            data.usd_ugx;

        document.getElementById(
            "eur-usd"
        ).innerText =
            data.eur_usd;

        document.getElementById(
            "gbp-usd"
        ).innerText =
            data.gbp_usd;

    }

    catch(error){

        console.log(error);

    }

}

loadMarketData();

setInterval(
    loadMarketData,
    60000
);

async function loadMarketData() {

    try {

        const response = await fetch('/market-data');

        const data = await response.json();

        document.getElementById('usd-ugx').innerText =
            data.usd_ugx;

        document.getElementById('eur-usd').innerText =
            data.eur_usd;

        document.getElementById('gbp-usd').innerText =
            data.gbp_usd;

    } catch (error) {

        console.log(error);

    }

}

loadMarketData();

setInterval(loadMarketData, 30000);
async function askAI() {

    let question =
        document.getElementById(
            "ai-question"
        ).value;

    let response =
        await fetch(
            "/ask-ai",
            {
                method: "POST",
                headers: {
                    "Content-Type":
                    "application/json"
                },
                body: JSON.stringify({
                    message: question
                })
            }
        );

    let data =
        await response.json();

    document.getElementById(
        "ai-response"
    ).innerHTML =
        data.reply;

}
function toggleTheme() {

    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {

        localStorage.setItem(
            "theme",
            "dark"
        );

    } else {

        localStorage.setItem(
            "theme",
            "light"
        );
    }
}

window.onload = function() {

    const theme = localStorage.getItem(
        "theme"
    );

    if (theme === "dark") {

        document.body.classList.add(
            "dark-mode"
        );
    }
}
async function loadCryptoPrices() {

    try {

        const response = await fetch(
            "/crypto-prices"
        );

        const data = await response.json();

        document.getElementById(
            "btc"
        ).innerHTML =
        "BTC: $" + data.btc;

        document.getElementById(
            "eth"
        ).innerHTML =
        "ETH: $" + data.eth;

        document.getElementById(
            "usdt"
        ).innerHTML =
        "USDT: $" + data.usdt;

    }

    catch(error) {

        console.log(error);

    }

}

loadCryptoPrices();

setInterval(
    loadCryptoPrices,
    30000
);