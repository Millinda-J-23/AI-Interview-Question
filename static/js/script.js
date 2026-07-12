// ======================================
// AI Interview Question Generator
// script.js
// ======================================

// Sidebar Active Link
document.addEventListener("DOMContentLoaded", function () {

    const links = document.querySelectorAll(".sidebar a");

    links.forEach(link => {

        if (link.href === window.location.href) {

            link.classList.add("active");

        }

    });

});

// ======================================
// Counter Animation
// ======================================

function animateCounter(element, target) {

    let count = 0;

    let speed = target / 60;

    const update = () => {

        count += speed;

        if (count < target) {

            element.innerText = Math.floor(count);

            requestAnimationFrame(update);

        } else {

            element.innerText = target;

        }

    };

    update();

}

document.querySelectorAll("[data-counter]").forEach(counter => {

    animateCounter(counter, Number(counter.dataset.counter));

});

// ======================================
// Fade In Animation
// ======================================

const observer = new IntersectionObserver(entries => {

    entries.forEach(entry => {

        if (entry.isIntersecting) {

            entry.target.classList.add("show");

        }

    });

});

document.querySelectorAll(".fade-up").forEach(item => {

    observer.observe(item);

});

// ======================================
// Scroll To Top
// ======================================

const topBtn = document.createElement("button");

topBtn.innerHTML = "↑";

topBtn.id = "topBtn";

document.body.appendChild(topBtn);

window.addEventListener("scroll", function () {

    topBtn.style.display = window.scrollY > 250 ? "block" : "none";

});

topBtn.onclick = function () {

    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

};

// ======================================
// Table Search
// ======================================

const search = document.getElementById("historySearch");

if (search) {

    search.addEventListener("keyup", function () {

        let value = this.value.toLowerCase();

        document.querySelectorAll("#historyTable tbody tr").forEach(row => {

            row.style.display = row.innerText.toLowerCase().includes(value)

                ? ""

                : "none";

        });

    });

}

// ======================================
// Copy Questions
// ======================================

function copyQuestions() {

    const el = document.getElementById("questionText") || document.getElementById("questions");

    if (!el) return;

    navigator.clipboard.writeText(el.innerText);

    showToast("Questions copied successfully!");

}

// ======================================
// Toast Notification
// ======================================

function showToast(message) {

    const toast = document.createElement("div");

    toast.className = "toast-message";

    toast.innerHTML = message;

    document.body.appendChild(toast);

    setTimeout(() => {

        toast.classList.add("show");

    }, 100);

    setTimeout(() => {

        toast.remove();

    }, 3000);

}

// ======================================
// Loading Screen
// ======================================

function startLoading() {

    const loading = document.getElementById("loadingScreen");

    if (!loading) return;

    loading.style.display = "flex";

}

// ======================================
// Smooth Scroll
// ======================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {

    anchor.addEventListener("click", function (e) {

        e.preventDefault();

        document.querySelector(this.getAttribute("href"))

            ?.scrollIntoView({

                behavior: "smooth"

            });

    });

});