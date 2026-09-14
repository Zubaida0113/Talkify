const taskInput = document.getElementById("taskInput");
const addTaskButton = document.getElementById("addTaskButton");
const taskList = document.getElementById("taskList");

let tasks = [];
let currentFilter = "all";

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

const voiceButton = document.getElementById("voiceButton");

async function startRecording() {

    try {

        const stream = await navigator.mediaDevices.getUserMedia({
            audio: true
        });

        mediaRecorder = new MediaRecorder(stream);

        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };


        mediaRecorder.onstop = async () => {

    const audioBlob = new Blob(audioChunks, {
        type: "audio/webm"
    });

    console.log("Recording complete");
    console.log("Audio size:", audioBlob.size);


    const formData = new FormData();

    formData.append(
        "file",
        audioBlob,
        "voice_task.webm"
    );


    try {

        const response = await fetch("/audio/upload", {
            method: "POST",
            body: formData
        });


        const result = await response.json();

        console.log("Server response:", result);


    } catch (error) {

        console.error(
            "Audio upload failed:",
            error
        );

    }


    stream.getTracks().forEach(
        track => track.stop()
    );
};


        mediaRecorder.start();

        isRecording = true;

        voiceButton.textContent = "⏹️ Stop";

        voiceButton.classList.add("recording");

        console.log("Recording started");

    } catch (error) {

        console.error("Microphone error:", error);

        alert(
            "Microphone access is required to record a voice task."
        );

    }
}

function stopRecording() {

    if (mediaRecorder && isRecording) {

        mediaRecorder.stop();

        isRecording = false;

        voiceButton.textContent = "🎙️ Record";

        voiceButton.classList.remove("recording");

    }
}

voiceButton.addEventListener("click", () => {

    if (!isRecording) {

        startRecording();

    } else {

        stopRecording();

    }

});


async function loadTasks() {
    const response = await fetch("/tasks/");
    tasks = await response.json();

    renderTasks();
}


function renderTasks() {

    taskList.innerHTML = "";

    let filteredTasks = tasks;

    if (currentFilter === "active") {
        filteredTasks = tasks.filter(task => !task.completed);
    }

    if (currentFilter === "completed") {
        filteredTasks = tasks.filter(task => task.completed);
    }


    filteredTasks.forEach(task => {

        const taskElement = document.createElement("div");

        taskElement.className = "task";

        if (task.completed) {
            taskElement.classList.add("completed");
        }


        taskElement.innerHTML = `
            <input
                type="checkbox"
                ${task.completed ? "checked" : ""}
                onchange="completeTask(${task.id})"
            >

            <div class="task-info">

                <div class="task-title">
                    ${task.title}
                </div>

                ${
                    task.description
                    ? `<div class="task-description">
                        ${task.description}
                       </div>`
                    : ""
                }

            </div>

            <div class="task-actions">

                <button onclick="deleteTask(${task.id})">
                    🗑️
                </button>

            </div>
        `;


        taskList.appendChild(taskElement);

    });
}


async function addTask() {

    const title = taskInput.value.trim();

    if (!title) {
        return;
    }


    const response = await fetch("/tasks/", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            title: title,
            description: null,
            due_date: null,
            priority: "medium"
        })

    });


    if (response.ok) {

        taskInput.value = "";

        await loadTasks();

    }

}


async function completeTask(taskId) {

    await fetch(`/tasks/${taskId}/complete`, {
        method: "POST"
    });

    await loadTasks();

}


async function deleteTask(taskId) {

    await fetch(`/tasks/${taskId}`, {
        method: "DELETE"
    });

    await loadTasks();

}


addTaskButton.addEventListener("click", addTask);


taskInput.addEventListener("keydown", (event) => {

    if (event.key === "Enter") {
        addTask();
    }

});


document.querySelectorAll(".filter").forEach(button => {

    button.addEventListener("click", () => {

        document.querySelector(".filter.active")
            .classList.remove("active");

        button.classList.add("active");

        currentFilter = button.dataset.filter;

        renderTasks();

    });

});


loadTasks();