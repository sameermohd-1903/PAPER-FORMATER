"use strict";

/* ==========================================================
   Pattern Builder
   Paper Formatter
   ========================================================== */


/* ==========================================================
   1. DOM ELEMENTS
   ========================================================== */

const addRowBtn = document.getElementById("addRowBtn");
const savePatternBtn = document.getElementById("savePattern");

const patternTable = document.getElementById("patternTable");
const patternBody = document.getElementById("patternBody");

const patternId = document.getElementById("pattern-id");

const totalMarks = document.getElementById("paperTotalMarks");
const saveStatus = document.getElementById("saveStatus");


/* ==========================================================
   2. GLOBAL VARIABLES
   ========================================================== */

let rowCount = 0;
let patternChanged = false;


/* ==========================================================
   3. INITIALIZATION
   ========================================================== */

document.addEventListener("DOMContentLoaded", initializePatternBuilder);


/* ==========================================================
   4. INITIALIZE APPLICATION
   ========================================================== */

function initializePatternBuilder() {

    console.log("Pattern Builder Initialized");

    bindEvents();
    loadSavedRows();
    document.addEventListener("click", function(e){

    if(e.target.classList.contains("delete-row")){

        e.target.closest("tr").remove();

        updateRowNumbers();

        markPatternChanged();

    }

});

}


function loadSavedRows(){

    const patternId = getPatternId();

    fetch(

        `/papers/builder/${patternId}/rows/`

    )

    .then(response => response.json())

    .then(data => {

        data.rows.forEach(function(row){

            createRow(row);

        });

    })

    .catch(function(error){

        console.error(error);

    });

}


/* ==========================================================
   5. EVENT BINDINGS
   ========================================================== */

function bindEvents() {

    if (addRowBtn) {

        addRowBtn.addEventListener("click", onAddRowClick);

    }

    if (savePatternBtn) {

        savePatternBtn.addEventListener("click", onSavePatternClick);

    }

    document.addEventListener("change", function () {

        markPatternChanged();

    });
        document.addEventListener("click", handleTableButtons);
        
}

function handleTableButtons(e){

    if(e.target.classList.contains("move-up")){

        moveRowUp(e.target);

    }

    if(e.target.classList.contains("move-down")){

        moveRowDown(e.target);

    }

    if(e.target.classList.contains("delete-row")){

        deleteRow(e.target);

    }

}

function moveRowUp(button){

    const row = button.closest("tr");

    const previous = row.previousElementSibling;

    if(previous){

        row.parentNode.insertBefore(row, previous);

        updateRowNumbers();

        updateQuestionNumbers();

        markPatternChanged();

    }

}

function moveRowDown(button){

    const row = button.closest("tr");

    const next = row.nextElementSibling;

    if(next){

        row.parentNode.insertBefore(next, row);

        updateRowNumbers();

        updateQuestionNumbers();

        markPatternChanged();

    }

}

function deleteRow(button){

    button.closest("tr").remove();

    updateRowNumbers();

    updateQuestionNumbers();

    markPatternChanged();

}


/* ==========================================================
   6. UTILITY FUNCTIONS
   ========================================================== */

/**
 * Get Django CSRF Token
 */
function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            const cookie = cookies[i].trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;

            }

        }

    }

    return cookieValue;

}


/**
 * Mark pattern as modified
 */
function markPatternChanged() {

    patternChanged = true;

    if (saveStatus) {

        saveStatus.classList.remove("d-none");
        saveStatus.classList.remove("text-success");
        saveStatus.classList.add("text-danger");

        saveStatus.innerHTML = "● Unsaved Changes";

    }

}


/**
 * Mark pattern as saved
 */
function markPatternSaved() {

    patternChanged = false;

    if (saveStatus) {

        saveStatus.classList.remove("text-danger");
        saveStatus.classList.add("text-success");

        saveStatus.innerHTML = "✔ Saved";

    }

}


/**
 * Bootstrap Alert
 */
function showAlert(message, type = "success") {

    alert(message);

}


/**
 * Get Pattern ID
 */
function getPatternId() {

    if (!patternId)
        return null;

    return patternId.value;

}


/* ==========================================================
   Create Table Row
========================================================== */

function createRow(data = null) {

    rowCount++;

    const row = document.createElement("tr");

    row.innerHTML = `

        <td class="row-order">
            ${rowCount}
        </td>

        <td>
            <input
                type="text"
                class="form-control question-number"
                name="question_number[]"
                value="${data ? data.question_number : 'Q' + rowCount}"
                readonly>
        </td>

        <td>
            <select
                class="form-select"
                name="attempt_rule[]">

                <option value="all">Attempt All</option>
                <option value="1of2">Attempt Any 1 out of 2</option>
                <option value="2of3">Attempt Any 2 out of 3</option>
                <option value="custom">Custom</option>

            </select>
        </td>

        <td>

            <select
                class="form-select"
                name="unit[]">

                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>

            </select>

        </td>

        <td>

            <select
                class="form-select"
                name="bloom[]">

                <option value="remember">Remember</option>
                <option value="understand">Understand</option>
                <option value="apply">Apply</option>
                <option value="analyze">Analyze</option>
                <option value="evaluate">Evaluate</option>
                <option value="create">Create</option>

            </select>

        </td>

        <td>

            <select
                class="form-select"
                name="difficulty[]">

                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>

            </select>

        </td>

        <td>

            <select
                class="form-select"
                name="question_type[]">

                <option value="mcq">MCQ</option>
                <option value="very_short">Very Short</option>
                <option value="short">Short</option>
                <option value="long">Long</option>
                <option value="case_study">Case Study</option>
                <option value="programming">Programming</option>

            </select>

        </td>

        <td>

            <input
                type="number"
                class="form-control"
                name="marks[]"
                min="1">

        </td>

        <td>

            <input
                type="number"
                class="form-control"
                name="number_of_questions[]"
                value="1"
                min="1">

        </td>

        <td>

            <div class="btn-group">

            <button
            type="button"
            class="btn btn-secondary btn-sm move-up">

            ↑

            </button>

            <button
            type="button"
            class="btn btn-secondary btn-sm move-down">

            ↓

            </button>

            <button
            type="button"
            class="btn btn-danger btn-sm delete-row">

            Delete

            </button>

            </div>

        </td>

    `;

    patternBody.appendChild(row);

}

/* ==========================================================
   Update Row Numbers
========================================================== */

function updateRowNumbers() {

    const rows = patternBody.querySelectorAll("tr");

    rowCount = 0;

    rows.forEach(function(row){

        rowCount++;

        row.querySelector(".row-order").innerText = rowCount;

        row.querySelector(".question-number").value = "Q" + rowCount;

    });

}



/* ==========================================================
   7. PLACEHOLDER FUNCTIONS
   ========================================================== */

function onAddRowClick() {

    createRow();

    updateRowNumbers();

    markPatternChanged();

}

function onSavePatternClick() {

    console.log(getPatternId());

    markPatternSaved();

}