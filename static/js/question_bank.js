console.log("Question Bank JS Loaded");

// ======================================================
// DOM ELEMENTS
// ======================================================

const level = document.getElementById("level");
const program = document.getElementById("program");
const semester = document.getElementById("semester");
const subject = document.getElementById("subject");

const selected = document.getElementById("selected-values");

// ======================================================
// SELECTED FILTER VALUES
// ======================================================

const selectedLevel = selected ? selected.dataset.level : "";
const selectedProgram = selected ? selected.dataset.program : "";
const selectedSemester = selected ? selected.dataset.semester : "";
const selectedSubject = selected ? selected.dataset.subject : "";

// ======================================================
// CSRF TOKEN
// ======================================================

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;
            }
        }
    }

    return cookieValue;
}

// ======================================================
// LOAD PROGRAMS
// ======================================================

function loadPrograms(levelValue, callback = null) {

    program.innerHTML =
        '<option value="">Select Program</option>';

    semester.innerHTML =
        '<option value="">Select Semester</option>';

    subject.innerHTML =
        '<option value="">Select Subject</option>';

    if (!levelValue) {

        if (callback) callback();

        return;
    }

    fetch(`/academic/ajax/programs/?level=${levelValue}`)

        .then(response => response.json())

        .then(data => {

            data.forEach(item => {

                const option = document.createElement("option");

                option.value = item.id;
                option.textContent = item.name;

                program.appendChild(option);

            });

            if (selectedProgram) {

                program.value = selectedProgram;

            }

            if (callback) callback();

        })

        .catch(error => {

            console.error("Program Error:", error);

        });

}

// ======================================================
// LOAD SEMESTERS
// ======================================================

function loadSemesters(programValue, callback = null) {

    semester.innerHTML =
        '<option value="">Select Semester</option>';

    subject.innerHTML =
        '<option value="">Select Subject</option>';

    if (!programValue) {

        if (callback) callback();

        return;
    }

    fetch(`/academic/ajax/semesters/?program=${programValue}`)

        .then(response => response.json())

        .then(data => {

            data.forEach(item => {

                const option = document.createElement("option");

                option.value = item.id;
                option.textContent = `Semester ${item.number}`;

                semester.appendChild(option);

            });

            if (selectedSemester) {

                semester.value = selectedSemester;

            }

            if (callback) callback();

        })

        .catch(error => {

            console.error("Semester Error:", error);

        });

}

// ======================================================
// LOAD SUBJECTS
// ======================================================

function loadSubjects(programValue, semesterValue, callback = null) {

    subject.innerHTML =
        '<option value="">Select Subject</option>';

    if (!programValue || !semesterValue) {

        if (callback) callback();

        return;
    }

    fetch(`/academic/ajax/subjects/?program=${programValue}&semester=${semesterValue}`)

        .then(response => response.json())

        .then(data => {

            data.forEach(item => {

                const option = document.createElement("option");

                option.value = item.id;
                option.textContent = item.name;

                subject.appendChild(option);

            });

            if (selectedSubject) {

                subject.value = selectedSubject;

            }

            if (callback) callback();

        })

        .catch(error => {

            console.error("Subject Error:", error);

        });

}

// ======================================================
// FILTER EVENTS
// ======================================================

if (level) {

    level.addEventListener("change", function () {

        loadPrograms(this.value);

    });

}

if (program) {

    program.addEventListener("change", function () {

        loadSemesters(this.value);

    });

}

if (semester) {

    semester.addEventListener("change", function () {

        loadSubjects(program.value, this.value);

    });

}

// ======================================================
// RESTORE FILTERS
// ======================================================

if (selectedLevel) {

    level.value = selectedLevel;

    loadPrograms(selectedLevel, function () {

        loadSemesters(selectedProgram, function () {

            loadSubjects(selectedProgram, selectedSemester);

        });

    });

}

console.log("Part 1 Loaded Successfully");
// ======================================================
// PART 2.1
// INLINE EDIT
// ======================================================

document.addEventListener("click", function (e) {

    const editBtn = e.target.closest(".edit-btn");

    if (!editBtn) return;

    e.preventDefault();

    const row = editBtn.closest("tr");

    enableEdit(row);

});

// ======================================================
// ENABLE EDIT MODE
// ======================================================

