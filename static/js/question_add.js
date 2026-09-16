"use strict";

document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // FORM ELEMENTS
    // =====================================================

    const levelSelect =
        document.getElementById("id_level");

    const programSelect =
        document.getElementById("id_program");

    const semesterSelect =
        document.getElementById("id_semester");

    const subjectSelect =
        document.getElementById("id_subject");

    const questionText =
        document.getElementById("id_question_text");


    // =====================================================
    // SIMILARITY ELEMENTS
    // =====================================================

    const checkSimilarityBtn =
        document.getElementById("checkSimilarityBtn");

    const similarityLoading =
        document.getElementById("similarityLoading");

    const similarityResult =
        document.getElementById("similarityResult");

    const similarityApproved =
        document.getElementById("similarityApproved");


    // =====================================================
    // LEVEL → PROGRAM
    // =====================================================

    levelSelect.addEventListener("change", function () {

        const level = this.value;

        programSelect.innerHTML =
            '<option value="">Select Program</option>';

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!level) {
            return;
        }

        fetch(
            `${programsUrl}?level=${encodeURIComponent(level)}`
        )
        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Failed to load programs."
                );
            }

            return response.json();

        })
        .then(data => {

            data.forEach(program => {

                const option =
                    document.createElement("option");

                option.value = program.id;
                option.textContent = program.name;

                programSelect.appendChild(option);

            });

        })
        .catch(error => {

            console.error(
                "Program loading error:",
                error
            );

        });

    });


    // =====================================================
    // PROGRAM → SEMESTER
    // =====================================================

    programSelect.addEventListener("change", function () {

        const programId = this.value;

        semesterSelect.innerHTML =
            '<option value="">Select Semester</option>';

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!programId) {
            return;
        }

        fetch(
            `${semestersUrl}?program=${programId}`
        )
        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Failed to load semesters."
                );
            }

            return response.json();

        })
        .then(data => {

            data.forEach(semester => {

                const option =
                    document.createElement("option");

                option.value = semester.id;
                option.textContent = semester.name;

                semesterSelect.appendChild(option);

            });

        })
        .catch(error => {

            console.error(
                "Semester loading error:",
                error
            );

        });

    });


    // =====================================================
    // SEMESTER → SUBJECT
    // =====================================================

    semesterSelect.addEventListener("change", function () {

        const semesterId = this.value;

        const programId =
            programSelect.value;

        subjectSelect.innerHTML =
            '<option value="">Select Subject</option>';

        if (!semesterId || !programId) {
            return;
        }

        fetch(
            `${subjectsUrl}?program=${programId}&semester=${semesterId}`
        )
        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Failed to load subjects."
                );
            }

            return response.json();

        })
        .then(data => {

            data.forEach(subject => {

                const option =
                    document.createElement("option");

                option.value = subject.id;
                option.textContent = subject.name;

                subjectSelect.appendChild(option);

            });

        })
        .catch(error => {

            console.error(
                "Subject loading error:",
                error
            );

        });

    });


    // =====================================================
    // CHECK QUESTION SIMILARITY
    // =====================================================

    checkSimilarityBtn.addEventListener(
        "click",
        function () {

            const text =
                questionText.value.trim();


            // ---------------------------------------------
            // Validate question
            // ---------------------------------------------

            if (!text) {

                alert(
                    "Please enter the question first."
                );

                questionText.focus();

                return;
            }


            // ---------------------------------------------
            // Validate Program
            // ---------------------------------------------

            if (!programSelect.value) {

                alert(
                    "Please select a Program first."
                );

                programSelect.focus();

                return;
            }


            // ---------------------------------------------
            // Validate Semester
            // ---------------------------------------------

            if (!semesterSelect.value) {

                alert(
                    "Please select a Semester first."
                );

                semesterSelect.focus();

                return;
            }


            // ---------------------------------------------
            // Validate Subject
            // ---------------------------------------------

            if (!subjectSelect.value) {

                alert(
                    "Please select a Subject first."
                );

                subjectSelect.focus();

                return;
            }


            // ---------------------------------------------
            // Start loading
            // ---------------------------------------------

            checkSimilarityBtn.disabled = true;

            similarityLoading.classList.remove(
                "d-none"
            );

            similarityResult.classList.add(
                "d-none"
            );


            // ---------------------------------------------
            // CSRF
            // ---------------------------------------------

            const csrfToken =
                document.querySelector(
                    "[name=csrfmiddlewaretoken]"
                ).value;


            // ---------------------------------------------
            // Form data
            // ---------------------------------------------

            const formData =
                new FormData();

            formData.append(
                "question_text",
                text
            );

            formData.append(
                "program",
                programSelect.value
            );

            formData.append(
                "semester",
                semesterSelect.value
            );

            formData.append(
                "subject",
                subjectSelect.value
            );


            // ---------------------------------------------
            // AJAX REQUEST
            // ---------------------------------------------

            fetch(
                similarityUrl,
                {
                    method: "POST",

                    headers: {
                        "X-CSRFToken": csrfToken
                    },

                    body: formData
                }
            )
            .then(response => {

                if (!response.ok) {

                    return response.json()
                        .then(data => {

                            throw new Error(
                                data.message ||
                                "Similarity request failed."
                            );

                        });

                }

                return response.json();

            })
            .then(data => {

                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "Similarity check failed."
                    );

                }


                // =========================================
                // NO SIMILAR QUESTIONS
                // =========================================

                if (!data.has_similar) {

                    if (similarityApproved) {
                        similarityApproved.value = "1";
                    }

                    similarityResult.innerHTML = `

                        <div class="alert alert-success">

                            <h6 class="fw-bold">
                                ✅ No Similar Question Found
                            </h6>

                            <p class="mb-0">

                                This question appears to be
                                sufficiently different from
                                your existing questions.

                            </p>

                        </div>

                    `;

                    similarityResult.classList.remove(
                        "d-none"
                    );

                    return;
                }


                // =========================================
                // SIMILAR QUESTIONS FOUND
                // =========================================

                let matchesHTML = "";


                data.matches.forEach(match => {

                    matchesHTML += `

                        <div class="card mb-2">

                            <div class="card-body">

                                <div class="d-flex
                                    justify-content-between
                                    align-items-start">

                                    <strong>
                                        Similarity:
                                        ${match.similarity}%
                                    </strong>

                                    <span
                                        class="badge bg-warning text-dark">

                                        Similar

                                    </span>

                                </div>

                                <p class="mb-0 mt-2">

                                    ${escapeHtml(
                                        match.question_text
                                    )}

                                </p>

                            </div>

                        </div>

                    `;

                });


                if (similarityApproved) {
                    similarityApproved.value = "0";
                }


                similarityResult.innerHTML = `

                    <div class="alert alert-warning">

                        <h6 class="fw-bold">

                            ⚠️ Similar Question(s) Found

                        </h6>

                        <p>

                            The following existing question(s)
                            are semantically similar to your
                            question.

                        </p>

                        ${matchesHTML}

                        <hr>

                        <p class="fw-bold">

                            Do you still want to add this
                            question?

                        </p>

                        <div class="d-flex gap-2">

                            <button
                                type="button"
                                id="cancelSimilarQuestion"
                                class="btn btn-secondary">

                                Cancel

                            </button>

                            <button
                                type="button"
                                id="keepSimilarQuestion"
                                class="btn btn-danger">

                                Keep Question

                            </button>

                        </div>

                    </div>

                `;

                similarityResult.classList.remove(
                    "d-none"
                );


                // =========================================
                // CANCEL
                // =========================================

                document
                    .getElementById(
                        "cancelSimilarQuestion"
                    )
                    .addEventListener(
                        "click",
                        function () {

                            if (similarityApproved) {
                                similarityApproved.value =
                                    "0";
                            }

                            similarityResult.classList.add(
                                "d-none"
                            );

                            questionText.focus();

                        }
                    );


                // =========================================
                // KEEP QUESTION
                // =========================================

                document
                    .getElementById(
                        "keepSimilarQuestion"
                    )
                    .addEventListener(
                        "click",
                        function () {

                            if (similarityApproved) {
                                similarityApproved.value =
                                    "1";
                            }

                            similarityResult.innerHTML = `

                                <div class="alert alert-info">

                                    ✅ Similarity warning
                                    acknowledged.

                                    <br>

                                    You can now save
                                    this question.

                                </div>

                            `;

                        }
                    );

            })
            .catch(error => {

                console.error(
                    "Similarity error:",
                    error
                );

                similarityResult.innerHTML = `

                    <div class="alert alert-danger">

                        ❌ Similarity check failed:

                        ${escapeHtml(
                            error.message
                        )}

                    </div>

                `;

                similarityResult.classList.remove(
                    "d-none"
                );

            })
            .finally(() => {

                checkSimilarityBtn.disabled = false;

                similarityLoading.classList.add(
                    "d-none"
                );

            });

        }
    );


    // =====================================================
    // RESET APPROVAL WHEN QUESTION CHANGES
    // =====================================================

    questionText.addEventListener(
        "input",
        function () {

            if (similarityApproved) {

                similarityApproved.value = "0";

            }

        }
    );


    // =====================================================
    // ESCAPE HTML
    // =====================================================

    function escapeHtml(text) {

        const div =
            document.createElement("div");

        div.textContent =
            text;

        return div.innerHTML;

    }

});



