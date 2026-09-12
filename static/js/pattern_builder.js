"use strict";

document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // DOM ELEMENTS
    // =========================================================

    const patternBody =
        document.getElementById("patternBody");

    const addRowBtn =
        document.getElementById("addRowBtn");

    const savePatternBtn =
        document.getElementById("savePattern");

    const currentMarksElement =
        document.getElementById("currentMarks");

    const maxMarksElement =
        document.getElementById("maxMarks");

    const saveStatus =
        document.getElementById("saveStatus");

    const patternIdElement =
        document.getElementById("pattern-id");


    if (!patternBody) {

        console.error(
            "patternBody not found"
        );

        return;

    }


    // =========================================================
    // PATTERN ID
    // =========================================================

    const patternId =
        patternIdElement
            ? patternIdElement.value
            : null;


    // =========================================================
    // ATTEMPT RULE INFORMATION
    // =========================================================

    const attemptRuleInfo = {

        "1of2": {
            available: 2,
            attempted: 1
        },

        "2of3": {
            available: 3,
            attempted: 2
        },

        "3of4": {
            available: 4,
            attempted: 3
        },

        "4of5": {
            available: 5,
            attempted: 4
        },

        "5of5": {
            available: 5,
            attempted: 5
        }

    };


    // =========================================================
    // GET ATTEMPT INFORMATION
    // =========================================================

    function getAttemptInfo(rule) {

        return (
            attemptRuleInfo[rule] || {
                available: 0,
                attempted: 0
            }
        );

    }


    // =========================================================
    // UPDATE ROW NUMBERS
    // =========================================================

    function updateRowNumbers() {

        const rows =
            patternBody.querySelectorAll(
                "tr.main-pattern-row"
            );


        rows.forEach(
            function (row, index) {

                const number =
                    index + 1;


                const order =
                    row.querySelector(
                        ".row-order"
                    );


                const questionNumber =
                    row.querySelector(
                        ".question-number"
                    );


                if (order) {

                    order.textContent =
                        number;

                }


                if (questionNumber) {

                    questionNumber.value =
                        "Q" + number;

                }

            }
        );

    }


    // =========================================================
    // CALCULATE PAPER TOTAL
    // =========================================================

    function calculatePaperTotal() {

        let currentMarks = 0;


        const rows =
            patternBody.querySelectorAll(
                "tr.main-pattern-row"
            );


        rows.forEach(
            function (row) {

                const attemptRule =
                    row.querySelector(
                        ".attempt-rule"
                    );


                const marksInput =
                    row.querySelector(
                        ".marks-input"
                    );


                if (
                    !attemptRule ||
                    !marksInput
                ) {

                    return;

                }


                const rule =
                    attemptRule.value;


                const marks =
                    parseInt(
                        marksInput.value
                    ) || 0;


                const info =
                    getAttemptInfo(rule);


                currentMarks +=
                    marks * info.attempted;

            }
        );


        if (currentMarksElement) {

            currentMarksElement.textContent =
                currentMarks;

        }


        if (maxMarksElement) {

            const maxMarks =
                parseInt(
                    maxMarksElement.textContent
                ) || 0;


            updateMarksMessage(
                currentMarks,
                maxMarks
            );

        }

    }


    // =========================================================
    // MARKS MESSAGE
    // =========================================================

    function updateMarksMessage(
        currentMarks,
        maxMarks
    ) {

        let message =
            document.getElementById(
                "marksValidationMessage"
            );


        if (!message) {

            message =
                document.createElement("div");


            message.id =
                "marksValidationMessage";


            message.className =
                "mt-3";


            const table =
                document.getElementById(
                    "patternTable"
                );


            if (table) {

                table.parentElement.after(
                    message
                );

            }

        }


        if (!message) {
            return;
        }


        if (currentMarks === 0) {

            message.innerHTML = "";

            return;

        }


        if (currentMarks === maxMarks) {

            message.innerHTML = `

                <div class="alert alert-success py-2">

                    ✓ Current Marks:
                    ${currentMarks} / ${maxMarks}

                    <br>

                    ✓ Total marks are correct.

                </div>

            `;

        } else {

            message.innerHTML = `

                <div class="alert alert-warning py-2">

                    ⚠ Current Marks:
                    ${currentMarks} / ${maxMarks}

                    <br>

                    Please make Current Marks equal
                    to Total Marks.

                </div>

            `;

        }

    }


    // =========================================================
    // CREATE NEW ROW
    // =========================================================

    function createRow(data = null) {

        const rowNumber =
            patternBody.querySelectorAll(
                "tr.main-pattern-row"
            ).length + 1;


        const row =
            document.createElement("tr");


        row.className =
            "main-pattern-row";


        row.innerHTML = `

            <!-- =================================================
                 ORDER
            ================================================== -->

            <td>

                <span class="row-order">
                    ${rowNumber}
                </span>


                <input
                    type="hidden"
                    name="question_number[]"
                    value="Q${rowNumber}"
                    class="question-number"
                >


                <input
                    type="hidden"
                    name="question_settings[]"
                    value="[]"
                    class="question-settings"
                >

            </td>


            <!-- =================================================
                 ATTEMPT RULE
            ================================================== -->

            <td>

                <select
                    name="attempt_rule[]"
                    class="form-select attempt-rule"
                >

                    <option value="">
                        Select Attempt Rule
                    </option>

                    <option value="1of2">
                        Attempt Any 1 out of 2
                    </option>

                    <option value="2of3">
                        Attempt Any 2 out of 3
                    </option>

                    <option value="3of4">
                        Attempt Any 3 out of 4
                    </option>

                    <option value="4of5">
                        Attempt Any 4 out of 5
                    </option>

                    <option value="5of5">
                        Attempt every question
                    </option>

                </select>

            </td>


            <!-- =================================================
                 QUESTION TYPE
            ================================================== -->

            <td>

                <select
                    name="question_type[]"
                    class="form-select question-type"
                >

                    <option value="mcq">
                        MCQ
                    </option>

                    <option value="ftq">
                        FTQ
                    </option>

                    <option value="casestudy">
                        Case Study
                    </option>

                </select>

            </td>


            <!-- =================================================
                 MARKS
            ================================================== -->

            <td>

                <input
                    type="number"
                    name="marks[]"
                    class="form-control marks-input"
                    min="1"
                    placeholder="Marks"
                    required
                >

                <small>
                    Per question
                </small>

            </td>


            <!-- =================================================
                 ACTION
            ================================================== -->

            <td>

                <button
                    type="button"
                    class="btn btn-danger btn-sm delete-row"
                >
                    Delete
                </button>


                <button
                    type="button"
                    class="btn btn-secondary btn-sm move-up"
                >
                    ↑
                </button>


                <button
                    type="button"
                    class="btn btn-secondary btn-sm move-down"
                >
                    ↓
                </button>

            </td>


            <!-- =================================================
                 APPLY
            ================================================== -->

            <td>

                <button
                    type="button"
                    class="btn btn-primary btn-sm apply-settings"
                >
                    Apply
                </button>

            </td>

        `;


        patternBody.appendChild(row);


        // =====================================================
        // LOAD EXISTING DATA
        // =====================================================

        if (data) {

            const attemptRule =
                row.querySelector(
                    ".attempt-rule"
                );


            const questionType =
                row.querySelector(
                    ".question-type"
                );


            const marksInput =
                row.querySelector(
                    ".marks-input"
                );


            if (
                attemptRule &&
                data.attempt_rule
            ) {

                attemptRule.value =
                    data.attempt_rule;

            }


            if (
                questionType &&
                data.question_type
            ) {

                questionType.value =
                    data.question_type;

            }


            if (
                marksInput &&
                data.marks
            ) {

                marksInput.value =
                    data.marks;

            }

        }


        updateRowNumbers();

        calculatePaperTotal();

    }


    // =========================================================
    // ADD ROW
    // =========================================================

    if (addRowBtn) {

        addRowBtn.addEventListener(
            "click",
            function () {

                console.log(
                    "ADD ROW BUTTON WORKING"
                );


                createRow();

            }
        );

    }


    // =========================================================
    // TABLE BUTTONS
    // =========================================================

    patternBody.addEventListener(
        "click",
        function (event) {


            // =================================================
            // DELETE
            // =================================================

            const deleteBtn =
                event.target.closest(
                    ".delete-row"
                );


            if (deleteBtn) {

                const row =
                    deleteBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (row) {

                    const settingsRow =
                        row.nextElementSibling;


                    if (
                        settingsRow &&
                        settingsRow.classList.contains(
                            "settings-row"
                        )
                    ) {

                        settingsRow.remove();

                    }


                    row.remove();

                }


                updateRowNumbers();

                calculatePaperTotal();

                return;

            }


            // =================================================
            // MOVE UP
            // =================================================

            const moveUpBtn =
                event.target.closest(
                    ".move-up"
                );


            if (moveUpBtn) {

                const row =
                    moveUpBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (
                    row &&
                    row.previousElementSibling
                ) {

                    const previousRow =
                        row.previousElementSibling;


                    if (
                        previousRow.classList.contains(
                            "settings-row"
                        )
                    ) {

                        return;

                    }


                    patternBody.insertBefore(
                        row,
                        previousRow
                    );

                }


                updateRowNumbers();

                return;

            }


            // =================================================
            // MOVE DOWN
            // =================================================

            const moveDownBtn =
                event.target.closest(
                    ".move-down"
                );


            if (moveDownBtn) {

                const row =
                    moveDownBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (!row) {
                    return;
                }


                const nextRow =
                    row.nextElementSibling;


                if (
                    nextRow &&
                    nextRow.classList.contains(
                        "settings-row"
                    )
                ) {

                    const rowAfterSettings =
                        nextRow.nextElementSibling;


                    if (rowAfterSettings) {

                        patternBody.insertBefore(
                            rowAfterSettings,
                            row
                        );

                    }

                } else if (nextRow) {

                    patternBody.insertBefore(
                        nextRow,
                        row
                    );

                }


                updateRowNumbers();

                return;

            }


            // =================================================
            // APPLY
            // =================================================

            const applyBtn =
                event.target.closest(
                    ".apply-settings"
                );


            if (applyBtn) {

                console.log(
                    "APPLY BUTTON WORKING"
                );


                const row =
                    applyBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (row) {

                    openSettings(row);

                }


                return;

            }

        }
    );


    // =========================================================
    // ATTEMPT RULE CHANGE
    // =========================================================

    patternBody.addEventListener(
        "change",
        function (event) {

            if (
                event.target.classList.contains(
                    "attempt-rule"
                )
            ) {

                calculatePaperTotal();

            }

        }
    );


    // =========================================================
    // MARKS CHANGE
    // =========================================================

    patternBody.addEventListener(
        "input",
        function (event) {

            if (
                event.target.classList.contains(
                    "marks-input"
                )
            ) {

                calculatePaperTotal();

            }

        }
    );


    // =========================================================
    // OPEN INLINE SETTINGS
    // =========================================================

    function openSettings(row) {

        // -----------------------------------------------------
        // REMOVE OLD SETTINGS
        // -----------------------------------------------------

        const oldSettings =
            document.querySelector(
                ".settings-row"
            );


        if (oldSettings) {

            oldSettings.remove();

        }


        // -----------------------------------------------------
        // GET ATTEMPT RULE
        // -----------------------------------------------------

        const attemptRule =
            row.querySelector(
                ".attempt-rule"
            );


        if (!attemptRule) {
            return;
        }


        const rule =
            attemptRule.value;


        // -----------------------------------------------------
        // CHECK ATTEMPT RULE
        // -----------------------------------------------------

        if (!rule) {

            showInlineMessage(
                row,
                "Please select an Attempt Rule first."
            );

            return;

        }


        const info =
            getAttemptInfo(rule);


        if (info.available === 0) {
            return;
        }


        // -----------------------------------------------------
        // GET EXISTING SETTINGS
        // -----------------------------------------------------

        const hiddenInput =
            row.querySelector(
                ".question-settings"
            );


        let existingSettings = [];


        if (hiddenInput) {

            try {

                existingSettings =
                    JSON.parse(
                        hiddenInput.value || "[]"
                    );

            } catch (error) {

                console.error(
                    "Invalid question settings JSON:",
                    error
                );


                existingSettings = [];

            }

        }


        // -----------------------------------------------------
        // CREATE SETTINGS ROW
        // -----------------------------------------------------

        const settingsRow =
            document.createElement("tr");


        settingsRow.className =
            "settings-row";


        const settingsCell =
            document.createElement("td");


        settingsCell.colSpan = 6;


        settingsCell.innerHTML = `

            <div
                class="border border-primary rounded p-3"
                style="background:#f8f9fa;"
            >

                <h5 class="mb-3">
                    ${info.available} Questions Settings
                </h5>


                <div
                    class="row g-3 settings-container"
                >
                </div>


                <div class="mt-3">

                    <button
                        type="button"
                        class="btn btn-success save-inline-settings"
                    >
                        Save
                    </button>


                    <button
                        type="button"
                        class="btn btn-secondary cancel-inline-settings"
                    >
                        Cancel
                    </button>

                </div>

            </div>

        `;


        settingsRow.appendChild(
            settingsCell
        );


        // -----------------------------------------------------
        // INSERT SETTINGS BELOW ROW
        // -----------------------------------------------------

        row.after(
            settingsRow
        );


        const settingsContainer =
            settingsRow.querySelector(
                ".settings-container"
            );


        // =====================================================
        // CREATE INDIVIDUAL QUESTION SETTINGS
        // =====================================================

        for (
            let i = 1;
            i <= info.available;
            i++
        ) {

            const existing =
                existingSettings.find(
                    function (item) {

                        return (
                            parseInt(
                                item.slot_number
                            ) === i
                        );

                    }
                );


            // -------------------------------------------------
            // EXISTING VALUES
            // -------------------------------------------------

            const unitValue =
                existing &&
                existing.unit !== undefined
                    ? String(existing.unit)
                    : "";


            const bloomValue =
                existing &&
                existing.bloom_level !== undefined
                    ? String(existing.bloom_level)
                    : "1";


            const coValue =
                existing &&
                existing.co
                    ? existing.co
                    : "CO1";


            const difficultyValue =
                existing &&
                existing.difficulty
                    ? String(
                        existing.difficulty
                    ).toLowerCase()
                    : "easy";


            // -------------------------------------------------
            // QUESTION CARD
            // -------------------------------------------------

            const settingCol =
                document.createElement("div");


            settingCol.className =
                "col-md-6";


            settingCol.innerHTML = `

                <div class="card h-100">

                    <div class="card-body">

                        <h6 class="card-title">
                            Question ${i} Settings
                        </h6>


                        <!-- =================================
                             UNIT
                        ================================== -->

                        <label class="form-label">
                            Unit
                        </label>


                        <select
                            class="form-select setting-unit mb-3"
                            data-index="${i}"
                        >

                            <option
                                value=""
                                ${unitValue === ""
                                    ? "selected"
                                    : ""}
                            >
                                All Units
                            </option>


                            <option
                                value="1"
                                ${unitValue === "1"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 1
                            </option>


                            <option
                                value="2"
                                ${unitValue === "2"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 2
                            </option>


                            <option
                                value="3"
                                ${unitValue === "3"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 3
                            </option>


                            <option
                                value="4"
                                ${unitValue === "4"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 4
                            </option>


                            <option
                                value="5"
                                ${unitValue === "5"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 5
                            </option>


                            <option
                                value="6"
                                ${unitValue === "6"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 6
                            </option>


                            <option
                                value="7"
                                ${unitValue === "7"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 7
                            </option>


                            <option
                                value="8"
                                ${unitValue === "8"
                                    ? "selected"
                                    : ""}
                            >
                                Unit 8
                            </option>

                        </select>


                        <!-- =================================
                             BLOOM LEVEL
                        ================================== -->

                        <label class="form-label">
                            Bloom Level
                        </label>


                        <select
                            class="form-select setting-bloom mb-3"
                            data-index="${i}"
                        >

                            <option
                                value="1"
                                ${bloomValue === "1"
                                    ? "selected"
                                    : ""}
                            >
                                Remember
                            </option>


                            <option
                                value="2"
                                ${bloomValue === "2"
                                    ? "selected"
                                    : ""}
                            >
                                Understand
                            </option>


                            <option
                                value="3"
                                ${bloomValue === "3"
                                    ? "selected"
                                    : ""}
                            >
                                Apply
                            </option>


                            <option
                                value="4"
                                ${bloomValue === "4"
                                    ? "selected"
                                    : ""}
                            >
                                Analyze
                            </option>


                            <option
                                value="5"
                                ${bloomValue === "5"
                                    ? "selected"
                                    : ""}
                            >
                                Evaluate
                            </option>


                            <option
                                value="6"
                                ${bloomValue === "6"
                                    ? "selected"
                                    : ""}
                            >
                                Create
                            </option>

                        </select>


                        <!-- =================================
                             CO
                        ================================== -->

                        <label class="form-label">
                            CO
                        </label>


                        <input
                            type="text"
                            class="form-control setting-co mb-3"
                            data-index="${i}"
                            value="${coValue}"
                        >


                        <!-- =================================
                             DIFFICULTY
                        ================================== -->

                        <label class="form-label">
                            Difficulty
                        </label>


                        <select
                            class="form-select setting-difficulty"
                            data-index="${i}"
                        >

                            <option
                                value="easy"
                                ${difficultyValue === "easy"
                                    ? "selected"
                                    : ""}
                            >
                                Easy
                            </option>


                            <option
                                value="medium"
                                ${difficultyValue === "medium"
                                    ? "selected"
                                    : ""}
                            >
                                Medium
                            </option>


                            <option
                                value="hard"
                                ${difficultyValue === "hard"
                                    ? "selected"
                                    : ""}
                            >
                                Hard
                            </option>

                        </select>

                    </div>

                </div>

            `;


            settingsContainer.appendChild(
                settingCol
            );

        }


        // =====================================================
        // SAVE INLINE SETTINGS
        // =====================================================

        settingsRow
            .querySelector(
                ".save-inline-settings"
            )
            .addEventListener(
                "click",
                function () {

                    const settings = [];


                    // -----------------------------------------
                    // COLLECT EVERY QUESTION'S SETTINGS
                    // -----------------------------------------

                    for (
                        let i = 1;
                        i <= info.available;
                        i++
                    ) {

                        const unit =
                            settingsRow.querySelector(
                                `.setting-unit[data-index="${i}"]`
                            );


                        const bloom =
                            settingsRow.querySelector(
                                `.setting-bloom[data-index="${i}"]`
                            );


                        const co =
                            settingsRow.querySelector(
                                `.setting-co[data-index="${i}"]`
                            );


                        const difficulty =
                            settingsRow.querySelector(
                                `.setting-difficulty[data-index="${i}"]`
                            );


                        settings.push({

                            // -----------------------------
                            // QUESTION SLOT
                            // -----------------------------

                            slot_number: i,


                            // -----------------------------
                            // INDIVIDUAL UNIT
                            // -----------------------------

                            unit:
                                unit
                                    ? unit.value
                                    : "",


                            // -----------------------------
                            // BLOOM
                            // -----------------------------

                            bloom_level:
                                bloom
                                    ? bloom.value
                                    : "1",


                            // -----------------------------
                            // CO
                            // -----------------------------

                            co:
                                co
                                    ? (
                                        co.value.trim() ||
                                        "CO1"
                                    )
                                    : "CO1",


                            // -----------------------------
                            // DIFFICULTY
                            // -----------------------------

                            difficulty:
                                difficulty
                                    ? difficulty.value
                                    : "easy"

                        });

                    }


                    // -----------------------------------------
                    // SAVE JSON
                    // -----------------------------------------

                    if (hiddenInput) {

                        hiddenInput.value =
                            JSON.stringify(
                                settings
                            );

                    }


                    console.log(
                        "Saved question settings:",
                        settings
                    );


                    settingsRow.remove();

                }
            );


        // =====================================================
        // CANCEL
        // =====================================================

        settingsRow
            .querySelector(
                ".cancel-inline-settings"
            )
            .addEventListener(
                "click",
                function () {

                    settingsRow.remove();

                }
            );

    }


    // =========================================================
    // INLINE MESSAGE
    // =========================================================

    function showInlineMessage(
        row,
        message
    ) {

        const oldMessage =
            document.querySelector(
                ".inline-row-message"
            );


        if (oldMessage) {

            oldMessage.remove();

        }


        const messageRow =
            document.createElement("tr");


        messageRow.className =
            "inline-row-message";


        messageRow.innerHTML = `

            <td colspan="6">

                <div class="alert alert-warning mb-0">

                    ${message}

                </div>

            </td>

        `;


        row.after(
            messageRow
        );


        setTimeout(
            function () {

                messageRow.remove();

            },
            2500
        );

    }


    // =========================================================
    // SAVE PATTERN
    // =========================================================

    if (savePatternBtn) {

        savePatternBtn.addEventListener(
            "click",
            function () {

                console.log(
                    "SAVE PATTERN BUTTON WORKING"
                );


                if (!patternId) {

                    showSaveMessage(
                        "Pattern ID not found.",
                        "danger"
                    );

                    return;

                }


                const rows = [];


                const tableRows =
                    patternBody.querySelectorAll(
                        "tr.main-pattern-row"
                    );


                tableRows.forEach(
                    function (row, index) {

                        const attemptRule =
                            row.querySelector(
                                ".attempt-rule"
                            );


                        const questionType =
                            row.querySelector(
                                ".question-type"
                            );


                        const marks =
                            row.querySelector(
                                ".marks-input"
                            );


                        const settingsInput =
                            row.querySelector(
                                ".question-settings"
                            );


                        let questionSettings = [];


                        if (settingsInput) {

                            try {

                                questionSettings =
                                    JSON.parse(
                                        settingsInput.value ||
                                        "[]"
                                    );

                            } catch (error) {

                                console.error(
                                    "Invalid settings:",
                                    error
                                );


                                questionSettings = [];

                            }

                        }


                        const rule =
                            attemptRule
                                ? attemptRule.value
                                : "";


                        const attemptInfo =
                            getAttemptInfo(rule);


                        rows.push({

                            display_order:
                                index + 1,


                            question_number:
                                "Q" +
                                (index + 1),


                            attempt_rule:
                                rule,


                            custom_attempt_text:
                                "",


                            // ---------------------------------
                            // SECTION UNIT IS NOW EMPTY
                            // ---------------------------------
                            // Unit belongs to each question
                            // inside question_settings.

                            unit:
                                "",


                            bloom_level:
                                "1",


                            co:
                                "CO1",


                            difficulty:
                                "easy",


                            question_type:
                                questionType
                                    ? questionType.value
                                    : "mcq",


                            marks:
                                marks
                                    ? marks.value
                                    : "",


                            // ---------------------------------
                            // NUMBER OF QUESTIONS
                            // ---------------------------------

                            number_of_questions:
                                attemptInfo.available,


                            // ---------------------------------
                            // INDIVIDUAL SETTINGS
                            // ---------------------------------

                            question_settings:
                                questionSettings

                        });

                    }
                );


                // =================================================
                // VALIDATION
                // =================================================

                for (
                    const row of rows
                ) {

                    if (!row.attempt_rule) {

                        showSaveMessage(
                            "Please select Attempt Rule for every row.",
                            "warning"
                        );

                        return;

                    }


                    if (
                        !row.marks ||
                        parseInt(row.marks) <= 0
                    ) {

                        showSaveMessage(
                            "Please enter Marks for every row.",
                            "warning"
                        );

                        return;

                    }


                    if (
                        !row.question_settings ||
                        row.question_settings.length !==
                        row.number_of_questions
                    ) {

                        showSaveMessage(
                            `Please click Apply and save settings for ${row.question_number}.`,
                            "warning"
                        );

                        return;

                    }


                    // -----------------------------------------
                    // CHECK EVERY SETTING HAS SLOT NUMBER
                    // -----------------------------------------

                    const invalidSetting =
                        row.question_settings.some(
                            function (setting) {

                                return (
                                    !setting.slot_number
                                );

                            }
                        );


                    if (invalidSetting) {

                        showSaveMessage(
                            `Invalid question settings for ${row.question_number}.`,
                            "warning"
                        );

                        return;

                    }

                }


                // =================================================
                // MARKS VALIDATION
                // =================================================

                const currentMarks =
                    parseInt(
                        currentMarksElement
                            ? currentMarksElement.textContent
                            : 0
                    ) || 0;


                const maxMarks =
                    parseInt(
                        maxMarksElement
                            ? maxMarksElement.textContent
                            : 0
                    ) || 0;


                if (
                    currentMarks !== maxMarks
                ) {

                    showSaveMessage(
                        `Current Marks (${currentMarks}) must equal Total Marks (${maxMarks}).`,
                        "warning"
                    );

                    return;

                }


                // =================================================
                // SEND TO DJANGO
                // =================================================

                fetch(
                    `/papers/builder/${patternId}/save/`,
                    {

                        method: "POST",


                        headers: {

                            "Content-Type":
                                "application/json",

                            "X-CSRFToken":
                                getCookie(
                                    "csrftoken"
                                )

                        },


                        body:
                            JSON.stringify({
                                rows: rows
                            })

                    }
                )

                .then(
                    function (response) {

                        if (!response.ok) {

                            throw new Error(
                                "Server returned " +
                                response.status
                            );

                        }


                        return response.json();

                    }
                )

                .then(
                    function (data) {

                        if (data.success) {

                            showSaveMessage(
                                data.message ||
                                "Pattern saved successfully.",
                                "success"
                            );

                        } else {

                            showSaveMessage(
                                data.message ||
                                "Unable to save pattern.",
                                "danger"
                            );

                        }

                    }
                )

                .catch(
                    function (error) {

                        console.error(
                            "Save Pattern Error:",
                            error
                        );


                        showSaveMessage(
                            "Something went wrong while saving the pattern.",
                            "danger"
                        );

                    }
                );

            }
        );

    }


    // =========================================================
    // SAVE MESSAGE
    // =========================================================

    function showSaveMessage(
        message,
        type
    ) {

        if (!saveStatus) {
            return;
        }


        saveStatus.className =
            `alert alert-${type} mt-3`;


        saveStatus.textContent =
            message;


        saveStatus.classList.remove(
            "d-none"
        );


        setTimeout(
            function () {

                saveStatus.classList.add(
                    "d-none"
                );

            },
            3000
        );

    }


    // =========================================================
    // CSRF
    // =========================================================

    function getCookie(name) {

        let cookieValue = null;


        if (document.cookie) {

            const cookies =
                document.cookie.split(";");


            for (
                let cookie of cookies
            ) {

                cookie =
                    cookie.trim();


                if (
                    cookie.startsWith(
                        name + "="
                    )
                ) {

                    cookieValue =
                        decodeURIComponent(
                            cookie.substring(
                                name.length + 1
                            )
                        );

                    break;

                }

            }

        }


        return cookieValue;

    }


    // =========================================================
    // INITIALIZE EXISTING ROWS
    // =========================================================

    const existingRows =
        patternBody.querySelectorAll(
            "tr.main-pattern-row"
        );


    existingRows.forEach(
        function (row) {

            // Do not convert arbitrary rows
            // into main pattern rows.

            if (
                !row.classList.contains(
                    "main-pattern-row"
                )
            ) {

                return;

            }

        }
    );


    updateRowNumbers();

    calculatePaperTotal();


    // =========================================================
    // DEBUG
    // =========================================================

    console.log(
        "======================================"
    );

    console.log(
        "PATTERN BUILDER JS LOADED"
    );

    console.log(
        "Pattern ID:",
        patternId
    );

    console.log(
        "Unit is configured per question"
    );

    console.log(
        "======================================"

    );

});