function enableEdit(row) {

    // Prevent opening edit mode twice
    if (row.dataset.editing === "true") {
        return;
    }

    row.dataset.editing = "true";

    // Backup row for Cancel button
    row.dataset.original = row.innerHTML;

    //--------------------------------------------------
    // Row data
    //--------------------------------------------------

    const programId = row.dataset.programId;
    const semesterId = row.dataset.semesterId;
    const subjectId = row.dataset.subjectId;

    const unit = row.dataset.unit;
    const questionType = row.dataset.questionType;
    const difficulty = row.dataset.difficulty;
    const bloom = row.dataset.bloom;
    const marks = row.dataset.marks;

    const cells = row.querySelectorAll("td");

    const question = cells[9].innerText.trim();

    //--------------------------------------------------
    // Program
    //--------------------------------------------------

    cells[1].innerHTML = `
        <select class="form-select form-select-sm program-edit">
            <option value="">Loading...</option>
        </select>
    `;

    //--------------------------------------------------
    // Semester
    //--------------------------------------------------

    cells[2].innerHTML = `
        <select class="form-select form-select-sm semester-edit">
            <option value="">Loading...</option>
        </select>
    `;

    //--------------------------------------------------
    // Subject
    //--------------------------------------------------

    cells[3].innerHTML = `
        <select class="form-select form-select-sm subject-edit">
            <option value="">Loading...</option>
        </select>
    `;

    //--------------------------------------------------
    // Unit
    //--------------------------------------------------

    cells[4].innerHTML = `
        <select class="form-select form-select-sm unit-edit">

            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>

        </select>
    `;

    row.querySelector(".unit-edit").value = unit;

    //--------------------------------------------------
    // Question Type
    //--------------------------------------------------

    cells[5].innerHTML = `
        <select class="form-select form-select-sm type-edit">

            <option value="mcq">MCQ</option>
            <option value="very_short">Very Short</option>
            <option value="short">Short Answer</option>
            <option value="long">Long Answer</option>
            <option value="case_study">Case Study</option>
            <option value="programming">Programming</option>
            <option value="numerical">Numerical</option>

        </select>
    `;

    row.querySelector(".type-edit").value = questionType;

    //--------------------------------------------------
    // Difficulty
    //--------------------------------------------------

    cells[6].innerHTML = `
        <select class="form-select form-select-sm difficulty-edit">

            <option value="easy">Easy</option>
            <option value="medium">Medium</option>
            <option value="hard">Hard</option>

        </select>
    `;

    row.querySelector(".difficulty-edit").value = difficulty;

    //--------------------------------------------------
    // Bloom
    //--------------------------------------------------

    cells[7].innerHTML = `
        <select class="form-select form-select-sm bloom-edit">

            <option value="remember">Remember</option>
            <option value="understand">Understand</option>
            <option value="apply">Apply</option>
            <option value="analyze">Analyze</option>
            <option value="evaluate">Evaluate</option>
            <option value="create">Create</option>

        </select>
    `;

    row.querySelector(".bloom-edit").value = bloom;

    //--------------------------------------------------
    // Marks
    //--------------------------------------------------

    cells[8].innerHTML = `
        <input
            type="number"
            class="form-control form-control-sm marks-edit"
            value="${marks}">
    `;

    //--------------------------------------------------
    // Question
    //--------------------------------------------------

    cells[9].innerHTML = `
        <textarea
            class="form-control form-control-sm question-edit"
            rows="3">${question}</textarea>
    `;

    //--------------------------------------------------
    // Buttons
    //--------------------------------------------------

    cells[10].innerHTML = `

        <button
            type="button"
            class="btn btn-success btn-sm save-btn">

            Save

        </button>

        <button
            type="button"
            class="btn btn-secondary btn-sm cancel-btn">

            Cancel

        </button>

    `;

    //--------------------------------------------------
    // Load dropdowns
    //--------------------------------------------------

    loadEditDropdowns(
        row,
        programId,
        semesterId,
        subjectId
    );

}

// ======================================================
// PART 2.2
// LOAD PROGRAM / SEMESTER / SUBJECT DROPDOWNS
// ======================================================

