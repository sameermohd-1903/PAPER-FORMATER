"use strict";

document.addEventListener("DOMContentLoaded", function () {

    console.log("QUESTION ADD JS LOADED");

    const levelSelect = document.getElementById("id_level");
    const programSelect = document.getElementById("id_program");
    const semesterSelect = document.getElementById("id_semester");
    const subjectSelect = document.getElementById("id_subject");

    console.log("Level:", levelSelect);
    console.log("Program:", programSelect);
    console.log("Semester:", semesterSelect);
    console.log("Subject:", subjectSelect);

    console.log("Programs URL:", window.programsUrl);
    console.log("Semesters URL:", window.semestersUrl);
    console.log("Subjects URL:", window.subjectsUrl);


    // =========================================================
    // CHECK ELEMENTS
    // =========================================================

    if (!levelSelect || !programSelect || !semesterSelect || !subjectSelect) {
        console.error("One or more dropdowns were not found.");
        return;
    }


    // =========================================================
    // LOAD PROGRAMS
    // =========================================================

    async function loadPrograms(level) {

        console.log("Loading programs for level:", level);

        programSelect.innerHTML =
            '<option value="">Select Program</option>';

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!level) {
            return;
        }

        try {

            const url =
                `${window.programsUrl}?level=${encodeURIComponent(level)}`;

            console.log("Fetching:", url);

            const response = await fetch(url);

            console.log("Program response:", response.status);

            if (!response.ok) {
                throw new Error(
                    `Program request failed: ${response.status}`
                );
            }

            const programs = await response.json();

            console.log("Programs received:", programs);

            programs.forEach(function (program) {

                const option =
                    document.createElement("option");

                option.value = program.id;
                option.textContent = program.name;

                programSelect.appendChild(option);
            });

        } catch (error) {

            console.error(
                "Program loading error:",
                error
            );
        }
    }


    // =========================================================
    // LEVEL → PROGRAM
    // =========================================================

    levelSelect.addEventListener("change", function () {

        loadPrograms(this.value);

    });


    // =========================================================
    // LOAD PROGRAMS WHEN PAGE OPENS
    // =========================================================

    if (levelSelect.value) {

        loadPrograms(levelSelect.value);

    }


    // =========================================================
    // PROGRAM → SEMESTER
    // =========================================================

    programSelect.addEventListener("change", async function () {

        const programId = this.value;

        console.log("Selected program:", programId);

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!programId) {
            return;
        }

        try {

            const response = await fetch(
                `${window.semestersUrl}?program=${encodeURIComponent(programId)}`
            );

            if (!response.ok) {
                throw new Error(
                    `Semester request failed: ${response.status}`
                );
            }

            const semesters = await response.json();

            console.log("Semesters received:", semesters);

            semesters.forEach(function (semester) {

                const option =
                    document.createElement("option");

                option.value = semester.id;

                option.textContent =
                    `Semester ${semester.number}`;

                semesterSelect.appendChild(option);

            });

        } catch (error) {

            console.error(
                "Semester loading error:",
                error
            );
        }
    });


    // =========================================================
    // SEMESTER → SUBJECT
    // =========================================================

    semesterSelect.addEventListener("change", async function () {

        const semesterId = this.value;
        const programId = programSelect.value;

        console.log(
            "Selected program:",
            programId,
            "Selected semester:",
            semesterId
        );

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!programId || !semesterId) {
            return;
        }

        try {

            const response = await fetch(
                `${window.subjectsUrl}?program=${encodeURIComponent(programId)}&semester=${encodeURIComponent(semesterId)}`
            );

            if (!response.ok) {
                throw new Error(
                    `Subject request failed: ${response.status}`
                );
            }

            const subjects = await response.json();

            console.log("Subjects received:", subjects);

            subjects.forEach(function (subject) {

                const option =
                    document.createElement("option");

                option.value = subject.id;
                option.textContent = subject.name;

                subjectSelect.appendChild(option);

            });

        } catch (error) {

            console.error(
                "Subject loading error:",
                error
            );
        }
    });

});




// ============================================================
// CHECK QUESTION SIMILARITY
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    const checkSimilarityBtn =
        document.getElementById("checkSimilarityBtn");

    const similarityLoading =
        document.getElementById("similarityLoading");

    const similarityResult =
        document.getElementById("similarityResult");

    if (!checkSimilarityBtn) {
        return;
    }

    checkSimilarityBtn.addEventListener("click", async function () {

        const questionField =
            document.getElementById("id_question_text");

        const programField =
            document.getElementById("id_program");

        const semesterField =
            document.getElementById("id_semester");

        const subjectField =
            document.getElementById("id_subject");

        const questionText =
            questionField ? questionField.value.trim() : "";

        const program =
            programField ? programField.value : "";

        const semester =
            semesterField ? semesterField.value : "";

        const subject =
            subjectField ? subjectField.value : "";

        // --------------------------------------------------------
        // Validate question
        // --------------------------------------------------------

        if (!questionText) {
            alert("Please enter a question first.");
            return;
        }

        // --------------------------------------------------------
        // Validate academic selections
        // --------------------------------------------------------

        if (!program || !semester || !subject) {
            alert(
                "Please select Program, Semester and Subject first."
            );
            return;
        }

        // --------------------------------------------------------
        // Show loading
        // --------------------------------------------------------

        similarityLoading.classList.remove("d-none");

        similarityResult.classList.add("d-none");
        similarityResult.innerHTML = "";

        checkSimilarityBtn.disabled = true;

        try {

            const formData = new FormData();

            formData.append(
                "question_text",
                questionText
            );

            formData.append(
                "program",
                program
            );

            formData.append(
                "semester",
                semester
            );

            formData.append(
                "subject",
                subject
            );

            // ----------------------------------------------------
            // Send request
            // ----------------------------------------------------

            const response = await fetch(
                window.similarityUrl,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": document.querySelector(
                            '[name=csrfmiddlewaretoken]'
                        ).value
                    },

                    body: formData
                }
            );

            const data = await response.json();

            // ----------------------------------------------------
            // Backend error
            // ----------------------------------------------------

            if (!response.ok || !data.success) {

                throw new Error(
                    data.message ||
                    "Similarity check failed."
                );
            }

            // ----------------------------------------------------
            // No similar questions
            // ----------------------------------------------------

            if (!data.has_similar) {

                similarityResult.innerHTML = `
                    <div class="alert alert-success">
                        <strong>✓ No Similar Questions Found</strong>
                        <br>
                        This question does not appear to be
                        similar to an existing question.
                    </div>
                `;

            }

            // ----------------------------------------------------
            // Similar questions found
            // ----------------------------------------------------

            else {

                let html = `
                    <div class="alert alert-warning">
                        <strong>⚠ Similar Questions Found</strong>
                        <br>
                        The following questions may be similar:
                    </div>

                    <div class="list-group">
                `;

                data.matches.forEach(function (match) {

                    html += `
                        <div class="list-group-item">
                            ${match.question_text || match.question || ""}
                        </div>
                    `;

                });

                html += `
                    </div>
                `;

                similarityResult.innerHTML = html;
            }

            similarityResult.classList.remove("d-none");

        }

        catch (error) {

            console.error(
                "Similarity check error:",
                error
            );

            similarityResult.innerHTML = `
                <div class="alert alert-danger">
                    <strong>Similarity Check Failed</strong>
                    <br>
                    ${error.message}
                </div>
            `;

            similarityResult.classList.remove("d-none");
        }

        finally {

            similarityLoading.classList.add("d-none");

            checkSimilarityBtn.disabled = false;
        }

    });

});
