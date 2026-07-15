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
const currentMarks =document.getElementById("currentMarks");

const maxMarks =document.getElementById("maxMarks");
const saveStatus = document.getElementById("saveStatus");
const alertBox = document.getElementById("alertBox");


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
        updateTotalMarks();

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
        updateTotalMarks();

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
    updateTotalMarks();

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

function updateTotalMarks(){

    let total = 0;

    document
    .querySelectorAll('[name="marks[]"]')
    .forEach(function(input){

        total += Number(input.value) || 0;

    });

    currentMarks.innerText = total;

    if(total > Number(maxMarks.innerText)){

        currentMarks.classList.remove("text-success");

        currentMarks.classList.add("text-danger");

    }

    else{

        currentMarks.classList.remove("text-danger");

        currentMarks.classList.add("text-success");

    }

}


/**
 * Bootstrap Alert
 */
function showAlert(message, type = "danger") {

    alertBox.className = `alert alert-${type} mb-3`;

    alertBox.innerHTML = message;

    alertBox.classList.remove("d-none");

    setTimeout(function(){

        alertBox.classList.add("d-none");

    },3000);

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
                <option value="3of4">Attempt Any 3 out of 4</option>
                <option value="4of5">Attempt Any 4 out of 5</option>
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
            name="co[]">

                <option value="CO1">CO1</option>
                <option value="CO2">CO2</option>
                <option value="CO3">CO3</option>
                <option value="CO4">CO4</option>
                <option value="CO5">CO5</option>
                <option value="CO6">CO6</option>

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
    
    if(data){

    row.querySelector('[name="attempt_rule[]"]').value =
        data.attempt_rule;

    row.querySelector('[name="unit[]"]').value =
        data.unit;

    row.querySelector('[name="bloom[]"]').value =
        data.bloom_level;

    row.querySelector('[name="co[]"]').value =
        data.co;    

    row.querySelector('[name="difficulty[]"]').value =
        data.difficulty;

    row.querySelector('[name="question_type[]"]').value =
        data.question_type;

    row.querySelector('[name="marks[]"]').value =
        data.marks;

    row.querySelector('[name="number_of_questions[]"]').value =
        data.number_of_questions;

    }

}   // <-- ADD THIS



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

function onAddRowClick(){
    createRow();
    updateRowNumbers();
    updateTotalMarks();
    markPatternChanged();
}

function onSavePatternClick(){

    const rows=[];

    document
    .querySelectorAll("#patternBody tr")
    .forEach(function(row,index){

        const marks =
        row.querySelector('[name="marks[]"]').value;

        const questions =
        row.querySelector('[name="number_of_questions[]"]').value;

        const unit =
        row.querySelector('[name="unit[]"]').value;

        const bloom =
        row.querySelector('[name="bloom[]"]').value;
        co:
        row.querySelector('[name="co[]"]').value;

        const difficulty =
        row.querySelector('[name="difficulty[]"]').value;

        const questionType =
        row.querySelector('[name="question_type[]"]').value;

        if(

            marks==="" ||

            questions==="" ||

            unit==="" ||

            bloom==="" ||

            difficulty==="" ||

            questionType===""

        ){

            showAlert(
                "Please complete all fields in Row " +
                (index + 1),
                "danger"
            );

            throw new Error("Validation Failed");

      }

        rows.push({

            display_order:
            row.querySelector(".row-order").innerText,

            question_number:
            row.querySelector('[name="question_number[]"]').value,

            attempt_rule:
            row.querySelector('[name="attempt_rule[]"]').value,

            custom_attempt_text:"",

            unit:
            row.querySelector('[name="unit[]"]').value,

            bloom_level:
            row.querySelector('[name="bloom[]"]').value,

            co:
            row.querySelector('[name="co[]"]').value,

            difficulty:
            row.querySelector('[name="difficulty[]"]').value,

            question_type:
            row.querySelector('[name="question_type[]"]').value,

            marks:
            row.querySelector('[name="marks[]"]').value,

            number_of_questions:
            row.querySelector('[name="number_of_questions[]"]').value,
        

        });

    });




    sendRows(rows);

}


function sendRows(rows){

    fetch(

        `/papers/builder/${getPatternId()}/save/`,

        {
            method:"POST",

            headers:{
                "Content-Type":"application/json",
                "X-CSRFToken":getCookie("csrftoken")
            },

            body:JSON.stringify({
                rows:rows
            })
        }

    )

    .then(response=>response.json())

    .then(data=>{

        if(data.success){

            markPatternSaved();

            showAlert(data.message);

        }else{

            showAlert("Save Failed", "danger");

        }

    })

    .catch(error=>{

        console.error(error);

    });

}