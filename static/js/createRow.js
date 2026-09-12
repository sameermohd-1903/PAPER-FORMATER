"use strict";

/* ==========================================================
   CREATE TABLE ROW
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
                name="bloom[]">

                <option value="">Select Bloom</option>
                <option value="1">Remember</option>
                <option value="2">Understand</option>
                <option value="3">Apply</option>
                <option value="4">Analyze</option>
                <option value="5">Evaluate</option>
                <option value="6">Create</option>

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
                <option value="ftq">FTQ</option>
                <option value="cs">Case Study</option>

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

    if (data) {

        row.querySelector('[name="attempt_rule[]"]').value =
            data.attempt_rule || "all";

        row.querySelector('[name="bloom[]"]').value =
            data.bloom_level || "";

        row.querySelector('[name="co[]"]').value =
            data.co || "CO1";

        row.querySelector('[name="difficulty[]"]').value =
            data.difficulty || "easy";

        if (data.question_type) {

            row.querySelector('[name="question_type[]"]').value =
                data.question_type.toLowerCase();

        }

        row.querySelector('[name="marks[]"]').value =
            data.marks || "";

    }

}