// =====================================================
// AI QUESTION CLASSIFICATION
// =====================================================

const aiClassifyBtn = document.getElementById(
    "aiClassifyBtn"
);

const aiLoading = document.getElementById(
    "aiLoading"
);

const aiResult = document.getElementById(
    "aiResult"
);

const aiBloom = document.getElementById(
    "aiBloom"
);

const aiDifficulty = document.getElementById(
    "aiDifficulty"
);

const aiQuestionType = document.getElementById(
    "aiQuestionType"
);

const questionTextField = document.getElementById(
    "id_question_text"
);


if (aiClassifyBtn) {

    aiClassifyBtn.addEventListener(
        "click",
        async function () {

            const questionText =
                questionTextField.value.trim();


            if (!questionText) {

                alert(
                    "Please enter the question first."
                );

                questionTextField.focus();

                return;
            }


            aiLoading.classList.remove(
                "d-none"
            );

            aiClassifyBtn.disabled = true;


            try {

                const formData =
                    new FormData();

                formData.append(
                    "question_text",
                    questionText
                );


                const response =
                    await fetch(
                        aiClassifyUrl,
                        {
                            method: "POST",

                            headers: {
                                "X-CSRFToken":
                                    getCookie("csrftoken")
                            },

                            body: formData
                        }
                    );


                const data =
                    await response.json();


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "AI classification failed."
                    );

                }


                // ---------------------------------
                // Bloom
                // ---------------------------------

                const bloomNames = {

                    "1": "Remember",
                    "2": "Understand",
                    "3": "Apply",
                    "4": "Analyze",
                    "5": "Evaluate",
                    "6": "Create"

                };


                aiBloom.textContent =
                    `${data.bloom_level} - ${
                        bloomNames[data.bloom_level]
                    }`;


                // ---------------------------------
                // Difficulty
                // ---------------------------------

                aiDifficulty.textContent =
                    data.difficulty
                        .charAt(0)
                        .toUpperCase() +
                    data.difficulty.slice(1);


                // ---------------------------------
                // Question Type
                // ---------------------------------

                const typeNames = {

                    "mcq":
                        "Multiple Choice Questions",

                    "ftq":
                        "Following the Questions",

                    "cs":
                        "Case Study"

                };


                aiQuestionType.textContent =
                    typeNames[data.question_type] ||
                    data.question_type;


                // Store AI result
                // for Apply button later

                aiResult.dataset.bloom =
                    data.bloom_level;

                aiResult.dataset.difficulty =
                    data.difficulty;

                aiResult.dataset.questionType =
                    data.question_type;


                aiResult.classList.remove(
                    "d-none"
                );

            }

            catch (error) {

                console.error(
                    "AI Error:",
                    error
                );

                alert(
                    "AI classification failed: " +
                    error.message
                );

            }

            finally {

                aiLoading.classList.add(
                    "d-none"
                );

                aiClassifyBtn.disabled =
                    false;

            }

        }
    );

}