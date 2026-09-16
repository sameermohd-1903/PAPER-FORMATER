"use strict";


document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // DOM
    // =========================================================

    const patternBody =
        document.getElementById("patternBody");

    const addRowBtn =
        document.getElementById("addRowBtn");

    const totalMarksInput =
        document.getElementById("id_total_marks");

    const patternForm =
        document.getElementById("patternForm");


    if (!patternBody) {

        console.error(
            "Create Pattern: #patternBody not found."
        );

        return;

    }


    // =========================================================
    // ATTEMPT RULE INFORMATION
    // =========================================================

    const attemptRuleInfo = {

        "": {
            available: 0,
            attempted: 0
        },

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
    // ROW COUNT
    // =========================================================

    let rowCount =
        patternBody.querySelectorAll(
            "tr.main-pattern-row"
        ).length;


    // =========================================================
    // GET ATTEMPT INFORMATION
    // =========================================================

    function getAttemptInfo(attemptRule) {

        return (
            attemptRuleInfo[attemptRule] ||
            attemptRuleInfo[""]
        );

    }


    // =========================================================
    // DEFAULT SETTINGS
    // =========================================================

    function createDefaultSettings(count) {

        const settings = [];

        for (
            let i = 1;
            i <= count;
            i++
        ) {

            settings.push({

                slot_number: i,

                bloom_level: "1",

                co: "CO1",

                difficulty: "Easy"

            });

        }

        return settings;

    }


    // =========================================================
    // RESIZE SETTINGS
    // =========================================================

    function resizeSettings(
        settings,
        available
    ) {

        let result =
            Array.isArray(settings)
                ? settings.slice(0, available)
                : [];


        while (
            result.length < available
        ) {

            result.push({

                slot_number:
                    result.length + 1,

                bloom_level:
                    "1",

                co:
                    "CO1",

                difficulty:
                    "Easy"

            });

        }


        result.forEach(
            function (setting, index) {

                setting.slot_number =
                    index + 1;

                setting.bloom_level =
                    setting.bloom_level || "1";

                setting.co =
                    setting.co || "CO1";

                setting.difficulty =
                    setting.difficulty || "Easy";

            }
        );


        return result;

    }


    // =========================================================
    // SAVE SETTINGS HIDDEN FIELD
    // =========================================================

    function saveSettingsToHiddenField(
        row,
        settings
    ) {

        const hidden =
            row.querySelector(
                ".question-settings"
            );


        if (!hidden) {
            return;
        }


        hidden.value =
            JSON.stringify(settings);

    }


    // =========================================================
    // READ SETTINGS
    // =========================================================

    function readSettingsFromRow(row) {

        const hidden =
            row.querySelector(
                ".question-settings"
            );


        if (!hidden) {
            return [];
        }


        try {

            const data =
                JSON.parse(
                    hidden.value || "[]"
                );


            return Array.isArray(data)
                ? data
                : [];

        } catch (error) {

            console.error(
                "Question settings JSON error:",
                error
            );

            return [];

        }

    }


    // =========================================================
    // HTML ESCAPE
    // =========================================================

    function escapeHtml(value) {

        return String(value)

            .replace(/&/g, "&amp;")

            .replace(/</g, "&lt;")

            .replace(/>/g, "&gt;")

            .replace(/"/g, "&quot;")

            .replace(/'/g, "&#039;");

    }


    // =========================================================
    // CREATE ROW
    // =========================================================

    function createRow(data = null) {

        rowCount++;


        const attemptRule =
            data?.attempt_rule || "";


        const questionType =
            data?.question_type || "mcq";


        const marks =
            data?.marks ?? "";


        const attemptInfo =
            getAttemptInfo(
                attemptRule
            );


        let settings =
            Array.isArray(
                data?.question_settings
            )
                ? data.question_settings
                : createDefaultSettings(
                    attemptInfo.available
                );


        settings =
            resizeSettings(
                settings,
                attemptInfo.available
            );


        // =====================================================
        // MAIN ROW
        // =====================================================

        const row =
            document.createElement("tr");


        row.className =
            "main-pattern-row";


        row.innerHTML = `

            <td>

                <span class="row-order">
                    ${rowCount}
                </span>

                <input
                    type="hidden"
                    name="question_number[]"
                    value="Q${rowCount}"
                    class="question-number"
                >

                <input
                    type="hidden"
                    name="question_settings[]"
                    class="question-settings"
                    value=""
                >

            </td>


            <td>

                <select
                    name="attempt_rule[]"
                    class="form-select attempt-rule"
                    required
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


            <td>

                <select
                    name="question_type[]"
                    class="form-select question-type"
                    required
                >

                    <option value="mcq">
                        MCQ
                    </option>

                    <option value="ftq">
                        FTQ
                    </option>

                    <option value="cs">
                        Case Study
                    </option>

                </select>

            </td>


            <td>

                <input
                    type="number"
                    name="marks[]"
                    class="form-control marks-input"
                    min="1"
                    step="1"
                    value="${escapeHtml(marks)}"
                    placeholder="Marks"
                    required
                >

                <small class="text-muted">
                    Per question
                </small>

            </td>


            <td>

                <div class="d-flex gap-1 flex-wrap">

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

                </div>

            </td>


            <td>

                <button
                    type="button"
                    class="btn btn-primary btn-sm apply-settings"
                >
                    Apply
                </button>

            </td>

        `;


        // =====================================================
        // SETTINGS ROW
        // =====================================================

        const settingsRow =
            document.createElement("tr");


        settingsRow.className =
            "question-settings-row";


        settingsRow.style.display =
            "none";


        settingsRow.innerHTML = `

            <td colspan="6">

                <div class="card border-primary shadow-sm">

                    <div class="card-header bg-light">

                        <strong class="settings-title">
                            Question Settings
                        </strong>

                    </div>

                    <div class="card-body">

                        <div class="settings-container row g-3">
                        </div>

                        <div class="mt-4 d-flex gap-2">

                            <button
                                type="button"
                                class="btn btn-success save-settings"
                            >
                                Save
                            </button>

                            <button
                                type="button"
                                class="btn btn-secondary cancel-settings"
                            >
                                Cancel
                            </button>

                        </div>

                    </div>

                </div>

            </td>

        `;


        patternBody.appendChild(row);

        patternBody.appendChild(
            settingsRow
        );


        row.querySelector(
            ".attempt-rule"
        ).value =
            attemptRule;


        row.querySelector(
            ".question-type"
        ).value =
            questionType;


        saveSettingsToHiddenField(
            row,
            settings
        );


        updateRowNumbers();

        calculatePaperTotal();

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


        rowCount =
            rows.length;

    }


    // =========================================================
    // CALCULATE TOTAL
    // =========================================================

    function calculatePaperTotal() {

        let calculatedTotal = 0;


        const rows =
            patternBody.querySelectorAll(
                "tr.main-pattern-row"
            );


        rows.forEach(
            function (row) {

                const attemptSelect =
                    row.querySelector(
                        ".attempt-rule"
                    );


                const marksInput =
                    row.querySelector(
                        ".marks-input"
                    );


                if (
                    !attemptSelect ||
                    !marksInput
                ) {

                    return;

                }


                const marks =
                    parseInt(
                        marksInput.value,
                        10
                    ) || 0;


                const info =
                    getAttemptInfo(
                        attemptSelect.value
                    );


                calculatedTotal +=
                    marks *
                    info.attempted;

            }
        );


        const validationBox =
            document.getElementById(
                "totalMarksValidation"
            );


        const enteredTotal =
            totalMarksInput
                ? parseInt(
                    totalMarksInput.value,
                    10
                ) || 0
                : 0;


        if (!validationBox) {
            return;
        }


        // =====================================================
        // TOTAL NOT ENTERED
        // =====================================================

        if (enteredTotal <= 0) {

            validationBox.innerHTML = `
                <div class="alert alert-warning py-2">
                    ⚠ Please enter the Total Marks of the paper.
                </div>
            `;

            return;

        }


        // =====================================================
        // TOTAL MATCH
        // =====================================================

        if (
            enteredTotal ===
            calculatedTotal
        ) {

            validationBox.innerHTML = `
                <div class="alert alert-success py-2">
                    ✓ Total marks are correct.
                    <br>
                    Total = ${calculatedTotal}
                </div>
            `;

        }

        // =====================================================
        // TOTAL DOES NOT MATCH
        // =====================================================

        else {

            validationBox.innerHTML = `
                <div class="alert alert-danger py-2">
                    ⚠ Total marks do not match.
                    <br>
                    <strong>Entered Total:</strong>
                    ${enteredTotal}
                    <br>
                    <strong>Calculated Total:</strong>
                    ${calculatedTotal}
                </div>
            `;

        }

    }


    // =========================================================
    // MARK VALIDATION
    // =========================================================

    function validateRows() {

        const rows =
            patternBody.querySelectorAll(
                "tr.main-pattern-row"
            );


        if (rows.length === 0) {

            return {
                valid: false,
                message:
                    "Please add at least one pattern row."
            };

        }


        for (
            let i = 0;
            i < rows.length;
            i++
        ) {

            const row =
                rows[i];


            const attemptRule =
                row.querySelector(
                    ".attempt-rule"
                )?.value;


            const marks =
                parseInt(
                    row.querySelector(
                        ".marks-input"
                    )?.value,
                    10
                ) || 0;


            if (!attemptRule) {

                return {
                    valid: false,
                    message:
                        `Please select Attempt Rule for Row ${i + 1}.`
                };

            }


            if (marks <= 0) {

                return {
                    valid: false,
                    message:
                        `Please enter Marks / Question for Row ${i + 1}.`
                };

            }

        }


        const enteredTotal =
            parseInt(
                totalMarksInput?.value,
                10
            ) || 0;


        if (enteredTotal <= 0) {

            return {
                valid: false,
                message:
                    "Please enter the Total Marks."
            };

        }


        let calculatedTotal = 0;


        rows.forEach(
            function (row) {

                const marks =
                    parseInt(
                        row.querySelector(
                            ".marks-input"
                        ).value,
                        10
                    ) || 0;


                const attempt =
                    row.querySelector(
                        ".attempt-rule"
                    ).value;


                calculatedTotal +=
                    marks *
                    getAttemptInfo(
                        attempt
                    ).attempted;

            }
        );


        if (
            calculatedTotal !==
            enteredTotal
        ) {

            return {
                valid: false,
                message:
                    `Total Marks mismatch. Entered: ${enteredTotal}, Calculated: ${calculatedTotal}.`
            };

        }


        return {
            valid: true,
            message: ""
        };

    }


    // =========================================================
    // ADD ROW
    // =========================================================

    if (addRowBtn) {

        addRowBtn.addEventListener(
            "click",
            function () {

                createRow();

            }
        );

    }


    // =========================================================
    // INPUT
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


    if (totalMarksInput) {

        totalMarksInput.addEventListener(
            "input",
            calculatePaperTotal
        );

    }


    // =========================================================
    // CHANGE
    // =========================================================

    patternBody.addEventListener(
        "change",
        function (event) {

            if (
                event.target.classList.contains(
                    "attempt-rule"
                )
            ) {

                const row =
                    event.target.closest(
                        "tr.main-pattern-row"
                    );


                if (!row) {
                    return;
                }


                const info =
                    getAttemptInfo(
                        event.target.value
                    );


                let settings =
                    readSettingsFromRow(
                        row
                    );


                settings =
                    resizeSettings(
                        settings,
                        info.available
                    );


                saveSettingsToHiddenField(
                    row,
                    settings
                );


                calculatePaperTotal();

            }

        }
    );


    // =========================================================
    // TABLE BUTTONS
    // =========================================================

    patternBody.addEventListener(
        "click",
        function (event) {

            // -------------------------------------------------
            // DELETE
            // -------------------------------------------------

            const deleteBtn =
                event.target.closest(
                    ".delete-row"
                );


            if (deleteBtn) {

                const row =
                    deleteBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (!row) {
                    return;
                }


                const settingsRow =
                    row.nextElementSibling;


                if (
                    settingsRow &&
                    settingsRow.classList.contains(
                        "question-settings-row"
                    )
                ) {

                    settingsRow.remove();

                }


                row.remove();


                updateRowNumbers();

                calculatePaperTotal();

                return;

            }


            // -------------------------------------------------
            // MOVE UP
            // -------------------------------------------------

            const moveUpBtn =
                event.target.closest(
                    ".move-up"
                );


            if (moveUpBtn) {

                const row =
                    moveUpBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (!row) {
                    return;
                }


                const settingsRow =
                    row.nextElementSibling;


                const previousSettings =
                    row.previousElementSibling;


                if (
                    previousSettings &&
                    previousSettings.classList.contains(
                        "question-settings-row"
                    )
                ) {

                    const previousRow =
                        previousSettings.previousElementSibling;


                    const previousRowSettings =
                        previousRow?.nextElementSibling;


                    if (
                        previousRow &&
                        previousRow.classList.contains(
                            "main-pattern-row"
                        )
                    ) {

                        patternBody.insertBefore(
                            row,
                            previousRow
                        );


                        patternBody.insertBefore(
                            settingsRow,
                            row.nextElementSibling
                        );

                    }

                }


                updateRowNumbers();

                return;

            }


            // -------------------------------------------------
            // MOVE DOWN
            // -------------------------------------------------

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


                const settingsRow =
                    row.nextElementSibling;


                const nextRow =
                    settingsRow?.nextElementSibling;


                if (
                    nextRow &&
                    nextRow.classList.contains(
                        "main-pattern-row"
                    )
                ) {

                    const nextSettings =
                        nextRow.nextElementSibling;


                    if (nextSettings) {

                        patternBody.insertBefore(
                            row,
                            nextSettings.nextElementSibling
                        );


                        patternBody.insertBefore(
                            settingsRow,
                            row.nextElementSibling
                        );

                    }

                }


                updateRowNumbers();

                return;

            }


            // -------------------------------------------------
            // APPLY
            // -------------------------------------------------

            const applyBtn =
                event.target.closest(
                    ".apply-settings"
                );


            if (applyBtn) {

                const row =
                    applyBtn.closest(
                        "tr.main-pattern-row"
                    );


                if (row) {

                    openSettings(
                        row
                    );

                }

                return;

            }


            // -------------------------------------------------
            // SAVE SETTINGS
            // -------------------------------------------------

            const saveSettingsBtn =
                event.target.closest(
                    ".save-settings"
                );


            if (saveSettingsBtn) {

                const settingsRow =
                    saveSettingsBtn.closest(
                        ".question-settings-row"
                    );


                if (!settingsRow) {
                    return;
                }


                const row =
                    settingsRow.previousElementSibling;


                if (
                    row &&
                    row.classList.contains(
                        "main-pattern-row"
                    )
                ) {

                    saveSettings(
                        row,
                        settingsRow
                    );

                }

                return;

            }


            // -------------------------------------------------
            // CANCEL SETTINGS
            // -------------------------------------------------

            const cancelSettingsBtn =
                event.target.closest(
                    ".cancel-settings"
                );


            if (cancelSettingsBtn) {

                const settingsRow =
                    cancelSettingsBtn.closest(
                        ".question-settings-row"
                    );


                if (!settingsRow) {
                    return;
                }


                settingsRow.style.display =
                    "none";

                return;

            }

        }
    );


    // =========================================================
    // OPEN SETTINGS
    // =========================================================

    function openSettings(row) {

        const settingsRow =
            row.nextElementSibling;


        if (
            !settingsRow ||
            !settingsRow.classList.contains(
                "question-settings-row"
            )
        ) {

            return;

        }


        renderSettings(
            row,
            settingsRow
        );


        settingsRow.style.display =
            "";


        settingsRow.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });

    }


    // =========================================================
    // RENDER SETTINGS
    // =========================================================

    function renderSettings(
        row,
        settingsRow
    ) {

        const attempt =
            row.querySelector(
                ".attempt-rule"
            ).value;


        const info =
            getAttemptInfo(
                attempt
            );


        let settings =
            readSettingsFromRow(
                row
            );


        settings =
            resizeSettings(
                settings,
                info.available
            );


        const container =
            settingsRow.querySelector(
                ".settings-container"
            );


        const title =
            settingsRow.querySelector(
                ".settings-title"
            );


        title.textContent =
            `${info.available} Question Settings`;


        container.innerHTML = "";


        settings.forEach(
            function (setting, index) {

                const wrapper =
                    document.createElement(
                        "div"
                    );


                wrapper.className =
                    "col-lg-4 col-md-6";


                wrapper.innerHTML = `

                    <div class="border rounded p-3 h-100 bg-light">

                        <h6>
                            Question ${index + 1} Settings
                        </h6>
                                                <div class="mb-3">
    <label class="form-label">Unit</label>

    <select
    class="form-select setting-unit"
    data-index="${index}"
>
        <option value="">All Units</option>
        <option value="1">Unit 1</option>
        <option value="2">Unit 2</option>
        <option value="3">Unit 3</option>
        <option value="4">Unit 4</option>
        <option value="5">Unit 5</option>
        <option value="6">Unit 6</option>
        <option value="7">Unit 7</option>
        <option value="8">Unit 8</option>
    </select>
</div>

                        <label class="form-label">
                            Bloom Level
                        </label>

                        <select
                            class="form-select setting-bloom mb-3"
                            data-index="${index}"
                        >

                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                            <option value="4">4</option>
                            <option value="5">5</option>
                            <option value="6">6</option>

                        </select>


                        <label class="form-label">
                            CO
                        </label>

                        <input
                            type="text"
                            class="form-control setting-co mb-3"
                            data-index="${index}"
                            value="${escapeHtml(
                                setting.co || "CO1"
                            )}"
                        >


                        <label class="form-label">
                            Difficulty
                        </label>

                        <select
                            class="form-select setting-difficulty"
                            data-index="${index}"
                        >

                            <option value="Easy">Easy</option>
                            <option value="Medium">Medium</option>
                            <option value="Hard">Hard</option>

                        </select>


                    </div>

                `;


                container.appendChild(
                    wrapper
                );

            }
        );


        container
            .querySelectorAll(
                ".setting-bloom"
            )
            .forEach(
                function (select, index) {

                    select.value =
                        settings[index]
                            ?.bloom_level ||
                        "1";

                }
            );


        container
            .querySelectorAll(
                ".setting-difficulty"
            )
            .forEach(
                function (select, index) {

                    select.value =
                        settings[index]
                            ?.difficulty ||
                        "Easy";

                }
            );

    }


    // =========================================================
    // SAVE SETTINGS
    // =========================================================

    function saveSettings(
        row,
        settingsRow
    ) {

        const info =
            getAttemptInfo(
                row.querySelector(
                    ".attempt-rule"
                ).value
            );


        const newSettings = [];


        for (
            let i = 0;
            i < info.available;
            i++
        ) {

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


            newSettings.push({

                slot_number:
                    i + 1,

                bloom_level:
                    bloom?.value || "1",

                co:
                    co?.value.trim() || "CO1",

                difficulty:
                    difficulty?.value || "Easy"

            });

        }


        saveSettingsToHiddenField(
            row,
            newSettings
        );


        settingsRow.style.display =
            "none";

    }


    // =========================================================
    // FORM SUBMIT
    // =========================================================

    if (patternForm) {

        patternForm.addEventListener(
            "submit",
            function (event) {

                const validation =
                    validateRows();


                if (!validation.valid) {

                    event.preventDefault();


                    alert(
                        validation.message
                    );


                    return;

                }


                /*
                    IMPORTANT:

                    NO FETCH HERE.

                    Django receives the normal
                    POST request.

                    create_pattern() creates:

                    PaperPattern
                    +
                    PatternSection rows
                */

            }
        );

    }


    // =========================================================
    // INITIAL ROW
    // =========================================================

    if (
        patternBody.querySelectorAll(
            "tr.main-pattern-row"
        ).length === 0
    ) {

        createRow();

    }


    calculatePaperTotal();

});