function loadEditDropdowns(row, programId, semesterId, subjectId) {

    const programSelect = row.querySelector(".program-edit");
    const semesterSelect = row.querySelector(".semester-edit");
    const subjectSelect = row.querySelector(".subject-edit");

    // ----------------------------
    // Load Programs
    // ----------------------------

    const levelValue = row.dataset.level || "UG";

    fetch(`/academic/ajax/programs/?level=${levelValue}`)

        .then(res => res.json())

        .then(programs => {

            programSelect.innerHTML = "";

            programs.forEach(program => {

                programSelect.innerHTML += `
                    <option value="${program.id}">
                        ${program.name}
                    </option>
                `;

            });

            programSelect.value = programId;

            loadSemestersEdit();

        });

    // ----------------------------
    // Load Semesters
    // ----------------------------

    function loadSemestersEdit() {

        fetch(`/academic/ajax/semesters/?program=${programSelect.value}`)

            .then(res => res.json())

            .then(semesters => {

                semesterSelect.innerHTML = "";

                semesters.forEach(semester => {

                    semesterSelect.innerHTML += `
                        <option value="${semester.id}">
                            Semester ${semester.number}
                        </option>
                    `;

                });

                semesterSelect.value = semesterId;

                loadSubjectsEdit();

            });

    }

    // ----------------------------
    // Load Subjects
    // ----------------------------

    function loadSubjectsEdit() {

        fetch(`/academic/ajax/subjects/?program=${programSelect.value}&semester=${semesterSelect.value}`)

            .then(res => res.json())

            .then(subjects => {

                subjectSelect.innerHTML = "";

                subjects.forEach(subject => {

                    subjectSelect.innerHTML += `
                        <option value="${subject.id}">
                            ${subject.name}
                        </option>
                    `;

                });

                subjectSelect.value = subjectId;

            });

    }

    // ----------------------------
    // Program Changed
    // ----------------------------

    programSelect.addEventListener("change", function () {

        loadSemestersEdit();

    });

    // ----------------------------
    // Semester Changed
    // ----------------------------

    semesterSelect.addEventListener("change", function () {

        loadSubjectsEdit();

    });

}


// ======================================================
// PART 3
// SAVE & CANCEL
// ======================================================

document.addEventListener("click", function (e) {

    // --------------------------
    // SAVE
    // --------------------------

    const saveBtn = e.target.closest(".save-btn");

    if (saveBtn) {

        const row = saveBtn.closest("tr");

        saveQuestion(row);

        return;
    }

    // --------------------------
    // CANCEL
    // --------------------------

    const cancelBtn = e.target.closest(".cancel-btn");

    if (cancelBtn) {

        const row = cancelBtn.closest("tr");

        row.innerHTML = row.dataset.original;

        row.dataset.editing = "false";

        return;
    }

});

// ======================================================
// SAVE QUESTION
// ======================================================

function saveQuestion(row) {

    const formData = new FormData();

    formData.append("id", row.dataset.id);

    formData.append(
        "program",
        row.querySelector(".program-edit").value
    );

    formData.append(
        "semester",
        row.querySelector(".semester-edit").value
    );

    formData.append(
        "subject",
        row.querySelector(".subject-edit").value
    );

    formData.append(
        "unit",
        row.querySelector(".unit-edit").value
    );

    formData.append(
        "question_type",
        row.querySelector(".type-edit").value
    );

    formData.append(
        "difficulty",
        row.querySelector(".difficulty-edit").value
    );

    formData.append(
        "bloom_level",
        row.querySelector(".bloom-edit").value
    );

    formData.append(
        "marks",
        row.querySelector(".marks-edit").value
    );

    formData.append(
        "question_text",
        row.querySelector(".question-edit").value
    );

    fetch("/api/question/update/", {

        method: "POST",

        headers: {

            "X-CSRFToken": getCookie("csrftoken")

        },

        body: formData

    })

    .then(res => res.json())

    .then(data => {

        if (data.success) {

            alert(data.message);

            location.reload();

        }

        else {

            alert("Unable to save.");

        }

    })

    .catch(error => {

        console.error(error);

        alert("Server Error");

    });

}


// ======================================================
// PART 4
// AJAX DELETE
// ======================================================

document.addEventListener("click", function (e) {

    const deleteBtn = e.target.closest(".delete-btn");

    if (!deleteBtn) return;

    e.preventDefault();

    if (!confirm("Delete this question?")) {

        return;

    }

    const row = deleteBtn.closest("tr");

    const formData = new FormData();

    formData.append("id", row.dataset.id);

    fetch("/api/question/delete/", {

        method: "POST",

        headers: {

            "X-CSRFToken": getCookie("csrftoken")

        },

        body: formData

    })

    .then(res => res.json())

    .then(data => {

        if (data.success) {

            row.remove();

            alert(data.message);

        }

        else {

            alert(data.message);

        }

    })

    .catch(error => {

        console.error(error);

        alert("Server Error");

    });

});