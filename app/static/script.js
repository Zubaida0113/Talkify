const taskInput = document.getElementById("taskInput");
const addTaskButton = document.getElementById("addTaskButton");
const taskList = document.getElementById("taskList");
const aiModal = document.getElementById("aiModal");
const aiTaskList = document.getElementById("aiTaskList");
const aiTranscript = document.getElementById("aiTranscript");
const closeModal = document.getElementById("closeModal");
const cancelAiTasks = document.getElementById("cancelAiTasks");
const addAiTasks = document.getElementById("addAiTasks");

let tasks = [];
let extractedTasks = [];
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

        if (!response.ok) {
            throw new Error(result.detail || "Failed to process the recording.");
        }

        showAiTasks(result.transcript, result.tasks || []);


    } catch (error) {

        console.error("Audio upload failed:", error);
        alert(`Audio upload failed: ${error.message}`);

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

const priorityOrder = {
    high: 1,
    medium: 2,
    low: 3
};

const taskGroups = [
    { key: "today", label: "Today" },
    { key: "tomorrow", label: "Tomorrow" },
    { key: "later", label: "Later" },
    { key: "urgent", label: "Urgent" }
];

function parseTaskDate(dateValue) {
    if (!dateValue) {
        return null;
    }

    const [year, month, day] = dateValue.split("-").map(Number);
    return new Date(year, month - 1, day);
}

function formatTaskDate(dateValue) {
    const date = parseTaskDate(dateValue);

    if (!date) {
        return "No deadline";
    }

    return new Intl.DateTimeFormat("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric"
    }).format(date);
}

function getDateKey(date) {
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

function getTaskGroup(task) {
    if (task.priority === "high") {
        return "urgent";
    }

    const taskDate = parseTaskDate(task.due_date);

    if (!taskDate) {
        return "later";
    }

    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);

    if (getDateKey(taskDate) === getDateKey(today)) {
        return "today";
    }

    if (getDateKey(taskDate) === getDateKey(tomorrow)) {
        return "tomorrow";
    }

    return "later";
}

function renderTasks() {

    taskList.innerHTML = "";

    let filteredTasks = [...tasks];

    if (currentFilter === "active") {
        filteredTasks = filteredTasks.filter(task => !task.completed);
    }

    if (currentFilter === "completed") {
        filteredTasks = filteredTasks.filter(task => task.completed);
    }

    filteredTasks.sort((a, b) => {

    // Tasks with dates come before tasks without dates
    if (!a.due_date && b.due_date) return 1;
    if (a.due_date && !b.due_date) return -1;

    // If both have dates, sort by closest date
    if (a.due_date && b.due_date) {

        const dateA = new Date(a.due_date);
        const dateB = new Date(b.due_date);

        const dateDifference = dateA - dateB;

        if (dateDifference !== 0) {
            return dateDifference;
        }
    }

    // Same date → priority
    return (
        (priorityOrder[a.priority] || 2) -
        (priorityOrder[b.priority] || 2)
    );
});
    const groupedTasks = Object.fromEntries(
        taskGroups.map(group => [group.key, []])
    );

    filteredTasks.forEach(task => {
        groupedTasks[getTaskGroup(task)].push(task);
    });

    taskGroups.forEach(group => {
        const groupTasks = groupedTasks[group.key];

        if (!groupTasks.length) {
            return;
        }

        const groupElement = document.createElement("section");
        groupElement.className = `task-group task-group-${group.key}`;
        groupElement.innerHTML = `<h3>${group.label} (${groupTasks.length})</h3>`;

        const groupList = document.createElement("div");
        groupList.className = "task-group-list";

        groupTasks.forEach(task => {

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

    <div class="task-meta">

        ${
            task.due_date
            ? `<span>📅 ${formatTaskDate(task.due_date)}</span>`
            : `<span>📅 No deadline</span>`
        }

        <span>
            ⭐ ${task.priority || "medium"}
        </span>

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


        groupList.appendChild(taskElement);

    });

        groupElement.appendChild(groupList);
        taskList.appendChild(groupElement);
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

function showAiTasks(transcript, foundTasks) {

    console.log("SHOW AI TASKS CALLED:", transcript, foundTasks);

    extractedTasks = foundTasks;
    aiTranscript.textContent = `Transcript: "${transcript}"`;
    aiTaskList.innerHTML = "";

    if (!foundTasks.length) {
        aiTaskList.textContent = "No tasks were found in the recording.";
        addAiTasks.disabled = true;
    } else {

        foundTasks.forEach((task, index) => {

            const taskElement = document.createElement("div");

            taskElement.className = "ai-task";

            taskElement.innerHTML = `
                <div class="ai-task-title">
                    ${index + 1}. ${task.title}
                </div>

                <div class="ai-task-details">
                    <span>📅 ${task.due_date || "No deadline"}</span>
                    <span>⭐ ${task.priority || "medium"}</span>
                </div>
            `;

            aiTaskList.appendChild(taskElement);
        });

        addAiTasks.disabled = false;
    }

    console.log("Removing hidden class");

    aiModal.classList.remove("hidden");

    console.log(
        "Modal class after remove:",
        aiModal.className
    );
}

function closeAiModal() {
    aiModal.classList.add("hidden");
    extractedTasks = [];
    addAiTasks.disabled = false;
}

async function addExtractedTasks() {
    addAiTasks.disabled = true;

    try {
        const responses = await Promise.all(
            extractedTasks.map(task => fetch("/tasks/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(task)
            }))
        );

        const failedResponse = responses.find(response => !response.ok);
        if (failedResponse) {
            throw new Error("One or more tasks could not be added.");
        }

        closeAiModal();
        await loadTasks();
    } catch (error) {
        console.error("Adding recorded tasks failed:", error);
        alert(error.message);
        addAiTasks.disabled = false;
    }
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


closeModal.addEventListener("click", closeAiModal);
cancelAiTasks.addEventListener("click", closeAiModal);
addAiTasks.addEventListener("click", addExtractedTasks);

loadTasks();