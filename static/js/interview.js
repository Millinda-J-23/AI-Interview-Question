// =====================================
// AI Interview Generator
// interview.js
// =====================================

document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("interviewForm");
    const overlay = document.getElementById("loadingOverlay");
    const progressBar = document.getElementById("progressBar");
    const percentText = document.getElementById("percentText");
    const loadingTitle = document.getElementById("loadingTitle");
    const loadingMessage = document.getElementById("loadingMessage");

    if (!form) return;

    form.addEventListener("submit", async function (e) {

        e.preventDefault();

        // Show Loading Screen
        overlay.style.display = "flex";

        let progress = 0;

        progressBar.style.width = "0%";
        percentText.innerText = "0%";

        // AI Status Messages
        const messages = [

    {
        title: "Initializing AI",
        message: "Starting the AI engine..."
    },

    {
        title: "Analyzing Profile",
        message: "Reading your job role and experience..."
    },

    {
        title: "Processing Skills",
        message: "Analyzing your technical skills..."
    },

    {
        title: "Researching Company",
        message: "Preparing company-specific interview questions..."
    },

    {
        title: "Generating Questions",
        message: "Creating personalized interview questions..."
    },

    {
        title: "Finalizing",
        message: "Optimizing your interview set..."
    }

];
        let messageIndex = 0;

        loadingTitle.innerText = "Generating Interview Questions...";
        loadingTitle.innerText = messages[0].title;
        loadingMessage.innerText = messages[0].message;

        // Progress Animation
        const timer = setInterval(() => {

            // Stop at 95% until AI finishes
            if (progress < 95) {

                progress++;

                progressBar.style.width = progress + "%";
                percentText.innerText = progress + "%";

            }

            // Change message every 15%
            if (progress % 15 === 0 && messageIndex < messages.length - 1) {

                messageIndex++;
                loadingTitle.innerText = messages[messageIndex].title;
                loadingMessage.innerText = messages[messageIndex].message;

            }

        }, 120);

        try {

            const formData = new FormData(form);

            const response = await fetch("/generate_questions", {

                method: "POST",
                body: formData

            });

            const data = await response.json();

            clearInterval(timer);

            loadingTitle.innerText = "Interview Ready!";
            loadingMessage.innerText = "Your AI interview questions have been generated successfully.";

            // Complete progress to 100%
            const finish = setInterval(() => {

                progress++;

                progressBar.style.width = progress + "%";
                percentText.innerText = progress + "%";

                if (progress >= 100) {

                    clearInterval(finish);

                    if (data.success) {

                        window.location.href = "/result/" + data.history_id;

                    } else {

                        overlay.style.display = "none";
                        alert(data.message);

                    }

                }

            }, 25);

        } catch (error) {

            clearInterval(timer);

            overlay.style.display = "none";

            alert("Unable to connect to AI.");

            console.error(error);

        }

    });

});